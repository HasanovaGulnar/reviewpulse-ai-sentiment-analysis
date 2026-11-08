# Deploying ReviewPulse publicly (free tier)

This repo is already deploy-ready:

- `models/reviewpulse_sentiment.joblib` (714 KB) is committed, so the app never
  downloads the Yelp sample or retrains at boot.
- `requirements.txt` pins every dependency, including the scikit-learn version
  that produced the artifact (`1.7.2`).
- `.streamlit/config.toml` sets the theme and disables usage stats.
- Runtime data (`data/`, `logs/`) is optional; the app reads metrics from
  `reports/`, which is committed.

Official reference:
<https://docs.streamlit.io/deploy/streamlit-community-cloud>

## Current live deployment

| Item | Value |
|---|---|
| URL | <https://reviewpulse-gulnar.streamlit.app> |
| Host | Streamlit Community Cloud, free tier |
| Branch tracked | `main` (every push redeploys) |
| Python | 3.13.18 (matches the committed artifact) |
| Public status | `https://reviewpulse-gulnar.streamlit.app/api/v2/app/status` → `"status": 5`, `"viewerAuthEnabled": false` |
| Uptime check | `.github/workflows/uptime.yml`, every 30 minutes |

Two things to know about the free tier: the app sleeps after a long period
without traffic and wakes on the next visit (the first load then takes a few
seconds), and the container filesystem resets on restart, so `logs/*.csv` are
per-instance unless `REVIEWPULSE_WEBHOOK_URL` is configured.

To redeploy by hand: open the app in <https://share.streamlit.io>, **Manage
app → Reboot**. To change the Python version: **Manage app → Settings**.

---

## Option A — Streamlit Community Cloud (permanent URL, recommended)

1. Push the repo to GitHub (`main` branch).
2. Open <https://share.streamlit.io> and sign in with GitHub.
3. Click **Create app** → **Yup, I have an app**.
4. Fill in:

   | Field | Value |
   |---|---|
   | Repository | `HasanovaGulnar/reviewpulse-ai-sentiment-analysis` |
   | Branch | `main` |
   | Main file path | `app.py` |
   | App URL | `reviewpulse-gulnar` (or any free subdomain) |

5. Open **Advanced settings**:
   - **Python version:** `3.13` — the model artifact was built with Python
     3.13.9 and scikit-learn 1.7.2. The current deployment runs 3.13.18. If
     3.13 is unavailable, deploy on 3.12 and check the logs; if the artifact
     fails to load, rebuild it locally with `python -m src.train` under the same
     version.
   - **Secrets** (optional, see below).
6. Click **Deploy** and wait 2–4 minutes.
7. Verify:
   - the app loads: `https://<your-subdomain>.streamlit.app`
   - the public status API reports the container as running:
     `https://<your-subdomain>.streamlit.app/api/v2/app/status`
     should contain `"status": 5` and `"viewerAuthEnabled": false`.
     (Community Cloud proxies the app, so `/_stcore/health` and
     `/~/+/healthz` are not usable from outside a browser; the status API is
     the app-specific signal the uptime workflow uses.)
8. Copy the URL into `README.md` and set the repo variable used by the uptime
   workflow:

   ```powershell
   gh variable set REVIEWPULSE_APP_URL --body "https://<your-subdomain>.streamlit.app"
   ```

   (Or: repository → **Settings → Secrets and variables → Actions → Variables**.)

### Secrets (optional but needed for durable feedback)

Paste this into the **Secrets** field:

```toml
REVIEWPULSE_WEBHOOK_URL = "https://script.google.com/macros/s/XXX/exec"
REVIEWPULSE_FEEDBACK_FORM_URL = "https://forms.gle/XXX"
```

- `REVIEWPULSE_WEBHOOK_URL` receives every feedback submission and anonymous
  session/analysis event as JSON. `docs/FEEDBACK.md` includes a Google Apps
  Script that writes them to a spreadsheet.
- `REVIEWPULSE_FEEDBACK_FORM_URL` adds an "open the Google Form" button next to
  the in-app form.

Without a webhook, submissions go to `logs/feedback.csv` inside the container.
That is enough for a laptop demo, but **Streamlit Cloud resets the filesystem
when the app restarts or sleeps**, so a public test round needs the webhook or a
Google Form.

### Notes and limits

- Free tier: 1 GB RAM, CPU only. This app needs ~150 MB, so it fits easily.
- Apps sleep after ~12 hours without traffic; the next visit wakes them.
- The logs tab is only visible to users with write access to the repo.
- Secrets are server-side. They are not sent to the browser.
- Community Cloud runs on Linux; this project has no OS-specific dependency.

### Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `The trained model is missing` | `models/*.joblib` was excluded by `.gitignore` | `git ls-files models/`; commit the artifact |
| `could not be loaded` / version warning | Python or scikit-learn mismatch | Set Python 3.13; confirm `scikit-learn==1.7.2` in the build log; retrain if needed |
| Build fails on install | A package or Python version conflict | Read the build log; all current dependencies ship wheels for 3.12/3.13 |
| App shows "Oh no" | Runtime exception | Open **Manage app → Logs**; also check `logs/errors.csv` locally |
| Feedback disappears | Ephemeral filesystem | Configure `REVIEWPULSE_WEBHOOK_URL` or use a Google Form |
| Uploaded CSV analysis is slow | Large batch | The app caps batches at 5,000 rows and says so |

---

## Option B — Cloudflare quick tunnel (local demo, no hosting account)

Useful when you want a shareable HTTPS link from the laptop without deploying
anything. It is **not** how ReviewPulse is published today: the live app runs on
Streamlit Community Cloud (see the table at the top).

```powershell
# terminal 1 — the app
cd C:\Users\User\reviewpulse-ai-sentiment-analysis

python -m streamlit run app.py --server.headless true --server.port 8501

# terminal 2 — the tunnel (cloudflared.exe downloaded separately)
.\cloudflared.exe tunnel --url http://127.0.0.1:8501 --no-autoupdate
```

The tunnel prints:

```text
https://<random-words>.trycloudflare.com
```

Check `https://<random-words>.trycloudflare.com/_stcore/health` → `ok`.

Limits, and why this is not the permanent answer:

- The URL changes every time `cloudflared` restarts.
- The laptop must stay awake and connected; closing the terminal kills the app.
- Free quick tunnels are rate-limited and not meant for production.
- If you point `REVIEWPULSE_APP_URL` at a tunnel, the uptime workflow will fail
  as soon as the laptop sleeps — that is exactly what happened before the
  Streamlit Cloud deployment.

---

## Option C — Hugging Face Spaces

1. Create a Space → **Streamlit** SDK → free CPU hardware.
2. Connect the GitHub repo, or upload `app.py`, `src/`, `models/`,
   `reports/`, `requirements.txt`, `.streamlit/config.toml`.
3. The Space installs `requirements.txt` and runs `app.py` on port 8501.
4. Add `REVIEWPULSE_WEBHOOK_URL` under **Settings → Variables and secrets**.
5. URL: `https://huggingface.co/spaces/<user>/<space>`.

Spaces sleep after inactivity on the free tier as well, and the filesystem is
ephemeral, so the same feedback guidance applies.

---

## Monitoring and session counts

- **Uptime:** `.github/workflows/uptime.yml` checks the app every 30 minutes and
  fails the job when it is down. It reads the public
  `/api/v2/app/status` endpoint and expects `"status": 5` (running) plus
  `"viewerAuthEnabled": false`, then confirms `GET /` returns 200 after the
  anonymous session redirect. History is the Actions tab. Set
  `REVIEWPULSE_APP_URL` first. GitHub may delay scheduled runs on the free tier;
  for stricter checks use a free UptimeRobot monitor (5-minute interval) on the
  app URL.
- **Errors:** the app logs unhandled prediction errors to `logs/errors.csv` and
  shows the tester a short reference id (`Reference: 1a2b3c4d`). On Cloud this
  file is ephemeral — forward it with the webhook or read the app logs.
- **Unique sessions:** each browser session gets a random 12-character id and
  one `session_start` row in `logs/usage.csv`. The sidebar and the **Model &
  data** tab show unique sessions / analyses / reviews for the current instance.
  Counts reset when a hosted instance restarts; the optional webhook makes them
  durable.

---

## Local reproduction

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

python -m src.data_pipeline   # only needed to rebuild data
python -m src.train           # writes models/ and reports/metrics.json

python -m unittest discover -s tests -v
python scripts/ui_smoke.py
streamlit run app.py
```

## Deployment checklist

- [ ] Repo pushed to `main`
- [ ] `git ls-files models/` shows `reviewpulse_sentiment.joblib`
- [ ] App runs under Python 3.13 (or the model rebuilt under the chosen version)
- [ ] `/api/v2/app/status` shows `"status": 5` and `"viewerAuthEnabled": false`
- [ ] Onboarding box visible in an incognito window
- [ ] One feedback submission lands in durable storage
- [ ] `REVIEWPULSE_APP_URL` set; uptime workflow green
- [ ] Live URL added to `README.md`
- [ ] 3 external testers invited (`docs/TESTER_MESSAGE.md`)
