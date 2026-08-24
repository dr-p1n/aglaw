# AG Law — website

Static site for **Alberto E. Guerra P.** (AG Law, Panama). Five pages, two languages (ES default, EN complete), typographic minimal aesthetic with a portrait-driven hero.

## Status: production

Live at **albertoeguerrap.com** (GoDaddy, Apache). Also mirrored on Cloudflare Pages — every push to `main` auto-deploys to `aglaw-preview.pages.dev`.

- `<meta name="robots" content="index, follow, …">` on all 10 pages.
- **No contact form and no JavaScript.** WhatsApp is the sole contact channel — linked from the nav, the hero CTA, and the Contacto section. The Contacto section also carries the address, hours, and a Google Maps embed.
- Both languages built. hreflang chains validated, sitemap symmetric (10 URLs, 3 alternates each).
- Schema.org: `Attorney` + `LegalService` + `Person` + `FAQPage` + `Article`, all JSON-LD.

### Deploy is two separate steps

Cloudflare Pages auto-deploys on push. **GoDaddy does not** — production serves files uploaded by hand via cPanel File Manager, so a push alone never reaches `albertoeguerrap.com`. Reaching production means regenerating `dist-multipage.zip`, pushing it, and having Jaime re-upload. See `HANDOFF-JAIME.md`.

### Planned: collapse it to one step

The manual upload exists only because the domain points at GoDaddy shared hosting. Pointing it at the Pages project instead makes every push a production deploy, and Jaime never touches files again.

Current DNS:

```
NS       ns75/ns76.domaincontrol.com   (GoDaddy)
A apex   198.12.237.228                (GoDaddy shared hosting)
www      CNAME → apex
MX       none
TXT      none
```

No MX and no TXT: the firm's email is Gmail, not domain email, so nothing but the site itself lives on this domain and a nameserver move cannot break anything else. **Re-check this before cutting over** — the absence of those records is the whole reason this is low-risk.

The route is full nameserver delegation to Cloudflare, not a `www` CNAME, because every canonical, hreflang and sitemap URL in the repo is apex; the CNAME route would force `www` as canonical and mean rewriting all of them.

Repo side is ready — `_headers`, `_redirects` and `404.html` cover everything `.htaccess` was doing that Pages does not do natively. What remains:

1. Attach `albertoeguerrap.com` and `www.albertoeguerrap.com` as custom domains on the `aglaw-preview` Pages project. Can be done before any DNS change.
2. Jaime changes the two nameservers at GoDaddy. One action, and his last.
3. Verify headers, the www redirect, the 404, and the Maps embed on the real domain.

Two things to settle first: during propagation some visitors still land on GoDaddy's older copy (have Jaime upload the current zip once beforehand if that matters), and afterwards the GoDaddy hosting plan is dead weight — cancellable, keeping the domain registration, once confirmed nothing else hangs off that account.

## Site structure

| Page | Spanish URL | English URL | Purpose |
|---|---|---|---|
| Home | `/` | `/en/` | Hero with portrait, intro, services teaser, contact section with Google Maps |
| Practice | `/practica/` | `/en/practice/` | 6-area grid (Internacional, Comercial, Propiedad Industrial, Aduanero, Marítimo, Deportivo) |
| Network | `/red/` | `/en/network/` | Corresponsales + Crespo & Ruiz alliance + history of the firm |
| Resources | `/recursos/` | `/en/resources/` | Educational hub — 10 free guides (accordion) + 6 long-form blog articles |
| About | `/perfil/` | `/en/about/` | Alberto's bio, WBC vice presidency, credentials |

Nav across all pages: **Práctica · Red · Recursos · Perfil · [WhatsApp button] · [ES|EN]**

### Heading rule

**Only the homepage has an `<h1>`.** The 8 sub-pages start at `<h2>` (`.page-hero-title`) and descend from there. This is a deliberate project decision — do not "fix" it.

## File map

```
AG_law/
├── index.html              Page 1 — Home (ES)
├── practica/index.html     Page 2 — Práctica (ES)
├── red/index.html          Page 3 — Red (ES)
├── recursos/index.html     Page 4 — Recursos (ES)
├── perfil/index.html       Page 5 — Perfil (ES)
├── en/
│   ├── index.html          Page 1 — Home (EN)
│   ├── practice/index.html Page 2 — Practice (EN)
│   ├── network/index.html  Page 3 — Network (EN)
│   ├── resources/index.html Page 4 — Resources (EN)
│   └── about/index.html     Page 5 — About (EN)
├── styles.css              Shared stylesheet — single source of truth for all CSS
├── img/alberto.jpg         Hero portrait (1280×853)
├── img/alberto-retrato.jpg Profile portrait (375×562) — © La Prensa, see below
├── img/alberto-cmb.jpg     With the WBC belt (527×338) — © El Siglo, see below
├── favicon.ico             Serif "A" monogram, gold on --bg — 16/32/48 px
├── favicon.svg             Vector version of the same mark
├── apple-touch-icon.png    180 px, iOS home-screen bookmark
├── content/                Source of truth for the Recursos copy (faqs.md, articles.md)
├── sitemap.xml             10 URLs, hreflang-symmetric
├── robots.txt              Crawler directives
├── .htaccess               Apache config — security headers, live on GoDaddy
├── _headers                Same headers for Cloudflare Pages, which ignores .htaccess
├── _redirects              www → apex, for Pages
├── 404.html                Real 404, served by Pages on unmatched paths
├── scripts/
│   ├── build-single-page.py    Regenerates dist/index.html
│   ├── build-dist-multipage.py Regenerates dist-multipage/ and the zip
│   ├── build-favicon.py        Regenerates the three icon files
│   └── extract-copy.py         Regenerates COPY-REVIEW.md from the 10 HTML files
├── dist/index.html         Single self-contained file (CSS inlined, photo base64)
├── dist-multipage/         Multi-file bundle — literal copy of the source files
├── dist-multipage.zip      What Jaime downloads and uploads
├── HANDOFF-JAIME.md        Upload instructions, in Spanish
└── README.md               This file
```

## Content Security Policy

The CSP lives in **two** places and browsers enforce **both**, intersecting them — a source missing from either one is blocked:

1. The response header — from `.htaccess` on Apache/GoDaddy, from `_headers` on Cloudflare Pages. Whichever host is serving the domain supplies it, so **the two files must carry the same policy**; they are byte-identical today and should stay that way.
2. A `<meta http-equiv="Content-Security-Policy">` in each HTML file.

Consequences worth remembering:

- `frame-src https://www.google.com` must be present in the response header **and** in the two home pages, or the Maps embed renders as an empty bordered box. This exact mismatch shipped once and silently blanked the map in production.
- `script-src` deliberately omits `'unsafe-inline'`. The only `<script>` tags left in the site are `type="application/ld+json"` data blocks, which are never evaluated and so are unaffected. Adding real inline JavaScript means loosening this.
- `style-src` keeps `'unsafe-inline'` — several elements still use `style=` attributes.
- `form-action 'none'` — there are no forms.

## Image rights

`img/alberto.jpg` is the client's own photo. The two images on the profile
pages are not:

| File | Source | Where it came from |
|---|---|---|
| `img/alberto-retrato.jpg` | © La Prensa (Panama) | Article on his WBC vice-presidency |
| `img/alberto-cmb.jpg` | © El Siglo (Panama) | Article on his WBC vice-presidency |

Neither is licensed. This was raised and the client's side chose to publish
them anyway; both carry a visible credit line in the page (`.photo-credit`)
rather than running uncredited. If either outlet objects, the fix is to drop
the two `<figure>` blocks from `perfil/index.html` and `en/about/index.html`
and delete the files — nothing else depends on them.

The durable fix is an original from Alberto. His Instagram (`@aguerra62`)
has WBC event photography that would replace both at higher resolution and
with clean rights.

## Regenerating the build artifacts

Run all three after any copy or style edit, then commit everything together:

```bash
python3 scripts/build-single-page.py
```

```bash
python3 scripts/build-dist-multipage.py
```

```bash
python3 scripts/extract-copy.py
```

`dist-multipage/` is a literal copy of the source files (including `.htaccess`), rezipped as `dist-multipage.zip`. The file list lives in `build-dist-multipage.py` — syncing it by hand is how the zip went stale once already. The zip is written with fixed timestamps, so an unchanged site rebuilds to a byte-identical zip instead of a spurious diff.

`build-favicon.py` only needs re-running if the mark itself changes. It requires Pillow and reads Baskerville from the macOS system fonts.

## Useful commands

```bash
python3 -m http.server 8000
```

Note that `python3 -m http.server` ignores `.htaccess`, so it does not reproduce the response-header CSP. Anything that depends on those headers has to be checked against Cloudflare Pages or production.
