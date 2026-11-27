# Mirror Generator Notes

## Maintenance workflow

- Regenerate the affected mirror pages from `repos/newbe/tools` and smoke check that assets render the default proxy mirrors and official source.
- GitHub mirror direct links are read from the public Syncer r2 endpoint:
  `https://syncer.hagicode.com/r2/index.json`, followed by the versioned
  `manifestPath` returned for each repository and release. The generator does
  not require `GITHUB_TOKEN` or GitHub Release metadata access for this data.
