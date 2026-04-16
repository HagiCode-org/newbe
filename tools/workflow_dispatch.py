from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests

DEFAULT_DISCOVERY_TIMEOUT_SECONDS = 120
DEFAULT_RUN_TIMEOUT_SECONDS = 1800
DEFAULT_POLL_INTERVAL_SECONDS = 10
API_VERSION = "2022-11-28"


class WorkflowDispatchError(RuntimeError):
    def __init__(self, message: str, run: "WorkflowRun | None" = None):
        super().__init__(message)
        self.run = run


class PermissionContractError(WorkflowDispatchError):
    pass


class WorkflowValidationError(WorkflowDispatchError):
    pass


class DispatchContractError(WorkflowDispatchError):
    pass


class RunDiscoveryTimeoutError(WorkflowDispatchError):
    pass


class RunCompletionTimeoutError(WorkflowDispatchError):
    pass


class DownstreamRunFailedError(WorkflowDispatchError):
    pass


class GitHubApiError(WorkflowDispatchError):
    def __init__(self, status_code: int, message: str, response_body: str):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


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


@dataclass
class DispatchContext:
    label: str
    repo: str
    workflow: str
    ref: str
    inputs: dict[str, Any] | None
    local_workflow_path: str | None


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dispatch a GitHub Actions workflow and wait for its run to finish.",
    )
    parser.add_argument("--repo", required=True, help="Target repository in owner/name form.")
    parser.add_argument("--workflow", required=True, help="Workflow file name or identifier.")
    parser.add_argument("--ref", required=True, help="Target branch or tag name.")
    parser.add_argument("--label", default="Workflow dispatch", help="Summary label.")
    parser.add_argument("--inputs-json", help="Optional workflow inputs as a JSON object string.")
    parser.add_argument(
        "--local-workflow-dir",
        help="Optional local .github/workflows directory used for same-repository validation.",
    )
    parser.add_argument("--token", help="GitHub token with workflow dispatch visibility.")
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
        help="Maximum time to wait for the dispatched run to appear.",
    )
    parser.add_argument(
        "--run-timeout-seconds",
        type=int,
        default=DEFAULT_RUN_TIMEOUT_SECONDS,
        help="Maximum time to wait for the dispatched run to finish.",
    )
    parser.add_argument(
        "--poll-interval-seconds",
        type=int,
        default=DEFAULT_POLL_INTERVAL_SECONDS,
        help="Polling interval for run discovery and completion checks.",
    )
    parser.add_argument("--summary-file", help="Path to a GitHub step summary file.")
    parser.add_argument("--github-output", help="Path to a GitHub output file.")
    return parser.parse_args(argv)


def parse_github_timestamp(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def parse_inputs_json(raw_inputs: str | None) -> dict[str, Any] | None:
    if not raw_inputs:
        return None

    try:
        payload = json.loads(raw_inputs)
    except json.JSONDecodeError as exc:
        raise WorkflowValidationError(
            f"Workflow inputs must be valid JSON. Received: {raw_inputs}",
        ) from exc

    if not isinstance(payload, dict):
        raise WorkflowValidationError("Workflow inputs JSON must decode to an object.")

    invalid_keys = [key for key in payload.keys() if not isinstance(key, str)]
    if invalid_keys:
        raise WorkflowValidationError(
            f"Workflow input keys must be strings. Invalid keys: {invalid_keys}",
        )

    return payload


def build_headers(token: str) -> dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": API_VERSION,
    }


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True)


def format_inputs(inputs: dict[str, Any] | None) -> str:
    return compact_json(inputs) if inputs else "(none)"


def extract_response_details(response: requests.Response) -> str:
    text = response.text.strip()
    if not text:
        return "(empty response body)"
    try:
        return compact_json(response.json())
    except ValueError:
        return re.sub(r"\s+", " ", text)


def github_request(
    session: requests.Session,
    method: str,
    url: str,
    token: str,
    repo: str,
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
            f"Token missing or lacks permission to dispatch/read workflows in {repo}. "
            "Confirm the token can use the Actions API and that the job grants actions: write.",
        )
    if response.status_code >= 400:
        raise GitHubApiError(
            response.status_code,
            f"GitHub API request failed: {response.status_code}",
            extract_response_details(response),
        )
    return response


def list_available_workflows(workflow_dir: Path) -> list[str]:
    patterns = ("*.yml", "*.yaml")
    found: list[str] = []
    for pattern in patterns:
        found.extend(path.name for path in workflow_dir.glob(pattern) if path.is_file())
    return sorted(set(found))


def resolve_local_workflow_path(workflow: str, local_workflow_dir: str) -> Path:
    workflow_id = workflow.strip()
    workflow_dir = Path(local_workflow_dir)
    if not workflow_id:
        available = ", ".join(list_available_workflows(workflow_dir)) or "(none found)"
        raise WorkflowValidationError(
            "Workflow identifier is not configured. Set the repository variable for the release workflow "
            f"to a file inside {workflow_dir}. Available workflows: {available}",
        )

    if not workflow_dir.exists():
        raise WorkflowValidationError(f"Local workflow directory not found: {workflow_dir}")

    workflow_path = Path(workflow_id)
    candidates: list[Path] = []
    if workflow_path.is_absolute():
        candidates.append(workflow_path)
    elif len(workflow_path.parts) >= 2 and workflow_path.parts[:2] == (".github", "workflows"):
        candidates.append(workflow_dir.parent.parent / workflow_path)
    else:
        candidates.append(workflow_dir / workflow_path.name)
        candidates.append(workflow_dir.parent.parent / workflow_path)

    for candidate in candidates:
        if candidate.exists():
            return candidate

    available = ", ".join(list_available_workflows(workflow_dir)) or "(none found)"
    raise WorkflowValidationError(
        f"Configured workflow '{workflow_id}' does not exist under {workflow_dir}. "
        f"Available workflows: {available}",
    )


def validate_local_workflow(workflow: str, local_workflow_dir: str) -> str:
    candidate = resolve_local_workflow_path(workflow, local_workflow_dir)
    content = candidate.read_text(encoding="utf-8")
    if not re.search(r"(?m)^\s*workflow_dispatch\s*:", content):
        raise WorkflowValidationError(
            f"Workflow '{workflow}' exists at {candidate} but does not declare workflow_dispatch. "
            "Add a manual trigger before using it as a release handoff target.",
        )
    return str(candidate)


def dispatch_workflow(
    session: requests.Session,
    api_base_url: str,
    repo: str,
    workflow: str,
    ref: str,
    token: str,
    inputs: dict[str, Any] | None,
) -> datetime:
    dispatched_at = datetime.now(timezone.utc)
    payload: dict[str, Any] = {"ref": ref}
    if inputs:
        payload["inputs"] = inputs

    try:
        github_request(
            session,
            "POST",
            f"{api_base_url}/repos/{repo}/actions/workflows/{workflow}/dispatches",
            token,
            repo,
            json=payload,
        )
    except GitHubApiError as exc:
        if exc.status_code == 422:
            raise DispatchContractError(
                "GitHub rejected the workflow_dispatch request with 422. Check that the workflow "
                "identifier is correct, the ref contains the workflow file, workflow_dispatch is enabled, "
                f"and the configured inputs match the target contract. GitHub response: {exc.response_body}",
            ) from exc
        if exc.status_code == 404:
            raise DispatchContractError(
                "GitHub could not resolve the target workflow dispatch endpoint. Check that the repository, "
                f"workflow identifier, and ref are correct. GitHub response: {exc.response_body}",
            ) from exc
        raise WorkflowDispatchError(
            f"GitHub dispatch request failed with status {exc.status_code}. Response: {exc.response_body}",
        ) from exc

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
        repo,
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
        repo,
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
            handle.write(f"{key}={compact_json(value) if isinstance(value, (dict, list)) else value}\n")


def format_summary(
    context: DispatchContext,
    result: str,
    run: WorkflowRun | None = None,
    error: str | None = None,
) -> list[str]:
    lines = [
        f"### {context.label}",
        f"- Result: {result}",
        f"- Repository: {context.repo}",
        f"- Workflow: {context.workflow or '(unset)'}",
        f"- Ref: {context.ref}",
        f"- Inputs: {format_inputs(context.inputs)}",
    ]
    if context.local_workflow_path:
        lines.append(f"- Local workflow file: `{context.local_workflow_path}`")
    if run:
        lines.extend(
            [
                f"- Run ID: `{run.run_id}`",
                f"- Run URL: {run.html_url}",
                f"- Status: {run.status}",
                f"- Conclusion: {run.conclusion or 'pending'}",
            ],
        )
    if error:
        lines.append(f"- Error: {error}")
    return lines


def resolve_token(args: argparse.Namespace) -> str:
    if args.token:
        return args.token
    token = os.environ.get(args.token_env, "")
    if token:
        return token
    raise PermissionContractError(
        f"GitHub token not found. Provide --token or set ${args.token_env}.",
    )


def dispatch_and_wait(
    session: requests.Session,
    args: argparse.Namespace,
    token: str,
    inputs: dict[str, Any] | None,
) -> tuple[WorkflowRun, str | None]:
    local_workflow_path = None
    if args.local_workflow_dir:
        local_workflow_path = validate_local_workflow(args.workflow, args.local_workflow_dir)

    dispatched_at = dispatch_workflow(
        session,
        args.api_base_url,
        args.repo,
        args.workflow,
        args.ref,
        token,
        inputs,
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
    return (
        poll_run_completion(
            session,
            args.api_base_url,
            args.repo,
            token,
            run,
            args.run_timeout_seconds,
            args.poll_interval_seconds,
        ),
        local_workflow_path,
    )


def main(argv: list[str] | None = None, session: requests.Session | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    active_session = session or requests.Session()
    inputs: dict[str, Any] | None = None
    local_workflow_path: str | None = None

    try:
        token = resolve_token(args)
        inputs = parse_inputs_json(args.inputs_json)
        run, local_workflow_path = dispatch_and_wait(active_session, args, token, inputs)
        context = DispatchContext(
            label=args.label,
            repo=args.repo,
            workflow=args.workflow,
            ref=args.ref,
            inputs=inputs,
            local_workflow_path=local_workflow_path,
        )
        append_summary(args.summary_file, format_summary(context, "success", run=run))
        write_github_output(
            args.github_output,
            {
                "result": "success",
                "run_id": run.run_id,
                "run_url": run.html_url,
                "run_status": run.status,
                "run_conclusion": run.conclusion or "",
            },
        )
        print(f"Workflow dispatch succeeded: run_id={run.run_id} conclusion={run.conclusion}")
        return 0
    except WorkflowDispatchError as exc:
        context = DispatchContext(
            label=args.label,
            repo=args.repo,
            workflow=args.workflow,
            ref=args.ref,
            inputs=inputs,
            local_workflow_path=local_workflow_path,
        )
        result = "failed" if exc.run else "failed before run discovery"
        append_summary(args.summary_file, format_summary(context, result, run=exc.run, error=str(exc)))
        output_values: dict[str, Any] = {"result": "failed"}
        if exc.run:
            output_values.update(
                {
                    "run_id": exc.run.run_id,
                    "run_url": exc.run.html_url,
                    "run_status": exc.run.status,
                    "run_conclusion": exc.run.conclusion or "",
                },
            )
        write_github_output(args.github_output, output_values)
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        if session is None:
            active_session.close()


if __name__ == "__main__":
    raise SystemExit(main())
