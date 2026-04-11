# Mirror Generator Notes

## Multi-repository 123Pan opt-in model

- `tools/mirrorsDef.json` can opt any GitHub mirror repository into manifest-driven provider links by declaring `repositoryKey`, `preferredProviders`, and `manifestSource`.
- The current reference opt-in list comes from `/home/newbe36524/repos/newbe-mono/repos/syncer/syncer.config.example.json`. Only repositories that exist in both the syncer config and `tools/mirrorsDef.json` should be enrolled.
- `preferredProviders` is repository-scoped. The current rollout uses `["123pan"]` for `ollama` plus the 14 syncer-managed repositories, but the generator contract stays provider-neutral.

## Manifest source contract

- `AZURE_STORAGE_BLOB_SAS_URL` should point to the Azure Blob container SAS URL. The generator reads the release-specific manifest during page generation, not in the browser at runtime.
- Manifest blobs are resolved by convention as `<AZURE_STORAGE_PREFIX>/<owner>/<repo>/<releaseTagName>/manifest.json`. `tools/mirrorsDef.json` currently uses `blobPrefix: "release-sync"`, so `microsoft/PowerToys` maps to `release-sync/microsoft/PowerToys/<releaseTagName>/manifest.json`.
- The normalized contract only depends on `repositoryKey`, `releaseTagName`, `assetName`, `providerName`, `shareUrl`, `status`, and a sync timestamp such as `lastSyncedAt`.
- Provider links are attached only when repository key, release tag, and asset name all match exactly. Missing or invalid manifest data falls back to the existing GitHub proxy mirrors and official source.
- `GithubMirrorLink` consumes a provider-neutral `resolvedMirrors` list, so future providers can be added without changing the modal contract again.

## Maintenance workflow

- When syncer adds a new 123Pan repository, first confirm the GitHub repo already has a matching entry and markdown page in `tools/mirrorsDef.json`.
- Then copy the shared Azure `manifestSource` shape from an existing opted-in repository, set the repository-specific `repositoryKey`, and add `preferredProviders: ["123pan"]`.
- Update the manifest contract tests in `tools/tests/test_ollama_123pan_manifest.py` and fixtures in `tools/tests/fixtures/` so the new repository is covered by the shared opt-in contract instead of a repository-specific special case.
- Regenerate the affected mirror pages from `repos/newbe/tools` and smoke check that matched assets can expose `preferredProviders` plus `resolvedMirrors`, while unmatched assets still render the default proxy mirrors and official source.
