# Parcours de Cyber Atelier

> Document dérivé de `content/courses.json` (6 parcours, 1800 min au total). En cas d’écart, le JSON fait foi. Après toute modification de `courses.json`, mettre ce document à jour (ids, durées, branches, tests et démonstrations).

## Vue d’ensemble

| Ordre | id | Titre | Durée | Missions (MR) | Tests (ids) | Démonstrations (ids) |
|---|---|---|---|---|---|---|
| 1 | `socle` | Socle Python & Git | 5 h (300 min) | 3 | S1 à S24 (24) | D1 à D2 (2) |
| 2 | `portpilot` | PortPilot | 5 h (300 min) | 3 | T1 à T8 (8) | — |
| 3 | `headerscope` | HeaderScope | 5 h (300 min) | 3 | H1 à H9 (9) | D1 à D3 (3) |
| 4 | `fileguard` | FileGuard | 5 h (300 min) | 3 | F1 à F14 (14) | — |
| 5 | `toolwrap` | ToolWrap — piloter un outil externe | 5 h (300 min) | 3 | W1 à W16 (16) | D1 à D3 (3) |
| 6 | `reconwrap` | ReconWrap — assembler un mini-framework | 5 h (300 min) | 3 | R1 à R17 (17) | D1 à D6 (6) |

Total : 6 parcours × 300 min = 30 h, 18 merge requests. Les ids de mission (`<parcours>-mr1` à `-mr3`) sont stockés dans la progression de l’apprenant : ils ne doivent jamais être renommés.

Les ids de tests sont uniques dans un même parcours. Les ids de démonstration (`D1`…) sont réutilisés d’un parcours à l’autre : on les cite toujours avec le parcours, par exemple « ToolWrap D1 ».

## Détail par parcours

### Socle Python & Git (`socle`)

- **Sous-titre** : Premiers pas en Python, tests unittest et Git en équipe
- **Niveau** : Débutant · **Durée** : 5 h · **Ressource** : `/content/socle.md`

**Objectifs**

- Écrire des fonctions pures avec conditions, boucles, listes, dictionnaires et chaînes de caractères.
- Écrire des tests unittest qui se relancent à chaque modification du code.
- Lire et écrire des fichiers en gérant les erreurs, puis manipuler JSON et pathlib.
- Utiliser Git en équipe : branche, commit, push, merge request, conflit, rebase simple et tag.

**Missions**

| Mission (id) | Titre | Branche | Min | Tests (ids) | Démonstrations (ids) |
|---|---|---|---|---|---|
| `socle-mr1` | MR1 — Fonctions pures, premier unittest et première merge request | `feat/bases` | 100 | S1, S2, S3, S4, S5, S6, S7, S8, S9, S10 | — |
| `socle-mr2` | MR2 — Fichiers, exceptions, JSON et Git de rattrapage | `feat/fichiers-erreurs` | 100 | S11, S12, S13, S14, S15, S16, S17, S18 | D1 |
| `socle-mr3` | MR3 — Analyseur complet, conflit de fusion, rebase et tag | `feat/analyseur` | 70 | S19, S20, S21, S22, S23, S24 | D2 |

**Compétences Git travaillées** (repérées dans le texte du parcours) : merge request, pipeline / CI, conflit de fusion, rebase, tag, revert, stash, restore, .gitignore, revue de diff, git log, branche par git switch -c.

**Lien avec le projet final** : Fondations, sans outil de sécurité : fonctions pures, tests unittest, fichiers, JSON et cycle Git en équipe. Tout ce qui suit s’appuie dessus.

**Limites déclarées dans le JSON**

- Données entièrement fictives (fixtures/socle, adresses 192.0.2.0/24) ; aucun réseau, aucune cible, aucun outil offensif.
- Les tests obligatoires n’ouvrent pas fixtures/ et n’ont besoin d’aucun service : ils tournent sur un runner sans labo. La lecture de auth.log reste une démonstration locale.
- Le parcours n’introduit ni pytest, ni packaging, ni CI complète : ce sont des étapes ultérieures.
- Le conflit et le rebase sont provoqués sur des branches locales jetables, jamais sur la branche principale.

### PortPilot (`portpilot`)

- **Sous-titre** : Scanner TCP local, tests et livraison GitLab
- **Niveau** : Débutant · **Durée** : 5 h · **Ressource** : `/content/portpilot.md`

**Objectifs**

- Valider une courte liste de ports sans conversion implicite.
- Tenter une connexion TCP locale avec un délai fixe et quatre états distincts.
- Tester une écoute éphémère autonome et préserver l’ordre des ports.
- Livrer le travail par trois MR avec une CI réellement bloquante si l’instance de l’école le permet.

**Missions**

| Mission (id) | Titre | Branche | Min | Tests (ids) | Démonstrations (ids) |
|---|---|---|---|---|---|
| `portpilot-mr1` | MR1 — Valider les ports et verrouiller la fusion | `feat/validation` | 80 | T1, T2, T3, T4, T5 | — |
| `portpilot-mr2` | MR2 — Connecter une socket locale | `feat/connexion` | 70 | T6 | — |
| `portpilot-mr3` | MR3 — Scanner, résumer et livrer | `feat/scan-bilan` | 80 | T7, T8 | — |

**Compétences Git travaillées** (repérées dans le texte du parcours) : merge request, pipeline / CI, .gitignore, branche par git switch -c.

**Lien avec le projet final** : Premier module **réseau** du futur framework : validation d’une liste de ports et connexion TCP limitée à `127.0.0.1`. Ce code est repris, adapté, dans le module réseau de ReconWrap.

**Limites déclarées dans le JSON**

- Le scan ne vise que 127.0.0.1, de façon séquentielle, avec 1 à 10 ports et 0,5 seconde par connexion.
- Un état OUVERT ne prouve ni vulnérabilité ni nature du service ; aucune donnée applicative n’est envoyée.
- T8 teste le comptage d’états fabriqués ; les états REFUSE, TIMEOUT et ERREUR ne sont pas provoqués par la suite minimale.
- Une CI bloquante exige runner, droits et règles GitLab accessibles dans l’instance de l’école.

### HeaderScope (`headerscope`)

- **Sous-titre** : Client HTTP local et contrôle de trois en-têtes
- **Niveau** : Débutant · **Durée** : 5 h · **Ressource** : `/content/headerscope.md`

**Objectifs**

- Comparer les noms et valeurs d’en-têtes selon un contrat explicite.
- Écrire au moins six cas de test autonomes sans réseau.
- Traiter séparément réponses HTTP, panne de connexion et timeout.
- Distinguer la CI reproductible de la démonstration avec le laboratoire local démarré explicitement.

**Missions**

| Mission (id) | Titre | Branche | Min | Tests (ids) | Démonstrations (ids) |
|---|---|---|---|---|---|
| `headerscope-mr1` | MR1 — Règles pures et tests | `feat/regles-entetes` | 85 | H1, H2, H3, H4, H5, H6, H7 | — |
| `headerscope-mr2` | MR2 — Client HTTP et erreurs distinctes | `feat/client-http` | 85 | H8, H9 | — |
| `headerscope-mr3` | MR3 — Orchestration, bilan et README | `feat/bilan` | 80 | — | D1, D2, D3 |

**Compétences Git travaillées** (repérées dans le texte du parcours) : pipeline / CI, branche par git switch -c.

**Lien avec le projet final** : Premier module **web** du futur framework : règles pures sur des en-têtes HTTP et client limité au labo. Ce code est repris, adapté, dans le module web de ReconWrap.

**Limites déclarées dans le JSON**

- Le client ne contacte que le laboratoire local et les quatre chemins définis.
- La CI ne suppose pas que le laboratoire du portail est accessible au runner scolaire ; les tests de classement n’attestent pas le client réseau réel.
- Les en-têtes sont des contrôles ciblés ; ils ne prouvent pas à eux seuls la sécurité complète d’une application.

### FileGuard (`fileguard`)

- **Sous-titre** : Manifeste SHA-256 et comparaison contrôlée
- **Niveau** : Débutant · **Durée** : 5 h · **Ressource** : `/content/fileguard.md`

**Objectifs**

- Calculer des empreintes SHA-256 sur les octets d’un fichier.
- Écrire un manifeste déterministe pour les fichiers réguliers du premier niveau.
- Comparer deux inventaires en quatre catégories.
- Tester avec des fichiers temporaires et trois MR dont la CI ne dépend pas du portail.

**Missions**

| Mission (id) | Titre | Branche | Min | Tests (ids) | Démonstrations (ids) |
|---|---|---|---|---|---|
| `fileguard-mr1` | MR1 — Empreinte de fichier | `feat/empreinte` | 85 | F1, F2, F3 | — |
| `fileguard-mr2` | MR2 — Manifeste déterministe | `feat/manifest` | 85 | F4, F5, F6, F7 | — |
| `fileguard-mr3` | MR3 — Comparaison et bilan | `feat/comparaison` | 80 | F8, F9, F10, F11, F12, F13, F14 | — |

**Compétences Git travaillées** (repérées dans le texte du parcours) : pipeline / CI, branche par git switch -c.

**Lien avec le projet final** : Pas un module du framework lui-même. Il entraîne au hachage, au JSON déterministe et à la comparaison d’inventaires, utiles pour des rapports et des contrôles de changements. Son périmètre est volontairement petit.

**Limites déclarées dans le JSON**

- Le manifeste est une référence de comparaison, pas une preuve d’authenticité ; protège sa provenance.
- Aucun antivirus, détection de malware, recherche de secrets ou analyse récursive.
- Les symlinks sont refusés et seuls les fichiers réguliers du premier niveau sont inclus.

### ToolWrap — piloter un outil externe (`toolwrap`)

- **Sous-titre** : Wrapper subprocess, CLI argparse et lecture de sorties XML et JSON
- **Niveau** : Débutant · **Durée** : 5 h · **Ressource** : `/content/toolwrap.md`

**Objectifs**

- Lancer un outil externe avec subprocess.run et une liste d’arguments, sans shell dès qu’une entrée utilisateur est en jeu.
- Normaliser le résultat d’un outil (code de retour, sorties, erreur) dans un dictionnaire unique, même en cas d’échec.
- Construire une CLI argparse avec sous-commandes, codes de sortie et liste blanche de cibles limitée au laboratoire.
- Analyser une sortie XML (nmap) et une sortie JSON (adsim), puis produire un rapport texte à partir de données communes.
- Pratiquer Git sur de petites branches : revue de diff, conflit de fusion résolu, rebase.

**Missions**

| Mission (id) | Titre | Branche | Min | Tests (ids) | Démonstrations (ids) |
|---|---|---|---|---|---|
| `toolwrap-mr1` | MR1 — Lancer un outil proprement (subprocess) | `feat/subprocess` | 100 | W1, W2, W3, W4, W5 | — |
| `toolwrap-mr2` | MR2 — CLI, périmètre et Git sous contrôle | `feat/cli-perimetre` | 100 | W6, W7, W8, W9, W10 | — |
| `toolwrap-mr3` | MR3 — Lire les sorties nmap et adsim, rapport et bilan | `feat/parsing` | 70 | W11, W12, W13, W14, W15, W16 | D1, D2, D3 |

**Compétences Git travaillées** (repérées dans le texte du parcours) : pipeline / CI, conflit de fusion, rebase, .gitignore, revue de diff, git log, branche par git switch -c.

**Lien avec le projet final** : Cœur du framework : lancer un outil externe (`subprocess`, sans `shell=True`), lire ses sorties (XML nmap, JSON adsim) et produire un format commun. Le simulateur adsim reste fictif : le vrai Active Directory se pratique dans le projet final.

**Limites déclarées dans le JSON**

- adsim est un simulateur FICTIF (domaine LAB.LOCAL) : il ne se connecte à aucun annuaire réel. Le vrai Active Directory sera traité dans le projet final, sur un domaine qui t’appartient.
- La cible reste 127.0.0.1 ; la liste blanche ne doit pas être élargie pendant ce parcours.
- Les tests mockent subprocess.run : ils prouvent la logique du wrapper, pas le comportement réel de nmap ou d’adsim. Ce rôle revient aux démonstrations.
- nmap n’est pas disponible sur un runner GitLab : les tests obligatoires ne l’appellent jamais.
- Un état open ne prouve ni la nature du service ni une vulnérabilité ; une sortie fictive ne prouve rien sur un vrai domaine.

### ReconWrap — assembler un mini-framework (`reconwrap`)

- **Sous-titre** : Parcours de synthèse : modules réseau, web et Active Directory, CLI et rapports
- **Niveau** : Débutant · **Durée** : 5 h · **Ressource** : `/content/reconwrap.md`

**Objectifs**

- Concevoir un contrat commun : chaque module reçoit une cible validée et retourne un résultat normalisé.
- Brancher des modules existants sans les copier à l’aveugle, et isoler l’échec d’un module pour que les autres continuent.
- Produire une CLI argparse et des rapports JSON et Markdown dont les tests sont déterministes.
- Livrer un projet documenté, taggé en v0.1.0, avec des tests unittest qui tournent sans labo ni nmap.

**Missions**

| Mission (id) | Titre | Branche | Min | Tests (ids) | Démonstrations (ids) |
|---|---|---|---|---|---|
| `reconwrap-mr1` | MR1 — Architecture, contrat et registre | `feat/architecture` | 100 | R1, R2, R3, R4, R5 | — |
| `reconwrap-mr2` | MR2 — Modules, CLI et rapports | `feat/orchestration-rapport` | 100 | R6, R7, R8, R9, R10, R11, R12, R13, R14 | D1, D2, D3, D4, D5, D6 |
| `reconwrap-mr3` | MR3 — Documentation, qualité et release v0.1.0 | `feat/doc-qualite` | 70 | R15, R16, R17 | — |

**Compétences Git travaillées** (repérées dans le texte du parcours) : merge request, pipeline / CI, conflit de fusion, tag, revert, stash, restore, .gitignore, revue de diff, branche par git switch -c.

**Lien avec le projet final** : Synthèse : contrat commun des modules réseau, web et Active Directory, registre, CLI argparse, rapports JSON et Markdown, packaging, CI et tag v0.1.0. C’est la maquette du projet final.

**Limites déclarées dans le JSON**

- Périmètre loopback : 127.0.0.1 seulement. Pas de scan de plage, pas de cible distante, pas d’exploitation.
- Les tests de CI s’appuient sur des fixtures : ils valident la logique, pas le comportement sur un vrai réseau. Les démonstrations exigent le labo démarré.
- adsim est un simulateur fictif (domaine LAB.LOCAL) : le module AD n’est pas testé contre un annuaire réel dans ce parcours.
- Un framework d’outils de sécurité ne vaut pas audit. Tout usage hors d’un cadre autorisé par écrit est interdit et engage ta responsabilité légale.

## Chemin conseillé

Suivre l’ordre du tableau : `socle` → `portpilot` → `headerscope` → `fileguard` → `toolwrap` → `reconwrap`. `reconwrap` assemble des éléments de `portpilot`, `headerscope` et `toolwrap` : ne pas le commencer avant eux.

