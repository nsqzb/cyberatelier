# Cahier des charges commun (agents de rédaction)

Projet : Cyber Atelier (lis /Users/anas/Documents/cyberatelier/CLAUDE.md d'abord, puis content/courses.json et content/headerscope.md comme MODÈLE de ton, de précision et de structure).

## But de l'apprenant
Débutant réel en Python (connaît variables, listes, fonctions). Il doit monter vite en compétence en Python + Git pour réaliser ensuite, à l'école, un **framework de pentest modulaire** (modules réseau, web, Active Directory ; interface CLI ou GUI ; documentation ; bonnes pratiques), dans un cadre scolaire autorisé. Le lab est une maquette réduite de ce projet. Plus le lab est complet et progressif, mieux c'est, mais la difficulté monte par petits paliers.

## Règles non négociables
- Français, tutoiement, ton direct et encourageant, jamais condescendant. Pas de promesse « expert en N heures ».
- **AUCUNE solution** : ni code Python d'exercice, ni .gitlab-ci.yml complet. Donne des contrats précis (entrées, sorties, erreurs, cas limites), des tests à écrire décrits en prose, des pistes de documentation officielle et des indices progressifs. Un court extrait de syntaxe générique (ex. forme d'une boucle `for` sur un exemple sans rapport avec l'exercice) est permis dans le parcours Socle uniquement, pour enseigner une notion.
- Cible réseau : uniquement 127.0.0.1 / le labo local (127.0.0.1:8000, routes /fragile /durci /absent /erreur). Jamais de cible externe, jamais d'exploit.
- Distinguer toujours : tests locaux / pipeline GitLab réel / autorisation de fusion / case cochée (déclarative). Sur un runner GitLab, 127.0.0.1 est le runner : les tests obligatoires (unittest) n'utilisent ni labo ni nmap réel ni réseau externe (mocks, fixtures, fichiers temporaires). Les vérifications qui exigent le labo ou nmap sont des **demos** (champ `demos`, ids D1, D2… ), pas des `tests`.
- Git est une compétence à part entière : chaque MR = branche `feat/...` créée depuis la principale à jour, commits atomiques au message clair, `git status`/`git diff`/`git log --oneline` avant commit, tests unitaires locaux avant push, relecture du diff de la MR. Introduis progressivement : branches, `git switch -c`, `.gitignore`, `git restore`, `git revert`, `git stash`, conflit de fusion provoqué volontairement (consignes pas à pas), `rebase` simple, tags. Le guide ne remplace pas le cours : demande à l'apprenant de PRATIQUER chaque commande sur son dépôt.
- Tests : l'apprenant écrit des tests **unittest** (bibliothèque standard) ; le parcours Socle les introduit. Chaque test décrit : id, title, input, expected (avec cas limites).
- Progressivité : chaque mission a 4 à 6 `tasks` ordonnées de la plus simple à la plus exigeante, un `hint` (3 niveaux séparés par « \n\nNiveau 2 : », « \n\nNiveau 3 : »), des `acceptance` observables. Les consignes expliquent le POURQUOI (lien avec le futur framework).
- Pas de dépendance pip hors bibliothèque standard, sauf mention explicite de l'environnement (venv avec `unittest` seulement ; pas de pytest).

## Format de sortie (dans /Users/anas/Documents/cyberatelier/drafts/<ID>/ uniquement)
1. `course.json` : UN objet parcours au même schéma que les parcours de content/courses.json : id, title, subtitle, description, level, color, durationMinutes=300, goals, prerequisites, scope, concepts, files, setup (label, command, note, optionnel interactive:true pour les commandes qui demandent une saisie ou un secret ; commandes d'une seule ligne si on veut le bouton « Préparer dans la console »), steps (EXACTEMENT 3, ids `<ID>-mr1`, `<ID>-mr2`, `<ID>-mr3`, avec title, branch, minutes, mission, tasks, tests, optionnel demos, acceptance, hint), timeline (somme EXACTE = 300 min, et chaque mission = minutes cohérentes avec la timeline), references (urls https://docs.python.org/... ou https://git-scm.com/... ou https://docs.gitlab.com/... uniquement ; vérifie qu'elles sont plausibles et officielles), resources (url "/content/<ID>.md"), completion, limits. JSON valide, indent 2, ensure_ascii=False, saut de ligne final.
2. `<ID>.md` : énoncé complet lisible seul (même esprit que content/headerscope.md : contrat, MR par MR, méthode GitLab, repères de temps, livrables, limites), cohérent mot pour mot avec course.json (mêmes ids de tests, mêmes noms de branches, mêmes durées).
3. `NOTES.md` : 10 lignes max — décisions prises, points à valider, ce que tu n'as pas pu vérifier.
Vérifie toi-même : `python3 -c "import json;json.load(open('drafts/<ID>/course.json'))"` et que la somme de timeline vaut 300.
Ne modifie AUCUN fichier hors de ton dossier drafts/<ID>/. Aucune commande git en écriture, aucun docker.
Réponds à la fin par : les chemins écrits, les ids de tests/demos créés, et tout doute.
