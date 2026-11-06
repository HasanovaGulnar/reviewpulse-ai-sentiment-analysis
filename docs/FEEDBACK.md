# Feedback round: how to collect it, and where it lands

Goal: **3 or more people outside the program** use the live app for ~5 minutes
and leave structured feedback. One tester can produce several items; three
testers is the minimum, five is a better signal.

## What counts as an external tester

Someone who has not seen the project, the proposal or the code — a classmate
from another track, a friend who sells online, a colleague. Do not coach them
through the UI; the onboarding text is part of what is being tested.

## The 5-minute script to send them

1. Open the live link (see `README.md`).
2. Without reading the repo, use the app: click one example, then paste a real
   review of your own.
3. Try **Batch CSV** → **Download the example CSV** → upload it → analyze.
4. Open **Feedback** and answer the questions below.
5. Screenshot anything that looks wrong.

Questions (the in-app form already asks the important ones):

| # | Question | Bucket |
|---|---|---|
| 1 | In one sentence, what do you think this app does? | Confusion |
| 2 | What did you try, and what did you expect to happen? | Confusion |
| 3 | Did anything break, freeze, or give a result you believe is wrong? | Bug |
| 4 | What is missing that would make this useful to you? | Feature request |
| 5 | Would you use it for your own reviews? Why / why not? | Other |
| 6 | Name or contact — optional, only if you want a reply | — |

## Where submissions land

The app supports three backends, in priority order:

1. **Webhook** (`REVIEWPULSE_WEBHOOK_URL`) — every feedback submission and
   anonymous session event is POSTed as JSON. Use this for a public round.
2. **Google Form** (`REVIEWPULSE_FEEDBACK_FORM_URL`) — a link appears above the
   in-app form; the tester can use either.
3. **Local CSV** (`logs/feedback.csv`) — always written, best effort. Survives
   for the current process only on Streamlit Community Cloud.

The in-app form shows the exact JSON record after submission when no webhook is
configured, so a tester can copy it into a chat if storage is ephemeral.

### Google Apps Script webhook (free, no server)

1. Create a Google Sheet with a tab named `feedback`.
2. Extensions → Apps Script → paste:

   ```javascript
   function doPost(e) {
     const body = JSON.parse(e.postData.contents);
     const sheet = SpreadsheetApp.openById('YOUR_SHEET_ID').getSheetByName('feedback');
     if (body.type === 'feedback') {
       sheet.appendRow([
         new Date(), body.session_id, body.category, body.page,
         body.message, body.contact
       ]);
     } else {
       sheet.appendRow([new Date(), body.session_id, body.type, '', JSON.stringify(body), '']);
     }
     return ContentService.createTextOutput('ok');
   }
   ```

3. Deploy → New deployment → Web app → Execute as **me**, access **Anyone**.
4. Copy the `/exec` URL into `REVIEWPULSE_WEBHOOK_URL` (locally in
   `.streamlit/secrets.toml`, on Cloud in app settings).

The script runs on the initial POST even if Google redirects the response
afterwards, so the row is written either way.

## Triage rules

| Bucket | Test | Example |
|---|---|---|
| **Bug** | The app is supposed to do X and does not, or does it incorrectly | "Download predictions CSV produced an empty file" |
| **Confusion** | The app works but the user cannot tell what happened or what to do | "I did not know which column to pick" |
| **Feature request** | The app works and is understood, but something is missing | "I want a per-product breakdown" |
| **Other** | Praise, questions, out-of-scope | "Nice that it runs locally" |

Rules of thumb:

- If two testers hit the same confusion, treat it as a bug in the interface.
- Do not merge a bug and a feature request into one item.
- Quote the tester verbatim. Paraphrasing hides the wording that caused the
  confusion.
- Severity: **S1** blocks the task, **S2** wrong result, **S3** friction,
  **S4** polish.

## Tracking table

Copy a row per submission. Keep the tester anonymous (initials are enough) and
never paste their review text into this file.

| ID | Date | Tester | Category | Step / page | Verbatim feedback | Severity | Status | Fix commit |
|---|---|---|---|---|---|---|---|---|
| F-01 | | | bug / confusion / feature / other | | | S1–S4 | new / accepted / fixed / declined | |
| F-02 | | | | | | | | |
| F-03 | | | | | | | | |
| F-04 | | | | | | | | |
| F-05 | | | | | | | | |
| F-06 | | | | | | | | |

Status meanings: **new** (not triaged), **accepted** (will fix), **fixed**
(shipped and verified), **declined** (out of scope, with a reason).

## After the round

For every accepted item add a line to `docs/BEFORE_AFTER.md`. The round is only
finished when:

- at least 3 external testers are recorded,
- every item has a bucket and a status,
- at least one accepted item has a shipped fix with a before/after note,
- `docs/LESSONS.md` has the "what real users taught us" summary.

## Consent and privacy

- The form says the app is being tested and that feedback is stored with an
  anonymous session id.
- Review text is never included in feedback records, analytics events or logs.
- Contact details are optional and only used to reply.
- Tell testers they can ask for their row to be deleted.
