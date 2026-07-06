---
name: deploy
description: Regenerate the dashboard pages, commit, push to master, and redeploy to Vercel production. Use when the user asks to deploy, publish, or push the dashboard changes live.
disable-model-invocation: true
---

Run this exact sequence, in order, from the repo root:

1. `python generate_dashboard.py` — regenerates `index.html`, `applications.html` and `aide.html` from `timeline.json`, `apps.json` and `help.json`.
2. `git status` — review what changed. Stage only the files relevant to the current change; don't sweep in unrelated pending edits (e.g. `timeline.json` updates dropped by an unrelated `/init` session hook).
3. Commit with a message describing what changed and why.
4. `git push`.
5. `vercel --yes --prod --scope isabelleweb13-gmailcoms-projects` — the `--prod` flag is required. Without it, Vercel only creates a preview deployment and leaves the production alias (`dashboard-self-pi-59.vercel.app`) untouched.

Confirm the deployment response shows `"target": "production"` before reporting success to the user.
