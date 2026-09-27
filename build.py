#!/usr/bin/env python3
"""Assemble SierraLV static pages: src/pages/*.html + shared header/footer -> ./*.html

Page files start with a JSON meta line: <!--{"title": "...", "desc": "...", "nav": "owners"}-->
Tokens inside page bodies:
  {{icon:name}}                         inline Lucide-style SVG
  {{pic:name|alt|class|eager}}          <picture> with WebP + JPG, real width/height
"""
import json, re, pathlib
from PIL import Image

ROOT = pathlib.Path(__file__).parent
IMG = ROOT / "assets" / "img"

PHONE = "702-553-1211"
EMAIL = "allyson@sierralasvegas.com"
PORTAL = "https://sierralvpropmgmtandrealty.appfolio.com/oportal/users/log_in"
LISTINGS = "https://sierralvpropmgmtandrealty.appfolio.com/listings"

ICONS = {
    "arrow": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "ext": '<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    "chev": '<path d="m6 9 6 6 6-6"/>',
    "plus": '<path d="M12 5v14"/><path d="M5 12h14"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.8 19.8 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.12 4.18 2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/>',
    "mail": '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "key": '<circle cx="7.5" cy="15.5" r="5.5"/><path d="m21 2-9.6 9.6"/><path d="m15.5 7.5 3 3L22 7l-3-3"/>',
    "home": '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>',
    "wrench": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "camera": '<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/>',
    "clipboard": '<rect width="8" height="4" x="8" y="2" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/>',
    "dollar": '<path d="M12 2v20"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
    "calendar": '<rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/>',
    "chart": '<path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>',
    "handshake": '<path d="m11 17 2 2a1 1 0 1 0 3-3"/><path d="m14 14 2.5 2.5a1 1 0 1 0 3-3l-3.88-3.88a3 3 0 0 0-4.24 0l-.88.88a1 1 0 1 1-3-3l2.81-2.81a5.79 5.79 0 0 1 7.06-.87l.47.28a2 2 0 0 0 1.42.25L21 4"/><path d="m21 3 1 11h-2"/><path d="M3 3 2 14l6.5 6.5a1 1 0 1 0 3-3"/><path d="M3 4h8"/>',
    "zap": '<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>',
    "star": '<path d="M11.5 2.3a.5.5 0 0 1 .9 0l2.3 4.7a2 2 0 0 0 1.6 1.1l5.2.8a.5.5 0 0 1 .3.9l-3.8 3.7a2 2 0 0 0-.6 1.9l.9 5.2a.5.5 0 0 1-.8.5l-4.6-2.4a2 2 0 0 0-1.9 0l-4.6 2.4a.5.5 0 0 1-.8-.5l.9-5.2a2 2 0 0 0-.6-1.9L1.2 9.8a.5.5 0 0 1 .3-.9l5.2-.8a2 2 0 0 0 1.6-1.1z"/>',
    "map": '<path d="M14.1 4.3 9.9 2.2a2 2 0 0 0-1.8 0L3.6 4.5A1 1 0 0 0 3 5.4v14.4a1 1 0 0 0 1.4.9l3.7-1.9a2 2 0 0 1 1.8 0l4.2 2.1a2 2 0 0 0 1.8 0l4.5-2.3a1 1 0 0 0 .6-.9V4.2a1 1 0 0 0-1.4-.9l-3.7 1.9a2 2 0 0 1-1.8 0z"/><path d="M15 5.8v15"/><path d="M9 3.2v15"/>',
    "news": '<path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/><path d="M18 14h-8"/><path d="M15 18h-5"/><path d="M10 6h8v4h-8V6Z"/>',
    "menu": '<path d="M4 6h16"/><path d="M4 12h16"/><path d="M4 18h16"/>',
}

def icon(name, cls="icon"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'

def pic(name, alt, cls="", eager=False, sizes="(min-width: 900px) 50vw, 100vw"):
    variants = sorted(IMG.glob(f"{name}-*.jpg"), key=lambda p: int(p.stem.rsplit("-", 1)[1]))
    if not variants:
        raise SystemExit(f"missing image {name}")
    dims = [Image.open(v).size for v in variants]
    w, h = dims[-1]
    src_webp = ", ".join(f"assets/img/{v.stem}.webp {d[0]}w" for v, d in zip(variants, dims))
    src_jpg = ", ".join(f"assets/img/{v.name} {d[0]}w" for v, d in zip(variants, dims))
    load = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return (f'<picture{c}><source type="image/webp" srcset="{src_webp}" sizes="{sizes}">'
            f'<img src="assets/img/{variants[-1].name}" srcset="{src_jpg}" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{alt}" {load}></picture>')

NAV = [
    ("rentals", "Rentals", [
        ("rentals.html", "Available Rentals", "Browse homes for lease"),
        ("rentals.html#apply", "How to Apply", "Screening criteria & steps"),
        ("rentals.html#find", "Help Me Find a Home", "Tell us what you need"),
    ]),
    ("owners", "Owners", [
        ("owners.html", "Property Management Services", "What's included"),
        ("owners.html#pricing", "Pricing & Fees", "Simple, published rates"),
        ("faq.html", "Owner FAQs", "Answers before you sign"),
        (PORTAL, "Owner Portal Login", "Statements & documents"),
    ]),
    ("residents", "Residents", [
        ("residents.html", "Resident Center", "Portal, rent & maintenance"),
        ("residents.html#utilities", "Utility Setup", "Required before move-in"),
        ("residents.html#diy", "DIY Troubleshooting", "Quick fixes before you call"),
        ("residents.html#fair-housing", "Fair Housing", "Your rights as a renter"),
    ]),
    ("agents", "Agents", None),
    ("about", "About", [
        ("about.html", "Meet Our Team", "The people behind SierraLV"),
        ("local-guide.html", "Las Vegas Local Guide", "Utilities, schools & city links"),
        ("https://www.sierralasvegas.com/news", "Community News", "Our Las Vegas blog"),
        ("about.html#careers", "Careers", "Now hiring"),
    ]),
    ("contact", "Contact", None),
]

def is_ext(h): return h.startswith("http")

def header(active):
    lis = []
    for key, label, sub in NAV:
        if sub is None:
            cur = ' aria-current="page"' if key == active else ""
            lis.append(f'<li class="nav__item"><a href="{key}.html"{cur}>{label}</a></li>')
        else:
            links = "".join(
                f'<li><a href="{h}"{" target=\"_blank\" rel=\"noopener\"" if is_ext(h) else ""}>{t}<small>{d}</small></a></li>'
                for h, t, d in sub)
            cur = ' style="color:var(--accent)"' if key == active else ""
            lis.append(f'<li class="nav__item" data-dropdown><button type="button" aria-expanded="false" aria-controls="sub-{key}"{cur}>{label}{icon("chev","caret")}</button>'
                       f'<ul class="nav__sub" id="sub-{key}">{links}</ul></li>')
    return f'''<a class="skip" href="#main">Skip to content</a>
<div class="topbar"><div class="container">
  <a href="tel:{PHONE}">Call {PHONE}</a>
  <span class="topbar__hours">Mon–Fri 9am–5pm · 2831 St Rose Pkwy #200, Henderson</span>
  <a href="{PORTAL}" target="_blank" rel="noopener">Portal Login</a>
</div></div>
<header class="site-header">
  <div class="container site-header__inner">
    <a class="brand" href="index.html" aria-label="SierraLV Property Management &amp; Realty — home"><img src="assets/img/logo.png" width="600" height="134" alt="SierraLV Property Management &amp; Realty"></a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">{icon("menu")}Menu</button>
    <nav class="nav" id="site-nav" aria-label="Main">
      <ul class="nav__list">{"".join(lis)}</ul>
      <div class="nav__cta">
        <a class="btn btn--ghost" href="{PORTAL}" target="_blank" rel="noopener">Portal Login</a>
        <a class="btn btn--primary" href="contact.html#rental-analysis">Free Rental Analysis</a>
      </div>
    </nav>
  </div>
</header>'''

def footer():
    return f'''<section class="cta-band">
  <div class="container cta-band__inner">
    <div class="stack-16">
      <p class="t-eyebrow" style="color:var(--on-accent-soft)">Own a rental in Las Vegas or Henderson?</p>
      <h2 class="t-h2">Find out what your home <em class="serif">should</em> rent for.</h2>
      <p class="t-lead">A free, no-obligation rental analysis based on comparable homes leased in your neighborhood over the last six months.</p>
    </div>
    <div class="btn-row">
      <a class="btn btn--light" href="contact.html#rental-analysis">Get My Free Analysis</a>
      <a class="btn btn--ghost-light" href="tel:{PHONE}">{icon("phone")}{PHONE}</a>
    </div>
  </div>
</section>
<footer class="site-footer">
  <div class="container">
    <div class="footer__top">
      <div class="footer__brand">
        <img src="assets/img/logo.png" width="600" height="134" alt="SierraLV Property Management &amp; Realty" loading="lazy">
        <p>Full-service residential property management and realty serving Las Vegas, Henderson and North Las Vegas for 20+ years.</p>
      </div>
      <div class="footer__col"><h2>Owners</h2><ul>
        <li><a href="owners.html">Management Services</a></li>
        <li><a href="owners.html#pricing">Pricing &amp; Fees</a></li>
        <li><a href="https://www.sierralasvegas.com/pm-agreement" target="_blank" rel="noopener">Management Agreement</a></li>
        <li><a href="faq.html">FAQs</a></li>
        <li><a href="https://www.sierralasvegas.com/properties" target="_blank" rel="noopener">Homes for Sale</a></li>
      </ul></div>
      <div class="footer__col"><h2>Residents</h2><ul>
        <li><a href="rentals.html">Available Rentals</a></li>
        <li><a href="residents.html">Resident Center</a></li>
        <li><a href="residents.html#utilities">Utility Setup</a></li>
        <li><a href="residents.html#diy">DIY Troubleshooting</a></li>
        <li><a href="local-guide.html">Local Guide</a></li>
      </ul></div>
      <div class="footer__col"><h2>Company</h2><ul>
        <li><a href="about.html">About Us</a></li>
        <li><a href="agents.html">Agent Referrals</a></li>
        <li><a href="https://www.sierralasvegas.com/news" target="_blank" rel="noopener">Community News</a></li>
        <li><a href="about.html#careers">Careers</a></li>
        <li><a href="contact.html">Contact</a></li>
      </ul></div>
      <div class="footer__col"><h2>Visit</h2><ul>
        <li>2831 St Rose Pkwy #200<br>Henderson, NV 89052</li>
        <li><a href="tel:{PHONE}">{PHONE}</a></li>
        <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
        <li>Mon–Fri 9am–5pm<br>Sat &amp; Sun closed</li>
      </ul></div>
    </div>
    <div class="footer__bottom">
      <div>© <span id="year">2026</span> SierraLV Property Management &amp; Realty · Broker Lic# NV B.1003308.LLC · PM# .0166264.BKR<br>
      SierraLV is an Equal Opportunity Employer and supports the Fair Housing Act. ·
      <a href="https://www.sierralasvegas.com/privacy-policy" target="_blank" rel="noopener">Privacy Policy</a> ·
      <a href="https://www.sierralasvegas.com/terms-and-conditions" target="_blank" rel="noopener">Terms</a></div>
      <div class="footer__badges"><span class="badge">NARPM® Member</span><span class="badge">{icon("home")}Equal Housing Opportunity</span></div>
    </div>
  </div>
</footer>
<script src="js/script.js" defer></script>'''

def render(path):
    raw = path.read_text()
    m = re.match(r"<!--(\{.*?\})-->\n", raw, re.S)
    meta = json.loads(m.group(1)); body = raw[m.end():]
    body = body.replace("{{PHONE}}", PHONE).replace("{{EMAIL}}", EMAIL).replace("{{PORTAL}}", PORTAL).replace("{{LISTINGS}}", LISTINGS)
    body = re.sub(r"\{\{icon:(\w+)\}\}", lambda mm: icon(mm.group(1)), body)
    def picsub(mm):
        parts = mm.group(1).split("|")
        return pic(parts[0], parts[1], parts[2] if len(parts) > 2 else "", len(parts) > 3 and parts[3] == "eager",
                   parts[4] if len(parts) > 4 else "(min-width: 900px) 50vw, 100vw")
    body = re.sub(r"\{\{pic:([^}]+)\}\}", picsub, body)
    preload = ""
    if meta.get("preload"):
        n = meta["preload"]
        vs = sorted(IMG.glob(f"{n}-*.webp"), key=lambda p: int(p.stem.rsplit("-", 1)[1]))
        ss = ", ".join(f"assets/img/{v.name} {Image.open(v).size[0]}w" for v in vs)
        preload = f'<link rel="preload" as="image" type="image/webp" imagesrcset="{ss}" imagesizes="100vw" fetchpriority="high">'
    html = f'''<!doctype html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{meta["title"]}</title>
<meta name="description" content="{meta["desc"]}">
<meta property="og:title" content="{meta["title"]}">
<meta property="og:description" content="{meta["desc"]}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#004187">
<link rel="preload" href="assets/fonts/InstrumentSerif-normal-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/Manrope-var.woff2" as="font" type="font/woff2" crossorigin>
{preload}
<link rel="stylesheet" href="css/styles.css">
{meta.get("head", "")}
</head>
<body>
{header(meta.get("nav"))}
<main id="main">
{body}
</main>
{footer()}
</body>
</html>
'''
    out = ROOT / path.name
    out.write_text(html)
    print("built", out.name)

for p in sorted((ROOT / "src" / "pages").glob("*.html")):
    render(p)
