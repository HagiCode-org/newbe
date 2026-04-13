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
3. If no diff exists, exit successfully as a no-op.
4. If a diff exists, rebase the generated patch onto `main`, create one automation commit, and push it directly to `main` with `GITHUB_TOKEN`.
5. Because `GITHUB_TOKEN` pushes do not fan out into other `push` workflows, explicitly dispatch `release.yml` on `main` after the direct push succeeds.
6. After the direct push succeeds, dispatch `HagiCode-org/index/.github/workflows/index-file-sync.yml` on `main` and wait for its terminal status.

The workflow reports success only when the direct push, the local release dispatch, and the downstream index sync path all complete successfully.

## Secret and permission contract

The in-repo publish path does not require a PAT anymore:

- `mirror-update.yml` pushes `main` with the built-in `GITHUB_TOKEN`.
- `mirror-update.yml` then explicitly triggers `release.yml` via `workflow_dispatch` so the main-branch publish still runs.

`NEWBE_GITHUB_PAT` remains optional only for the cross-repository `HagiCode-org/index` sync step:

- It must be allowed to dispatch and read workflow runs in `HagiCode-org/index`.

If the token is absent, the same-repository release dispatch still works, and only the cross-repository index sync step is skipped.

## Troubleshooting

- `GITHUB_TOKEN is required to dispatch release.yml`
  The built-in token is unavailable to the job, or workflow permissions are too narrow to call the Actions dispatch API.
- `Token missing or lacks permission to dispatch/read HagiCode-org/index workflows`
  The token can reach `newbe` but cannot dispatch or poll the downstream `index` workflow.
- `Mirror patch produced no staged changes on main`
  The generated diff became empty after rebasing onto `main`. Check whether another run already published the same batch.
- `Downstream run <id> completed with conclusion=<state>`
  The `index-file-sync.yml` workflow started, but it finished with `failure`, `cancelled`, or another non-`success` conclusion. Open that run and inspect its logs before retrying.
