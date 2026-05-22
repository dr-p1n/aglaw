# AG Law — website redesign

Static site for **Alberto E. Guerra P.** (AG Law, Panama). Two languages, single page each, typographic minimal aesthetic. Spanish at `/`, English mirror at `/en/`.

## Status: preview mode

Closed-loop UI review for the client. Wired to Cloudflare Pages — every push to `main` auto-deploys.

- Preview URL: _paste your `aglaw-preview.pages.dev` URL here once CF Pages is connected_
- `<meta name="robots" content="noindex, nofollow">` on both pages so the URL won't show up in Google.
- The contact form is stripped — replaced with a WhatsApp CTA button under the address block.
- No backend currently wired. The pieces are committed (`apps-script.gs`, `worker.js`, `.htaccess`) but inert until you flip back to production mode.

## File map

| File | Purpose | Active now? |
|---|---|---|
| `index.html` | Spanish landing (default language) | yes |
| `en/index.html` | English mirror | yes |
| `sitemap.xml` | URL index with hreflang | yes (harmless under noindex) |
| `robots.txt` | Crawler directives | yes |
| `.htaccess`, `en/.htaccess` | Apache config for eventual GoDaddy deploy (security headers, HTTPS, gzip, 404 routing) | no — Cloudflare Pages ignores these |
| `apps-script.gs` | Google Apps Script backend: form submissions → Google Sheet + email notification + 24-month retention | parked |
| `worker.js` | Cloudflare Worker form proxy through `forms.ptytropicsadvisors.com/aglaw` so the Apps Script URL never appears in HTML | parked |

## Going to production

When the design is approved and you're ready to deploy to GoDaddy for `albertoeguerrap.com`:

1. **Rebuild the contact form** in both `index.html` and `en/index.html`. It was stripped in the initial commit. The contract is documented in `apps-script.gs` — field names: `nombre`, `email`, `empresa`, `area`, `mensaje`, plus a hidden honeypot `website` and a `cf-turnstile-response` from the Turnstile widget. Submit posts to the Worker URL (`https://forms.ptytropicsadvisors.com/aglaw`).
2. **Flip robots meta** in both HTML files from `noindex, nofollow` to `index, follow, max-snippet:-1, max-image-preview:large`.
3. **Restore the production CSP** in both meta tags + `.htaccess`. Production CSP allows `https://challenges.cloudflare.com` (Turnstile) and `https://forms.ptytropicsadvisors.com` (form Worker).
4. **Set up Apps Script** — follow the 10-step block at the top of `apps-script.gs`. ~10 min.
5. **Set up the Cloudflare Worker proxy** — follow the 8-step block at the top of `worker.js`. ~5 min. The Worker holds the Apps Script URL as a secret env var.
6. **Set up Cloudflare Turnstile** — get a sitekey + secret from the Cloudflare dashboard. Sitekey → both HTML forms. Secret → Apps Script config.
7. **Hand off to Jaime** for GoDaddy upload. Files for `public_html/`:
   - `index.html`, `en/index.html`
   - `.htaccess`, `en/.htaccess`
   - `robots.txt`, `sitemap.xml`
   - Skip: `apps-script.gs`, `worker.js` — those live on Google / Cloudflare, not on the web server.

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

Worker, Apps Script, and Sheet are all under your account. The Apps Script URL never appears in HTML source — it's a secret env var inside the Worker.

## Useful commands

```bash
# Local preview (cleanest)
python3 -m http.server 8000   # then http://localhost:8000

# Auto-deploy via Cloudflare Pages
git add .
git commit -m "..."
git push
```

## Notes for future-me

- The hero copy "Si cruza fronteras, lo resolvemos" / "If it crosses borders, we handle it" is the core positioning line — uses the informal "we" voice consistently across the site.
- The contact form column is replaced with a WhatsApp CTA in preview mode. When restoring for production, the grid switches back to `1fr 1fr` (see the `.contact-layout` rule).
- The `_archive/` convention for parked files wasn't used — backend files just live in the repo root with `parked` status in the file map above.
