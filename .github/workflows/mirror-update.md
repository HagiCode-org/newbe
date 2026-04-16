# Mirror Update Automation

`mirror-update.yml` now publishes managed mirror changes directly to `main` after `invoke create-mirrors` completes. It no longer opens a pull request.

## Trigger rules

- `schedule`
- `workflow_dispatch`
- `push` to `mirror`

`push` to `main` is intentionally excluded. The workflow writes back to `main`, so re-listening to `main` would create a self-reinforcing publish loop.

## Release behavior

1. Generate mirror content from the triggering ref.
2. Detect whether the working tree contains a real diff.
3. If no diff exists, exit successfully as a no-op and skip both release handoff and index sync.
4. If a diff exists, rebase the generated patch onto `main`, create one automation commit, and push it directly to `main` with `GITHUB_TOKEN`.
5. After the direct push succeeds, validate the configured same-repository release workflow contract, dispatch it with the configured ref and optional inputs, then wait for the dispatched run to finish.
6. Only after the release handoff succeeds may the workflow continue to the optional `HagiCode-org/index` sync dispatch.

The workflow reports end-to-end success only when the direct publish succeeds and the release handoff reaches a `success` conclusion. Index sync still remains optional because it depends on `NEWBE_GITHUB_PAT`.

## Release handoff configuration

Mirror publish no longer assumes a hardcoded `release.yml`. Maintainers must configure the release handoff explicitly with repository variables:

- `NEWBE_RELEASE_WORKFLOW`: required for publish runs; the workflow file name or path under `.github/workflows/`, for example `release.yml` or `.github/workflows/release.yml`
- `NEWBE_RELEASE_WORKFLOW_REF`: optional; defaults to `main` when omitted
- `NEWBE_RELEASE_WORKFLOW_INPUTS_JSON`: optional; a JSON object string passed as `workflow_dispatch.inputs`

The helper validates the configured workflow before it sends the GitHub dispatch POST:

- the workflow identifier must be present
- the referenced file must exist under `.github/workflows/`
- the workflow file must declare `workflow_dispatch`

If any of those checks fail, the run stops before the API call and the step summary records the exact configuration problem.

## Summary states

The workflow summary now distinguishes these states:

- `Mirror publish: no-op`
- `Mirror publish: published`
- `Release handoff: skipped (no-op publish)`
- `Release handoff: success`
- `Release handoff: failed before run discovery`
- `Release handoff: failed`
- `Index sync: success` or `Index sync: skipped`

This makes it clear whether a run ended before publication, after direct publish, during release handoff validation/dispatch, or after downstream completion polling.

## Secret and permission contract

The in-repo publish path does not require a PAT:

- `mirror-update.yml` pushes `main` with the built-in `GITHUB_TOKEN`
- the same `GITHUB_TOKEN` dispatches and observes the configured same-repository release workflow

The job needs `actions: write` so it can dispatch workflows and poll their runs.

`NEWBE_GITHUB_PAT` remains optional only for the cross-repository `HagiCode-org/index` sync step:

- it must be allowed to dispatch and read workflow runs in `HagiCode-org/index`
- if the token is absent, release handoff still runs and the index sync step is reported as skipped

## Troubleshooting

### Missing or invalid release workflow configuration

If the summary shows `failed before run discovery`, check:

- `NEWBE_RELEASE_WORKFLOW` is set and matches an actual file under `.github/workflows/`
- the target workflow file contains a `workflow_dispatch` trigger
- `NEWBE_RELEASE_WORKFLOW_REF` points to a branch or tag that contains that workflow file
- `NEWBE_RELEASE_WORKFLOW_INPUTS_JSON` is valid JSON and matches the target workflow's input contract

The helper prints the workflow identifier, ref, input payload, and GitHub response so maintainers can distinguish missing workflow files from ref or input mismatches.

### Dispatch returns 401 or 403

`Token missing or lacks permission to dispatch/read workflows in <repo>` means the token cannot use the Actions API. Confirm:

- the job permissions include `actions: write`
- the token is not overridden with a narrower scope
- organization or repository policies are not blocking workflow dispatch or workflow run reads

### Dispatch returns 422

A 422 response usually means the dispatch contract does not match the target workflow. Check:

- the configured workflow identifier still matches the file in `.github/workflows/`
- the configured ref contains the workflow file
- the target workflow exposes `workflow_dispatch`
- the configured inputs JSON includes the required keys and value shapes

### Mirror patch produced no staged changes on main

The generated diff became empty after rebasing onto `main`. Check whether another run already published the same batch.

### Downstream run completed with a non-success conclusion

When the release or index handoff run is created but finishes with `failure`, `cancelled`, or times out, open that run URL from the step summary and inspect its logs before retrying.
