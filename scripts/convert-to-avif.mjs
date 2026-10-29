// Convert every tracked PNG/WebP image under static/ and src/ to AVIF, next to the source file.
// (static/images/icons/ is skipped: favicons and manifest icons must stay PNG.)
//
//   node scripts/convert-to-avif.mjs            convert and delete the source
//   node scripts/convert-to-avif.mjs --keep     convert and keep the source
//   node scripts/convert-to-avif.mjs path ...   only these files
//
// Keep AVIF files in `src/assets/` and reference them through webpack (markdown
// `![](@site/src/assets/images/x.avif)` or `import`), so Docusaurus emits them as
// `assets/images/<name>-<contenthash>.avif`. A file left in `static/` is published at a fixed
// address, so clients keep a stale cached copy.
//
// Typical use for a new image: drop `x.png` into `src/assets/images/`, run this script.
import { execFileSync } from 'node:child_process';
import { readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, extname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import sharp from 'sharp';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const keep = args.includes('--keep');
const explicit = args.filter((arg) => !arg.startsWith('--'));

const SOURCE_EXT = new Set(['.png', '.webp']);
// Screenshots carry text, so keep full-resolution chroma (4:4:4) and a high quality.
const AVIF_OPTIONS = { quality: 62, effort: 6, chromaSubsampling: '4:4:4' };

function listSources() {
  if (explicit.length > 0) return explicit;
  return execFileSync('git', ['ls-files', '--cached', '--others', '--exclude-standard', 'static', 'src'], { cwd: root, encoding: 'utf8' })
    .split('\n')
    .filter((file) => SOURCE_EXT.has(extname(file).toLowerCase()))
    .filter((file) => !file.startsWith('static/images/icons/'));
}

let before = 0;
let after = 0;

async function convert(file) {
  const source = join(root, file);
  const target = source.slice(0, -extname(source).length) + '.avif';
  const input = await readFile(source);
  const image = sharp(input);
  const { pages = 1 } = await image.metadata();
  if (pages > 1) {
    console.warn(`skip ${file}: animated image, AVIF output from sharp is still-only`);
    return;
  }
  const output = await image.avif(AVIF_OPTIONS).toBuffer();
  await writeFile(target, output);
  if (!keep) await rm(source);
  before += input.length;
  after += output.length;
  console.log(`${file} -> ${target.slice(root.length + 1)}  ${input.length} -> ${output.length}`);
}

// A small worker pool: AVIF encoding is CPU bound and the files are independent.
const queue = listSources();
const workers = Array.from({ length: Math.min(4, queue.length) }, async () => {
  for (let file = queue.shift(); file !== undefined; file = queue.shift()) await convert(file);
});
await Promise.all(workers);
console.log(`total ${before} -> ${after} bytes`);
