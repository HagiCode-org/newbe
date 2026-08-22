# Mirror Update Automation

`mirror-update.yml` now publishes managed mirror changes directly to `main` after `invoke create-mirrors` completes. It no longer opens a pull request.

## Trigger rules

- `schedule`
- `workflow_dispatch`
- `push` to `mirror`

`push` to `main` is intentionally excluded. The workflow writes back to `main`, so re-listening to `main` would create a self-reinforcing publish loop.

When starting the workflow manually, set the optional `full_refresh` input to
`true` to remove all generated files under `docs/Mirrors/` and the
`tools/tools/123pan-sync-state.json` baseline before rebuilding from GitHub
releases and the manifest source.

## Publish behavior

1. Generate mirror content from the triggering ref.
2. Detect whether the working tree contains a real diff.
3. If no diff exists, exit successfully as a no-op and skip the `main`-branch release trigger.
4. If a diff exists, rebase the generated patch onto `main`, create one automation commit, and push it directly to `main` with `GITHUB_TOKEN`.
5. After the push succeeds, explicitly dispatch `newbe-deploy-gh-pages.yml` with `GITHUB_TOKEN`.

The workflow reports success when the direct publish succeeds.

## Release trigger

`mirror-update.yml` relies on the repository's normal `push` to `main` automation. As soon as the mirror commit lands on `main`, the release workflow configured on that branch can run on its own trigger.

## Summary states

The workflow summary now distinguishes these states:

- `Mirror publish: no-op`
- `Mirror publish: published`
- `Release follow-up: skipped (no-op publish)`
- `Release follow-up: gh-pages workflow dispatched`

This makes it clear whether a run ended before publication or after direct publish.

## Secret and permission contract

The in-repo publish and deployment-dispatch paths use the built-in `GITHUB_TOKEN`:

- the workflow has `contents: write` permission to push `main`
- the workflow has `actions: write` permission to dispatch the gh-pages workflow
- explicit dispatch avoids relying on a `GITHUB_TOKEN` push to trigger another workflow

## Troubleshooting

### Mirror patch produced no staged changes on main

The generated diff became empty after rebasing onto `main`. Check whether another run already published the same batch.
