# Dashboard Claude

Un dashboard "glassmorphism" léger qui visualise l'usage (tokens et coût estimé) de vos sessions Claude Code, projet par projet.

![statique](https://img.shields.io/badge/build-python%20script-blue) ![licence](https://img.shields.io/badge/pages-1-lightgrey)

## Aperçu

- **Résumé** : nombre d'entrées, de projets, de tokens et coût total estimé.
- **Graphique** : total de tokens consommés par jour.
- **Timeline** : détail de chaque action, regroupée par date, avec une jauge visuelle par entrée.
- Filtrage par projet via un menu déroulant.

## Fonctionnement

- `timeline.json` contient la liste des entrées (date, heure, projet, action, tokens).
- `generate_dashboard.py` lit ce fichier et génère `index.html`, une page autonome (HTML/CSS/JS inline, sans dépendance externe).
- Le coût est estimé à partir de tarifs par million de tokens (input, output, écriture cache, lecture cache), configurables en tête de `generate_dashboard.py`.

## Utilisation

Régénérer le dashboard après une mise à jour de `timeline.json` :

```bash
python generate_dashboard.py
```

Le fichier `index.html` résultant peut s'ouvrir directement dans un navigateur, ou être déployé (ce dépôt est actuellement déployé sur Vercel).

## Ajouter une entrée

Utilisez `append_entry(entry)` dans `generate_dashboard.py` pour ajouter une nouvelle entrée à `timeline.json`, avec le format suivant :

```json
{
  "date": "05/07/2026",
  "time": "10:00",
  "project": "mon-projet",
  "action": "Description de l'action effectuée",
  "tokens": 12345,
  "input_tokens": 10,
  "output_tokens": 2000,
  "cache_creation_tokens": 500,
  "cache_read_tokens": 9835
}
```

## Stack

- Python (script de génération, aucune dépendance externe)
- HTML/CSS/JS vanilla (page générée, sans framework)
