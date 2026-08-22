# Mirror Update Automation

`mirror-update.yml` publishes managed mirror changes directly to `main` after `invoke create-mirrors` completes. It no longer opens a pull request.

## Trigger rules

- `schedule`
- `workflow_dispatch`
- `push` to `mirror`

`push` to `main` is intentionally excluded. The workflow writes back to `main`, so re-listening to `main` would create a self-reinforcing publish loop.

## Change decision (dual-source)

A publish is triggered when **either** the source content or the corresponding 123pan resource changes. This prevents stale mirrors when 123pan resources update while the source repository stays the same.

The workflow computes two independent signals before deciding to publish:

1. **Source resource state** — the working-tree diff after `invoke create-mirrors` regenerates the mirror documents. A non-empty diff means the source changed (`source_changed`).
2. **123pan resource state** — `invoke dump-123pan-snapshot` writes a deterministic snapshot of every 123pan record's `syncedAt`/`shareUrl` into `tools/123pan-sync-state.json`. That file is committed on publish, so each run compares the freshly generated snapshot against the previously committed baseline to derive `123pan_changed`.

The combined signal is `changed = source_changed || 123pan_changed`. Both signals must be unchanged for the run to end as a no-op.

### Change source labels

The summary reports which signal triggered the publish:

- `source` — only the source content changed.
- `123pan` — only the 123pan resource changed.
- `source+123pan` — both changed.
- `none` — neither changed (no-op).

### 123pan status unavailable

When `dump-123pan-snapshot` cannot read a configured manifest source (timeout, request failure, invalid JSON, missing repository), it exits non-zero. The workflow records an explicit `123pan status: unavailable` diagnostic and continues using the source-change judgment. The failure is **never** silently treated as "synced" — `123pan_changed` stays `false` and the summary flags the gap so a maintainer can investigate.

## Publish behavior

1. Capture the current 123pan resource snapshot and compare it to the committed baseline.
2. Generate mirror content from the triggering ref (`invoke create-mirrors`).
3. Detect whether the working tree contains a real diff (`source_changed`).
4. Combine the two signals into `changed`.
5. If no signal changed, exit successfully as a no-op and skip the `main`-branch release trigger.
6. If a signal changed, rebase the generated patch onto `main`, create one automation commit (also staging the updated `123pan-sync-state.json`), and push it directly to `main` with `GITHUB_TOKEN`.
7. After the push succeeds, explicitly dispatch `newbe-deploy-gh-pages.yml` with `GITHUB_TOKEN`.

The workflow reports success when the direct publish succeeds.

## Release trigger

`mirror-update.yml` relies on the repository's normal `push` to `main` automation. As soon as the mirror commit lands on `main`, the release workflow configured on that branch can run on its own trigger.

## Summary states

The workflow summary distinguishes these states:

- `Mirror publish: no-op` (with `Change source: none`)
- `Mirror publish: changes detected` (with `Change source`, `Source changed`, `123pan changed`, `123pan status`)
- `123pan resource state: unavailable` (diagnostic when a manifest source could not be read)
- `Release follow-up: skipped (no-op publish)`
- `Release follow-up: gh-pages workflow dispatched`

This makes it clear whether a run ended before publication, which resource triggered the publish, and whether the 123pan status was fully observed.

## Secret and permission contract

The in-repo publish and deployment-dispatch paths use the built-in `GITHUB_TOKEN`:

- the workflow has `contents: write` permission to push `main`
- the workflow has `actions: write` permission to dispatch the gh-pages workflow
- explicit dispatch avoids relying on a `GITHUB_TOKEN` push to trigger another workflow

## Troubleshooting

### Mirror patch produced no staged changes on main

The generated diff became empty after rebasing onto `main`. Check whether another run already published the same batch. This guard also protects against a run where the change signal fired but `create-mirrors` produced no net file diff: in that case nothing is committed and the run surfaces the empty-diff error rather than creating a no-op commit.

### 123pan resource state unavailable

The `123pan status: unavailable` summary entry means one or more manifest sources could not be read this run. The run still continues on source-change judgment, but the 123pan side is not treated as verified. Re-run after fixing the manifest source access (token, SAS URL, or upstream availability).
