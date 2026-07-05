# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projet

Dashboard glassmorphism statique qui visualise l'usage (tokens, coût estimé) de sessions Claude Code, par projet. `generate_dashboard.py` lit `timeline.json` et génère `index.html` (page autonome, sans dépendance externe).

## Commandes

Régénérer le dashboard après une modification de `timeline.json` :

```bash
python generate_dashboard.py
```

## Alimentation de timeline.json

Pas encore automatisée : les entrées sont ajoutées manuellement (via `append_entry()` dans `generate_dashboard.py`, ou édition directe du fichier). Il n'existe pour l'instant aucun hook ou script vérifié qui alimente ce fichier automatiquement.

## Déploiement

Pas de branches : on commit et pousse directement sur `master`. Le redéploiement Vercel est manuel :

```bash
vercel --yes --scope isabelleweb13-gmailcoms-projects
```

Le projet Vercel est `isabelleweb13-gmailcoms-projects/dashboard` (production : https://dashboard-self-pi-59.vercel.app).
