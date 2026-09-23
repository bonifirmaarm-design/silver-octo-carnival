#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrap redesign/index.html into a real HTML document.

index.html is written for the artifact viewer, which supplies <!doctype>, <head>
and <body> itself. Anywhere else that shell has to be here, or the page loses its
charset and its viewport and breaks on a phone.

Produces:
  docs/                      folder version — what you upload to a host
  dist/sferihome.html        one file, images inlined — what you send to someone
"""
import base64, io, mimetypes, os, re, shutil, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_SITE = os.path.join(ROOT, '..', 'docs')
OUT_ONE = os.path.join(ROOT, '..', 'dist')

TITLE = "SFERIHOME — дома из соломенных панелей"
DESC = ("Соломенные стеновые панели и кровельные системы. Производство — Цетине, "
        "Черногория. Стена 40 кг/м², сборка за 3–5 дней, каркас до 100 лет.")
ICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3E"
        "%3Crect width='30' height='30' fill='%23EDECE7'/%3E%3Cg fill='none' stroke='%23000' "
        "stroke-width='1.8'%3E%3Ccircle cx='15' cy='15' r='11'/%3E%3Cpath d='M4 11.5h22M4 18.5h22M15 4v22'/%3E"
        "%3C/g%3E%3C/svg%3E")

def head(og_image=None):
    og = ('<meta property="og:image" content="%s">\n' % og_image) if og_image else ''
    return ("""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#EDECE7">
<link rel="icon" href="%s">
<meta property="og:type" content="website">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
%s""" % (ICON, TITLE, DESC, og))

def main():
    src = io.open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    split = src.index('</style>') + len('</style>')
    head_part, body_part = src[:split], src[split:]

    # the artifact viewer took the title from <title>; keep one, spelled in full
    head_part = re.sub(r'<title>.*?</title>', '<title>%s</title>' % TITLE, head_part, count=1)
    head_part = re.sub(r'<meta name="description" content="[^"]*">',
                       '<meta name="description" content="%s">' % DESC, head_part, count=1)

    used = sorted(set(re.findall(r'src="img/([^"]+)"', src)))
    missing = [f for f in used if not os.path.exists(os.path.join(ROOT, 'img', f))]
    if missing:
        sys.exit("missing images: " + ", ".join(missing))

    # ---- folder version
    if os.path.isdir(OUT_SITE):
        shutil.rmtree(OUT_SITE)
    os.makedirs(os.path.join(OUT_SITE, 'img'))
    for f in used:
        shutil.copy2(os.path.join(ROOT, 'img', f), os.path.join(OUT_SITE, 'img', f))
    site = head(og_image='img/house.webp') + head_part + '\n</head>\n<body>' + body_part + '\n</body>\n</html>\n'
    io.open(os.path.join(OUT_SITE, 'index.html'), 'w', encoding='utf-8').write(site)
    # GitHub Pages runs Jekyll otherwise, which eats files it does not recognise
    io.open(os.path.join(OUT_SITE, '.nojekyll'), 'w').write('')

    # ---- one file
    one = head() + head_part + '\n</head>\n<body>' + body_part + '\n</body>\n</html>\n'
    for f in used:
        raw = open(os.path.join(ROOT, 'img', f), 'rb').read()
        mime = mimetypes.guess_type(f)[0] or 'image/webp'
        uri = 'data:%s;base64,%s' % (mime, base64.b64encode(raw).decode())
        one = one.replace('src="img/%s"' % f, 'src="%s"' % uri)
    if not os.path.isdir(OUT_ONE):
        os.makedirs(OUT_ONE)
    path_one = os.path.join(OUT_ONE, 'sferihome.html')
    io.open(path_one, 'w', encoding='utf-8').write(one)

    site_bytes = sum(os.path.getsize(os.path.join(dp, f))
                     for dp, _, fs in os.walk(OUT_SITE) for f in fs)
    print("docs/               %6.2f MB  (%d images)" % (site_bytes / 1e6, len(used)))
    print("dist/sferihome.html %6.2f MB  (one file)" % (os.path.getsize(path_one) / 1e6))

if __name__ == '__main__':
    main()
