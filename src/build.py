import sys, pathlib
root = pathlib.Path(sys.argv[1]); preview = pathlib.Path(sys.argv[2]); logo = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else root/"src"
page = (root/'src/page.html').read_text()
page = page.replace('{{MARK}}', (logo/'mark.inner').read_text()).replace('{{FULL}}', (logo/'full.inner').read_text())
head, rest = page.split('</style>', 1)
preview.write_text(page.replace('<!--HEAD_EXTRA-->\n', ''))
extra = '<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">\n<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">\n<meta property="og:title" content="Herning Social Running Club">\n<meta property="og:description" content="Løb sammen hver onsdag kl. 17.00 fra Herning Bibliotek. Gratis, alle tempoer.">\n<meta property="og:url" content="https://hsrc.dk/">\n<meta name="theme-color" content="#24388d">\n'
head = head.replace('<!--HEAD_EXTRA-->\n', extra)
(root/'index.html').write_text('<!doctype html>\n<html lang="da">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + head + '</style>\n</head>\n<body>' + rest + '</body>\n</html>\n')
