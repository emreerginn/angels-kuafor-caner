"""Şablondan TR / BG / EL statik sayfalarını ve SEO dosyalarını üretir.
Kullanım: python3 tools/build.py   (çıktı: site/)"""
import pathlib, re, json
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = ROOT/"src/template.html", ROOT/"site"
BASE = "https://kuaforcaner.com"
LANGS = {"tr": ("", "tr_TR"), "bg": ("bg/", "bg_BG"), "el": ("el/", "el_GR")}

def rel(frm, to):  # göreli bağlantı (yerel önizleme + yayında çalışır)
    up = "../" if LANGS[frm][0] else ""
    return (up + LANGS[to][0]) or "./"

OUT.mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    for lg, (path, locale) in LANGS.items():
        pg = b.new_page()
        pg.goto(SRC.as_uri())
        pg.evaluate(f"() => {{ lang = '{lg}'; applyLang(); }}")
        title = pg.title()
        desc = pg.eval_on_selector('meta[name="description"]', "e => e.content")
        html = pg.content()
        pg.close()
        url = BASE + "/" + path
        for code in LANGS: html = html.replace("{{HREF_%s}}" % code.upper(), rel(lg, code))
        html = html.replace("{{ROOT}}", "../" if path else "")
        html = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', html)
        html = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">', html)
        html = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{title}">', html)
        html = re.sub(r'<meta property="og:description" content="[^"]*">', lambda m: f'<meta property="og:description" content="{desc}">', html)
        html = re.sub(r'<meta property="og:locale" content="[^"]*">\n(<meta property="og:locale:alternate"[^>]*>\n)+',
                      f'<meta property="og:locale" content="{locale}">\n' +
                      "".join(f'<meta property="og:locale:alternate" content="{v[1]}">\n' for k, v in LANGS.items() if k != lg), html)
        assert "{{" not in html
        d = OUT/path; d.mkdir(parents=True, exist_ok=True)
        (d/"index.html").write_text(html, encoding="utf-8")

    # Site simgesi
    icon = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#3B1E36"/>
<g transform="translate(18 10)"><rect x="0" y="0" width="9" height="42" rx="4.5" fill="#B9824A" transform="rotate(-30 4 4)"/>
<rect x="0" y="0" width="9" height="42" rx="4.5" fill="#9C4E2B" transform="rotate(-15 4 4)"/>
<rect x="0" y="0" width="9" height="42" rx="4.5" fill="#B0436A"/></g></svg>'''
    (OUT/"favicon.svg").write_text(icon, encoding="utf-8")
    pg = b.new_page(viewport={"width": 180, "height": 180})
    pg.set_content(f'<body style="margin:0">{icon.replace("<svg ", "<svg width=180 height=180 ")}</body>')
    pg.screenshot(path=str(OUT/"apple-touch-icon.png"))

    # Paylaşım görseli 1200x630 (markalı, fotoğraf değil)
    pg = b.new_page(viewport={"width": 1200, "height": 630})
    sw = "".join(f'<li style="--i:{i};--c:{c}"></li>' for i, c in enumerate(
        ["#2B1D18","#4A2C20","#6E3A24","#9C4E2B","#B9824A","#D8B47C","#6A2E4E"]))
    pg.set_content(f'''<html><head><link href="https://fonts.googleapis.com/css2?family=Gloock&family=Figtree:wght@500;700&display=swap" rel="stylesheet">
<style>body{{margin:0;width:1200px;height:630px;background:#F6ECEE;font-family:Figtree,sans-serif;color:#3B1E36;position:relative;overflow:hidden}}
h1{{font:400 150px/1 Gloock,Georgia,serif;margin:0;position:absolute;left:80px;top:110px}}
h2{{font:400 52px/1.1 Gloock,Georgia,serif;margin:0;position:absolute;left:84px;top:300px}}
p{{position:absolute;left:84px;top:420px;margin:0;font-size:30px;font-weight:500}}
p b{{display:block;margin-top:14px;font-size:40px;font-weight:700}}
ul{{list-style:none;margin:0;padding:0;position:absolute;left:870px;top:90px}}
li{{position:absolute;width:62px;height:330px;border-radius:10px 10px 32px 32px;transform-origin:8px 8px;background:linear-gradient(100deg,rgba(255,255,255,.18) 0 12%,transparent 30% 55%,rgba(0,0,0,.18) 80%),var(--c);transform:rotate(calc(var(--i)*-9deg + 2deg))}}
</style></head><body><h1>Angels</h1><h2>Bayan Kuaförü Caner</h2><p>Edirne Merkez<b>(0284) 214 72 03</b></p><ul>{sw}</ul></body></html>''')
    pg.wait_for_timeout(1500)
    pg.screenshot(path=str(OUT/"og-image.png"))
    b.close()

(OUT/"robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
alts = "".join(f'    <xhtml:link rel="alternate" hreflang="{k}" href="{BASE}/{v[0]}"/>\n' for k, v in LANGS.items()) + \
       f'    <xhtml:link rel="alternate" hreflang="x-default" href="{BASE}/"/>\n'
urls = "".join(f"  <url>\n    <loc>{BASE}/{v[0]}</loc>\n{alts}  </url>\n" for v in LANGS.values())
(OUT/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + "</urlset>\n")
print("ok")
