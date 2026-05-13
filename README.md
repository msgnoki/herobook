# Les Jardins de Verre-Lune

Une aventure dont tu es le héros — pour les lectrices et lecteurs de 10 à 14 ans.

## 🌐 Jouer en ligne (sans rien installer)

**→ [https://msgnoki.github.io/herobook/](https://msgnoki.github.io/herobook/)**

Marche sur tout navigateur (Chrome, Safari, Firefox), ordinateur comme téléphone. La sauvegarde de partie reste dans le navigateur — si tu changes d'appareil, tu repars de zéro.

## 📱 App Android

**→ [Télécharger la dernière version (APK)](https://github.com/msgnoki/herobook/releases/latest)**

~4 Mo, Android 6.0 et plus. Ouvre le fichier après téléchargement et autorise « Sources inconnues » si demandé.

Pour partager à un proche : envoie-lui simplement le lien ci-dessus (ou l'URL de jeu en ligne) par mail ou WhatsApp.

Builds générés via Gradle dans `android/`. Voir [`AGENTS.md`](AGENTS.md) pour la procédure de build et de signature, et [`BACKLOG.md`](BACKLOG.md) pour la roadmap.

## 📚 Structure du projet

- `livre/Les_Jardins_de_Verre-Lune.md` — manuscrit source (350 sections)
- `livre/build_xhtml.py` — générateur statique (Python 3, stdlib uniquement)
- `livre/tag_spec.py` — parseur partagé des balises mécaniques Epic 9
- `livre/lint_tags.py` / `livre/audit_full.py` — validation des balises et audit de reprise
- `livre/xhtml/` — sortie générée (servie par GitHub Pages)
- `android/` — wrapper Android (WebView qui charge les XHTML embarqués)
- `BACKLOG.md` — roadmap : epics, sprints, hors-scope
- `HANDOVER.md` — brief pour reprendre la refonte éditoriale (Epic 9)
- `AGENTS.md` — guide technique du repo

## ⚖️ Crédits

Auteur, illustrations, code : `msgnoki`.

Made with [Claude Code](https://claude.com/claude-code).
