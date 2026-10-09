# Deploy CareerPilot AI to Cloudflare Workers

The original Python/Streamlit + SQLite app remains in the repository and still runs with `streamlit run app.py`. Cloudflare Workers cannot directly host that Python Streamlit server.

This repository now includes an independent, lightweight web edition in `web/` with a deterministic browser-side CV matcher, job application tracking, analytics, CSV export and JSON backups.

## Cloudflare Git integration

1. Cloudflare Dashboard → Workers & Pages → select the connected Worker.
2. Confirm the connected GitHub repository is `Fahimxbd/careerpilot-ai`, branch `main`.
3. Build command: **leave blank** (the web edition needs no build).
4. Deploy command: `npx wrangler deploy`.
5. Root directory: repository root. The root `wrangler.jsonc` points at `./web`.
6. Save and redeploy the latest commit. Wrangler prints the exact `*.workers.dev` URL after success.

Cloudflare may initially autodetect `requirements.txt` and run `pip install`; that installation is unrelated to the browser edition and can be disabled in the Cloudflare build settings to save time. No pip install is required for this Worker deployment.

## Privacy and limitations

- App data is stored in the browser via `localStorage`. No server-side SQLite or multi-device synchronization exists in this version.
- CV matching runs entirely in the browser. Its TF-IDF approximation may not be identical to scikit-learn.
- Export JSON backups regularly; clearing browser storage deletes records.
- Demo companies are fictitious.
- Do not submit confidential CVs on shared devices.
- No secrets, API keys or paid third-party service is required.

## Test before publishing

```bash
node --test web/matcher.test.mjs
npx wrangler deploy --dry-run
```

Production deploy:

```bash
npx wrangler deploy
```

Cloudflare credentials and account access must be configured before a manual deployment.
