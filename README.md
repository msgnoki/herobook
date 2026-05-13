# Les Jardins de Verre-Lune

Une aventure dont tu es le héros — pour les lectrices et lecteurs de 10 à 14 ans.

## 🌐 Jouer en ligne (sans rien installer)

**→ [https://msgnoki.github.io/herobook/](https://msgnoki.github.io/herobook/)**

Marche sur tout navigateur (Chrome, Safari, Firefox), ordinateur comme téléphone. La sauvegarde de partie reste dans le navigateur — si tu changes d'appareil, tu repars de zéro.

## 📱 App Android (debug / release)

Builds générés via Gradle dans `android/`. Voir [`AGENTS.md`](AGENTS.md) pour la procédure de build et de signature, et [`BACKLOG.md`](BACKLOG.md) pour la roadmap.

L'APK signé est partagé main à main (mail / WhatsApp) pour le cercle proche. Pas de Play Store pour l'instant.

## 📚 Structure du projet

- `livre/Les_Jardins_de_Verre-Lune.md` — manuscrit source (350 sections)
- `livre/build_xhtml.py` — générateur statique (Python 3, stdlib uniquement)
- `livre/xhtml/` — sortie générée (servie par GitHub Pages)
- `android/` — wrapper Android (WebView qui charge les XHTML embarqués)
- `BACKLOG.md` — roadmap : epics, sprints, hors-scope
- `AGENTS.md` — guide technique du repo

## ⚖️ Crédits

Auteur, illustrations, code : `msgnoki`.

Made with [Claude Code](https://claude.com/claude-code).
