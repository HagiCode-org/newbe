from __future__ import annotations

import os
import tempfile
import unittest
from unittest import mock

import dispatch_index_sync


SUCCESS_RUN = {
    "id": 101,
    "html_url": "https://github.com/HagiCode-org/index/actions/runs/101",
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


class DispatchIndexSyncTests(unittest.TestCase):
    def run_main(self, responses: list[FakeResponse], *extra_args: str, monotonic=None) -> tuple[int, str, str]:
        with tempfile.NamedTemporaryFile("r+", delete=False) as summary_file, tempfile.NamedTemporaryFile(
            "r+",
            delete=False,
        ) as output_file:
            summary_path = summary_file.name
            output_path = output_file.name

        try:
            args = [
                "--repo",
                "HagiCode-org/index",
                "--workflow",
                "index-file-sync.yml",
                "--ref",
                "main",
                "--token",
                "test-token",
                "--summary-file",
                summary_path,
                "--github-output",
                output_path,
                "--poll-interval-seconds",
                "0",
                *extra_args,
            ]
            patches = [mock.patch("dispatch_index_sync.time.sleep", return_value=None)]
            if monotonic is not None:
                patches.append(mock.patch("dispatch_index_sync.time.monotonic", side_effect=monotonic))

            with patches[0]:
                if len(patches) == 2:
                    with patches[1]:
                        exit_code = dispatch_index_sync.main(args, session=FakeSession(responses))
                else:
                    exit_code = dispatch_index_sync.main(args, session=FakeSession(responses))

            with open(summary_path, "r", encoding="utf-8") as handle:
                summary = handle.read()
            with open(output_path, "r", encoding="utf-8") as handle:
                output = handle.read()
            return exit_code, summary, output
        finally:
            os.unlink(summary_path)
            os.unlink(output_path)

    def test_main_success_writes_summary_and_outputs(self):
        exit_code, summary, output = self.run_main(
            [
                FakeResponse(204),
                FakeResponse(200, {"workflow_runs": [dict(SUCCESS_RUN, status="queued", conclusion=None)]}),
                FakeResponse(200, SUCCESS_RUN),
            ],
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("Result: success", summary)
        self.assertIn("Run ID: `101`", summary)
        self.assertIn("run_id=101", output)
        self.assertIn("run_conclusion=success", output)

    def test_main_fails_fast_when_permission_contract_is_missing(self):
        exit_code, summary, output = self.run_main(
            [
                FakeResponse(403, text="Forbidden"),
            ],
        )

        self.assertEqual(exit_code, 1)
        self.assertIn("failed before run discovery", summary)
        self.assertEqual(output, "")

    def test_main_fails_when_downstream_run_times_out(self):
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
            monotonic=[0, 0, 0, 0, 2],
        )

        self.assertEqual(exit_code, 1)
        self.assertIn("Result: failed", summary)
        self.assertIn("Conclusion: pending", summary)
        self.assertIn("run_id=101", output)

    def test_main_returns_failure_for_non_success_conclusion(self):
        exit_code, summary, output = self.run_main(
            [
                FakeResponse(204),
                FakeResponse(200, {"workflow_runs": [dict(SUCCESS_RUN, status="queued", conclusion=None)]}),
                FakeResponse(200, dict(SUCCESS_RUN, conclusion="failure")),
            ],
        )

        self.assertEqual(exit_code, 1)
        self.assertIn("Result: failed", summary)
        self.assertIn("Conclusion: failure", summary)
        self.assertIn("run_conclusion=failure", output)


if __name__ == "__main__":
    unittest.main()
