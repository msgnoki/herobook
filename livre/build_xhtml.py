#!/usr/bin/env python3
"""
Convertit Les_Jardins_de_Verre-Lune.md en arborescence XHTML interactive.

Le système gère un profil persistant (localStorage) avec compétences,
objets et mots-clés. Les choix qui requièrent une compétence/objet/mot-clé
non-acquis sont grisés et désactivés. Pages dédiées dynamiques pour le
récap. Bouton Nouvelle partie + reprise automatique.
"""

import re
import os
from pathlib import Path
import html
import json

SRC = Path(__file__).parent / "Les_Jardins_de_Verre-Lune.md"
OUT = Path(__file__).parent / "xhtml"
OUT.mkdir(exist_ok=True)

TITLE = "Les Jardins de Verre-Lune"
SUBTITLE = "Une aventure dont tu es le héros"

SKILLS = [
    "Observation", "Agilité", "Discrétion", "Soin des animaux",
    "Mémoire des légendes", "Bricolage", "Orientation",
]

SKILL_DESCRIPTIONS = {
    "Observation": "Tu remarques les détails que les autres ne voient pas : une trace, un symbole gravé, une couleur qui jure, un détail qui ne devrait pas être là.",
    "Agilité": "Tu grimpes, tu sautes, tu te faufiles. Quand ton corps doit bouger vite et bien, tu sais quoi faire.",
    "Discrétion": "Tu sais te taire, te cacher, écouter sans être vu. Les pas pesants, ce n'est pas pour toi.",
    "Soin des animaux": "Les bêtes te font confiance. Tu sais apaiser, comprendre, soigner ce qui respire.",
    "Mémoire des légendes": "Les vieilles comptines, les histoires de grands-mères, les symboles oubliés : tout cela vit en toi comme une carte invisible.",
    "Bricolage": "Devant un mécanisme grippé, une corde cassée, une planche manquante, tes mains trouvent la solution.",
    "Orientation": "Tu retrouves toujours ton chemin. Même dans le brouillard, même la nuit, même sous la terre.",
}

# Objets qui peuvent gater des choix (testés dans les "Si tu possèdes la X" etc.)
GATED_OBJECTS = [
    "Boussole d'argent", "Corde tressée", "Clé d'Ambre",
    "Graine lumineuse", "Flûte de brume", "Carnet du cartographe",
    "Pierre de mémoire", "Médaille d'astre",
]

# Tous les objets connus (principaux + secondaires) avec leur description
OBJECT_INFO = {
    # Objets principaux
    "Boussole d'argent": ("principal", "N'indique pas le nord, mais la direction de ce qui a été oublié."),
    "Corde tressée": ("principal", "Une corde robuste pour franchir les obstacles ou descendre en sécurité."),
    "Clé d'Ambre": ("principal", "Une clé translucide qui ouvre les portes anciennes — mais réveille ce qui dort derrière."),
    "Graine lumineuse": ("principal", "Une petite graine qui brille comme une braise verte. Pour éclairer, soigner, réveiller."),
    "Flûte de brume": ("principal", "Une flûte d'os blanc. Elle apaise certaines créatures et en attire d'autres."),
    "Carnet du cartographe": ("principal", "Le carnet de Vellan, plein de croquis incomplets et de fausses pistes."),
    "Pierre de mémoire": ("principal", "Une pierre lisse qui peut conserver un souvenir, une phrase, une image."),
    # Objets secondaires gates
    "Médaille d'astre": ("secondaire", "Médaille de bronze gravée d'un astre à six branches. S'emboîte dans un mécanisme."),
    # Autres secondaires
    "éclat de verre tiède": ("secondaire", "Un morceau de verre poli, étrangement chaud, donné par Lyse."),
    "figurine \"V\"": ("secondaire", "Petite figurine de bois gravée d'un V."),
    "Canne de pèlerin": ("secondaire", "Une canne noire usée à la prise."),
    "Coquille sonore": ("secondaire", "Une coquille qui dit des choses qu'on n'a pas eu le temps d'entendre."),
    "page de croquis de Vellan": ("secondaire", "Schéma à moitié dessiné d'une grande serre ronde."),
    "Boussole cassée de Vellan": ("secondaire", "Une boussole brisée, mais qui vibre."),
    "page arrachée": ("secondaire", "Page arrachée du carnet de Vellan."),
    "plume de verre": ("secondaire", "Une plume légère et froide, donnée par un oiseau étrange."),
    "page de carte de Vellan": ("secondaire", "Une carte malhabile du Pont des Racines."),
    "Bille du ciel": ("secondaire", "Sphère de verre contenant une carte d'étoiles vivante."),
    "Couteau d'os": ("secondaire", "Une fine lame d'artiste."),
    "Treizième Caillou": ("secondaire", "Un caillou plus sombre, donné par Mémorine."),
    "trois fleurs de cœur-de-neige": ("secondaire", "Trois petites fleurs blanches du Bassin."),
    "Plume de chouette": ("secondaire", "Plume laissée par la chouette de la Flûte."),
    "Mouchoir des passants": ("secondaire", "Brodé pour ceux qui passeront."),
    "Paille en huit": ("secondaire", "Brin de paille noué en huit, cadeau d'un lapin blanc."),
    "Feuille d'or": ("principal", "Feuille de chêne d'or, légère, marqueur du seuil de la Galerie."),
    "Caillou poli": ("secondaire", "Caillou plat, lisse comme s'il avait été en poche longtemps."),
    "Feuille vide": ("secondaire", "Feuille de papier vierge qui sent l'encre fraîche."),
    "Joubarbe verte": ("principal", "La petite plante de ton appui de fenêtre, redevenue verte."),
    "ruban d'écorce gravé": ("secondaire", "Marqué du signe ancien du Veilleur."),
    "Graine sombre": ("secondaire", "Une graine lourde, inverse de la lumineuse."),
    # Équipement de départ (accordé d'office à §4)
    "Pain aux noix de Mère Aïna": ("secondaire", "Un quignon dense, parfumé. Pour la faim, et un peu pour la maison."),
    "Ruban rouge": ("secondaire", "Noué à ton poignet par Mère Aïna. Peut être déposé en promesse au Pont."),
    "Lampe-tempête": ("secondaire", "Petite lampe à huile, à l'épreuve du vent. Lumière de réserve."),
    "Petit couteau": ("secondaire", "Lame courte, fidèle. Tu sais t'en servir."),
}

# Octrois manuels pour les cas spéciaux non détectés par les regex
MANUAL_GRANTS = {
    # Équipement de départ : accordé à la fin de la scène avec Mère Aïna.
    4: {"objects": ["Pain aux noix de Mère Aïna", "Ruban rouge",
                    "Lampe-tempête", "Petit couteau"]},
    200: {"keywords": ["AMITIÉ DE NILO"], "remove_keywords": ["FATIGUÉ"]},
    195: {"keywords": ["VEILLEUR APAISÉ"]},
    205: {"remove_keywords": ["FATIGUÉ", "BLESSÉ LÉGER"]},
    291: {"remove_keywords": ["FATIGUÉ", "BLESSÉ LÉGER"]},
    245: {"remove_keywords": ["FATIGUÉ"]},
}

# Mots-clés d'état (cumulables/retirable). PERDU a été retiré : il n'était
# jamais accordé ni testé, donc du code mort.
STATE_KEYWORDS = {"FATIGUÉ", "BLESSÉ LÉGER", "ACCOMPAGNÉ"}

# Fins reconnues (pour le toc)
ENDINGS = {333, 336, 339, 342, 345, 348, 350}


# ------------------------------- CSS -------------------------------

CSS = r"""
* { box-sizing: border-box; }
:root {
  --vl-paper: #fbf6ec;
  --vl-paper-warm: #f5ecd9;
  --vl-ink: #3a2a14;
  --vl-ink-soft: #5a4426;
  --vl-gold: #8b6b1f;
  --vl-gold-soft: #b8923a;
  --vl-choice-bg: #fbf2dc;
  --vl-choice-bar: #b8923a;
  --vl-chip-bg: #efe2bf;
  --vl-chip-border: #d8c48a;
  --vl-rule: #e6dac0;
  --vl-serif: "Cormorant Garamond", "EB Garamond", Georgia, "Times New Roman", serif;
  --vl-ui: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
body {
  font-family: var(--vl-serif);
  max-width: 760px;
  margin: 0 auto;
  padding: 1.25em 1.2em 6.5em;
  line-height: 1.65;
  color: var(--vl-ink);
  background: var(--vl-paper);
}
body.sheet-open { overflow: hidden; }
button { font: inherit; }
body > header { border-bottom: 1px solid var(--vl-rule); margin-bottom: 1.5em; padding-bottom: .8em; }
body > header h1 { font-size: 1.8em; line-height: 1.05; margin: 0; color: var(--vl-ink); }
body > header h2 { font-size: 1em; font-weight: normal; font-style: italic; margin: .25em 0 0; color: var(--vl-gold-soft); }
.reader { position: relative; }
article h1.sectnum {
  font-size: 2.55em;
  text-align: center;
  margin: .65em 0 .85em;
  color: #5a3a10;
  letter-spacing: .08em;
}
article h2.sectname {
  font-size: 1.3em;
  text-align: center;
  margin-top: -0.4em;
  margin-bottom: 1.5em;
  font-style: italic;
  color: #5a3a10;
}
p { margin: .5em 0 .8em; }
p.choice { margin: .35em 0; }
ul.choices { list-style: none; padding-left: 0; margin: 1em 0; }
ul.choices li {
  border-left: 4px solid var(--vl-choice-bar);
  margin: .55em 0;
  background: var(--vl-choice-bg);
  border-radius: 4px;
  transition: opacity .2s, background .2s;
}
ul.choices li .choice-link {
  display: flex;
  align-items: center;
  gap: .6em;
  min-height: 48px;
  padding: .75em 1em;
  color: var(--vl-gold);
  font-weight: bold;
  text-decoration: none;
  -webkit-tap-highlight-color: rgba(90, 58, 16, .12);
}
ul.choices li .choice-body { flex: 1 1 auto; min-width: 0; }
ul.choices li .choice-chevron {
  flex: 0 0 auto;
  font-size: 1.5em;
  line-height: 1;
  color: var(--vl-gold-soft);
}
ul.choices li .choice-link:hover { background: var(--vl-chip-bg); }
ul.choices li .choice-link:active { background: var(--vl-chip-bg); transform: scale(.995); }
ul.choices li .choice-text { color: var(--vl-ink, #2a1f08); font-weight: 600; }

/* Choix verrouillé : grisé et désactivé */
ul.choices li.locked {
  opacity: .55;
  background: #ece5d0;
  border-left-color: #999;
  cursor: not-allowed;
}
ul.choices li.locked .choice-link {
  color: #7a6a4a;
  pointer-events: none;
  cursor: not-allowed;
}
ul.choices li.locked .choice-text { color: #7a6a4a; }
ul.choices li.locked .choice-chevron {
  font-size: 0;
  color: #806a3a;
}
ul.choices li.locked .choice-chevron::before {
  content: "⛔";
  font-size: 18px;
  line-height: 1;
}

ul.choices .req-badges {
  display: inline-flex;
  flex-wrap: wrap;
  gap: .25em;
  margin-left: .5em;
  vertical-align: middle;
}
ul.choices .req {
  display: inline-block;
  font-size: .72em;
  font-weight: 600;
  letter-spacing: .02em;
  padding: .1em .55em;
  border-radius: 10px;
  border: 1px solid var(--vl-chip-border);
  background: var(--vl-chip-bg);
  color: var(--vl-ink-soft);
  white-space: nowrap;
}
ul.choices .req-skill   { border-color: #b9842f; color: #6a4310; }
ul.choices .req-object  { border-color: #6a8a3a; color: #3d5710; }
ul.choices .req-keyword { border-color: #8a5a8a; color: #4a2a55; }

.keyword { font-weight: bold; color: #5a3a0a; }
blockquote {
  font-style: italic;
  margin: 1em 1.5em;
  padding: .4em 1em;
  border-left: 3px solid var(--vl-gold-soft);
  background: var(--vl-paper-warm);
  color: var(--vl-ink-soft);
}

nav.bottom {
  margin-top: 1.5em;
  padding-top: 1em;
  border-top: 1px solid var(--vl-rule);
  display: flex;
  justify-content: space-between;
  font-size: .95em;
}
nav.bottom a {
  color: var(--vl-gold);
  text-decoration: none;
  padding: .3em .6em;
  border: 1px solid var(--vl-chip-border);
  border-radius: 3px;
  background: var(--vl-choice-bg);
}
nav.bottom a:hover { background: var(--vl-chip-bg); }
nav.bottom .center { text-align: center; flex-grow: 1; padding: 0 .5em; }

a { color: var(--vl-gold); }

table { border-collapse: collapse; margin: 1em 0; width: 100%; }
th, td { border: 1px solid var(--vl-chip-border); padding: .4em .6em; text-align: left; }
th { background: var(--vl-chip-bg); }

.fab-sheet {
  position: fixed;
  right: 18px;
  bottom: max(22px, calc(16px + env(safe-area-inset-bottom, 0px)));
  z-index: 70;
  width: 60px;
  height: 60px;
  border: 0;
  border-radius: 50%;
  background: var(--vl-ink);
  color: var(--vl-paper);
  box-shadow: 0 10px 24px rgba(58,42,20,.35), 0 2px 4px rgba(0,0,0,.2);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 100ms ease, box-shadow 100ms ease;
}
.fab-sheet:active {
  transform: scale(.96);
  box-shadow: 0 5px 14px rgba(58,42,20,.3), 0 1px 3px rgba(0,0,0,.18);
}
.fab-sheet svg { display: block; }

.sheet-layer[hidden] { display: none; }
.sheet-layer {
  position: fixed;
  inset: 0;
  z-index: 100;
  pointer-events: none;
}
.sheet-layer.is-open { pointer-events: auto; }
.sheet-scrim {
  position: absolute;
  inset: 0;
  background: rgba(20,15,8,.45);
  opacity: 0;
  transition: opacity 180ms linear;
}
.sheet-layer.is-open .sheet-scrim { opacity: 1; }
.sheet {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100%;
  max-height: 88vh;
  overflow-y: auto;
  background: var(--vl-paper);
  color: var(--vl-ink);
  border-top-left-radius: 18px;
  border-top-right-radius: 18px;
  padding: 14px 20px calc(22px + env(safe-area-inset-bottom, 0px));
  box-shadow: 0 -8px 30px rgba(0,0,0,.25);
  transform: translateY(100%);
  transition: transform 220ms cubic-bezier(.2,.7,.2,1);
  outline: none;
}
.sheet-layer.is-open .sheet { transform: translateY(0); }
.sheet-grabber {
  width: 44px;
  height: 4px;
  border-radius: 2px;
  background: var(--vl-rule);
  margin: 0 auto 14px;
  touch-action: none;
  cursor: grab;
}
.sheet-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}
.sheet-title-wrap { flex: 1; min-width: 0; }
.sheet-title {
  font-size: 1.45em;
  line-height: 1.15;
  margin: 0;
  color: var(--vl-ink);
  font-weight: 700;
}
.sheet-context {
  margin: .15em 0 0;
  font-size: .95em;
  line-height: 1.3;
  color: var(--vl-gold-soft);
  font-style: italic;
}
.sheet-close {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid var(--vl-rule);
  background: transparent;
  color: var(--vl-ink);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
.sheet-rule {
  height: 1px;
  background: var(--vl-rule);
  margin-bottom: 14px;
}
.sheet-block { margin-bottom: 14px; }
.sheet-block h3 {
  margin: 0 0 6px;
  font-family: var(--vl-ui);
  font-size: 11px;
  line-height: 1.2;
  letter-spacing: .14em;
  text-transform: uppercase;
  color: var(--vl-gold-soft);
  font-weight: 600;
}
.sheet-chips,
.sheet-keywords,
.sheet-state-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.sheet-chip {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  padding: 6px 12px;
  border-radius: 20px;
  background: var(--vl-chip-bg);
  border: 1px solid var(--vl-chip-border);
  color: #5a3a10;
  font-weight: 600;
  line-height: 1.25;
}
.sheet-empty {
  color: var(--vl-gold-soft);
  font-style: italic;
  font-size: 1em;
}
.sheet-object-list {
  display: grid;
  gap: 7px;
}
.sheet-object {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  color: var(--vl-ink-soft);
  line-height: 1.35;
}
.sheet-leaf {
  width: 18px;
  height: 18px;
  flex: 0 0 18px;
  margin-top: .1em;
  color: var(--vl-gold);
}
.sheet-object-main {
  min-width: 0;
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 6px;
}
.sheet-object-kind {
  font-family: var(--vl-ui);
  font-size: 10px;
  line-height: 1.2;
  letter-spacing: .05em;
  text-transform: uppercase;
  color: var(--vl-gold);
  border: 1px solid var(--vl-chip-border);
  border-radius: 4px;
  padding: 2px 5px;
}
.sheet-keyword {
  font-family: var(--vl-ui);
  font-size: 12px;
  line-height: 1.2;
  letter-spacing: .04em;
  text-transform: uppercase;
  padding: 4px 8px;
  border-radius: 4px;
  background: rgba(184,146,58,.15);
  border: 1px solid var(--vl-chip-border);
  color: #5a3a10;
}
.sheet-state {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid var(--vl-rule);
  color: var(--vl-ink-soft);
  font-family: var(--vl-ui);
  font-size: 14px;
  line-height: 1.25;
}
.sheet-state.is-active {
  background: var(--vl-chip-bg);
  border-color: var(--vl-chip-border);
  color: #5a3a10;
}
.sheet-state-box {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  border: 1.5px solid var(--vl-rule);
  flex: 0 0 10px;
}
.sheet-state.is-active .sheet-state-box {
  background: #5a3a10;
  border-color: #5a3a10;
}
.sheet-actions {
  display: flex;
  gap: 10px;
  margin-top: 18px;
}
.sheet-actions button {
  min-width: 0;
  min-height: 48px;
  flex: 1 1 0;
  padding: 11px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-family: var(--vl-serif);
  font-size: 16px;
  line-height: 1.15;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  text-align: center;
}
.sheet-menu {
  border: 1px solid var(--vl-ink);
  background: var(--vl-ink);
  color: var(--vl-paper);
}
.sheet-resume {
  border: 1px solid var(--vl-gold);
  background: transparent;
  color: #5a3a10;
}

@media (min-width: 760px) {
  .sheet {
    left: 50%;
    right: auto;
    max-width: 760px;
    transform: translate(-50%, 100%);
  }
  .sheet-layer.is-open .sheet { transform: translate(-50%, 0); }
  .fab-sheet { right: max(18px, calc((100vw - 760px) / 2 + 18px)); }
}

@media (prefers-reduced-motion: reduce) {
  .fab-sheet,
  .sheet-scrim,
  .sheet {
    transition: none;
  }
}

.toc-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(70px, 1fr));
  gap: .35em;
  margin: 1em 0;
}
.toc-grid a {
  display: block;
  text-align: center;
  padding: .35em 0;
  border: 1px solid var(--vl-chip-border);
  border-radius: 3px;
  background: var(--vl-choice-bg);
  color: var(--vl-gold);
  text-decoration: none;
  font-weight: bold;
}
.toc-grid a:hover { background: var(--vl-chip-bg); }
.toc-grid a.ending { background: #ead9a6; border-color: var(--vl-gold-soft); }
.toc-grid a.visited { background: #d8c987; }

hr { border: none; border-top: 1px solid var(--vl-rule); margin: 1.5em 0; }

/* Setup page */
#setup-skill-list { list-style: none; padding: 0; }
#setup-skill-list li {
  padding: .8em 1em;
  margin: .4em 0;
  background: var(--vl-choice-bg);
  border: 1px solid var(--vl-chip-border);
  border-radius: 4px;
  cursor: pointer;
  transition: background .15s;
}
#setup-skill-list li:hover { background: var(--vl-chip-bg); }
#setup-skill-list li.selected {
  background: var(--vl-chip-bg);
  border-color: var(--vl-gold);
  border-width: 2px;
  padding: calc(.8em - 1px) calc(1em - 1px);
}
#setup-skill-list label { cursor: pointer; display: block; }
#setup-skill-list input { margin-right: .8em; }
#setup-skill-list small { display: block; margin-top: .3em; color: var(--vl-ink-soft); font-style: italic; }
.big-btn {
  display: inline-block;
  padding: .7em 1.5em;
  background: var(--vl-ink);
  color: var(--vl-paper) !important;
  text-decoration: none;
  border-radius: 4px;
  font-size: 1.1em;
  border: none;
  cursor: pointer;
  font-family: inherit;
  margin: .4em;
}
.big-btn:hover { background: #5a3a10; }
.big-btn:disabled { background: #aaa; cursor: not-allowed; }
.big-btn.secondary { background: transparent; color: var(--vl-gold) !important; border: 2px solid var(--vl-gold); }
.big-btn.secondary:hover { background: var(--vl-chip-bg); }
.center { text-align: center; }
.profile-list {
  list-style: none;
  padding: 0;
}
.profile-list li {
  padding: .6em .9em;
  margin: .35em 0;
  background: var(--vl-choice-bg);
  border-left: 3px solid var(--vl-choice-bar);
}
.profile-list li.locked-skill {
  background: #ece5d0;
  opacity: .6;
  border-left-color: #999;
}
.profile-list li.locked-skill::after {
  content: " — à acquérir";
  font-style: italic;
  font-size: .9em;
  color: var(--vl-ink-soft);
}
.profile-list li.acquired::before {
  content: "✓ ";
  color: #4a7a08;
  font-weight: bold;
}
.notice {
  background: var(--vl-chip-bg);
  border: 1px solid var(--vl-chip-border);
  padding: .8em 1em;
  border-radius: 4px;
  margin: 1em 0;
}
"""

# ------------------------------- game.js -------------------------------

GAME_JS = r"""
// game.js — moteur de jeu pour Les Jardins de Verre-Lune
(function () {
  'use strict';

  const STATE_KEY = 'verre-lune-state-v1';

  const SKILLS_LIST = [
    'Observation', 'Agilité', 'Discrétion', 'Soin des animaux',
    'Mémoire des légendes', 'Bricolage', 'Orientation'
  ];

  const STATE_KEYWORDS = ['FATIGUÉ', 'BLESSÉ LÉGER', 'ACCOMPAGNÉ'];
  const STATE_LABELS = {
    'FATIGUÉ': 'Fatigué',
    'BLESSÉ LÉGER': 'Blessé léger',
    'ACCOMPAGNÉ': 'Accompagné'
  };

  const DEFAULT_STATE = {
    skills: [],
    objects: [],
    keywords: [],
    currentSection: null,
    visitedSections: [],
    startedAt: null,
  };

  function loadState() {
    try {
      const raw = localStorage.getItem(STATE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        return Object.assign({}, DEFAULT_STATE, parsed);
      }
    } catch (e) { console.warn('localStorage indisponible :', e); }
    return JSON.parse(JSON.stringify(DEFAULT_STATE));
  }

  function saveState(state) {
    try {
      localStorage.setItem(STATE_KEY, JSON.stringify(state));
    } catch (e) { console.warn('Sauvegarde impossible :', e); }
  }

  function resetState() {
    try { localStorage.removeItem(STATE_KEY); } catch (e) {}
  }

  function hasState() {
    try {
      return !!localStorage.getItem(STATE_KEY);
    } catch (e) { return false; }
  }

  function listFromAttr(article, attr) {
    if (!article) return [];
    const v = article.getAttribute(attr);
    return v ? v.split('|').filter(Boolean) : [];
  }

  function applyGrants(article, state) {
    const objs = listFromAttr(article, 'data-grants-objects');
    const kws = listFromAttr(article, 'data-grants-keywords');
    const rmKws = listFromAttr(article, 'data-removes-keywords');
    objs.forEach(o => {
      if (!state.objects.includes(o)) state.objects.push(o);
    });
    kws.forEach(k => {
      if (!state.keywords.includes(k)) state.keywords.push(k);
    });
    rmKws.forEach(k => {
      state.keywords = state.keywords.filter(x => x !== k);
    });
  }

  function meetsRequirements(li, state) {
    const reqSkills = (li.getAttribute('data-requires-skill') || '').split('|').filter(Boolean);
    const reqObjs = (li.getAttribute('data-requires-object') || '').split('|').filter(Boolean);
    const reqKws = (li.getAttribute('data-requires-keyword') || '').split('|').filter(Boolean);
    if (reqSkills.length && !reqSkills.every(s => state.skills.includes(s))) return false;
    if (reqObjs.length && !reqObjs.every(o => state.objects.includes(o))) return false;
    if (reqKws.length && !reqKws.every(k => state.keywords.includes(k))) return false;
    return true;
  }

  function updateChoices(state) {
    document.querySelectorAll('ul.choices li').forEach(li => {
      const hasAnyReq = li.hasAttribute('data-requires-skill')
                     || li.hasAttribute('data-requires-object')
                     || li.hasAttribute('data-requires-keyword');
      if (!hasAnyReq) {
        li.classList.remove('locked');
        return;
      }
      if (meetsRequirements(li, state)) {
        li.classList.remove('locked');
      } else {
        li.classList.add('locked');
        li.querySelectorAll('a').forEach(a => {
          a.addEventListener('click', e => { e.preventDefault(); });
        });
      }
    });
  }

  function escapeHtml(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  function normalizeKeyword(s) {
    return String(s || '').trim().toUpperCase();
  }

  function isStateKeyword(k) {
    return STATE_KEYWORDS.includes(normalizeKeyword(k));
  }

  function emptySheetValue() {
    return '<em class="sheet-empty">aucun pour l\'instant</em>';
  }

  function leafIcon() {
    return '<span class="sheet-leaf" aria-hidden="true">'
      + '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">'
      + '<path d="M20 4c-9 0-15 5-15 12 0 2 1 4 3 4 7 0 12-6 12-16z"></path>'
      + '<path d="M5 20c4-6 8-9 13-12"></path>'
      + '</svg></span>';
  }

  function objectKindLabel(info) {
    if (!info || !info[0]) return '';
    return info[0] === 'principal' ? 'objet-clé' : 'secondaire';
  }

  function renderAdventureSheet(state, article) {
    const sheet = document.getElementById('adventure-sheet');
    if (!sheet) return;

    const sectionName = article ? article.getAttribute('data-section-name') : '';
    const context = document.getElementById('sheet-context');
    if (context) {
      context.textContent = sectionName || 'Aventure en cours';
    }

    const skills = document.getElementById('sheet-skills');
    if (skills) {
      skills.innerHTML = state.skills.length
        ? state.skills.map(s => '<span class="sheet-chip">' + escapeHtml(s) + '</span>').join('')
        : emptySheetValue();
    }

    const objects = document.getElementById('sheet-objects');
    if (objects) {
      const infos = window.OBJECT_INFO || {};
      objects.innerHTML = state.objects.length
        ? state.objects.map(o => {
            const kind = objectKindLabel(infos[o]);
            return '<div class="sheet-object">'
              + leafIcon()
              + '<span class="sheet-object-main">'
              + '<span class="sheet-object-name">' + escapeHtml(o) + '</span>'
              + (kind ? '<span class="sheet-object-kind">' + escapeHtml(kind) + '</span>' : '')
              + '</span>'
              + '</div>';
          }).join('')
        : emptySheetValue();
    }

    const keywords = document.getElementById('sheet-keywords');
    if (keywords) {
      const storyKeywords = state.keywords.filter(k => !isStateKeyword(k));
      keywords.innerHTML = storyKeywords.length
        ? storyKeywords.map(k => '<span class="sheet-keyword">' + escapeHtml(k) + '</span>').join('')
        : emptySheetValue();
    }

    const states = document.getElementById('sheet-states');
    if (states) {
      states.innerHTML = STATE_KEYWORDS.map(key => {
        const active = state.keywords.some(k => normalizeKeyword(k) === key);
        return '<span class="sheet-state' + (active ? ' is-active' : '') + '">'
          + '<span class="sheet-state-box" aria-hidden="true"></span>'
          + escapeHtml(STATE_LABELS[key])
          + '</span>';
      }).join('');
    }
  }

  function setupAdventureSheetControls() {
    const fab = document.querySelector('.fab-sheet');
    const layer = document.getElementById('adventure-sheet-layer');
    const sheet = document.getElementById('adventure-sheet');
    if (!fab || !layer || !sheet) return;

    let lastFocused = null;
    let closeTimer = null;

    function isOpen() {
      return !layer.hidden && layer.classList.contains('is-open');
    }

    function motionDelay(ms) {
      return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : ms;
    }

    function focusableElements() {
      return Array.from(sheet.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'))
        .filter(el => !el.disabled && el.getAttribute('aria-hidden') !== 'true');
    }

    function openSheet() {
      clearTimeout(closeTimer);
      lastFocused = document.activeElement;
      layer.hidden = false;
      sheet.setAttribute('aria-hidden', 'false');
      sheet.scrollTop = 0;
      document.body.classList.add('sheet-open');
      requestAnimationFrame(() => {
        layer.classList.add('is-open');
        const first = sheet.querySelector('.sheet-close') || sheet;
        first.focus();
      });
    }

    function closeSheet() {
      if (layer.hidden) return;
      layer.classList.remove('is-open');
      sheet.setAttribute('aria-hidden', 'true');
      document.body.classList.remove('sheet-open');
      closeTimer = setTimeout(() => {
        layer.hidden = true;
        if (lastFocused && document.contains(lastFocused)) lastFocused.focus();
      }, motionDelay(180));
    }

    fab.addEventListener('click', openSheet);
    layer.querySelectorAll('[data-sheet-close]').forEach(el => {
      el.addEventListener('click', closeSheet);
    });

    const menuBtn = document.getElementById('sheet-menu-main');
    if (menuBtn) {
      menuBtn.addEventListener('click', function () {
        if (confirm('Retour au menu ? Ta progression sera sauvegardée.')) {
          window.location.href = 'index.htm';
        }
      });
    }

    document.addEventListener('keydown', function (e) {
      if (!isOpen()) return;
      if (e.key === 'Escape') {
        e.preventDefault();
        closeSheet();
        return;
      }
      if (e.key !== 'Tab') return;

      const focusables = focusableElements();
      if (!focusables.length) {
        e.preventDefault();
        sheet.focus();
        return;
      }
      const first = focusables[0];
      const last = focusables[focusables.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    });

    const grabber = sheet.querySelector('[data-sheet-grabber]');
    if (grabber) {
      let startY = null;
      let pointerId = null;
      grabber.addEventListener('pointerdown', function (e) {
        startY = e.clientY;
        pointerId = e.pointerId;
        grabber.setPointerCapture(pointerId);
      });
      grabber.addEventListener('pointerup', function (e) {
        if (startY !== null && e.clientY - startY > 50) closeSheet();
        startY = null;
        pointerId = null;
      });
      grabber.addEventListener('pointercancel', function () {
        startY = null;
        pointerId = null;
      });
    }
  }

  // -------- Rendu des pages dédiées --------

  function renderSkillsPage(state) {
    const list = document.getElementById('skills-list');
    if (!list) return;
    const descs = window.SKILL_DESCRIPTIONS || {};
    list.innerHTML = '';
    SKILLS_LIST.forEach(s => {
      const li = document.createElement('li');
      const acq = state.skills.includes(s);
      li.className = acq ? 'acquired' : 'locked-skill';
      li.innerHTML = '<strong>' + escapeHtml(s) + '</strong>'
        + (descs[s] ? ' — ' + escapeHtml(descs[s]) : '');
      list.appendChild(li);
    });
    const status = document.getElementById('skills-status');
    if (status) {
      status.textContent = state.skills.length
        ? 'Tu as choisi ' + state.skills.length + ' compétence(s). Les ' + (SKILLS_LIST.length - state.skills.length) + ' autres restent à acquérir lors d\'une autre partie.'
        : 'Tu n\'as pas encore choisi tes compétences. Commence une nouvelle partie pour choisir.';
    }
  }

  function renderObjectsPage(state) {
    const list = document.getElementById('objects-list');
    if (!list) return;
    const infos = window.OBJECT_INFO || {};
    list.innerHTML = '';
    if (!state.objects.length) {
      list.innerHTML = '<li><em>Tu ne portes encore aucun objet. Avance dans l\'aventure pour en trouver.</em></li>';
      return;
    }
    state.objects.forEach(o => {
      const li = document.createElement('li');
      li.className = 'acquired';
      const info = infos[o];
      const desc = info ? info[1] : '';
      li.innerHTML = '<strong>' + escapeHtml(o) + '</strong>'
        + (desc ? ' — ' + escapeHtml(desc) : '');
      list.appendChild(li);
    });
  }

  function renderKeywordsPage(state) {
    const list = document.getElementById('keywords-list');
    if (!list) return;
    list.innerHTML = '';
    if (!state.keywords.length) {
      list.innerHTML = '<li><em>Tu n\'as encore noté aucun mot-clé. Tes choix dans l\'aventure t\'en feront acquérir.</em></li>';
      return;
    }
    state.keywords.forEach(k => {
      const li = document.createElement('li');
      li.className = 'acquired';
      li.textContent = k;
      list.appendChild(li);
    });
  }

  // -------- Page d'accueil --------

  function renderHomePage(state) {
    const continueBtn = document.getElementById('continue-btn');
    const newGameBtn = document.getElementById('newgame-btn');
    const statusDiv = document.getElementById('home-status');
    if (continueBtn && state.currentSection) {
      continueBtn.style.display = 'inline-block';
      continueBtn.href = 'sect' + state.currentSection + '.htm';
      continueBtn.textContent = 'Reprendre →';
    } else if (continueBtn) {
      continueBtn.style.display = 'none';
    }
    if (statusDiv && state.currentSection) {
      statusDiv.innerHTML = 'Une aventure est en cours, avec <strong>' + state.skills.length
        + ' compétence(s)</strong>, <strong>' + state.objects.length
        + ' objet(s)</strong> et <strong>' + state.keywords.length + ' mot(s)-clé(s)</strong>.';
    } else if (statusDiv) {
      statusDiv.textContent = 'Aucune aventure en cours. Choisis « Nouvelle partie » pour commencer.';
    }
    if (newGameBtn) {
      newGameBtn.addEventListener('click', function (e) {
        e.preventDefault();
        if (state.currentSection) {
          if (!confirm('Tu as une aventure en cours. Vraiment commencer une nouvelle partie ?')) return;
        }
        resetState();
        window.location.href = 'setup.htm';
      });
    }
  }

  // -------- Page de setup (choix des compétences) --------

  function renderSetupPage() {
    const list = document.getElementById('setup-skill-list');
    if (!list) return;
    const descs = window.SKILL_DESCRIPTIONS || {};
    list.innerHTML = '';
    SKILLS_LIST.forEach((s, i) => {
      const li = document.createElement('li');
      li.innerHTML =
        '<label>'
        + '<input type="checkbox" value="' + escapeHtml(s) + '" />'
        + '<strong>' + escapeHtml(s) + '</strong>'
        + (descs[s] ? '<small>' + escapeHtml(descs[s]) + '</small>' : '')
        + '</label>';
      list.appendChild(li);
    });

    function updateUI() {
      const checked = list.querySelectorAll('input[type=checkbox]:checked');
      list.querySelectorAll('li').forEach(li => {
        const cb = li.querySelector('input');
        if (cb.checked) li.classList.add('selected');
        else li.classList.remove('selected');
      });
      list.querySelectorAll('input[type=checkbox]').forEach(cb => {
        cb.disabled = (!cb.checked && checked.length >= 2);
      });
      const startBtn = document.getElementById('start-btn');
      if (startBtn) startBtn.disabled = (checked.length !== 2);
    }

    list.addEventListener('change', updateUI);
    updateUI();

    const form = document.getElementById('setup-form');
    if (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        const chosen = Array.from(list.querySelectorAll('input[type=checkbox]:checked')).map(c => c.value);
        if (chosen.length !== 2) {
          alert('Choisis exactement 2 compétences.');
          return;
        }
        const state = JSON.parse(JSON.stringify(DEFAULT_STATE));
        state.skills = chosen;
        state.startedAt = new Date().toISOString();
        state.currentSection = 1;
        state.visitedSections = [];
        saveState(state);
        window.location.href = 'sect1.htm';
      });
    }
  }

  // -------- Initialisation par type de page --------

  function init() {
    const state = loadState();
    const article = document.querySelector('article[data-section]');

    if (article) {
      const num = parseInt(article.getAttribute('data-section'), 10);
      state.currentSection = num;
      if (!state.visitedSections.includes(num)) state.visitedSections.push(num);
      if (!state.startedAt) state.startedAt = new Date().toISOString();
      applyGrants(article, state);
      updateChoices(state);
      saveState(state);
    }

    renderAdventureSheet(state, article);
    setupAdventureSheetControls();
    renderHomePage(state);
    renderSkillsPage(state);
    renderObjectsPage(state);
    renderKeywordsPage(state);
    renderSetupPage();

    // Boutons globaux
    const resetBtn = document.getElementById('global-reset');
    if (resetBtn) {
      resetBtn.addEventListener('click', function (e) {
        e.preventDefault();
        if (confirm('Vraiment effacer ta sauvegarde et recommencer ?')) {
          resetState();
          window.location.href = 'index.htm';
        }
      });
    }

    // Marqueur des sections visitées dans le toc
    if (document.querySelector('.toc-grid')) {
      document.querySelectorAll('.toc-grid a').forEach(a => {
        const m = a.getAttribute('href').match(/sect(\d+)/);
        if (m && state.visitedSections.includes(parseInt(m[1], 10))) {
          a.classList.add('visited');
        }
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
"""

# ------------------------------- HELPERS -------------------------------


def page_wrap(title, body_html, nav_html="", extra_head=""):
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="main.css"/>
{extra_head}
</head>
<body>
<header>
<h1><a href="index.htm" style="color:inherit; text-decoration:none;">{html.escape(TITLE)}</a></h1>
<h2>{html.escape(SUBTITLE)}</h2>
</header>
<article>
{body_html}
</article>
{nav_html}
<script src="data.js"></script>
<script src="game.js"></script>
</body>
</html>
"""


def make_reader_sheet():
    return """
<button class="fab-sheet" type="button" aria-label="Ouvrir ma fiche d'aventure">
<svg class="icon-scroll" width="30" height="30" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
<path d="M7 6h14a3 3 0 0 1 3 3v14a3 3 0 0 1-3 3H10a3 3 0 0 1-3-3V6z"></path>
<path d="M7 6a3 3 0 0 0-3 3v2h3"></path>
<path d="M24 26a3 3 0 0 0 3-3v-2h-3"></path>
<path d="M11 12h9M11 16h9M11 20h6"></path>
</svg>
</button>
<div class="sheet-layer" id="adventure-sheet-layer" hidden>
<div class="sheet-scrim" data-sheet-close aria-hidden="true"></div>
<section class="sheet" id="adventure-sheet" role="dialog" aria-modal="true" aria-labelledby="sheet-title" aria-hidden="true" tabindex="-1">
<div class="sheet-grabber" data-sheet-grabber aria-hidden="true"></div>
<div class="sheet-top">
<div class="sheet-title-wrap">
<h2 class="sheet-title" id="sheet-title">Fiche d'aventure</h2>
<p class="sheet-context" id="sheet-context">Aventure en cours</p>
</div>
<button class="sheet-close" type="button" aria-label="Fermer" data-sheet-close>
<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true">
<path d="M6 6l12 12M18 6L6 18"></path>
</svg>
</button>
</div>
<div class="sheet-rule"></div>
<section class="sheet-block" data-block="competences">
<h3>Compétences</h3>
<div class="sheet-chips" id="sheet-skills"></div>
</section>
<section class="sheet-block" data-block="objets">
<h3>Objets</h3>
<div class="sheet-object-list" id="sheet-objects"></div>
</section>
<section class="sheet-block" data-block="mots-cles">
<h3>Mots-clés</h3>
<div class="sheet-keywords" id="sheet-keywords"></div>
</section>
<section class="sheet-block" data-block="etat">
<h3>État</h3>
<div class="sheet-state-list" id="sheet-states"></div>
</section>
<footer class="sheet-actions">
<button class="sheet-menu" id="sheet-menu-main" type="button">
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
<path d="M3 11l9-7 9 7"></path>
<path d="M5 10v9h14v-9"></path>
</svg>
Menu principal
</button>
<button class="sheet-resume" type="button" data-sheet-close>Reprendre la lecture</button>
</footer>
</section>
</div>
"""

def md_inline(text):
    """Convertit le markdown inline en HTML.

    Note : les références **N** dans la narration ne sont plus auto-linkées —
    les numéros de section sont cachés au lecteur. La navigation passe
    exclusivement par les <a> générés dans les listes de choix.
    """
    text = html.escape(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\w)\*([^\*\n]+?)\*(?!\w)', r'<em>\1</em>', text)
    text = re.sub(r'`([^`\n]+)`', r'<code>\1</code>', text)
    return text


# ------------------------------- DETECTION -------------------------------


def detect_grants(body):
    """Détecte les objets et mots-clés octroyés dans le corps d'une section."""
    objects = []
    keywords = []
    removed = []

    # Objets : on parcourt les noms connus. On reconnaît plusieurs tournures :
    #   **Ajoute la X à tes objets / à ta liste**
    #   **Prends la X dans tes objets**
    #   **Note la X sur ta fiche / dans tes objets**
    for obj_name in OBJECT_INFO.keys():
        patterns = [
            r'\*\*[^*]*?Ajoute[^*]{0,80}?' + re.escape(obj_name) +
                r'[^*]{0,80}?à (?:tes objets|ta liste)',
            r'\*\*[^*]*?Prends[^*]{0,80}?' + re.escape(obj_name) +
                r'[^*]{0,80}?(?:dans tes objets|à tes objets)',
            r'\*\*[^*]*?Note[^*]{0,80}?' + re.escape(obj_name) +
                r'[^*]{0,80}?(?:sur ta fiche|dans tes objets)',
        ]
        for pat in patterns:
            if re.search(pat, body, flags=re.IGNORECASE):
                if obj_name not in objects:
                    objects.append(obj_name)
                break

    # Mots-clés : "Note le mot-clé X sur ..."
    kw_pattern = re.compile(
        r'(?i)note\s+le\s+mot-clé\s+'
        r'([A-ZÀ-ÿ][A-ZÀ-ÿ\s\'\-]+?)'
        r'(?:\s+sur|\s+\(|\.\*\*|\s*\*\*|\s+si\s+tu|\.\s|$)',
        re.UNICODE,
    )
    for m in kw_pattern.finditer(body):
        kw = m.group(1).strip().rstrip('.,;')
        if kw and kw not in keywords:
            keywords.append(kw)

    # États : "**Tu es FATIGUÉ**", "**Tu es FATIGUÉ et BLESSÉ LÉGER**", etc.
    # On scanne TOUT le contenu du bloc en gras pour attraper TOUS les états
    # listés (sinon une formulation "et / ni" en perdait la moitié).
    state_grant = re.compile(r'\*\*Tu es\b([^*]+?)\*\*')
    for m in state_grant.finditer(body):
        chunk = m.group(1)
        for kw in STATE_KEYWORDS:
            if re.search(r'\b' + re.escape(kw) + r'\b', chunk):
                if kw not in keywords:
                    keywords.append(kw)

    # États retirés : "**Tu n'es plus FATIGUÉ ni BLESSÉ LÉGER**", etc.
    state_rm = re.compile(r"\*\*Tu n'es plus\b([^*]+?)\*\*")
    for m in state_rm.finditer(body):
        chunk = m.group(1)
        for kw in STATE_KEYWORDS:
            if re.search(r'\b' + re.escape(kw) + r'\b', chunk):
                if kw not in removed:
                    removed.append(kw)

    return objects, keywords, removed


def detect_choice_requirements(choice_text):
    """Pour une ligne de choix, renvoie (skills, objects, keywords) requis."""
    skills_req = []
    objects_req = []
    keywords_req = []

    # On parcourt toutes les zones **X** dans la ligne
    matches = list(re.finditer(r'\*\*([^\*\n]+)\*\*', choice_text))
    for m in matches:
        name = m.group(1).strip()
        if re.fullmatch(r'\d+', name):
            continue  # numéro de section
        start = m.start()
        prefix = choice_text[max(0, start - 50):start].lower()

        if 'compétence' in prefix and name in SKILLS:
            if name not in skills_req:
                skills_req.append(name)
        elif 'mot-clé' in prefix:
            if name not in keywords_req:
                keywords_req.append(name)
        elif name in GATED_OBJECTS:
            # Vérifie qu'il y a un verbe possessif avant
            if re.search(r'(?:possèdes|portes|as|tu as la)\b', prefix):
                if name not in objects_req:
                    objects_req.append(name)
            elif 'tu as' in prefix or 'tu portes' in prefix:
                if name not in objects_req:
                    objects_req.append(name)

    return skills_req, objects_req, keywords_req


# ------------------------------- Réécriture d'un choix -------------------------------


def _finalize_choice(s):
    s = s.strip().rstrip(',;')
    if not s:
        return s
    # Met une majuscule au premier caractère alphabétique, en sautant un **bold** initial.
    if s.startswith('**'):
        end = s.find('**', 2)
        if end > 2:
            inner = s[2:end]
            if inner and inner[0].islower():
                inner = inner[0].upper() + inner[1:]
            s = '**' + inner + s[end:]
    elif s[0].islower():
        s = s[0].upper() + s[1:]
    if s[-1] not in '.!?…':
        s += '.'
    return s


def _strip_action_prefix(rest):
    rest = re.sub(r'^tu\s+(?:peux|veux|voudrais|décides\s+de)\s+',
                  '', rest, flags=re.IGNORECASE)
    rest = re.sub(r'^pour\s+', '', rest, flags=re.IGNORECASE)
    return rest.strip()


def _normalize_modal(rest):
    """Dans une voix de choix, 'tu veux/voudrais X' lit mieux en 'tu peux X'."""
    return re.sub(r'^tu\s+(?:veux|voudrais)\b', 'tu peux',
                  rest, flags=re.IGNORECASE)


def rewrite_choice_display(text):
    """Transforme une ligne de choix en action directe.

    - Retire systématiquement « va au **N** » (la cible reste dans data-target).
    - Convertit les amorces conditionnelles « Si tu (possèdes|portes|as) …, tu
      peux X » en action directe « X. »
    - Strippe les amorces « Si tu <verbe> », « Si la/le … » et « Pour … ».
    Si rien ne matche proprement, on conserve le texte (sans le numéro).
    """
    # 1) Retire toute occurrence de "va au **N**" et la ponctuation qui la précède.
    text = re.sub(r'\s*[,;\.]?\s*[Vv]a au \*\*\d+\*\*\s*\.?', '', text)
    text = text.strip().rstrip(',;.')
    if not text:
        return text

    # 2a) "Si tu (possèdes|portes|as|peux) … et que tu (peux|veux|voudrais) X"
    #     → garde "Tu (peux|veux) X" comme voix déclarative.
    m = re.match(
        r'^Si\s+tu\s+(?:possèdes|portes|as|peux)\b.*?\s+et\s+que\s+'
        r'(tu\s+(?:peux|veux|voudrais|décides\s+de)\s+.+)$',
        text, flags=re.IGNORECASE)
    if m:
        return _finalize_choice(_normalize_modal(m.group(1)))

    # 2b) "Si tu (possèdes|portes|as|peux) …, tu (peux|veux|voudrais|décides) X"
    m = re.match(
        r'^Si\s+tu\s+(?:possèdes|portes|as|peux)\b.*,\s*'
        r'(tu\s+(?:peux|veux|voudrais|décides\s+de)\s+.+)$',
        text, flags=re.IGNORECASE)
    if m:
        return _finalize_choice(_normalize_modal(m.group(1)))

    # 2c) "Si tu (possèdes|portes|as|peux) …, <rest>" (fallback générique)
    m = re.match(
        r'^Si\s+tu\s+(?:possèdes|portes|as|peux)\b[^,]*?,\s*(.+)$',
        text, flags=re.IGNORECASE)
    if m:
        return _finalize_choice(m.group(1))

    # 2d) "Si tu <autre verbe> …" → "Tu <verbe> …" (on remet le sujet)
    m = re.match(
        r'^Si\s+tu\s+(?!possèdes|portes|as|peux\b)(.+)$',
        text, flags=re.IGNORECASE)
    if m:
        return _finalize_choice('Tu ' + m.group(1))

    # 2e) "Si la/les/un/une/<...> …" → retire "Si " (observation atmosphérique)
    m = re.match(r'^Si\s+(.+)$', text, flags=re.IGNORECASE)
    if m:
        return _finalize_choice(m.group(1))

    # 2f) "Pour <action>"
    m = re.match(r'^Pour\s+(.+)$', text)
    if m:
        return _finalize_choice(m.group(1))

    return _finalize_choice(text)


# ------------------------------- HTML pour section -------------------------------


def md_block_to_html(block_text):
    """Convertit un bloc markdown en HTML (paragraphes, listes, blockquotes,
    tableaux, code). Les listes 'Choix :' sont traitées spécialement par
    md_section_to_html (qui ajoute les data-* sur chaque <li>).
    """
    lines = block_text.split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            i += 1
            continue

        # Blockquote
        if line.startswith("> "):
            bq_lines = []
            while i < len(lines) and lines[i].rstrip().startswith("> "):
                bq_lines.append(lines[i].rstrip()[2:])
                i += 1
            content = "<br/>".join(md_inline(l) for l in bq_lines)
            out.append(f'<blockquote>{content}</blockquote>')
            continue

        # Tableau
        if line.startswith("|") and i + 1 < len(lines) and lines[i+1].strip().startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            if len(table_lines) >= 2:
                headers = [c.strip() for c in table_lines[0].strip("|").split("|")]
                second = table_lines[1]
                if re.match(r'^\|[\s\-\:|]+\|$', second.replace(" ", "")):
                    rows = table_lines[2:]
                else:
                    rows = table_lines[1:]
                out.append('<table><thead><tr>')
                for h in headers:
                    out.append(f'<th>{md_inline(h)}</th>')
                out.append('</tr></thead><tbody>')
                for row in rows:
                    cells = [c.strip() for c in row.strip("|").split("|")]
                    out.append('<tr>')
                    for c in cells:
                        out.append(f'<td>{md_inline(c)}</td>')
                    out.append('</tr>')
                out.append('</tbody></table>')
            continue

        # Code block
        if line.startswith("```"):
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].rstrip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1
            out.append(f'<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>')
            continue

        # Liste simple "- "
        if line.startswith("- "):
            out.append('<ul>')
            while i < len(lines) and lines[i].rstrip().startswith("- "):
                content = lines[i].rstrip()[2:]
                out.append(f'<li>{md_inline(content)}</li>')
                i += 1
            out.append('</ul>')
            continue

        # Paragraphe normal
        para_lines = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(("- ", "> ", "|", "```")):
            para_lines.append(lines[i].rstrip())
            i += 1
        para = " ".join(para_lines)
        out.append(f'<p>{md_inline(para)}</p>')

    return "\n".join(out)


def md_section_to_html(body):
    """Convertit un corps de section. Les listes commençant par 'Choix :'
    sont traitées avec ajout des data-requires-* sur chaque <li>."""
    # On découpe en blocs séparés par 'Choix :' (un seul bloc en général)
    if 'Choix :' not in body:
        return md_block_to_html(body)

    parts = body.split('Choix :', 1)
    pre = parts[0].strip()
    post = parts[1] if len(parts) > 1 else ''

    # Tout ce qui suit "Choix :" est une liste "- ... va au **N**"
    # On parse ligne par ligne
    out = []
    if pre:
        out.append(md_block_to_html(pre))
    out.append('<p><strong>Choix :</strong></p>')
    out.append('<ul class="choices">')

    # Récupère les lignes "- ..." de post
    post_lines = post.split('\n')
    for line in post_lines:
        s = line.rstrip()
        if not s.startswith('- '):
            # Si on tombe sur autre chose, on l'ignore en silence
            continue
        choice_text = s[2:]
        skills_req, objects_req, keywords_req = detect_choice_requirements(choice_text)

        # Extrait la cible avant toute réécriture (la regex source attend "va au **N**").
        target_m = re.search(r'va au \*\*(\d+)\*\*', choice_text, re.IGNORECASE)
        target = target_m.group(1) if target_m else None

        # Réécrit l'affichage : plus de "Si tu …", plus de "va au N".
        display_text = rewrite_choice_display(choice_text)

        attrs = []
        if target:
            attrs.append(f'data-target="{target}"')
        if skills_req:
            attrs.append(f'data-requires-skill="{html.escape("|".join(skills_req))}"')
        if objects_req:
            attrs.append(f'data-requires-object="{html.escape("|".join(objects_req))}"')
        if keywords_req:
            attrs.append(f'data-requires-keyword="{html.escape("|".join(keywords_req))}"')

        attrs_str = (' ' + ' '.join(attrs)) if attrs else ''
        inner = md_inline(display_text)

        # Badge des prérequis : visible à côté de l'action.
        badge_parts = []
        for sk in skills_req:
            badge_parts.append(f'<span class="req req-skill">⚑ {html.escape(sk)}</span>')
        for ob in objects_req:
            badge_parts.append(f'<span class="req req-object">◆ {html.escape(ob)}</span>')
        for kw in keywords_req:
            badge_parts.append(f'<span class="req req-keyword">✦ {html.escape(kw)}</span>')
        badges = (' <span class="req-badges">' + ''.join(badge_parts) + '</span>'
                  if badge_parts else '')

        # Le <li> entier est cliquable via un <a> qui pointe sur la section cible ;
        # le numéro n'est jamais affiché. Le contenu est structuré en deux blocs
        # (body + chevron) pour que le chevron reste à droite quand les badges
        # passent à la ligne sur mobile.
        body_html = (f'<span class="choice-body">'
                     f'<span class="choice-text">{inner}</span>{badges}'
                     f'</span>')
        chevron = '<span class="choice-chevron" aria-hidden="true">›</span>'
        if target:
            link_html = (f'<a class="choice-link" href="sect{target}.htm">'
                         f'{body_html}{chevron}</a>')
        else:
            link_html = f'<span class="choice-link">{body_html}{chevron}</span>'

        out.append(f'<li{attrs_str}>{link_html}</li>')

    out.append('</ul>')
    return '\n'.join(out)


# ------------------------------- LECTURE DU MD -------------------------------

with open(SRC, "r", encoding="utf-8") as f:
    md = f.read()

sect_pattern = re.compile(r'^### (\d+)(?:\s*—\s*(.+?))?\s*$', re.MULTILINE)
matches = list(sect_pattern.finditer(md))
assert matches, "Aucune section trouvée."

first_sect_start = matches[0].start()
front_matter = md[:first_sect_start]

annexes_match = re.search(r'^##\s+Annexes de contrôle\s*$', md, re.MULTILINE)
annexes_start = annexes_match.start() if annexes_match else len(md)

sections = []
for idx, m in enumerate(matches):
    num = int(m.group(1))
    name = m.group(2).strip() if m.group(2) else None
    body_start = m.end()
    body_end = matches[idx+1].start() if idx + 1 < len(matches) else annexes_start
    body = md[body_start:body_end].strip()
    body = re.sub(r'(^|\n)---\s*(\n|$)', r'\1\2', body).strip()
    sections.append((num, name, body))

print(f"Sections : {len(sections)}")


# ------------------------------- ÉCRITURE -------------------------------

# Fichier data.js : descriptions injectées dans le DOM
data_js_lines = [
    "// data.js — métadonnées injectées dans le DOM pour les pages dédiées",
    "window.SKILL_DESCRIPTIONS = " + json.dumps(SKILL_DESCRIPTIONS, ensure_ascii=False) + ";",
    "window.OBJECT_INFO = " + json.dumps({k: list(v) for k, v in OBJECT_INFO.items()}, ensure_ascii=False) + ";",
]
with open(OUT / "data.js", "w", encoding="utf-8") as f:
    f.write("\n".join(data_js_lines))

with open(OUT / "game.js", "w", encoding="utf-8") as f:
    f.write(GAME_JS.lstrip())

with open(OUT / "main.css", "w", encoding="utf-8") as f:
    f.write(CSS.lstrip())


# index.htm — page d'accueil avec Nouvelle partie / Continuer
index_body = """
<h1 class="sectnum" style="font-variant: small-caps;">Les Jardins de Verre-Lune</h1>
<p style="text-align:center; font-style:italic; margin-bottom:1.5em;">Une aventure dont tu es le héros — pour les lectrices et lecteurs de 10 à 14 ans.</p>

<h2>Introduction</h2>
<p>Depuis trois nuits, les étoiles s'effacent au-dessus du village de Brumeval. Au matin, les fleurs deviennent transparentes comme du verre et les bêtes oublient leur chemin. Les adultes haussent les épaules : « C'est la saison, c'est tout. » Mais toi, tu sens bien que ce n'est pas la saison.</p>

<p>Tu n'as que douze ans, et pourtant tu es certain d'une chose : si personne ne va voir ce qui se passe sous la forêt des Fils d'Argent, les étoiles ne reviendront plus.</p>

<p>Ta grand-mère, Mère Aïna, fredonne chaque soir une vieille comptine que plus personne n'écoute. Elle parle d'une serre cachée, d'une promesse oubliée et d'un Veilleur qui dort entre les racines. Personne n'y croit. Personne, sauf toi.</p>

<p>Cette aventure t'appartient. À chaque section, tu vivras une scène. À la fin de la plupart d'entre elles, tu choisiras ce que tu veux faire ensuite. Le système retient pour toi tes compétences, tes objets et tes mots-clés : les choix dont tu n'as pas les conditions seront grisés et bloqués jusqu'à ce que tu les remplisses.</p>

<p>Il existe au moins <strong>sept fins différentes</strong>. Une seule t'attend, celle que tu auras vraiment méritée.</p>

<div class="notice" id="home-status">
<em>Chargement de ta sauvegarde…</em>
</div>

<div class="center" style="margin: 1.5em 0;">
<a href="#" id="newgame-btn" class="big-btn">Nouvelle partie</a>
<a href="#" id="continue-btn" class="big-btn secondary">Reprendre</a>
</div>

<hr/>

<h2>Comment jouer</h2>
<p>L'aventure se déroule en <strong>350 scènes</strong>. Tu commences par choisir <strong>deux compétences</strong> parmi sept. Au fil de tes choix, tu trouveras des objets et noteras des mots-clés. Le système les retient automatiquement.</p>

<ul>
<li>Lis chaque section en entier avant de cliquer.</li>
<li>Les choix grisés (⛔) signalent que tu n'as pas la compétence, l'objet ou le mot-clé requis. Ils restent visibles mais bloqués.</li>
<li>Pendant la lecture, l'icône de fiche en bas à droite ouvre tes compétences, tes objets, tes mots-clés et ton état.</li>
<li>Ta partie est sauvegardée automatiquement. Tu peux fermer l'onglet et revenir plus tard.</li>
<li>« Nouvelle partie » efface complètement la sauvegarde et redémarre avec un nouveau choix de compétences.</li>
</ul>

<p>Si tu arrives à une <strong>fin</strong>, c'est qu'une de tes aventures est terminée. Rien ne t'empêche de recommencer pour essayer une autre route — il existe sept fins principales, dont une <em>secrète</em>.</p>
"""

with open(OUT / "index.htm", "w", encoding="utf-8") as f:
    f.write(page_wrap("Accueil", index_body, nav_html=""))


# setup.htm — choix des 2 compétences
setup_body = """
<h1 class="sectnum">Nouvelle partie</h1>
<p>Avant de partir pour Brumeval, choisis <strong>deux compétences</strong> parmi les sept proposées. Ce seront les talents particuliers de ton personnage. Tu pourras t'en servir tout au long de l'aventure pour ouvrir des chemins que les autres ne voient pas.</p>

<p class="notice">Une fois choisies, tes compétences sont fixées pour cette partie. Si tu veux changer plus tard, il faudra commencer une nouvelle partie.</p>

<form id="setup-form">
<ul id="setup-skill-list"></ul>
<div class="center" style="margin-top: 1.2em;">
<button type="submit" id="start-btn" class="big-btn" disabled>Commencer l'aventure →</button>
<br/>
<a href="index.htm" style="color:#6a3a08; font-size:.9em;">← Retour à l'accueil</a>
</div>
</form>
"""

with open(OUT / "setup.htm", "w", encoding="utf-8") as f:
    f.write(page_wrap("Nouvelle partie", setup_body, nav_html=""))


# skills.htm — dynamique
skills_body = """
<h1 class="sectnum">Compétences</h1>
<p id="skills-status">Chargement…</p>
<ul class="profile-list" id="skills-list"></ul>
<hr/>
<div class="center">
<a href="#" onclick="history.back(); return false;" class="big-btn secondary">← Retour</a>
<a href="index.htm" class="big-btn secondary">Accueil</a>
</div>
"""
with open(OUT / "skills.htm", "w", encoding="utf-8") as f:
    f.write(page_wrap("Compétences", skills_body, nav_html=""))


# objects.htm — dynamique, n'affiche que les acquis
objects_body = """
<h1 class="sectnum">Objets</h1>
<p>Voici les objets que tu portes actuellement.</p>
<ul class="profile-list" id="objects-list"></ul>
<hr/>
<div class="center">
<a href="#" onclick="history.back(); return false;" class="big-btn secondary">← Retour</a>
<a href="index.htm" class="big-btn secondary">Accueil</a>
</div>
"""
with open(OUT / "objects.htm", "w", encoding="utf-8") as f:
    f.write(page_wrap("Objets", objects_body, nav_html=""))


# keywords.htm — dynamique, n'affiche que les acquis
keywords_body = """
<h1 class="sectnum">Mots-clés</h1>
<p>Voici les mots-clés que tu as notés au fil de l'aventure.</p>
<ul class="profile-list" id="keywords-list"></ul>
<hr/>
<div class="center">
<a href="#" onclick="history.back(); return false;" class="big-btn secondary">← Retour</a>
<a href="index.htm" class="big-btn secondary">Accueil</a>
</div>
"""
with open(OUT / "keywords.htm", "w", encoding="utf-8") as f:
    f.write(page_wrap("Mots-clés", keywords_body, nav_html=""))


# toc.htm — grille des 350 sections
toc_links = []
for num, name, _ in sections:
    extra = " ending" if num in ENDINGS else ""
    toc_links.append(f'<a class="cell{extra}" href="sect{num}.htm">{num}</a>')
toc_body = f"""
<h1 class="sectnum">Table des sections</h1>
<p>Les sections que tu as visitées sont en doré sombre. Les fins de l'aventure (sections 333, 336, 339, 342, 345, 348, 350) sont en doré clair.</p>
<div class="toc-grid">
{"".join(toc_links)}
</div>
<hr/>
<div class="center">
<a href="index.htm" class="big-btn secondary">← Accueil</a>
<a href="#" id="global-reset" class="big-btn secondary">Effacer ma sauvegarde</a>
</div>
"""
with open(OUT / "toc.htm", "w", encoding="utf-8") as f:
    f.write(page_wrap("Table des sections", toc_body, nav_html=""))


# Sections individuelles
for num, name, body in sections:
    objs, kws, rm_kws = detect_grants(body)
    # Octrois manuels
    if num in MANUAL_GRANTS:
        for o in MANUAL_GRANTS[num].get("objects", []):
            if o not in objs:
                objs.append(o)
        for k in MANUAL_GRANTS[num].get("keywords", []):
            if k not in kws:
                kws.append(k)
        for k in MANUAL_GRANTS[num].get("remove_keywords", []):
            if k not in rm_kws:
                rm_kws.append(k)

    article_attrs = [f'data-section="{num}"']
    if name:
        article_attrs.append(f'data-section-name="{html.escape(name)}"')
    if objs:
        article_attrs.append(f'data-grants-objects="{html.escape("|".join(objs))}"')
    if kws:
        article_attrs.append(f'data-grants-keywords="{html.escape("|".join(kws))}"')
    if rm_kws:
        article_attrs.append(f'data-removes-keywords="{html.escape("|".join(rm_kws))}"')

    # Le numéro de section n'est plus affiché au lecteur ; il reste sur l'élément
    # <article data-section="…"> pour le moteur de jeu (sauvegarde, etc.).
    title_html = f'<h2 class="sectname">{html.escape(name)}</h2>' if name else ''

    body_html = md_section_to_html(body)

    # On remplace l'article ouvrant par celui avec les attributs
    article_open = '<article ' + ' '.join(article_attrs) + '>'

    # Construction manuelle de la page section (pas page_wrap car on doit
    # personnaliser l'article et ajouter la fiche d'aventure modale).
    page = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{html.escape(name) if name else html.escape(TITLE)}</title>
<link rel="stylesheet" href="main.css"/>
</head>
<body>
<header>
<h1>{html.escape(TITLE)}</h1>
<h2>{html.escape(SUBTITLE)}</h2>
</header>
<main class="reader">
{article_open}
{title_html}
{body_html}
</article>
{make_reader_sheet()}
</main>
<script src="data.js"></script>
<script src="game.js"></script>
</body>
</html>
"""
    with open(OUT / f"sect{num}.htm", "w", encoding="utf-8") as f:
        f.write(page)


# annexes.htm (statique)
if annexes_match:
    annexes_text = md[annexes_start:].strip()
    annexes_html_parts = []
    sub_blocks = re.split(r'(^##+\s+.+$)', annexes_text, flags=re.MULTILINE)
    for block in sub_blocks:
        block = block.strip()
        if not block:
            continue
        if block.startswith("###"):
            annexes_html_parts.append(f"<h3>{html.escape(block.lstrip('# ').strip())}</h3>")
        elif block.startswith("##"):
            annexes_html_parts.append(f"<h2>{html.escape(block.lstrip('# ').strip())}</h2>")
        else:
            annexes_html_parts.append(md_block_to_html(block))
    annexes_html = "\n".join(annexes_html_parts) + '\n<hr/><div class="center"><a href="index.htm" class="big-btn secondary">← Accueil</a></div>'
    with open(OUT / "annexes.htm", "w", encoding="utf-8") as f:
        f.write(page_wrap("Annexes de contrôle", annexes_html, nav_html=""))

# Supprime la vieille fiche.htm si présente
fiche_path = OUT / "fiche.htm"
if fiche_path.exists():
    fiche_path.unlink()
howto_path = OUT / "howto.htm"
if howto_path.exists():
    howto_path.unlink()


files = sorted(os.listdir(OUT))
print(f"Fichiers générés : {len(files)}")
print(f"Échantillon début : {files[:6]}")
print(f"Échantillon fin : {files[-4:]}")
