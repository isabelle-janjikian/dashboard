# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projet

Dashboard glassmorphism statique qui visualise l'usage (tokens, coût estimé) de sessions Claude Code, par projet. `generate_dashboard.py` lit `timeline.json` et génère `index.html` (page autonome, sans dépendance externe).

Le même script génère aussi `applications.html` ("Mes applications Claude Code") à partir de `apps.json` : une grille de cards (une par application réalisée avec Claude Code — les dépôts vides/greenfield ne sont pas listés), filtrable par type et par nom de projet, avec un popup "Détails" (description, date de réalisation, pas de lien GitHub). Par défaut, la vignette de chaque card est un placeholder généré (dégradé + initiales). Un champ optionnel `"image"` dans une entrée d'`apps.json` (chemin relatif ou URL) affiche une vraie image à la place sur la card (pas dans le popup) ; si l'image ne charge pas, le placeholder généré reste visible en secours. Les deux pages se référencent mutuellement via une barre de navigation.

## Commandes

Régénérer le dashboard et la page applications après une modification de `timeline.json` ou `apps.json` :

```bash
python generate_dashboard.py
```

## Alimentation de timeline.json

Un hook global (`~/.claude/hooks/log_init_complete.py`, déclenché sur `Stop` après un `/init`, hors de ce dépôt) alimente automatiquement `timeline.json` et régénère `index.html` en local — mais seulement pour les sessions `/init`. Il met à jour la même entrée au fil des tours d'un même `/init` (marqueur posé par `~/.claude/hooks/track_init_start.py`), et l'abandonne après 45 min d'inactivité.

En dehors de ce cas, l'alimentation reste manuelle (via `append_entry()` dans `generate_dashboard.py`, ou édition directe du fichier).

Dans tous les cas, la régénération locale de `index.html` ne suffit pas à mettre à jour le site déployé : il faut commit + push + redéployer (voir Déploiement ci-dessous).

## Déploiement

Pas de branches : on commit et pousse directement sur `master`. Le redéploiement Vercel est manuel :

```bash
vercel --yes --scope isabelleweb13-gmailcoms-projects
```

Le projet Vercel est `isabelleweb13-gmailcoms-projects/dashboard` (production : https://dashboard-self-pi-59.vercel.app).
