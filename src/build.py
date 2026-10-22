"""Build the HSRC site.

Writes index.html (Danish) and en/index.html (English) from src/page.html.
Every bilingual pair in the source is written as
<span lang="da">…</span><span lang="en">…</span>; each page keeps only its own language.

Usage: python3 src/build.py [site_root] [preview_out]   (site_root defaults to .)
  preview_out (optional) gets the Danish page without the <html>/<head> wrapper,
  for the Claude preview.
"""
import html as htmllib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
PREVIEW = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else None
SRC = ROOT / 'src'
SITE = 'https://hsrc.dk/'

# Fonts are self-hosted on the site so visitors' browsers don't contact Google.
# The Claude preview can't load local files, so it uses Google Fonts instead.
FONTS_SITE = '''<link rel="preload" href="/assets/fonts/figtree.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/outfit.woff2" as="font" type="font/woff2" crossorigin>
<style>
@font-face{font-family:"Outfit";font-weight:600 800;font-display:swap;src:url(/assets/fonts/outfit.woff2) format("woff2")}
@font-face{font-family:"Figtree";font-weight:400 700;font-display:swap;src:url(/assets/fonts/figtree.woff2) format("woff2")}
@font-face{font-family:"JetBrains Mono";font-weight:500;font-display:swap;src:url(/assets/fonts/jetbrains-mono.woff2) format("woff2")}
</style>
'''
FONTS_PREVIEW = '''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@600;800&family=Figtree:wght@400;500;700&family=JetBrains+Mono:wght@500&display=swap">
'''

LANGS = {
    'da': {
        'path': '',
        'locale': 'da_DK',
        'title': 'Herning Social Running Club – gratis løbeklub i Herning',
        'desc': 'Gratis, social løbeklub i Herning. Vi løber hver onsdag kl. 17.00 fra Herning Bibliotek '
                'i alle tempoer, uden tilmelding. English speakers welcome.',
        'og_title': 'Herning Social Running Club',
        'og_desc': 'Løb sammen hver onsdag kl. 17.00 fra Herning Bibliotek. Gratis, alle tempoer.',
        'og_alt': 'Herning Social Running Clubs smilende løber-maskot med orange planetring og teksten '
                  '»Løb sammen. Snak bagefter.« Onsdag kl. 17.00, Herning Bibliotek.',
        'org_desc': 'Gratis og uformel løbeklub i Herning for alle tempoer. Vi løber hver onsdag kl. 17.00 '
                    'fra Herning Bibliotek, Brændgårdvej 1, 7400 Herning. Intet medlemskab, mød bare op.',
    },
    'en': {
        'path': 'en/',
        'locale': 'en_GB',
        'title': 'Herning Social Running Club – free running club in Herning',
        'desc': 'Free, social running club in Herning, Denmark. We run every Wednesday at 17:00 from '
                'Herning Library. All paces, no sign-up, no fees.',
        'og_title': 'Herning Social Running Club',
        'og_desc': 'Run together every Wednesday at 17:00 from Herning Library. Free, every pace.',
        'og_alt': 'The Herning Social Running Club mascot, a smiling runner with an orange planet ring, '
                  'with the text "Run together. Talk after." Wednesday 17:00, Herning Library.',
        'org_desc': 'Free, informal running club in Herning for every pace. We run every Wednesday at 17:00 '
                    'from Herning Library, Brændgårdvej 1, 7400 Herning. No membership, just turn up.',
    },
}


def only_lang(html, keep):
    """Drop <span lang=other>…</span> (nesting-aware) and unwrap <span lang=keep>."""
    drop = 'en' if keep == 'da' else 'da'
    out, i, stack = [], 0, []  # stack holds 'drop' | 'unwrap' | 'keep' per open span
    for m in re.finditer(r'<span\b[^>]*>|</span>', html):
        t = m.group(0)
        dropping = 'drop' in stack
        if not dropping:
            out.append(html[i:m.start()])
        i = m.end()
        if t == '</span>':
            kind = stack.pop()
            if kind == 'keep' and 'drop' not in stack:
                out.append(t)
        else:
            kind = 'drop' if f'lang="{drop}"' in t else 'unwrap' if f'lang="{keep}"' in t else 'keep'
            if kind == 'keep' and not dropping:
                out.append(t)
            stack.append(kind)
    out.append(html[i:])
    return ''.join(out)


def json_ld(L, lang):
    org = {
        '@type': 'SportsOrganization',
        '@id': SITE + '#organization',
        'name': 'Herning Social Running Club',
        'alternateName': 'HSRC',
        'url': SITE,
        'logo': SITE + 'assets/icon-512.png',
        'image': SITE + 'assets/og-image.png',
        'description': L['org_desc'],
        'sport': 'Running',
        'knowsLanguage': ['da', 'en'],
        'areaServed': {'@type': 'City', 'name': 'Herning'},
        # The club meets at the library; it is not the club's own address.
        'location': {
            '@type': 'Place',
            'name': 'Herning Bibliotek',
            'address': {
                '@type': 'PostalAddress',
                'streetAddress': 'Brændgårdvej 1',
                'postalCode': '7400',
                'addressLocality': 'Herning',
                'addressCountry': 'DK',
            },
        },
        'sameAs': [
            'https://www.strava.com/clubs/1510591',
            'https://www.instagram.com/herningsocialrunningclub/',
        ],
    }
    website = {
        '@type': 'WebSite',
        '@id': SITE + '#website',
        'name': 'Herning Social Running Club',
        'alternateName': 'HSRC',
        'url': SITE,
        'inLanguage': ['da', 'en'],
        'publisher': {'@id': SITE + '#organization'},
    }
    data = {'@context': 'https://schema.org', '@graph': [org, website]}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>\n'


def head_extra(L, lang):
    url = SITE + L['path']
    L = {k: htmllib.escape(v, quote=True) for k, v in L.items()}
    return f'''<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="da" href="{SITE}">
<link rel="alternate" hreflang="en" href="{SITE}en/">
<link rel="alternate" hreflang="x-default" href="{SITE}">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="apple-mobile-web-app-title" content="HSRC">
<meta name="theme-color" media="(prefers-color-scheme: light)" content="#24388d">
<meta name="theme-color" media="(prefers-color-scheme: dark)" content="#161b38">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Herning Social Running Club">
<meta property="og:locale" content="{L['locale']}">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{L['og_title']}">
<meta property="og:description" content="{L['og_desc']}">
<meta property="og:image" content="{SITE}assets/og-image.png">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{L['og_alt']}">
<meta name="twitter:card" content="summary_large_image">
''' + json_ld(L, lang)


def render(lang, page):
    L = LANGS[lang]
    html = only_lang(page, lang)
    links = {
        'da': {'{{DA_HREF}}': './', '{{EN_HREF}}': 'en/', '{{DA_CURRENT}}': ' aria-current="page"', '{{EN_CURRENT}}': ''},
        'en': {'{{DA_HREF}}': '../', '{{EN_HREF}}': './', '{{DA_CURRENT}}': '', '{{EN_CURRENT}}': ' aria-current="page"'},
    }[lang]
    for k, v in {**links, '{{TITLE}}': htmllib.escape(L['title']), '{{DESC}}': htmllib.escape(L['desc'], quote=True)}.items():
        html = html.replace(k, v)
    assert '{{' not in html, re.findall(r'\{\{\w+\}\}', html)
    assert '<span lang=' not in html, 'unpaired language span left in page'
    return html


page = (SRC / 'page.html').read_text()
page = page.replace('{{MARK}}', (SRC / 'mark.inner').read_text()).replace('{{FULL}}', (SRC / 'full.inner').read_text())

for lang, L in LANGS.items():
    html = render(lang, page)
    if lang == 'da' and PREVIEW:
        PREVIEW.write_text(html.replace('<!--HEAD_EXTRA-->\n', '').replace('<!--FONTS-->\n', FONTS_PREVIEW))
    html = html.replace('<!--HEAD_EXTRA-->\n', head_extra(L, lang)).replace('<!--FONTS-->\n', FONTS_SITE)
    head, rest = html.split('</style>', 1)
    out = ROOT / L['path'] / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(
        f'<!doctype html>\n<html lang="{lang}">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + head + '</style>\n</head>\n<body>' + rest + '</body>\n</html>\n'
    )
    print('wrote', out.relative_to(ROOT))
