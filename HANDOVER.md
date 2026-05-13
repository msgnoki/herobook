# Handover — Reprise éditoriale du manuscrit

État au 2026-05-13.

> **Objet de cette note :** transférer à un nouvel·le assistant·e éditorial·e (humain·e ou IA) le contexte nécessaire pour reprendre le manuscrit `livre/Les_Jardins_de_Verre-Lune.md`, en partant du constat que les mécaniques de jeu et la gestion des 7 fins se sont dégradées au fil de l'écriture, et qu'il faut :
>
> 1. introduire un **système de balises** pour séparer la mécanique de la prose,
> 2. **retagger** l'intégralité du manuscrit (350 sections),
> 3. **auditer** les fins et chemins,
> 4. faire une **passe éditoriale** sens-aller puis sens-retour.

---

## 1 — Contexte projet

**Les Jardins de Verre-Lune** est un livre-jeu interactif (« dont tu es le héros ») pour les 10-14 ans, en français, de 350 sections (~70 000 mots). L'auteur le distribue à un cercle proche (~10 enfants) via :

- une version Android (APK signé, `android/`)
- une version web statique générée à partir du Markdown (`livre/xhtml/`, déployée sur GitHub Pages à <https://msgnoki.github.io/herobook/>)

Repository : <https://github.com/msgnoki/herobook> (public).

Le code-base est en Python 3 stdlib uniquement pour le générateur (`livre/build_xhtml.py`) ; l'app Android est un WebView qui charge les XHTML statiques (`android/app/src/main/assets/book/`).

---

## 2 — Ce qui marche déjà (technique)

- Générateur Markdown → XHTML opérationnel (350 sections + pages annexes)
- Splash écran avec couverture aquarelle (`livre/xhtml/cover.jpg`)
- Carte aquarelle (`livre/xhtml/map.jpg`) accessible depuis la fiche d'aventure
- Choix dont la cible est masquée au lecteur (plus de « va au 42 »)
- Choix gatés (compétence, objet, mot-clé) avec badge visible + verrouillage JS
- Sauvegarde localStorage (compétences, objets, mots-clés, états, section courante)
- Fiche d'aventure modale (bottom-sheet) listant compétences, objets, mots-clés, états
- 4 audits automatiques au build (cf. `livre/build_xhtml.py`) :
  - gates pointant vers une cible jamais accordée
  - mises à jour de fiche écrites hors gras (donc invisibles pour le parser)
  - mots-clés retirés jamais accordés
  - cohérence parser ↔ manuscrit

L'app et le site sont en production v1.0.0 (release GitHub : `v1.0.0`).

---

## 3 — Ce qui ne marche pas (éditorial)

**Diagnostic posé par l'auteur, à valider à la relecture :**

1. **Les 7 fins sont mal orchestrées.** Pas de contrat explicite sur ce qui mène à chacune. Conditions disséminées dans la prose. Difficile d'auditer qu'une fin est atteignable et qu'aucune n'est inaccessible.
2. **Beaucoup de « Si tu… » décoratifs.** Le manuscrit contient des phrases conditionnelles qui n'ont aucune conséquence mécanique mais ressemblent à des conditions de jeu. Confusion pour le lecteur, fragilité pour le parser.
3. **Dégradation progressive.** La qualité narrative et la cohérence mécanique sont solides au début du livre (§1–~§100) et se dégradent dans la 2e moitié. Probablement de la dette d'écriture accumulée.
4. **Mécanique noyée dans le texte.** Aujourd'hui le générateur extrait la mécanique par regex sur le français naturel (`r'\*\*Tu es FATIGUÉ\b'`, `r'note le mot-clé X'`, etc.). Fragile par construction.

**Pistes de fixes déjà appliquées partiellement (n'y revenir que si problème persistant) :**
- §90 et §166 avaient des branches gatées narratives jamais offertes en `Choix :` — corrigé.
- §200 et §306 avaient des grants conditionnels invisibles au parser (« si tu n'avais pas X, tu obtiens X ») — convertis en grants explicites.
- §4 ne traçait pas l'équipement de départ — ajouté via `MANUAL_GRANTS`.
- §101 grant `FATIGUÉ et BLESSÉ LÉGER` ne capturait que le premier — parser corrigé.
- État `PERDU` déclaré mais jamais utilisé — retiré du code.

Voir les commits sur `main` pour le détail.

---

## 4 — Mission proposée

### Schéma de balises (à valider en P1)

**Décision en suspens :** le format exact n'est pas tranché. La proposition par défaut est *inline* dans le Markdown, avec accolades :

```markdown
### 42 {lieu: Verger pâle}
{grants-object: Graine lumineuse}
{state+: FATIGUÉ}

Tu reprends ta route entre les arbres. Devant toi, un papillon de verre…

Choix :
- → 43 :: Tu poses le pied sur la première racine.
- → 44 :: Chercher un autre passage. {requires-skill: Orientation}
- → 45 :: Déposer la graine près du papillon. {requires-object: Graine lumineuse} {state-: FATIGUÉ}
```

Pour les fins :

```markdown
### 350 {lieu: La Serre} {ending: parfaite}
{requires-keywords: [GARDIEN DEVENU, AMITIÉ DE NILO, FAON SAUVÉ, CONFIANCE DES LUCIOLES, VEILLEUR APAISÉ, COMPTINE COMPLÈTE]}

Prose de la fin parfaite…
```

Pour les carrefours conditionnels :

```markdown
### 314 {lieu: Pont des Racines}
{branch: 348, requires-keyword: QUATRIÈME VOIE}
{branch: 345, requires-keyword: PROMESSE TRANSFORMÉE, requires-alliances-min: 2}
{branch: 342, requires-keyword: PROMESSE TRANSFORMÉE}
```

**Pourquoi ce format** : grep-able trivialement (`re.findall(r'\{([^}]+)\}', line)`), lisible par un humain qui édite à la main, cohabite avec l'ancien manuscrit pendant la migration.

**Alternatives discutées non choisies pour l'instant** : YAML front-matter par section, fichier sidecar `.meta.yaml` par section. Voir `BACKLOG.md` Epic 9.

### Plan en 4 phases

| Phase | Objet | Effort estimé |
|---|---|---|
| **P1 — Schema lock** | Valider la syntaxe + écrire le linter de la spec | ½ j |
| **P2 — Parser hybride + migration** | Le générateur accepte ancien format ET balises. Les tags ont priorité. Retagger section par section. | parser : ½ j • tagging : 1-2 j |
| **P3 — Audit + correctifs** | Avec balises : audit des 7 fins, linter exhaustif, fix des chaînes cassées | 1 j |
| **P4 — Pass éditorial** | Relecture front-to-back PUIS back-to-front. Mécanique verrouillée par les balises, libre de réécrire la prose. | 2-3 j |

---

## 5 — Anchors techniques à connaître

### Fichiers clés

| Fichier | Rôle |
|---|---|
| `livre/Les_Jardins_de_Verre-Lune.md` | Manuscrit source — **seule source de vérité éditoriale** |
| `livre/build_xhtml.py` | Générateur Python (~1900 lignes, tout en un). Contient SKILLS, OBJECT_INFO, GATED_OBJECTS, MANUAL_GRANTS, STATE_KEYWORDS, ENDINGS, CSS, JS embarqué, parser, rendu |
| `livre/xhtml/` | Sortie générée — **ne jamais éditer à la main**, regénérée à chaque build |
| `android/app/src/main/assets/book/` | Copie des `xhtml` pour l'app Android — synchronisée par la tâche Gradle `syncBookAssets` au build |
| `AGENTS.md` | Conventions techniques du repo (à lire) |
| `BACKLOG.md` | Roadmap (à mettre à jour si direction change) |

### Conventions parser actuelles (à conserver pendant la migration)

Ces patterns doivent rester reconnus par le parser en phase de transition :

- Grants d'objet : `**Ajoute la Graine lumineuse à tes objets.**`, `**Prends la X dans tes objets**`, `**Note la X sur ta fiche**`
- Grant de mot-clé : `Note le mot-clé X sur ta fiche` (insensible à la casse, peut être hors gras)
- Grant d'état : `**Tu es FATIGUÉ**` (ou avec plusieurs : `**Tu es FATIGUÉ et BLESSÉ LÉGER**` — le parser scanne tout le bloc gras)
- Removal d'état : `**Tu n'es plus FATIGUÉ**`
- Cible de choix : `va au **N**` à la fin d'un item de liste sous `Choix :`
- Gate de choix : tokens en `**X**` dans la ligne, qualifiés par les mots précédents (`possèdes`, `portes`, `compétence`, `mot-clé`)

Le parser est volontairement tolérant aux variations de ponctuation. Ne pas le casser sans une bonne raison.

### Pipeline de build

```bash
# 1. Génération XHTML (depuis la racine du repo)
python3 livre/build_xhtml.py

# 2. Sync vers Android
cp -r livre/xhtml/. android/app/src/main/assets/book/

# 3. Build APK release signé (keystore privé, voir AGENTS.md)
cd android && ./gradlew :app:assembleRelease

# 4. Vérification visuelle locale
python3 -m http.server 8765 -d livre/xhtml --bind 0.0.0.0
# → http://localhost:8765/index.htm
```

Le déploiement web sur GitHub Pages est automatique à chaque push qui touche `livre/xhtml/` (workflow `.github/workflows/pages.yml`).

### Audits déjà disponibles (à conserver / étendre)

Tous embarqués dans le générateur. Voir `detect_grants`, `detect_choice_requirements`, et la table `MANUAL_GRANTS` pour les cas spéciaux non détectables par regex.

Pour ajouter de nouveaux audits (recommandé en P3) : créer `livre/audit_*.py` à côté du générateur. Pattern existant :

```python
import sys
sys.path.insert(0, "livre")
from build_xhtml import OBJECT_INFO, MANUAL_GRANTS, STATE_KEYWORDS, detect_grants, detect_choice_requirements

import re
from pathlib import Path
text = Path("livre/Les_Jardins_de_Verre-Lune.md").read_text(encoding="utf-8")
sections = re.split(r"^### (\d+)\s*$", text, flags=re.MULTILINE)
# ...
```

---

## 6 — Non-négociables

À ne **pas** changer sans accord explicite de l'auteur :

1. **`livre/xhtml/` est généré, jamais édité à la main.** Toute modif visuelle passe par `build_xhtml.py`.
2. **`MEMORY.md` et `~/.claude/projects/-home-msgnoki-Hero/memory/`** appartiennent à l'IA de session précédente. Ne pas y écrire sans raison.
3. **L'identité de commit** : utiliser `git -c user.name=msgnoki -c user.email=msgnoki@gmail.com commit ...` inline (ne JAMAIS modifier le `git config --global`).
4. **Le keystore Android** : `~/.keystores/herobook-release.jks` est hors du repo. Ne pas le copier dans le repo. Si tu construis un APK release, lis le `.properties` à côté.
5. **Les numéros de section sont cachés au lecteur** côté UI. Ils restent dans `data-section` côté HTML pour la mécanique JS. Ne pas les ré-exposer.
6. **Le manuscrit `.md` est la source de vérité.** Si une incohérence apparaît entre `.md` et `xhtml/`, c'est le `.md` qu'on corrige, pas l'inverse.
7. **Ne pas chercher à automatiser une « traduction LLM » du manuscrit ** dans cette mission. L'i18n est une mission distincte (Epic 5 du backlog), à faire **après** la stabilisation éditoriale.

---

## 7 — Comment valider ton travail

À chaque session, avant de pousser :

```bash
python3 livre/build_xhtml.py                # doit sortir 'Sections : 350' sans warning
python3 livre/audit_full.py 2>&1            # (à recréer si supprimé) doit reporter 0 problème
```

Tester visuellement :
- splash : `livre/xhtml/index.htm`
- une section gatée connue : `livre/xhtml/sect100.htm` (CONFIANCE DES LUCIOLES, RÊVE D'ANYA)
- une fin : `livre/xhtml/sect350.htm`
- la carte : `livre/xhtml/carte.htm`

Si tu touches au parser, vérifier que les **8 sections suivantes** continuent à granter ce qu'il faut :

| Section | Grant attendu |
|---|---|
| §4 | Boussole d'argent + Pain aux noix + Ruban rouge + Lampe-tempête + Petit couteau |
| §44 | RENARD GUIDE + ruban d'écorce gravé |
| §97 | FATIGUÉ |
| §101 | FATIGUÉ + BLESSÉ LÉGER (les **deux**) |
| §195 | VEILLEUR APAISÉ |
| §200 | AMITIÉ DE NILO, removal FATIGUÉ |
| §205 | removal FATIGUÉ + BLESSÉ LÉGER |
| §306 | VEILLEUR REMERCIÉ + VEILLEUR APAISÉ |

Cf. le commit `0d3af79` et les commits suivants.

---

## 8 — Décisions encore ouvertes

À trancher avec l'auteur **avant** de coder :

1. **Syntaxe finale des balises** : `{clé: valeur}` inline (ma proposition) vs YAML front-matter vs fichier sidecar. Voir Epic 9 du backlog.
2. **Migration big-bang vs incrémentale.** Recommandé : incrémentale (parser hybride pendant la transition). Moins risqué.
3. **Audit fins d'abord ou balises d'abord.** L'auteur penche pour faire les balises d'abord — elles permettent un audit fins propre. Mais on peut commencer par une cartographie sèche des 7 fins pour identifier les pires ratés.
4. **Périmètre P4 (passe éditoriale)** : qui écrit ? L'IA propose, l'auteur valide ? Tout l'auteur ? Mix ? La passe back-to-front est particulièrement importante pour l'auteur (cf. dégradation de qualité dans la 2e moitié).

---

## 9 — Pour démarrer

1. Lire `AGENTS.md` (conventions du repo).
2. Lire `BACKLOG.md` (statut roadmap).
3. Lire ce HANDOVER.md (cette note).
4. Lire les ~100 premières lignes de `livre/Les_Jardins_de_Verre-Lune.md` pour saisir le ton et la structure.
5. Lire `livre/build_xhtml.py` : surtout les constantes du début, `detect_grants`, `detect_choice_requirements`, `rewrite_choice_display`, `md_section_to_html`. ~300 lignes en tout, le reste est CSS/JS embarqués.
6. Ouvrir un nouveau chat avec l'auteur : confirmer le format de balises avant de toucher au manuscrit.

Bonne reprise.
