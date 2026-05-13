# Backlog — Les Jardins de Verre-Lune

État au 2026-05-13. Sprints ≈ 1 semaine. Priorité implicite : du haut vers le bas.

## Légende
- ✅ done — déjà sur `main`
- 🚧 in progress
- ⏳ planned

---

## Epic 1 — Moteur livre-jeu

But : passer du manuscrit Markdown à une app statique jouable.

| # | Story | Statut |
|---|---|---|
| 1.1 | Parser des sections, choix, conditions | ✅ |
| 1.2 | Détection objets / mots-clés / états + audits cohérence | ✅ |
| 1.3 | Réécriture des choix (« Si tu… va au N » → « Tu …. ») | ✅ |
| 1.4 | Masquage complet des numéros de section côté lecteur | ✅ |
| 1.5 | Persistance JS via `localStorage` (sauvegarde auto) | ✅ |
| 1.6 | Choix gatés grisés / déverrouillés selon la fiche | ✅ |

## Epic 2 — UX mobile

| # | Story | Statut |
|---|---|---|
| 2.1 | Ligne de choix entière cliquable, tap target 48 px | ✅ |
| 2.2 | Chevron `›` comme affordance, ⛔ pour locked | ✅ |
| 2.3 | Sheet fiche d'aventure (FAB + bottom-sheet, safe-area) | ✅ |
| 2.4 | Splash : couverture aquarelle + 3 boutons | ✅ |
| 2.5 | Page Aide séparée (Intro + Comment jouer) | ✅ |
| 2.6 | Feedback tap (background + scale + tap-highlight muté) | ✅ |

## Epic 3 — Éditorial & audits

| # | Story | Statut |
|---|---|---|
| 3.1 | Audit gates → cibles fantômes (§90, §166 corrigées) | ✅ |
| 3.2 | Parser : grants multiples dans un bloc gras | ✅ |
| 3.3 | Parser : `Prends X dans tes objets`, `Note X sur ta fiche` | ✅ |
| 3.4 | Conditional grants → grants explicites (§200, §306) | ✅ |
| 3.5 | Équipement de départ tracké (Pain, Ruban, Lampe, Couteau) | ✅ |
| 3.6 | Suppression des consignes « Coche/Décoche la case » | ✅ |
| 3.7 | Suppression de PERDU (état mort) | ✅ |
| 3.8 | Tests sur le téléphone de la fille | 🚧 |
| 3.9 | Reformulation des 2 choix observationnels (Si la canopée / Si un vent) | ⏳ |
| 3.10 | Audit chaînes d'aventure : toute fin est atteignable depuis §1 | ⏳ |

## Epic 4 — Distribution iOS (PWA) — **back-burner**

> Déprioritisé le 2026-05-13. À reprendre uniquement si quelqu'un sur iPhone le réclame.
> Pas d'urgence : Android couvre le besoin courant, le code est prêt à recevoir cette couche sans refactor.

| # | Story | Effort | Statut |
|---|---|---|---|
| 4.1 | `manifest.json` (nom, theme-color, icônes) | 30 min | ⏳ later |
| 4.2 | `service-worker.js` (cache offline ~360 fichiers) | 1 h | ⏳ later |
| 4.3 | Icônes apple-touch + maskable (5 tailles depuis `cover.jpg`) | 30 min | ⏳ later |
| 4.4 | Meta tags `apple-mobile-web-app-*` + theme-color | 15 min | ⏳ later |
| 4.5 | Activer GitHub Pages, racine `livre/xhtml/` | 15 min | ⏳ later |
| 4.6 | Test « Add to Home Screen » sur iPhone | 15 min | ⏳ later |

**Sortie sprint quand on y reviendra** : URL HTTPS, icône, plein écran, fonctionne hors-ligne dès la 2e ouverture.

## Epic 9 — Refonte éditoriale + balises (🚧, **priorité 1**)

> **Trigger 2026-05-13** : l'auteur constate que les 7 fins sont mal orchestrées, que beaucoup de « Si tu… » de la prose n'ont aucune conséquence mécanique, et que la qualité narrative + mécanique se dégrade dans la 2e moitié du livre. Décision : sortir la mécanique de la prose via un système de balises explicites, puis retagger + relire l'ensemble.
>
> **Bloque** : Epic 5 (i18n). Inutile de traduire un manuscrit instable.
>
> Voir [`HANDOVER.md`](HANDOVER.md) pour le brief complet à un nouvel·le contributeur·rice (humain·e ou IA).

### Phase 9.1 — Schema lock
| # | Story | Statut |
|---|---|---|
| 9.1.1 | Valider la syntaxe finale des balises (`{clé: valeur}` inline vs YAML front-matter vs sidecar) | ✅ inline |
| 9.1.2 | Définir le vocabulaire : `lieu`, `grants-object`, `grants-keyword`, `state+`, `state-`, `requires-skill`, `requires-object`, `requires-keyword`, `ending`, `branch`, `requires-alliances-min`, etc. | ✅ |
| 9.1.3 | Documenter la spec dans `AGENTS.md` | ✅ |
| 9.1.4 | Écrire un linter dédié à la spec (`livre/lint_tags.py`) qui vérifie la syntaxe et la cohérence des balises | ✅ |

### Phase 9.2 — Parser hybride et migration
| # | Story | Statut |
|---|---|---|
| 9.2.1 | `build_xhtml.py` : extraire les balises avant le parsing prose. Tags ont priorité ; la prose reste fallback pendant la migration. | ✅ |
| 9.2.2 | Retagger section par section (350 sections). Sens forward + back, en deux passes. | ⏳ |
| 9.2.3 | Une fois 100% balisé : retirer le parsing prose-based (regex `Tu es FATIGUÉ`, etc.) du moteur. | ⏳ |

### Phase 9.3 — Audit + correctifs
| # | Story |
|---|---|
| 9.3.1 | Cartographier les 7 fins : conditions, sections-source, atteignabilité depuis §1 |
| 9.3.2 | Linter complet : sections orphelines, compétences/objets/mots-clés jamais utilisés, fins inatteignables, fins-piège |
| 9.3.3 | Corriger les chaînes cassées identifiées par 9.3.2 |

### Phase 9.4 — Pass éditorial
| # | Story |
|---|---|
| 9.4.1 | Relecture forward (§1 → §350) avec mécanique verrouillée par les balises — fluidité de prose |
| 9.4.2 | Relecture back-to-forward (§350 → §1) — cohérence terminale → causale |
| 9.4.3 | Régulariser le ton (la qualité se dégrade dans la 2e moitié, à rééquilibrer) |
| 9.4.4 | Éliminer les « Si tu… » décoratifs qui ne sont pas des conditions de jeu |

**Effort total estimé** : 5-7 jours de travail technique + relecture éditoriale.

---

## Epic 5 — Internationalisation

But : versions EN + ES sans toucher au moteur français.

### Sprint i18n-1 — Refactor du générateur (≈ 1 j)
| # | Story |
|---|---|
| 5.1.1 | Externaliser SKILLS / OBJECT_INFO / STATE_KEYWORDS / UI strings dans `locale_<lang>.py` |
| 5.1.2 | Paramétrer les regex parser (`Tu es / Note le mot-clé / Ajoute X`) par locale |
| 5.1.3 | CLI : `python3 build_xhtml.py --locale fr\|en\|es` |
| 5.1.4 | OUT par locale : `xhtml/fr/`, `xhtml/en/`, `xhtml/es/` |
| 5.1.5 | Sélecteur de langue sur le splash + persistance |

### Sprint i18n-2 — Anglais (≈ 3 j)
| # | Story |
|---|---|
| 5.2.1 | Traduction LLM FR → EN du manuscrit |
| 5.2.2 | Rewriter EN : « If you do X » → « Do X. » ou « You do X. » |
| 5.2.3 | `locale_en.py` (objets, états, regex traduits) |
| 5.2.4 | Relecture native anglaise |
| 5.2.5 | QA : rejouer 20 sections gatées + 7 fins |

### Sprint i18n-3 — Espagnol (≈ 3 j)
| # | Story |
|---|---|
| 5.3.1 | Traduction LLM FR → ES |
| 5.3.2 | Rewriter ES (impératif / présent indicatif) |
| 5.3.3 | `locale_es.py` |
| 5.3.4 | Décision éditoriale : neutre (cansade) vs sélecteur de genre au setup |
| 5.3.5 | Relecture native espagnole |
| 5.3.6 | QA |

## Epic 6 — Distribution Android étendue

| # | Story | Statut |
|---|---|---|
| 6.1 | Icône launcher dédiée (depuis `cover.jpg`, adaptive-icon) | ⏳ |
| 6.2 | Signature release (keystore + Play App Signing) | ⏳ |
| 6.3 | APK release optimisé (R8, sans debug symbols) | ⏳ |
| 6.4 | Publication F-Droid ou hébergement APK direct | ⏳ |

## Epic 8 — Outillage pour les prochains livres (⏳, futur)

| # | Story |
|---|---|
| 8.1 | Système de détection automatique du **lieu courant** par section (front-matter `[lieu: Brumeval]` dans la source, ou tag de zone hérité jusqu'à override) — réactive le header "Lieu seul" du proposal de Verre-Lune sans passer par un mapping manuel sur 350 sections. |
| 8.2 | Lint pré-build : section déclarée sans lieu, lieu déclaré mais inutilisé, etc. |
| 8.3 | Generator multi-livres (1 manuscrit = 1 ouvrage, partage le moteur) — découpler `OUT`, `TITLE`, `OBJECT_INFO` par projet. |

## Epic 7 — Métriques & vie de l'œuvre (NICE)

| # | Story |
|---|---|
| 7.1 | Compteur local de chemins empruntés (localStorage, anonymisé) |
| 7.2 | Galerie des fins atteintes / fins découvertes |
| 7.3 | Achievements légers (tous les objets ramassés, fin secrète…) |
| 7.4 | Replay : marquer les sections déjà visitées dans le TOC |

---

## Plan de sprints (indicatif)

| Sprint | Objectif | Epics |
|---|---|---|
| **S0 (clos)** | Stabilisation FR + distribution v1.0.0 (APK release + GitHub Pages) | 1.*, 2.*, 3.*, 6.2 |
| **S1 (en cours)** | Schema balises validé + parser hybride | 9.1, 9.2.1 |
| **S2** | Manuscrit 100% retaggé | 9.2.2, 9.2.3 |
| **S3** | Audit fins + correctifs | 9.3 |
| **S4** | Pass éditorial forward + back | 9.4 |
| **S5** | Refactor i18n du générateur | 5.1 |
| **S6** | Version anglaise livrée et relue | 5.2 |
| **S7** | Version espagnole livrée et relue | 5.3 |
| **S8** | Polish Android release + icône launcher | 6.1, 6.3, 6.4 |
| **— LATER —** | PWA iPhone (Epic 4) | 4.* |
| **— LATER —** | Métriques replay et fins découvertes | 7.* |

**Critère de fin de sprint** : un push sur `main` correspondant à l'objectif, validé sur device réel (Android pour le moment).

**Note 2026-05-13** : la session technique avec l'IA est en pause après v1.0.0. La suite éditoriale (Epic 9) est reprise avec une autre IA / un humain. Voir [`HANDOVER.md`](HANDOVER.md) pour le brief.

---

## Hors-scope explicite

- App Store Apple : pas avant qu'il y ait une raison commerciale (99 €/an).
- Multijoueur, scoring social, leaderboards : pas un livre-jeu narratif.
- Backend serveur : tout reste statique (localStorage suffit).
