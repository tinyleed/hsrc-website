# Herning Social Running Club

Website for [hsrc.dk](https://hsrc.dk), hosted on GitHub Pages from the `main` branch.

## Pages

- `index.html` is the Danish page at https://hsrc.dk/
- `en/index.html` is the English page at https://hsrc.dk/en/

Both are generated. Don't edit them by hand.

## Editing

All text lives in `src/page.html`. Every piece of text that differs by language is written as a pair:

```html
<span lang="da">Onsdagsløbet</span><span lang="en">The Wednesday run</span>
```

The build keeps the Danish half for `index.html` and the English half for `en/index.html`. Page titles, descriptions, share text and the structured data (JSON-LD) are set in `src/build.py`.

After changing anything in `src/`, rebuild:

```sh
python3 src/build.py
```

## Images and icons

- `src/og.html` is the template for the link preview image (`assets/og-image.png`, 1200×630).
- `assets/favicon.svg` is the browser tab icon. The PNG icons and `favicon.ico` are made from it.

To re-render the preview image and icons (needs Node with Playwright and Chromium):

```sh
node src/render-assets.js
```

If you change the preview image later, give it a new file name and update `og:image` in `src/build.py`, because WhatsApp and Facebook cache previews by image URL.

`assets/hsrc-logo.svg` (logo with name) and `assets/hsrc-mark.svg` (mascot only) are the official logo files. The page inlines a minified copy of them from `src/full.inner` and `src/mark.inner`, with colours set by CSS variables so the logo adapts to dark mode.

Fonts (Outfit, Figtree, JetBrains Mono, all SIL Open Font License) are self-hosted in `assets/fonts/` so visitors' browsers don't contact Google.

## Other files

- `CNAME` tells GitHub Pages to serve the site on hsrc.dk.
- `robots.txt` and `sitemap.xml` help search engines find both pages.
- `site.webmanifest` sets the name and icon when someone adds the site to their phone's home screen.
- `404.html` is shown for any address that doesn't exist.
