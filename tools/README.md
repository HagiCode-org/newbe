# Mirror Generator Notes

## Multi-repository 123Pan opt-in model

- `tools/mirrorsDef.json` can opt any GitHub mirror repository into manifest-driven provider links by declaring `repositoryKey`, `preferredProviders`, and `manifestSource`.
- The current reference opt-in list comes from `/home/newbe36524/repos/newbe-mono/repos/syncer/syncer.config.example.json`. Only repositories that exist in both the syncer config and `tools/mirrorsDef.json` should be enrolled.
- `preferredProviders` is repository-scoped. The current rollout uses `["123pan"]` for `ollama` plus the 14 syncer-managed repositories, but the generator contract stays provider-neutral.

## Manifest source contract

- `AZURE_STORAGE_BLOB_SAS_URL` should point to the Azure Blob container SAS URL. The generator reads Azure metadata during page generation, not in the browser at runtime.
- The generator now reads the root index first at `<AZURE_STORAGE_PREFIX>/index.json`. `tools/mirrorsDef.json` currently uses `blobPrefix: "release-sync"`, so the default root index path is `release-sync/index.json`.
- Versioned manifest blobs still resolve by convention as `<AZURE_STORAGE_PREFIX>/<owner>/<repo>/<releaseTagName>/manifest.json`. With `blobPrefix: "release-sync"`, `microsoft/PowerToys` maps to `release-sync/microsoft/PowerToys/<releaseTagName>/manifest.json`.
- The root index contract is intentionally small: the top-level payload must expose a `repositories` array, each repository entry must provide `repositoryKey` plus `releases`, and each release summary must provide `releaseTagName`, `recordCount`, `status`, and `lastSuccessfulAt`. Optional fields such as `manifestPath` and `lastAttemptedAt` are preserved when present.
- The normalized contract only depends on `repositoryKey`, `releaseTagName`, `assetName`, `providerName`, `shareUrl`, `status`, and a sync timestamp such as `lastSyncedAt`.
- Provider links are attached only when repository key, release tag, and asset name all match exactly. Missing or invalid manifest data falls back to the existing GitHub proxy mirrors and official source.
- `GithubMirrorLink` consumes a provider-neutral `resolvedMirrors` list, so future providers can be added without changing the modal contract again.

## Root index candidate filtering

- When the root index loads successfully and contains the current repository, only release summaries with `recordCount > 0` and `lastSuccessfulAt != null` are treated as candidates for a follow-up versioned `manifest.json` request.
- Releases omitted from the repository summary, or present without usable sync evidence, do not trigger a versioned manifest request. They continue to render the default proxy mirrors and official source links.
- If the root index request fails, the payload is invalid, or the index does not contain the current repository entry, the generator falls back to the legacy direct probe path and checks each release's versioned manifest exactly as before.

## Cache scope

- Root index responses are cached in process memory by the resolved root-index URL. A single generation run only downloads the same root `index.json` once, even if multiple releases or multiple page generations reuse that Azure root.
- Different Azure roots stay isolated because the cache key includes the fully resolved root-index URL.

## Maintenance workflow

- When syncer adds a new 123Pan repository, first confirm the GitHub repo already has a matching entry and markdown page in `tools/mirrorsDef.json`.
- Then copy the shared Azure `manifestSource` shape from an existing opted-in repository, set the repository-specific `repositoryKey`, and add `preferredProviders: ["123pan"]`.
- Update the manifest contract tests in `tools/tests/test_ollama_123pan_manifest.py` and fixtures in `tools/tests/fixtures/` so the new repository is covered by the shared opt-in contract instead of a repository-specific special case. Keep both the root index fixture and the versioned manifest fixtures in sync when the contract changes.
- Regenerate the affected mirror pages from `repos/newbe/tools` and smoke check that matched assets can expose `preferredProviders` plus `resolvedMirrors`, while unmatched assets still render the default proxy mirrors and official source.
