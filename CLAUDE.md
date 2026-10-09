# CLAUDE.md — Cyber Atelier (mémoire de passation)

Ce fichier permet à une nouvelle conversation ou à une autre IA de reprendre le projet en quelques minutes. Les affirmations ont été vérifiées dans le code à la date de rédaction. Si le code change, mets ce fichier à jour.

## 1. Résumé du projet

Cyber Atelier est une application web locale, lancée avec Docker, pour un débutant en Python. Elle propose 15 h de pratique en 3 parcours de 5 h (300 min chacun), eux-mêmes découpés en 3 merge requests (MR) :
- **PortPilot** : scanner TCP limité à 127.0.0.1.
- **HeaderScope** : client HTTP limité au labo local, qui vérifie trois en-têtes de sécurité.
- **FileGuard** : manifeste SHA-256 et comparaison inchangé / modifié / supprimé / ajouté.

L'application fournit consignes, éditeur, console et laboratoire HTTP. Elle ne fournit **ni solutions Python ni `.gitlab-ci.yml` corrigés**. Stack : Python 3 bibliothèque standard uniquement, HTML/CSS/JS natifs sans build ni CDN, stockage JSON et dossiers.

## 2. Carte des fichiers (qui fait quoi)

### Racine
- `README.md` : documentation destinée à l'apprenant (démarrage, console, Git interactif, arrêt, mise à jour, sauvegarde, tests d'infrastructure).
- `Dockerfile` : image `python:3.12-slim`, installe git, bash, openssh-client ; utilisateur `atelier` (UID 10001) ; code copié dans `/app` puis rendu en lecture seule (dossiers 0555, fichiers 0444) ; `CMD python server.py` ; HEALTHCHECK sur `/api/health`.
- `compose.yaml` : service `atelier`, port publié `127.0.0.1:${ATELIER_PORT:-8080}:8080`, volumes nommés `workspaces`, `data`, `home` ; `read_only: true`, `/tmp` en tmpfs 64 Mo `noexec`, `cap_drop: ALL`, `no-new-privileges`, `restart: unless-stopped`.
- `.dockerignore` : exclut `.git`, caches Python, `backups/`, `userdata/`, `workspaces/`, `data/`. Il cite aussi `CONTRACT.md`, `tests/QA_PLAN.md`, `tests/browser_checks.py` et `.gitignore`, qui n'existent pas (inoffensif, à nettoyer).
- `server.py` : serveur `ThreadingHTTPServer` (453 lignes). Constantes : `COURSES`, `MAX_FILE` et `MAX_STATE` = 1 Mio, `MAX_RUN_OUTPUT` = 64 Kio, `MAX_ZIP` = 20 Mio, `MAX_FILES` = 2000.
  - `_state_normalize` : valide la progression (version 1).
  - `AtelierServer.__init__` : crée `workspaces/<parcours>` et `data`, démarre le labo (échec ignoré) ; `server_close` arrête le labo.
  - `RequestHandler._check_local` : contrôle Host et Origin (localhost, 127.0.0.1, ::1 uniquement).
  - `_relative_path` et `_safe_target` : refusent chemins absolus, `..`, `\`, exclusions et liens symboliques.
  - `_dispatch` : convertit les exceptions en 400, 403, 404, 409, 413 ou 500.
  - `_api` : routes ; `_run` : `bash -lc` dans le cwd, groupe de processus tué, délai max 30 s, une seule exécution à la fois (`run_lock`), sortie bornée ; `_workspace_zip` : exclut `.git`, `.venv`, `__pycache__`, symlinks.
  - `_static` : sert `web/`, `web/downloads/`, `content/courses.json` et `content/*.md`.
  - `_atomic_write` : fichier temporaire puis `os.replace` ; `createOnly` passe par `os.link` (atomique).
  - `create_server` : lit `ATELIER_HOST`, `ATELIER_PORT`, `WORKSPACES_DIR`, `DATA_DIR`, `LAB_PORT`.
- `labs.py` (102 lignes) : `LabManager` (`start`, `stop`, `status`, idempotents, liaison loopback obligatoire) et le serveur de démonstration. Routes : `/` (aide), `/fragile` (200 sans en-têtes), `/durci` (200 avec CSP, nosniff et X-Frame-Options DENY), `/absent` (404), `/erreur` (500). Port 8000 par défaut.

### Interface (`web/`)
- `web/index.html` : barre latérale (navigation des parcours, progression, bouton « Progression & sauvegarde »), vues `dashboard`, `course`, `coder`, `gitlab`, et `<dialog id="settings-dialog">` (export/import JSON, export ZIP). Le bouton `#settings-open-mobile` n'apparaît que sous 760 px (classe `mobile-only`).
- `web/app.js` (112 lignes, style compact, une IIFE). Fonctions clés :
  - `request` / `jsonPost` : appels `fetch`.
  - `saveState`, `scheduleSave` (délai 450 ms, révisions), `flushState` (`fetch keepalive` sur `pagehide`).
  - `normalizeProgression` : validation de l'import JSON.
  - `renderProgress`, `renderCourse`, `renderMissions`, `makeMission` (cases, liens MR, tests puis démonstrations séparés), `renderSetup` (bouton « Préparer dans la console »), `renderNotes`.
  - `renderCoder`, `openCoder`, `loadFiles`, `loadFile`, `saveFile`.
  - `runCommand` : enregistre le brouillon avant exécution, affiche le code de sortie. `runCurrentFile` : lance `python -- <fichier>`. `validCwd` : cwd relatif simple.
  - `toggleLab`, `downloadZip`, `renderGuide` (guide GitLab et environnement), `openSettings`, `canLeave` (confirmation avant abandon de modifications), `safeUrl`, `init`.
- `web/styles.css` : 7 lignes très longues (fichier minifié). Variables sur `:root`, points de rupture 1050, 760, 520 et 440 px, règles d'impression. Pas de mode sombre (`color-scheme: light`).
- `web/downloads/PortPilot.pdf` : énoncé complet PortPilot (généré avec ReportLab, source absente). Texte extrait avec `pypdf` (12 pages) : il **vouvoie** l'apprenant, propose `git clone <URL>` sans le point final, et une démonstration avec `python -m http.server 8000` alors que le labo occupe déjà 8000 dans Cyber Atelier (l'UI et `portpilot.md` le précisent). Contrats et tests T1–T8 cohérents avec le JSON.

### Contenu (`content/`)
- `content/courses.json` (indent 2, `ensure_ascii=False`, saut de ligne final) : clés racine `version`, `title`, `totalMinutes` (900), `description`, `courses` (3), `gitlabGuide` (7 sections), `environmentGuide` (4 sections). Chaque parcours contient `id`, `title`, `durationMinutes` (300), `goals`, `prerequisites`, `scope`, `concepts`, `files`, `setup` (`label`, `command`, `note`, `interactive`), `steps` (3), `timeline` (somme 300), `references`, `resources`, `completion`, `limits`.
  - Une mission (`steps`) a : `id`, `title`, `branch`, `minutes`, `mission`, `tasks`, `tests` (`id`, `title`, `input`, `expected`), `acceptance`, `hint`. Seule la MR3 de HeaderScope a aussi `demos` (D1 à D3).
  - Identifiants de mission : `portpilot-mr1..3`, `headerscope-mr1..3`, `fileguard-mr1..3`. **Ne jamais les renommer** : ils sont stockés dans la progression.
  - Tests automatisés : PortPilot T1–T8, HeaderScope H1–H9, FileGuard F1–F14.
- `content/portpilot.md`, `content/headerscope.md`, `content/fileguard.md` : énoncés Markdown, téléchargeables depuis l'UI.

### Fixtures et tests
- `fixtures/integrity/` : `README.txt`, `message.txt`, `settings.ini`, fictifs, sans manifeste de référence. Dans le conteneur, ils sont dans `/app/fixtures/integrity` (lecture seule) ; l'apprenant les copie avec la commande de la section FileGuard.
- `tests/test_server.py` (8 tests), `tests/test_labs.py` (5 tests), `tests/test_content.py` (7 tests, **non suivi par git**).

## 3. Lancer, tester, mettre à jour, sauvegarder

- **Lancer ou mettre à jour** : `docker compose up --build -d`, puis ouvrir http://127.0.0.1:8080. Les volumes sont conservés.
- **Statut** : `docker compose ps`.
- **Tests de Cyber Atelier** (pas ceux de l'apprenant) : `docker compose exec -T atelier python -m unittest discover -s tests -p 'test_*.py' -v`. Il y a 20 méthodes de test (8 + 5 + 7) ; dernier passage dans Docker : 20/20 OK (13 d'origine + 7 de `test_content.py`).
- **Limite des tests** : dans `test_server.py`, `process_is_running` lit `/proc`. Sans `/proc` (macOS natif), elle renvoie `False` et les tests de mort de processus passent sans rien prouver. Ils ne sont probants que dans Linux/Docker.
- **Shell interactif** (Git, SSH, `git clone`) : `docker compose exec atelier bash`.
- **Arrêter sans perdre les données** : `docker compose stop`, puis `docker compose start`. `docker compose down` supprime les conteneurs mais garde les volumes.
- **Sauvegarder** : `docker compose exec -T atelier tar -czf - -C / workspaces data > backups/...tar.gz`. Le volume `home` est volontairement exclu (clé SSH privée possible).
- **Interdit** : `docker compose down -v` et toute suppression de volumes. Elles effacent le code et la progression de l'apprenant.

## 4. API et formats de données

Routes (serveur sur `0.0.0.0:8080` dans le conteneur, publié sur `127.0.0.1` uniquement) :
- `GET /api/health` : statut, version de Python, version de Git, état du labo.
- `GET /api/state` et `POST /api/state` : progression. Le POST renvoie la progression normalisée.
- `GET /api/files?course=` : liste `{path, size}` (2000 fichiers max).
- `GET /api/file?course=&path=` et `POST /api/file` : lecture et écriture (`course`, `path`, `content`, `createOnly` optionnel).
- `POST /api/run` : `{course, command, cwd?, timeout?}` ; réponse `exitCode`, `stdout`, `duration`, `timedOut`, `truncated`, `cwd`. Erreur 409 si une commande tourne déjà.
- `GET /api/lab` et `POST /api/lab` (`{"running": bool}`).
- `GET /api/workspace.zip?course=` : export ZIP.

Codes d'erreur : 400 (requête ou chemin invalide), 403 (Host ou Origin non local), 404, 409 (fichier existant avec `createOnly`, ou commande déjà en cours), 413 (trop volumineux), 500 (erreur interne).

Progression (`/data/state.json`, version 1) : `{"version":1, "selectedCourse", "completed": [ids de missions], "notes": {parcours: texte}, "mrLinks": {id de mission: URL}}`.
- Le serveur valide le format, la taille et la liste des parcours, mais pas l'appartenance des identifiants de mission. Le client (`normalizeProgression`) filtre ces identifiants.

## 5. Règles pédagogiques et produit (non négociables)

- **Langue** : interface et documentation en français, avec tutoiement. L'apprenant connaît les variables, les listes et les fonctions.
- **Pas de solutions** d'exercices sans demande explicite. Les améliorations d'infrastructure (serveur, interface, tests de Cyber Atelier) peuvent contenir du code complet.
- **Ne jamais confondre** quatre niveaux : tests locaux, pipeline GitLab réellement exécuté, autorisation effective de fusion, case cochée dans Cyber Atelier (déclarative, sans vérification).
- **Runner GitLab** : sur le runner, `127.0.0.1` désigne le runner, pas le conteneur. Les tests obligatoires (`verification.py`, CI) ne doivent donc jamais dépendre du labo.
- **Démonstrations séparées** : les vérifications qui exigent le labo sont dans le champ `demos` (ids D1 à D3 pour HeaderScope MR3), affichées à part et hors CI.
- **Cohérence** : `content/courses.json`, `content/*.md`, `web/downloads/PortPilot.pdf` et l'interface doivent rester alignés. Un changement de contenu se répercute dans les trois.
- **Durée** : 15 h = 3 × 300 min. `tests/test_content.py` le vérifie.
- **Dépendances** : bibliothèque standard uniquement, sans framework ni dépendance sans bénéfice concret.
- **Réseau** : ne pas exposer le service au réseau, ne pas élargir les exercices à des cibles externes. Le labo et les exercices restent sur 127.0.0.1.
- **Git de travail** : une branche dédiée, modifications limitées et faciles à intégrer (une autre IA peut travailler en parallèle).

## 6. Conventions de code

- **Python** : bibliothèque standard uniquement (`server.py` utilise `from __future__ import annotations`). Erreurs de validation en `ValueError` (message en français), mappées en codes HTTP dans `_dispatch`.
- **Sécurité des chemins** : toujours passer par `_relative_path` et `_safe_target`. Ne jamais construire un chemin à partir d'une entrée brute.
- **JavaScript** : style compact, une IIFE, `'use strict'`, pas de build. Les textes sont insérés avec `textContent` (`element`, `button`), jamais en HTML brut. Les liens passent par `safeUrl` (http/https seulement).
- **CSS** : variables sur `:root`, pas de framework. Les nouveaux éléments suivent le même style (petites tailles de police, 11 px minimum).
- **Accessibilité** : `aria-current` sur la navigation, focus sur le titre lors d'un changement de vue, `role="status"` ou `alert` pour les messages.
- **Tests** : `unittest` ; nouveaux tests dans `tests/`, en utilisant des répertoires temporaires.

## 7. État actuel de la branche et vérifications

Dépôt git local : `main` = commit `6734f3f` (« Import initial de l'archive Cyber Atelier »). Branche courante : **`amelioration/fiabilite-parcours`**, sans commit.

Fichiers modifiés (`git diff --stat main` : 7 fichiers, 135 insertions, 42 suppressions) : `README.md`, `content/courses.json`, `content/fileguard.md`, `content/headerscope.md`, `web/app.js`, `web/index.html`, `web/styles.css`. Fichier non suivi : `tests/test_content.py`.

Contenu des changements (d'après la passation et le diff) :
- **Interface** : enregistrement du fichier ouvert avant toute commande ; console conservée par parcours ; code de sortie annoncé ; `fetch keepalive` au `pagehide` ; avertissement de fermeture si la sauvegarde a échoué ; tests automatisés et démonstrations affichés séparément ; bouton « Préparer dans la console » (remplit sans exécuter) ; bouton ⚙ mobile.
- **Contenu** : identité Git dans les 3 parcours ; clone marqué `interactive` ; PortPilot : création de branche séparée de `git status` ; FileGuard : copie des fixtures avec `chmod u+w` ; HeaderScope MR3 : anciens H11 à H13 devenus D1 à D3 ; guide GitLab (« Quatre résultats à ne pas confondre », premier clone, 127.0.0.1 sur le runner).
- **Tests** : `tests/test_content.py` (ids stables, 900/300 min, ids de cas uniques, aucun test automatisé dépendant du labo, liens locaux existants, fixtures présentes).

Vérifications effectuées : 20/20 tests OK dans Docker ; parcours navigateur : sauvegarde avant exécution, console conservée, fixtures copiées et modifiables, démos D1 à D3, note sauvegardée malgré un rechargement immédiat, bouton mobile, pas de défilement horizontal à 375 px.

## 8. À faire et limites

### Pistes non réalisées
- Script de recette navigateur reproductible (aucun test navigateur automatisé dans le dépôt).
- Empêcher deux exécutions simultanées côté interface : désactiver les boutons pendant `/api/run`.
- Renommer ou supprimer un fichier depuis l'interface.
- Mémoriser le dossier de travail (cwd) par parcours : `state.cwdByCourse` existe en mémoire seulement, il est perdu au rechargement.
- Afficher une aide claire dans la console en cas d'échec d'une commande interactive (clone SSH).
- Régénérer le PDF en tutoiement si la source est retrouvée.
- Publier un patch (`git diff main > cyberatelier.patch`) ou une archive à chaque livraison.

### Limites connues
- Le PDF PortPilot : vouvoiement et suggestion de `python -m http.server 8000`, alors que le labo occupe déjà le port 8000. Non modifié (source ReportLab absente).
- `web/index.html` contient des valeurs d'attente « 0 / 9 MR » et « 9 missions » : elles sont remplacées par `renderProgress` au démarrage.
- Le tableau de bord affiche « 15 h » en dur dans `renderProgress` (constante produit, acceptable).
- `flushState` utilise `fetch keepalive`, limité à 64 Ko : une progression plus grosse n'est pas sauvegardée à la fermeture.
- `.dockerignore` cite des fichiers absents (voir section 2).
- Le bouton « Lancer les tests » lance `python verification.py` dans le cwd courant : il exécute le code de l'apprenant, pas les tests de Cyber Atelier.
- Pas de mode sombre dans l'interface.

## 9. Objectif réel de l'apprenant et décision en attente

L'utilisateur veut monter en compétence en Python et Git pour **écrire un wrapper de pentest en Python** dans le cadre d'un projet. Analyse faite le 2026-10-10 : le programme actuel donne de bonnes bases (séparation règles pures / I/O dans HeaderScope, validation et exceptions dans PortPilot, JSON dans FileGuard, cycle MR + CI), mais ne couvre pas ce qu'exige un wrapper, et l'interdit même parfois :
- `subprocess` (lancer un outil, timeout, code de retour, **jamais `shell=True` avec une entrée**) : absent ;
- `argparse` : interdit par les énoncés ; rapports écrits sur disque : interdits (PortPilot) ;
- lecture de sorties d'outils (XML nmap via `xml.etree`, JSON) : absente ;
- packaging, `venv`, `pip`, plusieurs modules : interdits ;
- `unittest`/`pytest` et mock de `subprocess` : remplacés par un `verification.py` maison, mocks interdits ;
- liste blanche de cibles (`ipaddress`) : absente ;
- Git réel : conflit de fusion, `rebase`, `revert` : absents. La preuve « pipeline rouge bloque la fusion » est répétée dans les 9 MR (trop lourd).

Proposition faite (**non encore validée par l'utilisateur, rien d'implémenté**) :
1. Alléger les parcours existants : preuve du rouge bloquant seulement dans PortPilot MR1, passage à `unittest`, un conflit de fusion provoqué.
2. Ajouter un parcours de synthèse « ReconWrap » (5 h, 3 MR, programme porté à 20 h) : MR1 CLI `argparse` + périmètre `ipaddress` + `subprocess.run` en liste avec timeout, tests avec mock ; MR2 nmap installé dans le conteneur, ciblant uniquement le labo, lecture du XML, tests sur fixtures XML sans réseau ; MR3 orchestration de nmap + modules PortPilot/HeaderScope de l'apprenant, rapport JSON/Markdown, `logging`, package, `venv`, CI tests + linter.

Questions posées à l'utilisateur, en attente de réponse : quels outils son wrapper doit piloter (nmap, ffuf/gobuster, nuclei…) ; ajouter un 4ᵉ parcours (20 h) ou remplacer FileGuard (rester à 15 h). Les solutions des exercices ne doivent toujours pas être fournies.
