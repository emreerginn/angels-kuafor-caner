"""Şablondan TR / BG / EL statik sayfalarını, 404 sayfasını ve paylaşım dosyalarını üretir.
Kullanım: python3 tools/build.py   (çıktı: site/)

Ayarlar aşağıda. WhatsApp numarası gelince WHATSAPP'a 90 ile başlayan rakamları yazın
(ör. "905321234567") ve betiği yeniden çalıştırın."""
import pathlib, re, shutil
from playwright.sync_api import sync_playwright

# ---------- Ayarlar ----------
WHATSAPP = ""                                          # boşsa sayfada yer tutucu görünür
CANONICAL = "https://kuaforcaner.com"                  # arama motorları için asıl adres
PUBLIC = "https://emreerginn.github.io/angels-kuafor-caner/"   # sitenin şu an yayında olduğu adres
BASE_PATH = "/angels-kuafor-caner/"                    # 404 sayfası için kök yol
# -----------------------------

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "src/template.html", ROOT / "site"
LANGS = {"tr": ("", "tr_TR"), "bg": ("bg/", "bg_BG"), "el": ("el/", "el_GR")}

WA = WHATSAPP or "WHATSAPP-NUMARASI"
WA_DISPLAY = ("+" + WHATSAPP) if WHATSAPP else '<span class="ph">[WHATSAPP NUMARASI]</span>'
TOKENS = {"{{WA}}": WA, "{{WA_URL}}": f"https://wa.me/{WA}", "{{WA_DISPLAY}}": WA_DISPLAY, "{{PUBLIC}}": PUBLIC}


def rel(frm, to):  # göreli bağlantı (yerel önizleme + yayında çalışır)
    up = "../" if LANGS[frm][0] else ""
    return (up + LANGS[to][0]) or "./"


OUT.mkdir(exist_ok=True)
if (OUT / "fonts").exists():
    shutil.rmtree(OUT / "fonts")
shutil.copytree(ROOT / "src/fonts", OUT / "fonts")

tmp = ROOT / "src/.build.html"
src = SRC.read_text(encoding="utf-8")
for k, v in TOKENS.items():
    src = src.replace(k, v)
tmp.write_text(src, encoding="utf-8")

with sync_playwright() as p:
    b = p.chromium.launch()
    for lg, (path, locale) in LANGS.items():
        pg = b.new_page()
        pg.goto(tmp.as_uri())
        pg.evaluate(f"() => {{ lang = '{lg}'; applyLang(); }}")
        title = pg.title()
        desc = pg.eval_on_selector('meta[name="description"]', "e => e.content")
        html = pg.content()
        pg.close()
        # tarayıcının eklediği çalışma anı sınıflarını temizle
        html = html.replace('<html lang="%s" class="js">' % lg, '<html lang="%s">' % lg)
        html = html.replace('class="swatch open"', 'class="swatch"')
        for code in LANGS:
            html = html.replace("{{HREF_%s}}" % code.upper(), rel(lg, code))
        html = html.replace("{{ROOT}}", "../" if path else "")
        html = html.replace("{{PUBLIC_PAGE}}", PUBLIC + path)
        html = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{CANONICAL}/{path}">', html)
        html = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{title}">', html)
        html = re.sub(r'<meta property="og:description" content="[^"]*">', lambda m: f'<meta property="og:description" content="{desc}">', html)
        html = re.sub(r'<meta property="og:locale" content="[^"]*">\n(<meta property="og:locale:alternate"[^>]*>\n)+',
                      f'<meta property="og:locale" content="{locale}">\n' +
                      "".join(f'<meta property="og:locale:alternate" content="{v[1]}">\n' for k, v in LANGS.items() if k != lg), html)
        assert "{{" not in html, re.findall(r"\{\{\w+\}\}", html)
        assert len(desc) < 160, (lg, len(desc))
        d = OUT / path
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(html, encoding="utf-8")

    # Site simgesi
    icon = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#3B1E36"/>
<g transform="translate(18 10)"><rect x="0" y="0" width="9" height="42" rx="4.5" fill="#B9824A" transform="rotate(-30 4 4)"/>
<rect x="0" y="0" width="9" height="42" rx="4.5" fill="#9C4E2B" transform="rotate(-15 4 4)"/>
<rect x="0" y="0" width="9" height="42" rx="4.5" fill="#B0436A"/></g></svg>'''
    (OUT / "favicon.svg").write_text(icon, encoding="utf-8")
    pg = b.new_page(viewport={"width": 180, "height": 180})
    pg.set_content(f'<body style="margin:0">{icon.replace("<svg ", "<svg width=180 height=180 ")}</body>')
    pg.screenshot(path=str(OUT / "apple-touch-icon.png"))

    # Paylaşım görseli 1200x630 (gömülü yazı tipleriyle)
    sw = "".join(f'<li style="--i:{i};--c:{c}"></li>' for i, c in enumerate(
        ["#2B1D18", "#4A2C20", "#6E3A24", "#9C4E2B", "#B9824A", "#D8B47C", "#6A2E4E"]))
    og = OUT / "_og.html"
    og.write_text(f'''<!DOCTYPE html><html lang="tr"><head><meta charset="utf-8"><style>
@font-face{{font-family:Gloock;src:url(fonts/gloock-latin-400-normal.woff2) format("woff2")}}
@font-face{{font-family:Gloock;src:url(fonts/gloock-latin-ext-400-normal.woff2) format("woff2");unicode-range:U+0100-02BA}}
@font-face{{font-family:Figtree;font-weight:500;src:url(fonts/figtree-latin-500-normal.woff2) format("woff2")}}
@font-face{{font-family:Figtree;font-weight:700;src:url(fonts/figtree-latin-700-normal.woff2) format("woff2")}}
body{{margin:0;width:1200px;height:630px;background:#F6ECEE;font-family:Figtree,sans-serif;color:#3B1E36;position:relative;overflow:hidden}}
h1{{font:400 168px/1 Gloock,serif;margin:0;position:absolute;left:78px;top:92px;letter-spacing:-3px}}
h2{{font:400 54px/1.1 Gloock,serif;margin:0;position:absolute;left:84px;top:300px}}
p{{position:absolute;left:84px;top:420px;margin:0;font-size:30px;font-weight:500}}
p b{{display:block;margin-top:12px;font-size:36px;font-weight:700}}
ul{{list-style:none;margin:0;padding:0;position:absolute;left:880px;top:96px}}
li{{position:absolute;width:62px;height:330px;border-radius:10px 10px 32px 32px;transform-origin:8px 8px;background:linear-gradient(100deg,rgba(255,255,255,.18) 0 12%,transparent 30% 55%,rgba(0,0,0,.18) 80%),var(--c);transform:rotate(calc(var(--i)*-9deg + 2deg))}}
</style></head><body><h1>Angels</h1><h2>Bayan Kuaförü Caner</h2><p>Kadın kuaförü<b>Edirne Merkez</b></p><ul>{sw}</ul></body></html>''', encoding="utf-8")
    pg = b.new_page(viewport={"width": 1200, "height": 630})
    pg.goto(og.as_uri())
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(300)
    assert pg.evaluate("document.fonts.check('168px Gloock')"), "Gloock yüklenmedi"
    pg.screenshot(path=str(OUT / "og-image.png"))
    og.unlink()
    b.close()
tmp.unlink()

# 404 sayfası (GitHub Pages her bilinmeyen adreste bunu gösterir; yollar mutlak)
(OUT / "404.html").write_text(f'''<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sayfa bulunamadı | Angels Bayan Kuaförü Caner</title>
<meta name="robots" content="noindex">
<link rel="icon" href="{BASE_PATH}favicon.svg" type="image/svg+xml">
<style>
  @font-face{{font-family:"Gloock";font-display:swap;src:url({BASE_PATH}fonts/gloock-latin-400-normal.woff2) format("woff2")}}
  @font-face{{font-family:"Figtree";font-weight:400;font-display:swap;src:url({BASE_PATH}fonts/figtree-latin-400-normal.woff2) format("woff2")}}
  @font-face{{font-family:"Figtree";font-weight:700;font-display:swap;src:url({BASE_PATH}fonts/figtree-latin-700-normal.woff2) format("woff2")}}
  *{{box-sizing:border-box}}
  body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#F6ECEE;color:#2A1C27;font:400 1.0625rem/1.6 Figtree,system-ui,sans-serif;padding:2rem 1.25rem}}
  main{{max-width:32rem}}
  h1{{font:400 clamp(2.4rem,9vw,3.5rem)/1.05 Gloock,Georgia,serif;color:#3B1E36;margin:0 0 1rem}}
  p{{margin:0 0 .5rem}}
  .alt{{color:#5A4757}}
  a{{display:inline-flex;align-items:center;min-height:3.25rem;margin-top:1.5rem;padding:0 1.4rem;border-radius:999px;background:#3B1E36;color:#fff;font-weight:700;text-decoration:none;transition:background-color .16s,transform .16s}}
  a:hover{{background:#B0436A;transform:translateY(-2px)}}
  a:focus-visible{{outline:3px solid #B0436A;outline-offset:3px}}
</style>
</head>
<body>
<main>
  <h1>Bu sayfa bulunamadı</h1>
  <p>Aradığınız adres değişmiş ya da kaldırılmış olabilir.</p>
  <p class="alt" lang="bg">Страницата не е намерена.</p>
  <p class="alt" lang="el">Η σελίδα δεν βρέθηκε.</p>
  <a href="{BASE_PATH}">Angels Bayan Kuaförü Caner ana sayfasına dön</a>
</main>
</body>
</html>
''', encoding="utf-8")

(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {CANONICAL}/sitemap.xml\n")
alts = "".join(f'    <xhtml:link rel="alternate" hreflang="{k}" href="{CANONICAL}/{v[0]}"/>\n' for k, v in LANGS.items()) + \
       f'    <xhtml:link rel="alternate" hreflang="x-default" href="{CANONICAL}/"/>\n'
urls = "".join(f"  <url>\n    <loc>{CANONICAL}/{v[0]}</loc>\n{alts}  </url>\n" for v in LANGS.values())
(OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + "</urlset>\n")
print("ok")
