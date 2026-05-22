/**
 * ════════════════════════════════════════════════════════════════
 *  AG LAW — Cloudflare Worker form proxy
 *
 *  Sits between albertoeguerrap.com and the Google Apps Script
 *  Web App. Browser → forms.ptytropicsadvisors.com/aglaw → Apps
 *  Script → Sheet/email. The script URL never appears in HTML.
 * ════════════════════════════════════════════════════════════════
 *
 *  DEPLOY (Cloudflare dashboard — ≈ 5 minutes):
 *
 *  1. Sign in at https://dash.cloudflare.com with
 *     prototype1@ptyadvisors.com.
 *
 *  2. Pick the ptytropicsadvisors.com zone. Make sure DNS is on
 *     Cloudflare nameservers (Overview tab should say "Active").
 *
 *  3. Workers & Pages → Create application → Create Worker.
 *     Name: ag-law-forms. Click Deploy (creates a stub),
 *     then "Edit code".
 *
 *  4. Delete the stub. Paste this entire file. Save and Deploy.
 *
 *  5. Settings → Triggers → Custom Domains → Add Custom Domain
 *     → forms.ptytropicsadvisors.com. Cloudflare provisions DNS
 *     + SSL automatically (~1 min, no certs to manage).
 *
 *  6. Settings → Variables → Add variable → Type: Secret
 *     Name:  APPS_SCRIPT_URL
 *     Value: <the Apps Script Web App URL from apps-script.gs setup>
 *     Save and Deploy.
 *
 *  7. Verify health check:
 *       curl https://forms.ptytropicsadvisors.com/aglaw
 *       → {"ok":true,"service":"ag-law-forms"}
 *
 *  8. Verify forwarding (the Sheet should get a row + email):
 *       curl -X POST https://forms.ptytropicsadvisors.com/aglaw \
 *         -H "Origin: https://albertoeguerrap.com" \
 *         --data-urlencode "nombre=Worker Test" \
 *         --data-urlencode "email=julioernestolv@gmail.com" \
 *         --data-urlencode "mensaje=Forwarded through worker"
 *
 *  Rotating the backend later: just change the APPS_SCRIPT_URL
 *  secret in step 6. No HTML changes needed.
 *
 * ════════════════════════════════════════════════════════════════
 */

const ALLOWED_ORIGINS = new Set([
  "https://albertoeguerrap.com",
  "https://www.albertoeguerrap.com",
]);

const ROUTE = "/aglaw";

function corsHeaders(origin) {
  const allow = ALLOWED_ORIGINS.has(origin) ? origin : "https://albertoeguerrap.com";
  return {
    "Access-Control-Allow-Origin":  allow,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age":       "86400",
    "Vary":                         "Origin",
  };
}

function jsonResponse(obj, status, origin) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      ...corsHeaders(origin),
    },
  });
}

export default {
  async fetch(request, env) {
    const url    = new URL(request.url);
    const origin = request.headers.get("Origin") || "";

    // ── Preflight ─────────────────────────────────────────────
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(origin) });
    }

    // ── Health check ──────────────────────────────────────────
    if (request.method === "GET" && url.pathname === ROUTE) {
      return jsonResponse({ ok: true, service: "ag-law-forms" }, 200, origin);
    }

    // ── Wrong method / wrong route ────────────────────────────
    if (request.method !== "POST" || url.pathname !== ROUTE) {
      return jsonResponse({ ok: false, error: "not_found" }, 404, origin);
    }

    // ── Origin lock (defense in depth — browser also enforces) ─
    if (!ALLOWED_ORIGINS.has(origin)) {
      return jsonResponse({ ok: false, error: "forbidden_origin" }, 403, origin);
    }

    // ── Config sanity ─────────────────────────────────────────
    if (!env.APPS_SCRIPT_URL) {
      return jsonResponse({ ok: false, error: "backend_not_configured" }, 500, origin);
    }

    // ── Forward to Apps Script ────────────────────────────────
    try {
      const body = await request.text();

      const upstream = await fetch(env.APPS_SCRIPT_URL, {
        method: "POST",
        headers: {
          "Content-Type":
            request.headers.get("Content-Type") || "application/x-www-form-urlencoded",
        },
        body,
        redirect: "follow",
      });

      const text = await upstream.text();
      return new Response(text, {
        status: 200, // Apps Script always returns 200 regardless; normalize.
        headers: {
          "Content-Type":
            upstream.headers.get("Content-Type") || "application/json; charset=utf-8",
          ...corsHeaders(origin),
        },
      });
    } catch (err) {
      return jsonResponse({ ok: false, error: "upstream_failed" }, 502, origin);
    }
  },
};
