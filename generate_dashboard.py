"""Génère index.html (dashboard glassmorphism) à partir de timeline.json."""

import json
import os

DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
TIMELINE_PATH = os.path.join(DASHBOARD_DIR, "timeline.json")
OUTPUT_PATH = os.path.join(DASHBOARD_DIR, "index.html")
APPS_PATH = os.path.join(DASHBOARD_DIR, "apps.json")
APPS_OUTPUT_PATH = os.path.join(DASHBOARD_DIR, "applications.html")

# Coûts approximatifs, en euros, pour 1 million de tokens de chaque catégorie.
# Valeurs modifiables facilement.
COUT_INPUT_PAR_MILLION = 3.0
COUT_OUTPUT_PAR_MILLION = 15.0
COUT_CACHE_ECRITURE_PAR_MILLION = 3.75
COUT_CACHE_LECTURE_PAR_MILLION = 0.3


def load_entries():
    """Retourne la liste des entrées lues depuis timeline.json (liste vide si absent/invalide)."""
    if not os.path.exists(TIMELINE_PATH):
        return []
    try:
        with open(TIMELINE_PATH, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(data, list):
        return []
    return data


def load_apps():
    """Retourne la liste des applications lues depuis apps.json (liste vide si absent/invalide)."""
    if not os.path.exists(APPS_PATH):
        return []
    try:
        with open(APPS_PATH, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(data, list):
        return []
    return data


def save_entries(entries):
    """Réécrit timeline.json avec la liste d'entrées donnée."""
    with open(TIMELINE_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def save_apps(apps):
    """Réécrit apps.json avec la liste d'applications donnée."""
    with open(APPS_PATH, "w", encoding="utf-8") as f:
        json.dump(apps, f, ensure_ascii=False, indent=2)


def append_entry(entry):
    """Ajoute une entrée à timeline.json et réécrit le fichier. Retourne la liste mise à jour."""
    entries = load_entries()
    entries.append(entry)
    save_entries(entries)
    return entries


def _embed_json(data):
    """Sérialise en JSON, en échappant les séquences pouvant fermer une balise <script>."""
    raw = json.dumps(data, ensure_ascii=False)
    return raw.replace("</", "<\\/")


_EMPTY_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard Claude</title>
<style>
__BASE_CSS__
</style>
</head>
<body>
__BACKGROUND__
<div class="app-shell">
  <div class="nav-links">
    <a href="index.html" class="nav-link active">Dashboard usage</a>
    <a href="applications.html" class="nav-link">Mes applications</a>
  </div>
  <h1>Dashboard Claude</h1>
  <div class="glass-card">
    <p class="empty-message">Aucune entrée pour l'instant.</p>
  </div>
  __FOOTNOTES__
</div>
</body>
</html>
"""

_FULL_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard Claude</title>
<style>
__BASE_CSS__
__FULL_CSS__
</style>
</head>
<body>
__BACKGROUND__
<div class="app-shell">
  <div class="nav-links">
    <a href="index.html" class="nav-link active">Dashboard usage</a>
    <a href="applications.html" class="nav-link">Mes applications</a>
  </div>
  <h1>Dashboard Claude</h1>

  <div class="glass-card">
    <div class="controls-row">
      <label for="project-filter">Projet</label>
      <select id="project-filter"></select>
    </div>
    <div class="summary" id="summary"></div>
    <p class="disclaimer">* Estimation approximative — le tarif réel dépend du modèle et du ratio entrée/sortie des tokens.</p>
    <div class="chart" id="chart"></div>
  </div>

  <div class="glass-card">
    <div id="timeline"></div>
  </div>
  __FOOTNOTES__
</div>

<script>
const ENTRIES = __ENTRIES_JSON__;
const COUT_INPUT_PAR_MILLION = __COUT_INPUT__;
const COUT_OUTPUT_PAR_MILLION = __COUT_OUTPUT__;
const COUT_CACHE_ECRITURE_PAR_MILLION = __COUT_CACHE_ECRITURE__;
const COUT_CACHE_LECTURE_PAR_MILLION = __COUT_CACHE_LECTURE__;

function coutDe(entry) {
  // Format historique : seul le total "tokens" est connu, on l'estime au tarif input.
  if (typeof entry.input_tokens !== 'number') {
    return (entry.tokens / 1000000) * COUT_INPUT_PAR_MILLION;
  }
  return (entry.input_tokens / 1000000) * COUT_INPUT_PAR_MILLION
    + (entry.output_tokens / 1000000) * COUT_OUTPUT_PAR_MILLION
    + (entry.cache_creation_tokens / 1000000) * COUT_CACHE_ECRITURE_PAR_MILLION
    + (entry.cache_read_tokens / 1000000) * COUT_CACHE_LECTURE_PAR_MILLION;
}

function parseDateFR(d) {
  const [jour, mois, annee] = d.split('/').map(Number);
  return new Date(annee, mois - 1, jour);
}

function hashString(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

function colorForProject(name) {
  if (name === 'dashboard') return 'hsl(330, 75%, 60%)';
  const hue = hashString(name) % 360;
  if (hue >= 285 && hue <= 350) return '#000000';
  return `hsl(${hue}, 68%, 58%)`;
}

function fmtNombre(n) {
  return n.toLocaleString('fr-FR');
}

function projetsDistincts(entries) {
  const set = new Set(entries.map(e => e.project));
  return Array.from(set).sort((a, b) => a.localeCompare(b, 'fr'));
}

const dropdown = document.getElementById('project-filter');
const tousProjets = projetsDistincts(ENTRIES);

const optionTous = document.createElement('option');
optionTous.value = '__TOUS__';
optionTous.textContent = 'Tous les projets';
dropdown.appendChild(optionTous);

tousProjets.forEach(p => {
  const opt = document.createElement('option');
  opt.value = p;
  opt.textContent = p;
  dropdown.appendChild(opt);
});

dropdown.value = '__TOUS__';

function renderSummary(entries) {
  const totalTokens = entries.reduce((s, e) => s + e.tokens, 0);
  const totalCout = entries.reduce((s, e) => s + coutDe(e), 0);
  const nbProjets = projetsDistincts(entries).length;
  const el = document.getElementById('summary');
  el.innerHTML = `
    <div class="stat"><span class="stat-value">${fmtNombre(entries.length)}</span><span class="stat-label">entrées</span></div>
    <div class="stat"><span class="stat-value">${fmtNombre(nbProjets)}</span><span class="stat-label">projet(s)</span></div>
    <div class="stat"><span class="stat-value">${fmtNombre(totalTokens)}</span><span class="stat-label">tokens</span></div>
    <div class="stat"><span class="stat-value">${totalCout.toFixed(3)} €</span><span class="stat-label">coût estimé</span></div>
  `;
}

function renderChart(entries, filtre) {
  const el = document.getElementById('chart');
  if (entries.length === 0) {
    el.innerHTML = '';
    return;
  }
  const parJour = new Map();
  entries.forEach(e => {
    const total = parJour.get(e.date) || 0;
    parJour.set(e.date, total + e.tokens);
  });
  const jours = Array.from(parJour.keys()).sort((a, b) => parseDateFR(a) - parseDateFR(b));
  const maxTotal = Math.max(...jours.map(j => parJour.get(j)));
  const couleurBarre = filtre === '__TOUS__' ? 'var(--accent-color)' : colorForProject(filtre);

  el.innerHTML = `<div class="bars">${jours.map(j => {
    const total = parJour.get(j);
    const hauteur = maxTotal > 0 ? (total / maxTotal) * 100 : 0;
    return `
      <div class="bar-col">
        <span class="bar-value">${fmtNombre(total)}</span>
        <div class="bar" style="height:${hauteur}%; background:${couleurBarre};"></div>
        <span class="bar-date">${j}</span>
      </div>
    `;
  }).join('')}</div>`;
}

function renderTimeline(entries) {
  const el = document.getElementById('timeline');
  if (entries.length === 0) {
    el.innerHTML = '<p class="empty-message">Aucune entrée pour ce filtre.</p>';
    return;
  }
  const maxTokens = Math.max(...entries.map(e => e.tokens));

  const parDate = new Map();
  entries.forEach(e => {
    if (!parDate.has(e.date)) parDate.set(e.date, []);
    parDate.get(e.date).push(e);
  });
  const dates = Array.from(parDate.keys()).sort((a, b) => parseDateFR(b) - parseDateFR(a));

  el.innerHTML = dates.map(date => {
    const items = parDate.get(date).slice().sort((a, b) => a.time.localeCompare(b.time));
    return `
      <div class="date-group">
        <h2 class="date-heading">${date}</h2>
        ${items.map(e => {
          const couleur = colorForProject(e.project);
          const largeur = maxTokens > 0 ? (e.tokens / maxTokens) * 100 : 0;
          return `
            <div class="entry-row">
              <div class="entry-header">
                <span class="entry-time">${e.time}</span>
                <span class="entry-project" style="background:${couleur};">${e.project}</span>
                <span class="entry-action">${e.action}</span>
                <span class="entry-tokens">${fmtNombre(e.tokens)} tok</span>
                <span class="entry-cout">${coutDe(e).toFixed(3)} €</span>
              </div>
              <div class="gauge-track">
                <div class="gauge-fill" style="width:${largeur}%; background:${couleur};"></div>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;
  }).join('');
}

function renderAll(filtre) {
  const entries = filtre === '__TOUS__' ? ENTRIES : ENTRIES.filter(e => e.project === filtre);
  renderSummary(entries);
  renderChart(entries, filtre);
  renderTimeline(entries);
}

dropdown.addEventListener('change', () => renderAll(dropdown.value));

renderAll('__TOUS__');
</script>
</body>
</html>
"""

_BASE_CSS = """
* { box-sizing: border-box; }
body {
  margin: 0;
  min-height: 100vh;
  font-family: -apple-system, "Segoe UI", Roboto, sans-serif;
  color: #1c2b3a;
  position: relative;
  overflow-x: hidden;
}
.background {
  position: fixed;
  inset: 0;
  z-index: -1;
  background: linear-gradient(160deg, #5bc8f0 0%, #1f6fc2 100%);
  overflow: hidden;
}
.petal {
  position: absolute;
  filter: blur(2px);
}
.app-shell {
  max-width: 1100px;
  margin: 0 auto;
  padding: 48px 70px 80px;
}
h1 {
  color: #ffffff;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
  font-size: 2rem;
  margin-bottom: 24px;
}
.nav-links {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}
.nav-link {
  display: inline-block;
  padding: 8px 18px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.22);
  border: 1px solid rgba(255, 255, 255, 0.35);
  color: #ffffff;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 600;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  transition: background 0.15s ease;
}
.nav-link:hover {
  background: rgba(255, 255, 255, 0.34);
}
.nav-link.active {
  background: rgba(255, 255, 255, 0.85);
  color: #0f2d50;
}
.glass-card {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(19px);
  -webkit-backdrop-filter: blur(19px);
  border: 1px solid rgba(255, 255, 255, 0.35);
  border-radius: 22px;
  box-shadow: 0 12px 40px rgba(15, 45, 80, 0.25);
  padding: 28px 32px;
  margin-bottom: 28px;
}
.empty-message {
  text-align: center;
  color: #ffffff;
  font-size: 1.1rem;
  margin: 20px 0;
}
.app-credit {
  position: fixed;
  left: 16px;
  bottom: 14px;
  font-size: 0.7rem;
  color: #ffffff;
  opacity: 0.85;
  z-index: 10;
}
.app-install-note {
  position: fixed;
  right: 16px;
  bottom: 14px;
  max-width: 240px;
  font-size: 0.68rem;
  line-height: 1.35;
  text-align: right;
  color: #ffffff;
  background: rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 12px;
  padding: 8px 12px;
  z-index: 10;
}
@media (max-width: 640px) {
  .app-shell {
    padding: 28px 16px 120px;
  }
  h1 {
    font-size: 1.5rem;
  }
  .glass-card {
    padding: 18px 16px;
    border-radius: 18px;
  }
  .app-credit,
  .app-install-note {
    position: static;
    max-width: 100%;
    text-align: left;
    margin: 10px 0 0;
  }
  .nav-link {
    padding: 7px 14px;
    font-size: 0.82rem;
  }
}
"""

_FULL_CSS = """
.controls-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}
.controls-row label {
  font-weight: 600;
  color: #0f2d50;
}
#project-filter {
  padding: 8px 14px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.55);
  font-size: 0.95rem;
  color: #0f2d50;
  cursor: pointer;
}
.summary {
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
  margin-bottom: 6px;
}
.stat {
  background: #ffffff;
  border: 1px solid rgba(15, 45, 80, 0.08);
  box-shadow: 0 4px 14px rgba(15, 45, 80, 0.15);
  border-radius: 16px;
  padding: 12px 20px;
  min-width: 130px;
  text-align: center;
}
.stat-value {
  display: block;
  font-size: 1.4rem;
  font-weight: 700;
  color: #0f2d50;
}
.stat-label {
  display: block;
  font-size: 0.8rem;
  color: #2c4a68;
  margin-top: 2px;
}
.disclaimer {
  font-size: 0.72rem;
  color: #2c4a68;
  opacity: 0.85;
  margin: 4px 0 20px;
}
.chart {
  margin-top: 8px;
}
.bars {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  height: 220px;
  padding: 0 4px;
  overflow-x: auto;
}
.bar-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  flex: 1 0 44px;
  max-width: 70px;
  height: 100%;
}
.bar-value {
  font-size: 0.72rem;
  font-weight: 600;
  color: #0f2d50;
  margin-bottom: 4px;
  white-space: nowrap;
}
.bar {
  width: 100%;
  border-radius: 8px 8px 4px 4px;
  min-height: 3px;
  box-shadow: 0 4px 14px rgba(15, 45, 80, 0.25);
}
.bar-date {
  font-size: 0.68rem;
  color: #0f2d50;
  margin-top: 6px;
  white-space: nowrap;
}
:root {
  --accent-color: linear-gradient(180deg, #ffb14d, #e2622a);
}
.date-heading {
  font-size: 1.05rem;
  color: #0f2d50;
  margin: 22px 0 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.4);
}
.date-heading:first-child {
  margin-top: 0;
}
.entry-row {
  background: rgba(255, 255, 255, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.35);
  border-radius: 14px;
  padding: 10px 16px;
  margin-bottom: 10px;
}
.entry-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
}
.entry-time {
  font-variant-numeric: tabular-nums;
  color: #0f2d50;
  font-weight: 600;
  min-width: 42px;
}
.entry-project {
  color: #fff;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
}
.entry-action {
  flex: 1 1 200px;
  color: #1c2b3a;
}
.entry-tokens {
  color: #0f2d50;
  font-size: 0.8rem;
  white-space: nowrap;
}
.entry-cout {
  color: #0f2d50;
  font-weight: 600;
  font-size: 0.8rem;
  white-space: nowrap;
}
.gauge-track {
  margin-top: 8px;
  height: 7px;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 999px;
  overflow: hidden;
}
.gauge-fill {
  height: 100%;
  border-radius: 999px;
}
@media (max-width: 640px) {
  .controls-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  #project-filter {
    width: 100%;
  }
  .summary {
    gap: 10px;
  }
  .stat {
    flex: 1 1 calc(50% - 10px);
    min-width: 0;
    padding: 10px 12px;
  }
  .stat-value {
    font-size: 1.15rem;
  }
  .bars {
    height: 160px;
    gap: 6px;
  }
  .bar-col {
    flex: 1 0 32px;
  }
  .entry-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  .entry-action {
    flex: 1 1 100%;
  }
}
"""

_APPS_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mes applications Claude Code</title>
<style>
__BASE_CSS__
__APPS_CSS__
</style>
</head>
<body>
__BACKGROUND__
<div class="app-shell">
  <div class="nav-links">
    <a href="index.html" class="nav-link">Dashboard usage</a>
    <a href="applications.html" class="nav-link active">Mes applications</a>
  </div>
  <h1>Mes applications Claude Code</h1>

  <div class="glass-card">
    <div class="controls-row">
      <div class="control-group">
        <label for="type-filter">Type</label>
        <select id="type-filter" class="filter-select"></select>
      </div>
      <div class="control-group">
        <label for="name-filter">Projet</label>
        <select id="name-filter" class="filter-select"></select>
      </div>
    </div>
  </div>

  <div id="apps-grid" class="apps-grid"></div>
  <p id="apps-empty" class="empty-message" hidden>Aucune application ne correspond à ce filtre.</p>

  <div id="app-modal" class="modal-overlay" hidden>
    <div class="modal-card glass-card">
      <button type="button" class="modal-close" id="modal-close" aria-label="Fermer">&times;</button>
      <div id="modal-body"></div>
    </div>
  </div>

  __FOOTNOTES__
</div>

<script>
const APPS = __APPS_JSON__;

function hashString(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

function colorForApp(app) {
  if (app.name === 'dashboard') return 'hsl(330, 75%, 60%)';
  const hue = hashString(app.type || app.name) % 360;
  if (hue >= 285 && hue <= 350) return '#000000';
  return `hsl(${hue}, 68%, 55%)`;
}

function initials(name) {
  const parts = name.split(/[^a-zA-Z0-9À-ÿ]+/).filter(Boolean);
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
  return name.slice(0, 2).toUpperCase();
}

function distinctSorted(values) {
  return Array.from(new Set(values)).sort((a, b) => a.localeCompare(b, 'fr'));
}

const typeFilter = document.getElementById('type-filter');
const nameFilter = document.getElementById('name-filter');
const grid = document.getElementById('apps-grid');
const emptyMsg = document.getElementById('apps-empty');
const modal = document.getElementById('app-modal');
const modalBody = document.getElementById('modal-body');
const modalClose = document.getElementById('modal-close');

function fillDropdown(select, values, allLabel) {
  const optAll = document.createElement('option');
  optAll.value = '__TOUS__';
  optAll.textContent = allLabel;
  select.appendChild(optAll);
  values.forEach(v => {
    const opt = document.createElement('option');
    opt.value = v;
    opt.textContent = v;
    select.appendChild(opt);
  });
  select.value = '__TOUS__';
}

fillDropdown(typeFilter, distinctSorted(APPS.map(a => a.type)), 'Tous les types');
fillDropdown(nameFilter, distinctSorted(APPS.map(a => a.name)), 'Tous les projets');

function openModal(app) {
  modalBody.innerHTML = `
    <h2 class="modal-title">${app.name}</h2>
    <span class="app-type-badge" style="background:${colorForApp(app)};">${app.type}</span>
    <p class="modal-description">${app.description}</p>
    <p class="modal-date">Réalisé le ${app.date}</p>
  `;
  modal.hidden = false;
}

function closeModal() {
  modal.hidden = true;
}

modalClose.addEventListener('click', closeModal);
modal.addEventListener('click', (e) => {
  if (e.target === modal) closeModal();
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && !modal.hidden) closeModal();
});

function renderGrid() {
  const typeVal = typeFilter.value;
  const nameVal = nameFilter.value;
  const filtered = APPS.filter(a =>
    (typeVal === '__TOUS__' || a.type === typeVal) &&
    (nameVal === '__TOUS__' || a.name === nameVal)
  );

  if (filtered.length === 0) {
    grid.innerHTML = '';
    emptyMsg.hidden = false;
    return;
  }
  emptyMsg.hidden = true;

  grid.innerHTML = filtered.map((app, i) => `
    <div class="app-card">
      <div class="app-thumb" style="background: linear-gradient(135deg, ${colorForApp(app)}, rgba(255,255,255,0.15));">
        <span class="app-thumb-initials">${initials(app.name)}</span>
        ${app.image ? `<img class="app-thumb-img" src="${app.image}" alt="" onerror="this.style.display='none'">` : ''}
      </div>
      <div class="app-card-body">
        <h3 class="app-title">${app.name}</h3>
        <span class="app-type-badge" style="background:${colorForApp(app)};">${app.type}</span>
        <button type="button" class="btn-details" data-index="${i}">Détails</button>
      </div>
    </div>
  `).join('');

  grid.querySelectorAll('.btn-details').forEach(btn => {
    btn.addEventListener('click', () => openModal(filtered[Number(btn.dataset.index)]));
  });
}

typeFilter.addEventListener('change', renderGrid);
nameFilter.addEventListener('change', renderGrid);

renderGrid();
</script>
</body>
</html>
"""

_APPS_CSS = """
.controls-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 20px;
}
.control-group {
  display: flex;
  align-items: center;
  gap: 10px;
}
.control-group label {
  font-weight: 600;
  color: #0f2d50;
}
.filter-select {
  padding: 8px 14px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.55);
  font-size: 0.95rem;
  color: #0f2d50;
  cursor: pointer;
}
.apps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 22px;
}
.app-card {
  background: rgba(255, 255, 255, 0.28);
  backdrop-filter: blur(19px);
  -webkit-backdrop-filter: blur(19px);
  border: 1px solid rgba(255, 255, 255, 0.35);
  border-radius: 20px;
  box-shadow: 0 12px 32px rgba(15, 45, 80, 0.22);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.app-thumb {
  position: relative;
  height: 130px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.app-thumb-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.app-thumb-initials {
  font-size: 2.2rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.25);
  letter-spacing: 1px;
}
.app-card-body {
  padding: 16px 18px 20px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
}
.app-title {
  margin: 0;
  font-size: 1.1rem;
  color: #0f2d50;
}
.app-type-badge {
  display: inline-block;
  color: #fff;
  padding: 3px 12px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}
.btn-details {
  margin-top: 4px;
  align-self: stretch;
  padding: 9px 16px;
  border-radius: 12px;
  border: 1px solid rgba(15, 45, 80, 0.15);
  background: rgba(255, 255, 255, 0.7);
  color: #0f2d50;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.15s ease, box-shadow 0.15s ease;
}
.btn-details:hover {
  background: #ffffff;
  box-shadow: 0 4px 14px rgba(15, 45, 80, 0.2);
}
.btn-details:active {
  background: rgba(255, 225, 150, 0.9);
  box-shadow: 0 0 0 3px rgba(255, 177, 77, 0.5);
}
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(10, 25, 45, 0.45);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 100;
}
.modal-overlay[hidden] {
  display: none;
}
.modal-card {
  position: relative;
  max-width: 460px;
  width: 100%;
  background: rgba(255, 255, 255, 0.85);
}
.modal-close {
  position: absolute;
  top: 14px;
  right: 16px;
  border: none;
  background: transparent;
  font-size: 1.4rem;
  line-height: 1;
  color: #0f2d50;
  cursor: pointer;
}
.modal-title {
  margin: 0 0 10px;
  color: #0f2d50;
  font-size: 1.3rem;
  padding-right: 24px;
}
.modal-description {
  color: #1c2b3a;
  line-height: 1.5;
  margin: 14px 0 10px;
}
.modal-date {
  color: #2c4a68;
  font-size: 0.85rem;
  font-weight: 600;
}
@media (max-width: 640px) {
  .controls-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  .control-group {
    width: 100%;
  }
  .filter-select {
    flex: 1;
  }
  .apps-grid {
    grid-template-columns: 1fr;
  }
  .modal-card {
    max-width: 100%;
  }
}
"""

_BACKGROUND_SVG = """
<div class="background">
  <svg width="100%" height="100%" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
    <defs>
      <linearGradient id="petal1" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#ffe27a"/>
        <stop offset="50%" stop-color="#ffb14d"/>
        <stop offset="100%" stop-color="#e2622a"/>
      </linearGradient>
      <linearGradient id="petal2" x1="100%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#ffb14d"/>
        <stop offset="100%" stop-color="#e2622a"/>
      </linearGradient>
    </defs>
    <path d="M 1440 0 C 1100 100, 1000 350, 1250 550 C 1450 700, 1500 300, 1440 0 Z" fill="url(#petal1)" opacity="0.9"/>
    <path d="M 0 900 C 250 750, 500 850, 450 650 C 400 450, 100 550, 0 900 Z" fill="url(#petal2)" opacity="0.92"/>
    <path d="M 1440 900 C 1250 700, 950 800, 1050 650 C 1150 500, 1400 600, 1440 900 Z" fill="url(#petal1)" opacity="0.9"/>
    <path d="M 0 0 C 150 200, 350 100, 250 -50 C 150 -150, -50 -100, 0 0 Z" fill="url(#petal2)" opacity="0.85"/>
  </svg>
</div>
"""


_FOOTNOTES_HTML = """
  <p class="app-credit">Réalisé par IsabelleWeb13@</p>
  <p class="app-install-note">Cette application peut être installée chez vous : copiez le dossier de scripts (README + install + hooks + dashboard).</p>
"""


def generate_html(entries):
    if not entries:
        html = _EMPTY_TEMPLATE
        html = html.replace("__BASE_CSS__", _BASE_CSS)
        html = html.replace("__BACKGROUND__", _BACKGROUND_SVG)
        html = html.replace("__FOOTNOTES__", _FOOTNOTES_HTML)
        return html

    html = _FULL_TEMPLATE
    html = html.replace("__BASE_CSS__", _BASE_CSS)
    html = html.replace("__FULL_CSS__", _FULL_CSS)
    html = html.replace("__BACKGROUND__", _BACKGROUND_SVG)
    html = html.replace("__FOOTNOTES__", _FOOTNOTES_HTML)
    html = html.replace("__ENTRIES_JSON__", _embed_json(entries))
    html = html.replace("__COUT_INPUT__", repr(COUT_INPUT_PAR_MILLION))
    html = html.replace("__COUT_OUTPUT__", repr(COUT_OUTPUT_PAR_MILLION))
    html = html.replace("__COUT_CACHE_ECRITURE__", repr(COUT_CACHE_ECRITURE_PAR_MILLION))
    html = html.replace("__COUT_CACHE_LECTURE__", repr(COUT_CACHE_LECTURE_PAR_MILLION))
    html = html.replace("__TOUS__", "__TOUS__")
    return html


def generate_apps_html(apps):
    html = _APPS_TEMPLATE
    html = html.replace("__BASE_CSS__", _BASE_CSS)
    html = html.replace("__APPS_CSS__", _APPS_CSS)
    html = html.replace("__BACKGROUND__", _BACKGROUND_SVG)
    html = html.replace("__FOOTNOTES__", _FOOTNOTES_HTML)
    html = html.replace("__APPS_JSON__", _embed_json(apps))
    return html


def main():
    entries = load_entries()
    html = generate_html(entries)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"index.html généré ({len(entries)} entrée(s)).")

    apps = load_apps()
    apps_html = generate_apps_html(apps)
    with open(APPS_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(apps_html)
    print(f"applications.html généré ({len(apps)} application(s)).")


if __name__ == "__main__":
    main()
