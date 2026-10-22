// Renders the share image and app icons from src/og.html and assets/favicon.svg.
// Usage: node src/render-assets.js   (needs Playwright with Chromium)
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '..');
const fav = fs.readFileSync(path.join(root, 'assets/favicon.svg'), 'utf8');
const square = fav.replace(' rx="14"', '');                       // full bleed: iOS and Android round it themselves
const maskable = square.replace(/(<rect[^>]*\/>)([\s\S]*)<\/svg>/, '$1<g transform="translate(6.4 6.4) scale(.8)">$2</g></svg>');
(async () => {
  const b = await chromium.launch();
  const og = await b.newPage({ viewport: { width: 1200, height: 630 } });
  await og.goto('file://' + path.join(root, 'src/og.html'), { waitUntil: 'networkidle' });
  await og.evaluate(() => document.fonts.ready);
  const over = await og.evaluate(() => [...document.querySelectorAll('h1,.sub,.en,.band')].some(e => e.scrollWidth > e.clientWidth));
  if (over) throw new Error('Share image text overflows; lower the h1 font size in src/og.html');
  await og.screenshot({ path: path.join(root, 'assets/og-image.png') });
  const shot = async (svg, size, file, transparent) => {
    const p = await b.newPage({ viewport: { width: size, height: size } });
    await p.setContent(`<style>html,body{margin:0;background:transparent}svg{display:block;width:${size}px;height:${size}px}</style>${svg}`);
    await p.screenshot({ path: file, omitBackground: transparent });
    await p.close();
  };
  const tmp = path.join(root, 'src/.icons'); fs.mkdirSync(tmp, { recursive: true });
  await shot(fav, 192, path.join(root, 'assets/icon-192.png'), true);
  await shot(fav, 512, path.join(root, 'assets/icon-512.png'), true);
  await shot(maskable, 512, path.join(root, 'assets/icon-512-maskable.png'), false);
  await shot(square, 180, path.join(root, 'assets/apple-touch-icon.png'), false);
  for (const s of [16, 32, 48]) await shot(fav, s, path.join(tmp, `fav-${s}.png`), true);
  await b.close();
  // favicon.ico holding 16, 32 and 48 px PNGs
  const pngs = [16, 32, 48].map(s => fs.readFileSync(path.join(tmp, `fav-${s}.png`)));
  const header = Buffer.alloc(6); header.writeUInt16LE(0, 0); header.writeUInt16LE(1, 2); header.writeUInt16LE(pngs.length, 4);
  let offset = 6 + 16 * pngs.length;
  const dir = pngs.map((png, i) => {
    const s = [16, 32, 48][i], e = Buffer.alloc(16);
    e.writeUInt8(s, 0); e.writeUInt8(s, 1); e.writeUInt8(0, 2); e.writeUInt8(0, 3);
    e.writeUInt16LE(1, 4); e.writeUInt16LE(32, 6); e.writeUInt32LE(png.length, 8); e.writeUInt32LE(offset, 12);
    offset += png.length; return e;
  });
  fs.writeFileSync(path.join(root, 'favicon.ico'), Buffer.concat([header, ...dir, ...pngs]));
  fs.rmSync(tmp, { recursive: true, force: true });
  console.log('rendered og-image.png, icons and favicon.ico');
})().catch(e => { console.error(e); process.exit(1); });
