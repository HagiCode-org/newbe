from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import workflow_dispatch


SUCCESS_RUN = {
    "id": 201,
    "html_url": "https://github.com/HagiCode-org/newbe/actions/runs/201",
    "status": "completed",
    "conclusion": "success",
    "head_branch": "main",
    "event": "workflow_dispatch",
    "created_at": "2099-04-07T10:00:00Z",
}


class FakeResponse:
    def __init__(self, status_code: int, payload: dict | None = None, text: str = ""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self) -> dict:
        return self._payload


class FakeSession:
    def __init__(self, responses: list[FakeResponse]):
        self._responses = list(responses)

    def request(self, method, url, headers=None, timeout=None, **kwargs):
        if not self._responses:
            raise AssertionError(f"Unexpected request: {method} {url}")
        return self._responses.pop(0)


class WorkflowDispatchTests(unittest.TestCase):
    def make_workflow_dir(self, content: str = "name: Release\non:\n  workflow_dispatch:\n"):
        tempdir = tempfile.TemporaryDirectory()
        workflow_dir = Path(tempdir.name) / ".github" / "workflows"
        workflow_dir.mkdir(parents=True)
        (workflow_dir / "release.yml").write_text(content, encoding="utf-8")
        return tempdir, workflow_dir

    def run_main(
        self,
        responses: list[FakeResponse],
        *extra_args: str,
        local_workflow_dir: Path | None = None,
        monotonic=None,
    ) -> tuple[int, str, str]:
        with tempfile.NamedTemporaryFile("r+", delete=False) as summary_file, tempfile.NamedTemporaryFile(
            "r+",
            delete=False,
        ) as output_file:
            summary_path = summary_file.name
            output_path = output_file.name

        try:
            args = [
                "--repo",
                "HagiCode-org/newbe",
                "--workflow",
                "release.yml",
                "--ref",
                "main",
                "--token",
                "test-token",
                "--label",
                "Release handoff",
                "--summary-file",
                summary_path,
                "--github-output",
                output_path,
                "--poll-interval-seconds",
                "0",
                *extra_args,
            ]
            if local_workflow_dir is not None:
                args.extend(["--local-workflow-dir", str(local_workflow_dir)])

            patches = [mock.patch("workflow_dispatch.time.sleep", return_value=None)]
            if monotonic is not None:
                patches.append(mock.patch("workflow_dispatch.time.monotonic", side_effect=monotonic))

            with patches[0]:
                if len(patches) == 2:
                    with patches[1]:
                        exit_code = workflow_dispatch.main(args, session=FakeSession(responses))
                else:
                    exit_code = workflow_dispatch.main(args, session=FakeSession(responses))

            with open(summary_path, "r", encoding="utf-8") as handle:
                summary = handle.read()
            with open(output_path, "r", encoding="utf-8") as handle:
                output = handle.read()
            return exit_code, summary, output
        finally:
            os.unlink(summary_path)
            os.unlink(output_path)

    def test_main_fails_before_dispatch_when_workflow_is_missing(self):
        with tempfile.TemporaryDirectory() as tempdir:
            workflow_dir = Path(tempdir) / ".github" / "workflows"
            workflow_dir.mkdir(parents=True)
            exit_code, summary, output = self.run_main([], local_workflow_dir=workflow_dir)

        self.assertEqual(exit_code, 1)
        self.assertIn("failed before run discovery", summary)
        self.assertIn("does not exist under", summary)
        self.assertIn("result=failed", output)

    def test_main_surfaces_422_contract_diagnostics(self):
        tempdir, workflow_dir = self.make_workflow_dir()
        try:
            exit_code, summary, output = self.run_main(
                [
                    FakeResponse(
                        422,
                        payload={"message": "Required input missing: channel"},
                        text='{"message":"Required input missing: channel"}',
                    ),
                ],
                "--inputs-json",
                '{"channel":"stable"}',
                local_workflow_dir=workflow_dir,
            )
        finally:
            tempdir.cleanup()

        self.assertEqual(exit_code, 1)
        self.assertIn("GitHub rejected the workflow_dispatch request with 422", summary)
        self.assertIn('-Inputs:{"channel":"stable"}', summary.replace(" ", ""))
        self.assertIn("Required input missing: channel", summary)
        self.assertIn("result=failed", output)

    def test_main_success_discovers_and_reports_run(self):
        tempdir, workflow_dir = self.make_workflow_dir()
        try:
            exit_code, summary, output = self.run_main(
                [
                    FakeResponse(204),
                    FakeResponse(200, {"workflow_runs": [dict(SUCCESS_RUN, status="queued", conclusion=None)]}),
                    FakeResponse(200, SUCCESS_RUN),
                ],
                local_workflow_dir=workflow_dir,
            )
        finally:
            tempdir.cleanup()

        self.assertEqual(exit_code, 0)
        self.assertIn("Result: success", summary)
        self.assertIn("Local workflow file:", summary)
        self.assertIn("run_id=201", output)
        self.assertIn("run_conclusion=success", output)

    def test_main_returns_failure_for_non_success_conclusion(self):
        tempdir, workflow_dir = self.make_workflow_dir()
        try:
            exit_code, summary, output = self.run_main(
                [
                    FakeResponse(204),
                    FakeResponse(200, {"workflow_runs": [dict(SUCCESS_RUN, status="queued", conclusion=None)]}),
                    FakeResponse(200, dict(SUCCESS_RUN, conclusion="failure")),
                ],
                local_workflow_dir=workflow_dir,
            )
        finally:
            tempdir.cleanup()

        self.assertEqual(exit_code, 1)
        self.assertIn("Result: failed", summary)
        self.assertIn("Conclusion: failure", summary)
        self.assertIn("run_conclusion=failure", output)

    def test_main_times_out_when_run_never_finishes(self):
        tempdir, workflow_dir = self.make_workflow_dir()
        try:
            exit_code, summary, output = self.run_main(
                [
                    FakeResponse(204),
                    FakeResponse(200, {"workflow_runs": [dict(SUCCESS_RUN, status="queued", conclusion=None)]}),
                    FakeResponse(200, dict(SUCCESS_RUN, status="in_progress", conclusion=None)),
                ],
                "--discovery-timeout-seconds",
                "1",
                "--run-timeout-seconds",
                "1",
                local_workflow_dir=workflow_dir,
                monotonic=[0, 0, 0, 0, 2],
            )
        finally:
            tempdir.cleanup()

        self.assertEqual(exit_code, 1)
        self.assertIn("Result: failed", summary)
        self.assertIn("Conclusion: pending", summary)
        self.assertIn("run_id=201", output)


if __name__ == "__main__":
    unittest.main()
