from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import requests

DEFAULT_DISCOVERY_TIMEOUT_SECONDS = 120
DEFAULT_RUN_TIMEOUT_SECONDS = 1800
DEFAULT_POLL_INTERVAL_SECONDS = 10
API_VERSION = "2022-11-28"


class IndexSyncError(RuntimeError):
    def __init__(self, message: str, run: "WorkflowRun | None" = None):
        super().__init__(message)
        self.run = run


class PermissionContractError(IndexSyncError):
    pass


class RunDiscoveryTimeoutError(IndexSyncError):
    pass


class RunCompletionTimeoutError(IndexSyncError):
    pass


class DownstreamRunFailedError(IndexSyncError):
    pass


@dataclass
class WorkflowRun:
    run_id: int
    html_url: str
    status: str
    conclusion: str | None
    head_branch: str
    event: str
    created_at: datetime

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "WorkflowRun":
        return cls(
            run_id=payload["id"],
            html_url=payload["html_url"],
            status=payload["status"],
            conclusion=payload.get("conclusion"),
            head_branch=payload["head_branch"],
            event=payload["event"],
            created_at=parse_github_timestamp(payload["created_at"]),
        )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dispatch repos/index index-file-sync workflow and wait for completion.",
    )
    parser.add_argument("--repo", required=True, help="Target repository in owner/name form.")
    parser.add_argument("--workflow", default="index-file-sync.yml", help="Workflow file name.")
    parser.add_argument("--ref", default="main", help="Target branch or tag name.")
    parser.add_argument("--token", help="GitHub token with push/dispatch visibility.")
    parser.add_argument(
        "--token-env",
        default="GH_TOKEN",
        help="Environment variable used when --token is omitted.",
    )
    parser.add_argument(
        "--api-base-url",
        default=os.environ.get("GITHUB_API_URL", "https://api.github.com"),
        help="GitHub API base URL.",
    )
    parser.add_argument(
        "--discovery-timeout-seconds",
        type=int,
        default=DEFAULT_DISCOVERY_TIMEOUT_SECONDS,
        help="Maximum time to wait for the downstream run to appear.",
    )
    parser.add_argument(
        "--run-timeout-seconds",
        type=int,
        default=DEFAULT_RUN_TIMEOUT_SECONDS,
        help="Maximum time to wait for the downstream run to finish.",
    )
    parser.add_argument(
        "--poll-interval-seconds",
        type=int,
        default=DEFAULT_POLL_INTERVAL_SECONDS,
        help="Polling interval for run discovery and completion checks.",
    )
    parser.add_argument(
        "--summary-file",
        help="Path to a GitHub step summary file.",
    )
    parser.add_argument(
        "--github-output",
        help="Path to a GitHub output file.",
    )
    return parser.parse_args(argv)


def parse_github_timestamp(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def build_headers(token: str) -> dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": API_VERSION,
    }


def github_request(
    session: requests.Session,
    method: str,
    url: str,
    token: str,
    **kwargs: Any,
) -> requests.Response:
    response = session.request(
        method,
        url,
        headers=build_headers(token),
        timeout=30,
        **kwargs,
    )
    if response.status_code in (401, 403):
        raise PermissionContractError(
            "Token missing or lacks permission to dispatch/read HagiCode-org/index workflows.",
        )
    if response.status_code >= 400:
        details = response.text.strip()
        raise IndexSyncError(f"GitHub API request failed: {response.status_code} {details}")
    return response


def dispatch_workflow(
    session: requests.Session,
    api_base_url: str,
    repo: str,
    workflow: str,
    ref: str,
    token: str,
) -> datetime:
    dispatched_at = datetime.now(timezone.utc)
    github_request(
        session,
        "POST",
        f"{api_base_url}/repos/{repo}/actions/workflows/{workflow}/dispatches",
        token,
        json={"ref": ref},
    )
    return dispatched_at


def list_workflow_runs(
    session: requests.Session,
    api_base_url: str,
    repo: str,
    workflow: str,
    ref: str,
    token: str,
) -> list[WorkflowRun]:
    response = github_request(
        session,
        "GET",
        f"{api_base_url}/repos/{repo}/actions/workflows/{workflow}/runs",
        token,
        params={"event": "workflow_dispatch", "branch": ref, "per_page": 20},
    )
    payload = response.json()
    return [WorkflowRun.from_payload(run) for run in payload.get("workflow_runs", [])]


def find_dispatched_run(
    session: requests.Session,
    api_base_url: str,
    repo: str,
    workflow: str,
    ref: str,
    token: str,
    dispatched_at: datetime,
    discovery_timeout_seconds: int,
    poll_interval_seconds: int,
) -> WorkflowRun:
    deadline = time.monotonic() + discovery_timeout_seconds
    not_before = dispatched_at - timedelta(seconds=5)

    while time.monotonic() <= deadline:
        for run in list_workflow_runs(session, api_base_url, repo, workflow, ref, token):
            if run.event != "workflow_dispatch":
                continue
            if run.head_branch != ref:
                continue
            if run.created_at < not_before:
                continue
            return run
        time.sleep(poll_interval_seconds)

    raise RunDiscoveryTimeoutError(
        f"Timed out waiting for {repo}:{workflow} to create a new workflow run.",
    )


def get_run(
    session: requests.Session,
    api_base_url: str,
    repo: str,
    run_id: int,
    token: str,
) -> WorkflowRun:
    response = github_request(
        session,
        "GET",
        f"{api_base_url}/repos/{repo}/actions/runs/{run_id}",
        token,
    )
    return WorkflowRun.from_payload(response.json())


def poll_run_completion(
    session: requests.Session,
    api_base_url: str,
    repo: str,
    token: str,
    run: WorkflowRun,
    run_timeout_seconds: int,
    poll_interval_seconds: int,
) -> WorkflowRun:
    deadline = time.monotonic() + run_timeout_seconds

    while time.monotonic() <= deadline:
        current_run = get_run(session, api_base_url, repo, run.run_id, token)
        if current_run.status == "completed":
            if current_run.conclusion != "success":
                raise DownstreamRunFailedError(
                    f"Downstream run {current_run.run_id} completed with conclusion={current_run.conclusion}.",
                    run=current_run,
                )
            return current_run
        time.sleep(poll_interval_seconds)

    raise RunCompletionTimeoutError(
        f"Timed out waiting for downstream run {run.run_id} to complete.",
        run=run,
    )


def append_summary(summary_file: str | None, lines: list[str]) -> None:
    if not summary_file:
        return
    with open(summary_file, "a", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def write_github_output(output_file: str | None, values: dict[str, Any]) -> None:
    if not output_file:
        return
    with open(output_file, "a", encoding="utf-8") as handle:
        for key, value in values.items():
            handle.write(f"{key}={json.dumps(value) if isinstance(value, (dict, list)) else value}\n")


def sync_index_workflow(
    session: requests.Session,
    args: argparse.Namespace,
    token: str,
) -> WorkflowRun:
    dispatched_at = dispatch_workflow(
        session,
        args.api_base_url,
        args.repo,
        args.workflow,
        args.ref,
        token,
    )
    run = find_dispatched_run(
        session,
        args.api_base_url,
        args.repo,
        args.workflow,
        args.ref,
        token,
        dispatched_at,
        args.discovery_timeout_seconds,
        args.poll_interval_seconds,
    )
    return poll_run_completion(
        session,
        args.api_base_url,
        args.repo,
        token,
        run,
        args.run_timeout_seconds,
        args.poll_interval_seconds,
    )


def format_summary(repo: str, workflow: str, ref: str, run: WorkflowRun, result: str) -> list[str]:
    return [
        "### Index sync",
        f"- Result: {result}",
        f"- Repository: {repo}",
        f"- Workflow: {workflow}",
        f"- Ref: {ref}",
        f"- Run ID: `{run.run_id}`",
        f"- Run URL: {run.html_url}",
        f"- Status: {run.status}",
        f"- Conclusion: {run.conclusion or 'pending'}",
    ]


def resolve_token(args: argparse.Namespace) -> str:
    if args.token:
        return args.token
    token = os.environ.get(args.token_env, "")
    if token:
        return token
    raise PermissionContractError(
        f"GitHub token not found. Provide --token or set ${args.token_env}.",
    )


def main(argv: list[str] | None = None, session: requests.Session | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    active_session = session or requests.Session()
    discovered_run: WorkflowRun | None = None

    try:
        token = resolve_token(args)
        run = sync_index_workflow(active_session, args, token)
        append_summary(
            args.summary_file,
            format_summary(args.repo, args.workflow, args.ref, run, "success"),
        )
        write_github_output(
            args.github_output,
            {
                "run_id": run.run_id,
                "run_url": run.html_url,
                "run_status": run.status,
                "run_conclusion": run.conclusion or "",
            },
        )
        print(f"Downstream workflow succeeded: run_id={run.run_id} conclusion={run.conclusion}")
        return 0
    except IndexSyncError as exc:
        discovered_run = exc.run
        if discovered_run:
            append_summary(
                args.summary_file,
                format_summary(args.repo, args.workflow, args.ref, discovered_run, "failed"),
            )
            write_github_output(
                args.github_output,
                {
                    "run_id": discovered_run.run_id,
                    "run_url": discovered_run.html_url,
                    "run_status": discovered_run.status,
                    "run_conclusion": discovered_run.conclusion or "",
                },
            )
        else:
            append_summary(
                args.summary_file,
                [
                    "### Index sync",
                    "- Result: failed before run discovery",
                    f"- Repository: {args.repo}",
                    f"- Workflow: {args.workflow}",
                    f"- Ref: {args.ref}",
                    f"- Error: {exc}",
                ],
            )
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        if session is None:
            active_session.close()


if __name__ == "__main__":
    raise SystemExit(main())
