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
4. If a diff exists, rebase the generated patch onto `main`, create one automation commit, and push it directly to `main`.
5. After the direct push succeeds, dispatch `HagiCode-org/index/.github/workflows/index-file-sync.yml` on `main` and wait for its terminal status.

The workflow reports success only when both the direct push and the downstream index sync complete successfully.

## Secret and permission contract

`NEWBE_GITHUB_PAT` must satisfy both halves of the chain:

- It must be allowed to push the automation commit to `HagiCode-org/newbe` on `main`.
- It must be allowed to dispatch and read workflow runs in `HagiCode-org/index`.

If the token cannot satisfy both requirements, the workflow fails fast before reporting success.

## Troubleshooting

- `NEWBE_GITHUB_PAT is required to push main`
  The secret is missing in `HagiCode-org/newbe`, or the job cannot read it.
- `Token missing or lacks permission to dispatch/read HagiCode-org/index workflows`
  The token can reach `newbe` but cannot dispatch or poll the downstream `index` workflow.
- `Mirror patch produced no staged changes on main`
  The generated diff became empty after rebasing onto `main`. Check whether another run already published the same batch.
- `Downstream run <id> completed with conclusion=<state>`
  The `index-file-sync.yml` workflow started, but it finished with `failure`, `cancelled`, or another non-`success` conclusion. Open that run and inspect its logs before retrying.
