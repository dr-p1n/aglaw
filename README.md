# AG Law — website redesign

Static site for **Alberto E. Guerra P.** (AG Law, Panama). Five pages, two languages (ES default, EN coming), typographic minimal aesthetic with a portrait-driven hero.

## Status: preview mode

Closed-loop UI review for the client. Wired to Cloudflare Pages — every push to `main` auto-deploys.

- Preview URL: _paste your `aglaw-preview.pages.dev` URL here once CF Pages is connected_
- `<meta name="robots" content="noindex, nofollow">` on every page.
- No contact form. The persistent WhatsApp CTA in the nav is the primary contact channel during preview.
- Hero photo is a temporary import from the old WordPress site (`/img/alberto-temp.jpg`). Swap when professional headshots arrive.
- Both languages built. hreflang chains validated, sitemap symmetric (10 URLs, 3 alternates each).

## Site structure

| Page | Spanish URL | English URL | Purpose |
|---|---|---|---|
| Home | `/` | `/en/` | Hero with portrait, intro, services teaser, contact section with Google Maps |
| Practice | `/practica/` | `/en/practice/` | 6-area grid (Internacional, Comercial, Propiedad Industrial, Aduanero, Marítimo, Deportivo) |
| Network | `/red/` | `/en/network/` | Corresponsales + Crespo & Ruiz alliance + history of the firm |
| Resources | `/recursos/` | `/en/resources/` | FAQ-style legal resources (4 questions, FAQPage schema) |
| About | `/perfil/` | `/en/about/` | Alberto's bio, WBC vice presidency, credentials |

Nav across all pages: **Práctica · Red · Recursos · Perfil · [WhatsApp button] · [ES|EN]**

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
│   └── about/index.html    Page 5 — About (EN)
├── styles.css              Shared stylesheet — single source of truth for all CSS
├── img/alberto-temp.jpg    Temp hero portrait from WordPress site
├── sitemap.xml             10 URLs, hreflang-symmetric
├── robots.txt              Crawler directives (irrelevant under noindex but harmless)
├── .htaccess               Apache config — parked until GoDaddy production
├── apps-script.gs          Backend — parked, full setup docs in file header
├── worker.js               Cloudflare Worker form proxy — parked, full setup docs in file header
└── README.md               This file
```

## Going to production

When the design is approved and you're ready to deploy to GoDaddy:

1. **Add a contact form** to the Home page (or its own `/contacto/` page). The form contract is documented in `apps-script.gs`.
2. **Flip robots meta** in all 5 (eventually 10) HTML files from `noindex, nofollow` to `index, follow, max-snippet:-1, max-image-preview:large`.
3. **Restore the production CSP** to allow Turnstile + the Worker domain.
4. **Set up the Apps Script backend** — instructions in `apps-script.gs` header.
5. **Set up the Cloudflare Worker proxy** — instructions in `worker.js` header.
6. **Set up Cloudflare Turnstile** — sitekey into the form, secret into Apps Script config.
7. **Hand off to Jaime** for GoDaddy upload. Files for `public_html/`:
   - All HTML files (preserving subdirectory structure)
   - `styles.css`, `img/`, `sitemap.xml`, `robots.txt`, `.htaccess`
   - Skip: `apps-script.gs`, `worker.js` (those live on Google / Cloudflare)

## Production architecture (for reference)

```
Browser (albertoeguerrap.com)
        ↓ form POST
forms.ptytropicsadvisors.com/aglaw    Cloudflare Worker
        ↓
script.google.com/macros/.../exec     Apps Script (Google)
        ↓
Google Sheet                          submissions land here
                                      email fires to Alberto
```

Worker, Apps Script, and Sheet are all under your account.

## Useful commands

```bash
# Local preview (cleanest)
python3 -m http.server 8000   # then http://localhost:8000

# Auto-deploy via Cloudflare Pages
git add .
git commit -m "..."
git push
```
