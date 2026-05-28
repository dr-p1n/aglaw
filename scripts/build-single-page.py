#!/usr/bin/env python3
"""
Build dist/index.html — a single self-contained HTML file for drop-in
deployment on any web server (GoDaddy, etc).

Combines the 5 Spanish pages into one long-scroll page with anchor nav,
inlines styles.css, embeds the hero photo as base64, merges all
schema.org JSON-LD into one @graph.

Output: dist/index.html  (no other files needed)

Run from repo root:   python3 scripts/build-single-page.py
"""
import re
import json
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist'
DIST.mkdir(exist_ok=True)


# ─── Inputs ──────────────────────────────────────────────────────────
CSS = (ROOT / 'styles.css').read_text()
PHOTO_URI = 'data:image/jpeg;base64,' + base64.b64encode(
    (ROOT / 'img/alberto-temp.jpg').read_bytes()
).decode()


def read(path):
    return (ROOT / path).read_text()


def main_inner(html):
    m = re.search(r'<main[^>]*>(.*?)</main>', html, re.S)
    return m.group(1).strip() if m else ''


def get_section_by_class(html, cls):
    """Return one <section class=\"cls\"> ... </section> block, depth-aware."""
    m = re.search(rf'<section\s+class="{cls}"[^>]*>', html)
    if not m:
        return ''
    start = m.start()
    depth = 0
    pos = m.end()
    while pos < len(html):
        no = re.search(r'<section\b[^>]*>', html[pos:])
        nc = re.search(r'</section>', html[pos:])
        if not nc:
            break
        if no and no.start() < nc.start():
            depth += 1
            pos += no.end()
        else:
            if depth == 0:
                return html[start:pos + nc.end()]
            depth -= 1
            pos += nc.end()
    return ''


def extract_schema_graph_items(html):
    """Pull the JSON-LD object(s) from a page and return a list of @graph items."""
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    items = []
    for block in blocks:
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        if '@graph' in data:
            items.extend(data['@graph'])
        else:
            # Strip top-level @context — will be set once on the combined graph
            data.pop('@context', None)
            items.append(data)
    return items


# ─── Pull all the page content ────────────────────────────────────────
home_html     = read('index.html')
practica_html = read('practica/index.html')
red_html      = read('red/index.html')
recursos_html = read('recursos/index.html')
perfil_html   = read('perfil/index.html')

home_main = main_inner(home_html)
hero_section    = get_section_by_class(home_main, 'hero')
intro_section   = get_section_by_class(home_main, 'intro')
contact_section = get_section_by_class(home_main, 'contact')
form_section    = get_section_by_class(home_main, 'contact-form-section')

# Swap in base64 photo
hero_section = hero_section.replace('/img/alberto-temp.jpg', PHOTO_URI)

# Sub-page <main> blocks wrapped with anchor ids for nav targets
def wrap_with_anchor(html, anchor_id):
    inner = main_inner(html)
    # Rewrite internal links to point to anchors instead of separate URLs
    inner = inner.replace('href="/practica/"', 'href="#practica"')
    inner = inner.replace('href="/red/"',      'href="#red"')
    inner = inner.replace('href="/recursos/"', 'href="#recursos"')
    inner = inner.replace('href="/perfil/"',   'href="#perfil"')
    return f'<div id="{anchor_id}">\n{inner}\n</div>'


practica_block = wrap_with_anchor(practica_html, 'practica')
red_block      = wrap_with_anchor(red_html, 'red')
recursos_block = wrap_with_anchor(recursos_html, 'recursos')
perfil_block   = wrap_with_anchor(perfil_html, 'perfil')


# ─── Merge schema ─────────────────────────────────────────────────────
graph_items = []
seen_ids = set()
for src in (home_html, practica_html, red_html, recursos_html, perfil_html):
    for item in extract_schema_graph_items(src):
        item_id = item.get('@id')
        if item_id and item_id in seen_ids:
            continue
        if item_id:
            seen_ids.add(item_id)
        graph_items.append(item)

combined_schema = {
    "@context": "https://schema.org",
    "@graph": graph_items,
}


# ─── Footer (from any page, but pull from home for safety) ────────────
footer_match = re.search(r'<footer[^>]*>(.*?)</footer>', home_html, re.S)
footer_inner = footer_match.group(1) if footer_match else ''


# ─── Compose final HTML ───────────────────────────────────────────────
HTML = f'''<!DOCTYPE html>
<!--
═══════════════════════════════════════════════════════════════════════
  ALBERTO E. GUERRA P. — single-file deployment build
  ════════════════════════════════════════════════════════════════════
  Generated from the 5-page source in /Users/jelv/AG_law/ via
  scripts/build-single-page.py. Re-run after copy edits to refresh.

  Drop this file as index.html on any web server. No other files
  needed — CSS is inlined, hero photo is base64-embedded, fonts and
  the form backend are external. The contact form posts to
  forms.ptytropicsadvisors.com/aglaw (Cloudflare Worker → Apps Script).

  Before launch:
    1. Replace YOUR_TURNSTILE_SITEKEY (search this file) with a real
       Cloudflare Turnstile sitekey.
    2. Make sure the Worker (forms.ptytropicsadvisors.com/aglaw) is
       deployed and pointing at the Apps Script Web App URL.
═══════════════════════════════════════════════════════════════════════
-->
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="referrer" content="strict-origin-when-cross-origin">

<title>Alberto Guerra | Abogado Internacional en Panamá</title>
<meta name="description" content="Bufete de abogados en Panamá con 38 años de trayectoria internacional. Derecho internacional, comercial, marítimo, deportivo y propiedad industrial. Alianza con Crespo &amp; Ruiz, Madrid.">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
<link rel="canonical" href="https://albertoeguerrap.com/">

<meta property="og:type" content="website">
<meta property="og:url" content="https://albertoeguerrap.com/">
<meta property="og:title" content="Alberto Guerra | Abogado Internacional en Panamá">
<meta property="og:description" content="38 años resolviendo asuntos legales complejos en Panamá y el mundo.">
<meta property="og:locale" content="es_PA">

<meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; script-src 'self' 'unsafe-inline' https://challenges.cloudflare.com; frame-src https://www.google.com https://challenges.cloudflare.com; connect-src https://forms.ptytropicsadvisors.com https://challenges.cloudflare.com; form-action https://forms.ptytropicsadvisors.com;">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Outfit:wght@200;300;400&display=swap" rel="stylesheet">

<script type="application/ld+json">
{json.dumps(combined_schema, indent=2, ensure_ascii=False)}
</script>

<style>
{CSS}
</style>
</head>
<body>

<a href="#main" class="skip-link">Saltar al contenido</a>

<nav aria-label="Navegación principal">
  <a href="#top" class="nav-logo">Alberto Guerra</a>
  <ul class="nav-links" role="list">
    <li><a href="#practica">Práctica</a></li>
    <li><a href="#red">Red</a></li>
    <li><a href="#recursos">Recursos</a></li>
    <li><a href="#perfil">Perfil</a></li>
    <li class="nav-cta-wrap">
      <a href="https://wa.me/50766129095?text=Hola%2C%20me%20gustar%C3%ADa%20consultar%20un%20asunto%20legal."
         class="nav-cta" target="_blank" rel="noopener">WhatsApp</a>
    </li>
  </ul>
</nav>

<main id="main">
<span id="top" aria-hidden="true"></span>

{hero_section}

{intro_section}

{practica_block}

{red_block}

{recursos_block}

{perfil_block}

{contact_section}

{form_section}

</main>

<footer role="contentinfo">{footer_inner}</footer>

<!-- Cloudflare Turnstile loader (deferred, non-blocking) -->
<script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>

<!-- Form submit handler -->
<script>
(function() {{
  const form = document.getElementById('contact-form');
  if (!form) return;
  const status     = form.querySelector('.form-status');
  const submitBtn  = form.querySelector('.form-submit');
  const submitText = submitBtn.innerHTML;

  form.addEventListener('submit', async function(e) {{
    e.preventDefault();
    submitBtn.disabled    = true;
    submitBtn.textContent = 'Enviando…';
    status.textContent    = '';
    status.className      = 'form-status';

    try {{
      const res  = await fetch(form.action, {{ method: 'POST', body: new FormData(form) }});
      const data = await res.json();

      if (data.ok) {{
        form.reset();
        status.className   = 'form-status form-status-ok';
        status.textContent = 'Mensaje recibido. Le respondemos en menos de 48 horas hábiles.';
        if (window.turnstile) window.turnstile.reset();
      }} else {{
        throw new Error(data.error || 'unknown');
      }}
    }} catch (err) {{
      status.className   = 'form-status form-status-err';
      status.textContent = 'No pudimos enviar el mensaje. Por favor escríbanos por WhatsApp.';
      console.error('form error:', err);
    }} finally {{
      submitBtn.disabled  = false;
      submitBtn.innerHTML = submitText;
    }}
  }});
}})();
</script>

</body>
</html>
'''

# ─── Write ────────────────────────────────────────────────────────────
out_path = DIST / 'index.html'
out_path.write_text(HTML)

size_kb = out_path.stat().st_size / 1024
print(f'Wrote {out_path} ({size_kb:.1f} KB)')
print(f'  - {len(graph_items)} schema items merged into one @graph')
print(f'  - CSS inlined ({len(CSS)} chars)')
print(f'  - Photo embedded as base64 ({len(PHOTO_URI)} chars)')
