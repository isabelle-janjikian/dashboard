# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projet

Dashboard glassmorphism statique qui visualise l'usage (tokens, coût estimé) de sessions Claude Code, par projet. `generate_dashboard.py` lit `timeline.json` et génère `index.html` (page autonome, sans dépendance externe).

Le même script génère aussi `applications.html` ("Mes applications Claude Code") à partir de `apps.json` : une grille de cards (une par application réalisée avec Claude Code — les dépôts vides/greenfield ne sont pas listés), filtrable par type et par nom de projet, avec un popup "Détails" (description, date de réalisation, pas de lien GitHub). Par défaut, la vignette de chaque card est un placeholder généré (dégradé + initiales). Un champ optionnel `"image"` dans une entrée d'`apps.json` (chemin relatif ou URL) affiche une vraie image à la place sur la card (pas dans le popup) ; si l'image ne charge pas, le placeholder généré reste visible en secours. Un champ optionnel `"url"` affiche un bouton lien ("Voir le site ↗") dans le popup Détails, pour les applications ayant un site déployé (ex. le dashboard lui-même).

Le script génère enfin `aide.html` ("Centre d'aide") à partir de `help.json` : une liste de catégories (Prise en main, FAQ, Documentation technique, Contact), chacune avec ses questions/réponses affichées en accordéon, filtrable par catégorie et par recherche texte (sur la question et la réponse).

Le script génère aussi `contact.html` (page statique, pas de fichier JSON associé) : un formulaire (nom, email, objet en menu déroulant, message) qui envoie le message par `fetch` vers Formspree (`https://formspree.io/f/xnjkrakl`, destinataire isabelleweb13@gmail.com, objet fixe "Message via Dashboard Claude" via le champ caché `_subject`). Le succès affiche un popup/modal (pas un texte inline). **Pas de champ pièce jointe** : le plan Formspree gratuit rejette en bloc toute soumission contenant un fichier (`400 File Uploads Not Permitted`), ce qui faisait échouer l'envoi de tout le formulaire — ne pas le réintroduire sans passer sur une offre payante. Le skill `.claude/skills/page-contact` documente cette page.

Les quatre pages se référencent mutuellement via une barre de navigation.

## Commandes

Régénérer les trois pages après une modification de `timeline.json`, `apps.json` ou `help.json` :

```bash
python generate_dashboard.py
```

`load_entries()`/`load_apps()`/`load_help()` avalent silencieusement toute erreur de lecture (JSON invalide, fichier absent) et retournent une liste vide — un `timeline.json`/`apps.json`/`help.json` corrompu produit donc une page vide sans message d'erreur explicite (juste `(0 entrée(s))` en console). Vérifier la validité du JSON après une édition manuelle.

## Alimentation de timeline.json

Un hook global (`~/.claude/hooks/log_init_complete.py`, déclenché sur `Stop` après un `/init`, hors de ce dépôt) alimente automatiquement `timeline.json` et régénère `index.html` en local — mais seulement pour les sessions `/init`. Il met à jour la même entrée au fil des tours d'un même `/init` (marqueur posé par `~/.claude/hooks/track_init_start.py`), et l'abandonne après 45 min d'inactivité.

Le texte de l'`action` enregistrée suit cet ordre de priorité :
1. **Intention déclarée par l'utilisateur** : si le tout premier message texte libre de la session a été capté par `~/.claude/hooks/save_session_intent.py` (hook global `UserPromptSubmit`, hors de ce dépôt — se déclenche sur chaque message envoyé) et enregistré dans `.markers/{session_id}_intent.txt`, il est utilisé tel quel, sans reformulation. (`track_init_start.py`, lui, reste sur `UserPromptExpansion` avec vérification stricte interne, car cet événement ne se déclenche en pratique que pour l'invocation des commandes slash elles-mêmes.)
2. **Titres des commits git** faits depuis le début du `/init` (dans le projet courant et dans ce dépôt dashboard), juxtaposés avec « ; ».
3. **Dernier message de l'assistant** (comportement d'origine), en dernier recours.

Le fichier d'intention est nettoyé en même temps que le marqueur `/init` (même délai de 45 min).

En dehors de ce cas, l'alimentation reste manuelle (via `append_entry()` dans `generate_dashboard.py`, ou édition directe du fichier).

Dans tous les cas, la régénération locale de `index.html` ne suffit pas à mettre à jour le site déployé : il faut commit + push + redéployer (voir Déploiement ci-dessous).

## Déploiement

Pas de branches : on commit et pousse directement sur `master`. Le redéploiement Vercel est manuel :

```bash
vercel --yes --prod --scope isabelleweb13-gmailcoms-projects
```

Sans `--prod`, la commande crée un déploiement preview (`target: null`) qui ne touche pas l'alias de production.

Le projet Vercel est `isabelleweb13-gmailcoms-projects/dashboard` (production : https://dashboard-self-pi-59.vercel.app).
