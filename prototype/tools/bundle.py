#!/usr/bin/env python3
"""Bundle the prototype into one self-contained HTML file.

Inlines styles.css (with the Onest fonts as data: URIs), i18n.js and app.js,
so the page opens with a double-click or travels as a single attachment.

Usage:  python3 tools/bundle.py      -> dist/sferihome-prototype.html
"""

import base64
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "dist" / "sferihome-prototype.html"


def inline_fonts(css: str) -> str:
    def repl(m):
        data = base64.b64encode((ROOT / m.group(1)).read_bytes()).decode("ascii")
        return f'url("data:font/woff2;base64,{data}")'
    return re.sub(r'url\("(fonts/[^"]+\.woff2)"\)', repl, css)


def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    css = inline_fonts((ROOT / "styles.css").read_text(encoding="utf-8"))
    html = html.replace('<link rel="stylesheet" href="styles.css">', f"<style>\n{css}\n</style>")
    for name in ("i18n.js", "app.js"):
        js = (ROOT / name).read_text(encoding="utf-8").replace("</script", "<\\/script")
        html = html.replace(f'<script src="{name}"></script>', f"<script>\n{js}\n</script>")
    if re.search(r'(href|src)="(styles\.css|i18n\.js|app\.js|fonts/)', html):
        raise SystemExit("an external reference survived bundling")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}  {OUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
