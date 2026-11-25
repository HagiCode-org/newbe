# Mirror Generator Notes

## Output layout

- The generator writes mirror pages only to `docs/Mirrors/` (`../docs/Mirrors/` from `tasks.py`). It never writes another `docs/` directory: the site publishes mirror pages and the homepage only, and the blog sections (`Mic`, `Projects`, `Tutorial`) were removed.
- `repos/newbe/tests/mirror-only-content.test.cjs` checks that `docs/` holds only `intro.md` and `Mirrors/`, and that every AVIF under `src/assets/` is still referenced. Run `node --test tests/*.test.cjs` from `repos/newbe` after changing generated output.

## Maintenance workflow

- Regenerate the affected mirror pages from `repos/newbe/tools` and smoke check that assets render the default proxy mirrors and official source.
- GitHub mirror direct links are read from the public Syncer r2 endpoint:
  `https://syncer.hagicode.com/r2/index.json`, followed by the versioned
  `manifestPath` returned for each repository and release. The generator does
  not require `GITHUB_TOKEN` or GitHub Release metadata access for this data.
