# Mirror Update Automation

`mirror-update.yml` now publishes managed mirror changes directly to `main` after `invoke create-mirrors` completes. It no longer opens a pull request.

## Trigger rules

- `schedule`
- `workflow_dispatch`
- `push` to `mirror`

`push` to `main` is intentionally excluded. The workflow writes back to `main`, so re-listening to `main` would create a self-reinforcing publish loop.

## Publish behavior

1. Generate mirror content from the triggering ref.
2. Detect whether the working tree contains a real diff.
3. If no diff exists, exit successfully as a no-op and skip both the `main`-branch release trigger and index sync.
4. If a diff exists, rebase the generated patch onto `main`, create one automation commit, and push it directly to `main` with `GITHUB_TOKEN`.
5. The push to `main` is the release trigger. `mirror-update.yml` does not dispatch any same-repository release workflow itself.
6. After the direct push succeeds, the workflow may continue to the optional `HagiCode-org/index` sync dispatch.

The workflow reports success when the direct publish succeeds. Index sync still remains optional because it depends on `NEWBE_GITHUB_PAT`.

## Release trigger

`mirror-update.yml` relies on the repository's normal `push` to `main` automation. As soon as the mirror commit lands on `main`, the release workflow configured on that branch can run on its own trigger.

## Summary states

The workflow summary now distinguishes these states:

- `Mirror publish: no-op`
- `Mirror publish: published`
- `Release follow-up: skipped (no-op publish)`
- `Release follow-up: delegated to main push`
- `Index sync: success` or `Index sync: skipped`

This makes it clear whether a run ended before publication, after direct publish, or after the optional downstream index sync attempt.

## Secret and permission contract

The in-repo publish path does not require a PAT:

- `mirror-update.yml` pushes `main` with the built-in `GITHUB_TOKEN`

`NEWBE_GITHUB_PAT` remains optional only for the cross-repository `HagiCode-org/index` sync step:

- it must be allowed to dispatch and read workflow runs in `HagiCode-org/index`
- if the token is absent, the index sync step is reported as skipped

## Troubleshooting

### Mirror patch produced no staged changes on main

The generated diff became empty after rebasing onto `main`. Check whether another run already published the same batch.
