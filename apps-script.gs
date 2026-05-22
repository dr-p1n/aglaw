/**
 * ════════════════════════════════════════════════════════════════
 *  AG LAW — Contact form backend (Google Apps Script)
 *
 *  Receives form submissions from albertoeguerrap.com (and /en/),
 *  logs each one to a Google Sheet, emails Alberto, screens spam
 *  with Cloudflare Turnstile + honeypot, and archives rows older
 *  than 24 months on a monthly schedule.
 * ════════════════════════════════════════════════════════════════
 *
 *  SETUP (≈ 10 minutes, one time):
 *
 *  1. Sign in to Google with the account that should own submissions
 *     (julioernestolv@gmail.com is the recommended owner; that's
 *     your retainer leverage — see "Sheet sharing" notes below).
 *
 *  2. Go to https://sheets.google.com → blank sheet → rename it
 *     "AG Law — Contact Form Submissions".
 *
 *  3. Extensions menu → Apps Script. Delete any starter code in the
 *     editor and paste this entire file in. Save (Ctrl/Cmd+S).
 *
 *  4. (OPTIONAL but recommended — adds bot protection)
 *     Get a free Turnstile sitekey + secret at
 *     https://dash.cloudflare.com/?to=/:account/turnstile.
 *     Configure widget mode "Invisible". You'll get TWO values:
 *       - Sitekey  → goes into index.html and en/index.html
 *                    (replace YOUR_TURNSTILE_SITEKEY in both)
 *       - Secret   → goes into TURNSTILE_SECRET below
 *     Skip this step entirely to deploy with only the honeypot.
 *     (Leave TURNSTILE_SECRET = "" and remove the .cf-turnstile div
 *     from both HTML files.)
 *
 *  5. Edit the CONFIG block below:
 *     - NOTIFY_EMAIL    : where new-submission emails go (Alberto).
 *     - SHEET_NAME      : main tab name. Default "Sheet1" matches a
 *                          fresh sheet; change if you renamed the tab.
 *     - TURNSTILE_SECRET: from step 4, or leave "" to skip.
 *
 *  6. Click "Deploy" (top right) → "New deployment" →
 *     gear icon → "Web app".
 *     - Description     : "AG Law contact form v1"
 *     - Execute as      : Me (your account)
 *     - Who has access  : Anyone
 *     Click "Deploy". Google will ask for permissions — approve:
 *       · See, edit, create, and delete your spreadsheets in Drive
 *       · Send email as you
 *       · Connect to an external service (only if Turnstile enabled)
 *     You'll see "Google hasn't verified" — Advanced → "Go to …
 *     (unsafe)". It's your own script, safe to approve.
 *
 *  7. Copy the "Web app URL". Looks like:
 *     https://script.google.com/macros/s/AKfycb…/exec
 *
 *  8. The HTML files don't talk to this URL directly — they go
 *     through a Cloudflare Worker proxy (see worker.js). Open the
 *     ag-law-forms Worker in the Cloudflare dashboard, Settings →
 *     Variables → APPS_SCRIPT_URL (Secret), and paste this URL.
 *     Save and Deploy. No HTML edits needed.
 *
 *  9. Set up the retention trigger (one-time):
 *     In the editor, click the clock icon (Triggers) in the left
 *     rail → Add Trigger → function: archiveOldRows →
 *     event source: Time-driven → type: Month timer → 1st of every
 *     month, 03:00–04:00. Save.
 *
 * 10. Iterating later: each time you edit this script, click
 *     "Deploy" → "Manage deployments" → pencil icon → Version
 *     "New version" → Deploy. The URL stays the same.
 *     OR: while iterating, use Deploy → "Test deployments" →
 *     copy that URL into ENDPOINT in the HTML. The Test URL always
 *     reflects the latest saved code, no redeploy needed.
 *
 * ════════════════════════════════════════════════════════════════
 *  SHEET SHARING & RETAINER LEVERAGE
 *
 *  The Sheet stays under julioernestolv@gmail.com. Alberto receives
 *  email notifications but no Sheet access by default. If he asks
 *  to browse historic leads, share as Viewer (read-only) and note
 *  the date you did. Jaime gets no access — he never sees customer
 *  data. If the relationship ends, you hand over a CSV export, not
 *  the live pipeline.
 * ════════════════════════════════════════════════════════════════
 */

// ── CONFIG ──────────────────────────────────────────────────────
const NOTIFY_EMAIL      = "guerra.juridico10@gmail.com";
const SHEET_NAME        = "Sheet1";
const SPAM_SHEET_NAME   = "Spam Attempts";
const SITE_NAME         = "albertoeguerrap.com";

// Cloudflare Turnstile secret. Get one free at
// https://dash.cloudflare.com/?to=/:account/turnstile
// Leave as "" to skip verification (useful while testing the basic flow).
const TURNSTILE_SECRET  = "";
// ────────────────────────────────────────────────────────────────


function doPost(e) {
  try {
    const data = e.parameter || {};

    // Honeypot: bots fill every field. Real users won't touch "website".
    if (data.website) {
      logSpam(data, "honeypot");
      return jsonResponse({ ok: true, skipped: "honeypot" });
    }

    // Turnstile verification (skipped if secret not configured)
    if (TURNSTILE_SECRET) {
      const token = data["cf-turnstile-response"];
      if (!verifyTurnstile(token)) {
        logSpam(data, "turnstile_failed");
        // Return ok to avoid signalling bots that they were caught
        return jsonResponse({ ok: true, skipped: "turnstile" });
      }
    }

    const row = {
      timestamp: new Date(),
      nombre:    (data.nombre  || "").toString().slice(0, 200),
      email:     (data.email   || "").toString().slice(0, 200),
      empresa:   (data.empresa || "").toString().slice(0, 200),
      area:      (data.area    || "").toString().slice(0, 200),
      mensaje:   (data.mensaje || "").toString().slice(0, 5000)
    };

    // Minimum sanity check
    if (!row.nombre || !row.email || !row.mensaje) {
      return jsonResponse({ ok: false, error: "missing_fields" }, 400);
    }

    appendToSheet(row);
    sendNotification(row);

    return jsonResponse({ ok: true });
  } catch (err) {
    console.error(err);
    return jsonResponse({ ok: false, error: String(err) }, 500);
  }
}


function verifyTurnstile(token) {
  if (!token) return false;
  try {
    const res = UrlFetchApp.fetch(
      "https://challenges.cloudflare.com/turnstile/v0/siteverify",
      {
        method: "post",
        payload: { secret: TURNSTILE_SECRET, response: token },
        muteHttpExceptions: true
      }
    );
    const body = JSON.parse(res.getContentText());
    return body && body.success === true;
  } catch (err) {
    console.error("Turnstile verify failed:", err);
    return false;
  }
}


function logSpam(data, reason) {
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let sheet = ss.getSheetByName(SPAM_SHEET_NAME);
    if (!sheet) {
      sheet = ss.insertSheet(SPAM_SHEET_NAME);
      sheet.appendRow(["Fecha", "Motivo", "Nombre", "Email", "Mensaje (truncado)"]);
      sheet.getRange(1, 1, 1, 5).setFontWeight("bold");
      sheet.setFrozenRows(1);
    }
    sheet.appendRow([
      new Date(),
      reason,
      (data.nombre  || "").toString().slice(0, 200),
      (data.email   || "").toString().slice(0, 200),
      (data.mensaje || "").toString().slice(0, 500)
    ]);
  } catch (err) {
    console.error("logSpam failed:", err);
  }
}


function appendToSheet(row) {
  const ss    = SpreadsheetApp.getActiveSpreadsheet();
  let sheet   = ss.getSheetByName(SHEET_NAME);
  if (!sheet) sheet = ss.insertSheet(SHEET_NAME);

  // Add header row if sheet is empty
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(["Fecha", "Nombre", "Email", "Empresa", "Área", "Mensaje"]);
    sheet.getRange(1, 1, 1, 6).setFontWeight("bold");
    sheet.setFrozenRows(1);
  }

  sheet.appendRow([
    row.timestamp,
    row.nombre,
    row.email,
    row.empresa,
    row.area,
    row.mensaje
  ]);
}


function sendNotification(row) {
  const subject = "Nueva consulta — " + (row.nombre || "Sin nombre") + " · " + SITE_NAME;

  const body =
    "Nueva consulta recibida desde " + SITE_NAME + ":\n\n" +
    "Nombre:   " + row.nombre  + "\n" +
    "Email:    " + row.email   + "\n" +
    "Empresa:  " + (row.empresa || "—") + "\n" +
    "Área:     " + (row.area    || "—") + "\n\n" +
    "Mensaje:\n" + row.mensaje + "\n\n" +
    "—\n" +
    "Recibida: " + row.timestamp.toLocaleString("es-PA") + "\n" +
    "Para responder, simplemente responda este correo " +
    "(el remitente aparecerá como el cliente).";

  MailApp.sendEmail({
    to:      NOTIFY_EMAIL,
    subject: subject,
    body:    body,
    replyTo: row.email
  });
}


function jsonResponse(obj, status) {
  // Apps Script Web Apps don't expose HTTP status codes to the client,
  // but we set the body so the fetch() call can inspect res.ok via the
  // "ok" key if it ever parses JSON. (Default fetch only checks status,
  // which Apps Script always returns 200 for — that's a limitation.)
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}


// Optional: lets you visit the Web App URL in a browser to confirm
// it's deployed correctly. You should see {"ok":true,"service":"AG Law contact"}
function doGet() {
  return jsonResponse({ ok: true, service: "AG Law contact" });
}


/**
 * ─── RETENTION ──────────────────────────────────────────────────
 *  Moves rows older than RETENTION_MONTHS from the main sheet
 *  to an "Archive" tab. Run manually once to verify, then attach
 *  a monthly time-driven trigger:
 *
 *    1. In the Apps Script editor, click the clock icon (Triggers)
 *       in the left rail.
 *    2. Add Trigger → function: archiveOldRows
 *       event source: Time-driven
 *       type: Month timer → 1st of every month, 03:00–04:00.
 *    3. Save. Google will ask for additional permissions (Drive scope).
 *
 *  Sheets auto-versions in Drive, so the Archive tab is itself
 *  recoverable. No separate backup needed for years.
 * ────────────────────────────────────────────────────────────────
 */
const RETENTION_MONTHS = 24;
const ARCHIVE_SHEET_NAME = "Archive";

function archiveOldRows() {
  const ss      = SpreadsheetApp.getActiveSpreadsheet();
  const source  = ss.getSheetByName(SHEET_NAME);
  if (!source || source.getLastRow() < 2) return;

  let archive = ss.getSheetByName(ARCHIVE_SHEET_NAME);
  if (!archive) {
    archive = ss.insertSheet(ARCHIVE_SHEET_NAME);
    archive.appendRow(source.getRange(1, 1, 1, source.getLastColumn()).getValues()[0]);
    archive.getRange(1, 1, 1, source.getLastColumn()).setFontWeight("bold");
    archive.setFrozenRows(1);
  }

  const cutoff = new Date();
  cutoff.setMonth(cutoff.getMonth() - RETENTION_MONTHS);

  const lastRow = source.getLastRow();
  const range   = source.getRange(2, 1, lastRow - 1, source.getLastColumn());
  const values  = range.getValues();

  const toArchive = [];
  const toKeep    = [];
  values.forEach(row => {
    const ts = row[0] instanceof Date ? row[0] : new Date(row[0]);
    (ts < cutoff ? toArchive : toKeep).push(row);
  });

  if (toArchive.length === 0) return;

  archive.getRange(archive.getLastRow() + 1, 1, toArchive.length, toArchive[0].length)
         .setValues(toArchive);

  range.clearContent();
  if (toKeep.length) {
    source.getRange(2, 1, toKeep.length, toKeep[0].length).setValues(toKeep);
  }

  console.log("Archived " + toArchive.length + " row(s) older than " + RETENTION_MONTHS + " months.");
}
