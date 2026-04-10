# Mirror Generator Notes

## Ollama 123Pan manifest integration

- `tools/mirrorsDef.json` can opt a GitHub mirror repository into manifest-driven provider links with `manifestSource`, `repositoryKey`, and `preferredProviders`.
- `AZURE_STORAGE_BLOB_SAS_URL` should point to the Azure Blob container SAS URL. The generator reads the release-specific manifest during page generation, not in the browser at runtime.
- Ollama manifest blobs are resolved by convention as `<AZURE_STORAGE_PREFIX>/<owner>/<repo>/<releaseTagName>/manifest.json`. `tools/mirrorsDef.json` currently uses `blobPrefix: "release-sync"` so `ollama/ollama` maps to `release-sync/ollama/ollama/<releaseTagName>/manifest.json`.
- The current normalized contract only depends on `repositoryKey`, `releaseTagName`, `assetName`, `providerName`, `shareUrl`, `status`, and a sync timestamp such as `lastSyncedAt`.
- Provider links are attached only when repository key, release tag, and asset name all match exactly. Missing or invalid manifest data falls back to the existing GitHub proxy mirrors and official source.
- `GithubMirrorLink` consumes a provider-neutral `resolvedMirrors` list so future providers can be added without changing the modal contract again.
