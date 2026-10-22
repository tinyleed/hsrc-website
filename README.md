# Herning Social Running Club

Website for [hsrc.dk](https://hsrc.dk), hosted on GitHub Pages.

- `index.html` is the published page (Danish and English, toggle in the menu).
- `assets/` holds the logo, favicon and touch icon.
- `src/page.html` is the editable source. After changing it, rebuild with:

```sh
python3 src/build.py . /tmp/preview.html src
```

This writes `index.html` (and a preview copy without the HTML head, used for the Claude preview).
