# CLAUDE.md — Cyber Atelier (mémoire de passation)

Ce fichier permet à une nouvelle conversation ou à une autre IA de reprendre le projet en quelques minutes. Les affirmations ont été vérifiées dans le code à la date de rédaction (2026-10-10). Si le code change, mets ce fichier à jour.

## 1. Résumé du projet

Cyber Atelier est une application web locale, lancée avec Docker, pour un débutant en Python qui doit monter vite en compétence en Python et Git. Elle propose **30 h de pratique en 6 parcours de 5 h (300 min chacun)**, eux-mêmes découpés en **3 merge requests (MR) chacun, soit 18 missions**. Ordre imposé dans l'interface et dans les tests : `socle` > `portpilot` > `headerscope` > `fileguard` > `toolwrap` > `reconwrap`.

- **Socle Python & Git** (`socle`) : fonctions pures, tests unittest, lecture de fichiers et JSON, Git en équipe (conflit, rebase, tag). Journal fictif `auth.log`.
- **PortPilot** (`portpilot`) : scanner TCP limité à 127.0.0.1, validation de ports, CI.
- **HeaderScope** (`headerscope`) : client HTTP limité au labo local, qui vérifie trois en-têtes de sécurité.
- **FileGuard** (`fileguard`) : manifeste SHA-256 et comparaison inchangé / modifié / supprimé / ajouté.
- **ToolWrap** (`toolwrap`) : lancer un outil externe avec `subprocess`, CLI `argparse`, liste blanche de cibles, lecture des sorties XML (nmap) et JSON (adsim).
- **ReconWrap** (`reconwrap`) : parcours de synthèse, assemblage d'un mini-framework (contrat de module, registre, modules réseau / web / Active Directory, CLI, rapports JSON et Markdown, tag v0.1.0).

Contexte de l'apprenant : il veut écrire ensuite, dans un cadre scolaire autorisé, un framework de pentest modulaire (réseau, web, Active Directory). Le lab est une maquette réduite de ce projet. Le vrai Active Directory n'est pas dans le lab : il se pratiquera dans le projet final, sur un domaine personnel.

L'application fournit consignes, éditeur, console, laboratoire HTTP et outils fournis (nmap, adsim fictif, fixtures). Elle ne fournit **ni solutions Python ni `.gitlab-ci.yml` corrigés**. Stack : Python 3 bibliothèque standard uniquement, HTML/CSS/JS natifs sans build ni CDN, stockage JSON et dossiers.

## 2. Carte des fichiers (qui fait quoi)

### Racine
- `README.md` : documentation destinée à l'apprenant (démarrage, parcours, outils fournis et leurs limites, console, Git interactif, arrêt, mise à jour, sauvegarde, tests d'infrastructure).
- `Dockerfile` : image `python:3.12-slim`, installe `git`, `bash`, `openssh-client`, `ca-certificates` et **`nmap`** (paquet Debian) ; utilisateur `atelier` (UID 10001) ; code copié dans `/app` puis rendu en lecture seule (dossiers 0555, fichiers 0444) ; `CMD python server.py` ; HEALTHCHECK sur `/api/health`.
- `compose.yaml` : service `atelier`, port publié `127.0.0.1:${ATELIER_PORT:-8080}:8080`, volumes nommés `workspaces`, `data`, `home` ; `read_only: true`, `/tmp` en tmpfs 64 Mo `noexec`, `cap_drop: ALL`, `no-new-privileges`, `restart: unless-stopped`.
- `.dockerignore` : exclut `.git`, caches Python, `backups/`, `userdata/`, `workspaces/`, `data/` et **`drafts/`** (ébauches non livrées dans l'image). Il cite aussi `.gitignore`, `CONTRACT.md`, `tests/QA_PLAN.md` et `tests/browser_checks.py`, qui n'existent pas (inoffensif, à nettoyer). Le motif `*.log` ne devrait viser que la racine (sémantique Docker, à confirmer par un build) : `fixtures/socle/auth.log` ne devrait donc pas être exclu de l'image.
- `.gitignore` (non commité, créé à 01:03) : `workspaces/`, `backups/`, `.env`, caches Python, `.venv/`, `.DS_Store`. Les projets d'exercice ont leur propre dépôt Git dans `workspaces/`.
- `compose.override.yaml` (non commité, créé à 01:03) : mode « je code dans VS Code ». Compose le charge automatiquement : le dossier `./workspaces` de l'hôte remplace le volume nommé `workspaces` (`./workspaces:/workspaces`). Pour revenir au volume nommé, retirer ce fichier ; le volume existant n'est pas supprimé.
- `server.py` (453 lignes) : serveur `ThreadingHTTPServer`. Constantes : `COURSES` (les 6 ids), `MAX_FILE` et `MAX_STATE` = 1 Mio, `MAX_RUN_OUTPUT` = 64 Kio, `MAX_ZIP` = 20 Mio, `MAX_FILES` = 2000, `DEFAULT_STATE` (`selectedCourse` = `socle`).
  - `_state_normalize` : valide la progression (version 1).
  - `AtelierServer.__init__` : crée `workspaces/<parcours>` et `data`, démarre le labo (échec ignoré) ; `server_close` arrête le labo.
  - `RequestHandler._check_local` : contrôle Host et Origin (localhost, 127.0.0.1, ::1 uniquement).
  - `_relative_path` et `_safe_target` : refusent chemins absolus, `..`, `\`, exclusions et liens symboliques.
  - `_dispatch` : convertit les exceptions en 400, 403, 404, 409, 413 ou 500.
  - `_api` : routes ; `_run` : `bash -lc` dans le cwd, groupe de processus tué, délai max 30 s, une seule exécution à la fois (`run_lock`), sortie bornée ; `_workspace_zip` : exclut `.git`, `.venv`, `__pycache__`, symlinks.
  - `_static` : sert `web/`, `web/downloads/`, `content/courses.json` et `content/*.md`.
  - `_atomic_write` : fichier temporaire puis `os.replace` ; `createOnly` passe par `os.link` (atomique).
  - `create_server` : lit `ATELIER_HOST`, `ATELIER_PORT`, `WORKSPACES_DIR`, `DATA_DIR`, `LAB_PORT`.
- `labs.py` (119 lignes) : `LabManager` (`start`, `stop`, `status`, idempotents, liaison loopback obligatoire) et le serveur de démonstration. Routes : `/` (aide), `/fragile` (200 sans en-têtes), `/durci` (200 avec CSP, nosniff et X-Frame-Options DENY), `/absent` (404), `/erreur` (500). Port 8000 par défaut. Lancement direct sur le Mac, hors Docker : `python3 labs.py` (labo sur `127.0.0.1:8000`, arrêt avec Ctrl+C). Bloc `__main__` non commité (section 8).

### Interface (`web/`)
- `web/index.html` : barre latérale (navigation des parcours, progression, bouton « Progression & sauvegarde »), vues `dashboard`, `course`, `coder`, `gitlab`, et `<dialog id="settings-dialog">` (export/import JSON, export ZIP). Le bouton `#settings-open-mobile` n'apparaît que sous 760 px (classe `mobile-only`). Textes d'accueil **en dur** : `#side-info` (« 30 h · 6 parcours · 18 missions ») et le paragraphe d'accueil (« Six parcours, dix-huit missions »), à mettre à jour si le programme change.
- `web/app.js` (113 lignes, style compact, une IIFE). Constante `ids` (les 6 parcours, dans l'ordre), `state.courseId` = `socle`. Fonctions clés :
  - `request` / `jsonPost` : appels `fetch`.
  - `saveState`, `scheduleSave` (délai 450 ms, révisions), `flushState` (`fetch keepalive` sur `pagehide`), `state.saveError` (avertissement de fermeture si la sauvegarde a échoué, via `beforeunload`).
  - `normalizeProgression` : validation de l'import JSON ; filtre les ids de mission inconnus.
  - `renderProgress` (total d'heures calculé par `courseTotalMinutes()`, nombre de MR calculé), `renderCourse`, `renderMissions`, `makeMission` (cases, liens MR, tests puis démonstrations séparés), `renderSetup` (bouton « Préparer dans la console »), `renderNotes`.
  - `focusView` : focus sur le titre lors d'un changement de vue ; `aria-current` sur la navigation.
  - `renderCoder`, `openCoder`, `loadFiles`, `loadFile`, `saveFile`.
  - `runCommand` : **enregistre le brouillon avant exécution** si l'éditeur est modifié, puis affiche la sortie et le code de sortie. La console est conservée par parcours (`consoleByCourse`). `runCurrentFile` : lance `python -- <fichier>`. `validCwd` : cwd relatif simple.
  - `toggleLab`, `downloadZip`, `renderGuide` (guide GitLab et environnement), `openSettings`, `canLeave` (confirmation avant abandon de modifications), `safeUrl`, `init`.
- `web/styles.css` : fichier minifié (peu de lignes très longues). Variables sur `:root`, points de rupture 1050, 760, 520 et 440 px, règles d'impression. Tailles de police d'au moins 11 px. Pas de mode sombre (aucun `prefers-color-scheme`, aucun `color-scheme`).
- `web/downloads/PortPilot.pdf` : énoncé complet PortPilot (généré avec ReportLab, source absente). Texte extrait avec `pypdf` (12 pages) : il **vouvoie** l'apprenant, propose `git clone <URL>` sans le point final, et une démonstration avec `python -m http.server 8000` alors que le labo occupe déjà 8000 dans Cyber Atelier (l'UI et `portpilot.md` le précisent). Non modifié (source absente). Aucun PDF pour les autres parcours.

### Outils fournis (`tools/`, lecture seule dans l'image sous `/app/tools/`)
- `tools/adsim.py` (193 lignes) : simulateur **FICTIF** d'un outil Active Directory, domaine `LAB.LOCAL`. Bibliothèque standard uniquement, aucun import réseau (un test le vérifie). Lit `fixtures/adsim/domain.json` relatif au script. Voir `docs/OUTILS.md`.
- nmap : outil réel, installé par le Dockerfile, utilisé seulement en démonstration sur `127.0.0.1:8000`. Aucun test obligatoire ne l'appelle.

### Contenu (`content/`)
- `content/courses.json` (indent 2, `ensure_ascii=False`, saut de ligne final) : clés racine `version` (1), `title`, `totalMinutes` (1800), `description`, `courses` (6), `gitlabGuide` (liste de 7 sections), `environmentGuide` (liste de 4 sections). Chaque parcours contient `id`, `title`, `subtitle`, `description`, `level`, `color`, `durationMinutes` (300), `goals`, `prerequisites`, `scope`, `concepts`, `files`, `setup` (`label`, `command`, `note`, `interactive` optionnel), `steps` (3), `timeline` (somme 300), `references`, `resources`, `completion`, `limits`.
  - **Format en paliers (les 18 missions)** : chaque mission a `paliers` (8 à 11 par mission, 153 au total) à la place de `tasks`/`hint`. Un palier : `id` (`<mission>-p<n>`), `title`, `minutes`, `goal`, `do` (liste), `commands` (liste, boutons Copier), `tests` (ids de tests de la mission demandés dans CE palier), `check`, `hint`. Règles vérifiées par `tests/test_content.py` : somme des minutes des paliers = `minutes` de la mission ; chaque test de la mission est demandé dans exactement un palier ; ids uniques. `web/app.js` : `renderPaliers`. Le modèle de référence est `socle-mr1`. **Règle produit : ne jamais raccourcir un exercice en le convertissant ; découper en paliers plus nombreux et plus guidés** (exemple travaillé sans rapport avec l'exercice pour toute notion nouvelle). `drafts/PALIERS.md` et `drafts/validate_paliers.py` servent à faire écrire de nouveaux paliers par un agent.
  - Une mission (`steps`) a : `id`, `title`, `branch`, `minutes`, `mission`, `paliers`, `tests` (`id`, `title`, `input`, `expected`), `acceptance`, et `demos` pour les parcours qui en ont (`socle` MR2 et MR3, `headerscope` MR3, `toolwrap` MR3, `reconwrap` MR2).
  - **Ids de mission** : `<parcours>-mr1`, `-mr2`, `-mr3`, soit 18 ids stables. **Ne jamais les renommer** : ils sont stockés dans la progression de l'apprenant.
  - Ids de tests (automatisés, uniques par parcours) : socle S1–S24, PortPilot T1–T8, HeaderScope H1–H9, FileGuard F1–F14, ToolWrap W1–W16, ReconWrap R1–R17.
  - Ids de démonstrations (hors CI, ids réutilisés d'un parcours à l'autre) : socle D1–D2, HeaderScope D1–D3, ToolWrap D1–D3, ReconWrap D1–D6.
- `content/<id>.md` : énoncé Markdown de chacun des 6 parcours (`socle.md`, `portpilot.md`, `headerscope.md`, `fileguard.md`, `toolwrap.md`, `reconwrap.md`), téléchargeable depuis l'UI.
- `docs/PARCOURS.md` : tableau des parcours généré à partir du JSON (ids, objectifs, MR, branches, ids de tests et démos, compétences Git repérées, lien avec le projet final).

### Ébauches (`drafts/`, non livrées dans l'image)
- `drafts/BRIEF.md` : cahier des charges utilisé pour rédiger les parcours (règles pédagogiques, format de sortie).
- `drafts/OUTILS.md` : contrat d'environnement d'outils (nmap, adsim, fixtures). Il cite aussi `127.0.0.1:8080` comme cible autorisée : **écart**, la décision est de n'utiliser que `127.0.0.1:8000` (voir section 9).
- `drafts/socle/`, `drafts/toolwrap/`, `drafts/reconwrap/` : `course.json`, `<id>.md`, `NOTES.md` des ébauches. Les versions utilisées sont dans `content/`.

### Fixtures (`fixtures/`, copiées par l'apprenant, originaux en lecture seule dans `/app/fixtures/`)
- `fixtures/integrity/` : `README.txt`, `message.txt`, `settings.ini` (FileGuard). Fictifs, sans manifeste de référence.
- `fixtures/socle/auth.log` : 40 lignes de connexions fictives (`LOGIN_OK` / `LOGIN_FAIL`, adresses `192.0.2.0/24`), 3 ou 4 lignes malformées volontairement (un test le vérifie).
- `fixtures/nmap/` : `open_8000.xml`, `closed_8000.xml`, `mixed.xml` (open, closed, filtered), `broken.xml` (XML invalide). Sorties au format `nmap -oX`, fictives, pour `127.0.0.1` port 8000.
- `fixtures/adsim/` : `domain.json` (domaine lu par adsim), `users.json`, `users.txt`, `groups.json`, `computers.json`, `broken.json` (JSON invalide). Les sorties capturées sont comparées octet par octet à la sortie réelle d'adsim.

### Tests (`tests/`)
- `tests/test_server.py` (8 tests) : API, chemins, codes d'erreur, exécution de commandes, ZIP.
- `tests/test_labs.py` (5 tests) : cycle de vie du labo et en-têtes.
- `tests/test_content.py` (7 tests) : cohérence de `courses.json` avec `server.py` et `app.js`, ids, durées, cas de test, liens, fixtures.
- `tests/test_tools.py` (26 tests) : adsim (sujets, formats, codes de sortie, délai, fixtures, absence d'import réseau) et cohérence des fixtures nmap et auth.log.

## 3. Lancer, tester, mettre à jour, sauvegarder

- **Lancer ou mettre à jour** : `docker compose up --build -d`, puis ouvrir http://127.0.0.1:8080. Les volumes sont conservés. Si `compose.override.yaml` est présent (mode VS Code), `workspaces` est le dossier `./workspaces` de l'hôte, et non le volume nommé : `docker compose down -v` ne supprime pas ce dossier de l'hôte. La sauvegarde ci-dessous (`tar -C / workspaces data` dans le conteneur) lit `/workspaces`, donc inclut aussi ce dossier monté.
- **Statut** : `docker compose ps`.
- **Tests de Cyber Atelier** (pas ceux de l'apprenant) : `docker compose exec -T atelier python -m unittest discover -s tests -p 'test_*.py' -v`. Il y a **46 méthodes de test** : 13 d'origine (`test_server` 8 + `test_labs` 5), 7 de `test_content.py`, 26 de `test_tools.py`. Dernier passage dans Docker selon la passation : 46/46 OK (non revérifié ici, pas de Docker dans ce travail). Passage local hors Docker (macOS, Python 3.14, `PYTHONDONTWRITEBYTECODE=1`) le 2026-10-10 : 46 OK.
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

Progression (`/data/state.json`, version 1) : `{"version":1, "selectedCourse", "completed": [ids de missions], "notes": {parcours: texte}, "mrLinks": {id de mission: URL}, "paliers": [ids de paliers cochés]}`. La clé `paliers` est optionnelle (défaut `[]`, 500 entrées max) : les anciennes progressions restent valides sans migration.
- `selectedCourse` par défaut : `socle` (`DEFAULT_STATE`). Une progression ancienne sans cette clé est lue avec `portpilot` (valeur de repli de `_state_normalize`) : **écart**, voir section 8.
- Les anciennes progressions (portpilot, headerscope, fileguard) restent valides. Les clés de notes manquantes (`socle`, `toolwrap`, `reconwrap`) sont ajoutées vides.
- Le serveur valide le format, la taille et la liste des parcours, mais pas l'appartenance des identifiants de mission. Le client (`normalizeProgression`) filtre ces identifiants.

## 5. Règles pédagogiques et produit (non négociables)

- **Langue** : interface et documentation en français, avec tutoiement dans le contenu destiné à l'apprenant. L'apprenant connaît les variables, les listes et les fonctions.
- **Pas de solutions** d'exercices sans demande explicite. Les améliorations d'infrastructure (serveur, interface, tests de Cyber Atelier) peuvent contenir du code complet. Le parcours `socle` peut contenir un court extrait de syntaxe générique, sans rapport avec l'exercice.
- **Ne jamais confondre** quatre niveaux : tests locaux, pipeline GitLab réellement exécuté, autorisation effective de fusion, case cochée dans Cyber Atelier (déclarative, sans vérification).
- **Runner GitLab** : sur le runner, `127.0.0.1` désigne le runner, pas le conteneur. Les tests obligatoires (`unittest`, `verification.py`, CI) ne doivent donc jamais dépendre du labo, de nmap ou du réseau : ils utilisent des mocks, des fixtures et des fichiers temporaires.
- **Démonstrations séparées** : les vérifications qui exigent le labo ou nmap sont dans le champ `demos`, affichées à part et hors CI.
- **Cohérence** : `content/courses.json`, `content/*.md`, `web/downloads/PortPilot.pdf` et l'interface doivent rester alignés. Un changement de contenu se répercute dans les trois.
- **Durée** : 30 h = 6 × 300 min. `tests/test_content.py` le vérifie (somme de `timeline` = 300 par parcours, `totalMinutes` = 1800).
- **Dépendances** : bibliothèque standard uniquement, sans framework ni dépendance sans bénéfice concret.
- **Réseau** : ne pas exposer le service au réseau, ne pas élargir les exercices à des cibles externes. Le labo, nmap et les exercices restent sur `127.0.0.1`.
- **Git de travail** : une branche `feat/...` par MR, créée depuis la branche principale à jour, commits atomiques, diff relu avant fusion (une autre IA peut travailler en parallèle).

## 6. Conventions de code

- **Python** : bibliothèque standard uniquement (`server.py` et `tools/adsim.py` utilisent `from __future__ import annotations`). Erreurs de validation en `ValueError` (message en français), mappées en codes HTTP dans `_dispatch`.
- **Sécurité des chemins** : toujours passer par `_relative_path` et `_safe_target`. Ne jamais construire un chemin à partir d'une entrée brute.
- **JavaScript** : style compact, une IIFE, `'use strict'`, pas de build. Les textes sont insérés avec `textContent` (`element`, `button`), jamais en HTML brut. Les liens passent par `safeUrl` (http/https seulement).
- **CSS** : variables sur `:root`, pas de framework. Les nouveaux éléments suivent le même style (11 px minimum).
- **Accessibilité** : `aria-current` sur la navigation, focus sur le titre lors d'un changement de vue, `role="status"` ou `alert` pour les messages.
- **Tests** : `unittest` ; nouveaux tests dans `tests/`, en utilisant des répertoires temporaires. Pas de pytest.

## 7. Ajouter un parcours (checklist)

1. `content/courses.json` : ajouter l'objet dans `courses` (à la bonne place), avec 3 `steps` aux ids `<id>-mr1..3`, `durationMinutes` 300, `timeline` de somme 300, et augmenter `totalMinutes` de 300.
2. `content/<id>.md` : énoncé lisible seul, cohérent mot pour mot avec le JSON.
3. `server.py` : ajouter l'id à `COURSES`.
4. `web/app.js` : ajouter l'id à `const ids` (dans l'ordre voulu).
5. `tests/test_content.py` : ajouter l'id à `COURSE_ORDER`.
6. `web/index.html` : mettre à jour `#side-info` et le paragraphe d'accueil (textes en dur).
7. Si le parcours a des fixtures : `fixtures/<id>/` (le `Dockerfile` copie tout `/app`, rien d'autre à faire).
8. Régénérer ou mettre à jour `docs/PARCOURS.md`, `README.md` (section des parcours), et cette fiche.
9. Lancer la suite de tests dans Docker (section 3).

Un parcours ne doit pas renommer les ids existants.

## 8. État actuel de la branche et vérifications

Dépôt git local : `main` = commit `6734f3f` (« Import initial de l'archive Cyber Atelier »). Branche courante : **`amelioration/fiabilite-parcours`**, avec un commit `3c38487` (« Fiabilise l'éditeur et étend le programme à 6 parcours (30 h) », 2026-10-10 00:59) au-dessus de `main`. État constaté à 01:03 ; le dépôt peut évoluer pendant qu'une autre session travaille.

`git diff --stat main` (commit compris) : **31 fichiers, 2998 insertions, 64 suppressions**. Le commit `3c38487` contient le programme à 6 parcours (`content/`, `tools/`, `fixtures/`, `tests/`, `web/`, `server.py`, `Dockerfile`, `.dockerignore`, `drafts/BRIEF.md`, `drafts/OUTILS.md`). Dans ce commit, `CLAUDE.md` et `README.md` sont dans leur version antérieure.

Modifications non commitées (état à 01:03) : `CLAUDE.md`, `README.md` et `labs.py` modifiés. Le bloc `__main__` de `labs.py` (lancement direct `python3 labs.py` pour VS Code sur le Mac, labo sur `127.0.0.1:8000`) n'est pas commité. Non suivis : `.gitignore`, `compose.override.yaml`, `docs/`, `drafts/socle/`, `drafts/toolwrap/`, `drafts/reconwrap/` (ébauches). Le dossier `workspaces/` (racine, un sous-dossier par parcours) existe sur le disque et est ignoré par `.gitignore`. Relire `git status` avant tout commit ; ne pas faire `git add -A` sans relecture.

Contenu des changements (détail dans `docs/JOURNAL.md`) :
- **Interface** : enregistrement du fichier ouvert avant toute commande ; console conservée par parcours ; code de sortie annoncé ; `fetch keepalive` au `pagehide` ; avertissement de fermeture si la sauvegarde a échoué ; tests automatisés et démonstrations affichés séparément ; bouton « Préparer dans la console » ; bouton ⚙ mobile ; `aria-current`, focus sur le titre, tailles de police relevées.
- **Contenu** : identité Git dans les 6 parcours ; clone marqué `interactive` ; fixtures FileGuard copiées avec `chmod u+w` ; HeaderScope MR3 : démos D1 à D3 ; guide GitLab « Quatre résultats à ne pas confondre » ; 3 parcours ajoutés (socle, toolwrap, reconwrap).
- **Outils** : `tools/adsim.py`, `fixtures/adsim`, `fixtures/nmap`, `fixtures/socle` ; nmap ajouté dans le Dockerfile.
- **Tests** : `tests/test_content.py` (7) et `tests/test_tools.py` (26), 46 au total.

Vérifications : 46 tests OK en local (macOS, hors Docker) le 2026-10-10 ; 46 OK dans Docker selon la passation. Parcours navigateur (passation) : sauvegarde avant exécution, console conservée, fixtures copiées et modifiables, démos HeaderScope D1 à D3, bouton mobile, pas de défilement horizontal à 375 px.

### Limites connues
- **Progression sans `selectedCourse`** : `_state_normalize` relit `portpilot` (`value.get("selectedCourse", "portpilot")`) alors que `DEFAULT_STATE` vaut `socle`. Non corrigé.
- **Textes d'accueil en dur** dans `web/index.html` (`#side-info`, paragraphe d'accueil). Les compteurs de `renderProgress` (heures, MR) sont, eux, calculés.
- **Gabarit `hint`** : les parcours `portpilot`, `headerscope` et `fileguard` ont un indice unique ; `socle`, `toolwrap` et `reconwrap` ont trois niveaux (`Niveau 2 :`, `Niveau 3 :`), comme le demande `drafts/BRIEF.md`.
- **Tests dépendant de `/proc`** : voir section 3.
- **PDF PortPilot** : vouvoiement et suggestion de `python -m http.server 8000`, alors que le labo occupe déjà le port 8000. Source ReportLab absente.
- `flushState` utilise `fetch keepalive`, limité à 64 Ko : une progression plus grosse n'est pas sauvegardée à la fermeture.
- `.dockerignore` cite des fichiers absents (voir section 2).
- Le bouton « Lancer les tests » lance `python verification.py` dans le cwd courant : il exécute le code de l'apprenant, pas les tests de Cyber Atelier.
- Pas de mode sombre dans l'interface.
- `drafts/OUTILS.md` cite le port 8080 comme cible nmap : écart avec la décision (section 9). Aucun contenu livré n'utilise 8080.
- Les ids de démonstration (`D1`…) sont réutilisés d'un parcours à l'autre : toujours les citer avec le parcours.
- La MR3 de 70 min est jugée serrée (`socle`, `toolwrap`, `reconwrap`) : à surveiller au premier retour d'apprenant.

## 9. Décisions prises

- **6 parcours, 30 h, 18 MR**. Ordre : socle > portpilot > headerscope > fileguard > toolwrap > reconwrap. Les ids de mission ne changent plus.
- **ToolWrap et ReconWrap** couvrent `subprocess`, `argparse`, `ipaddress`, la lecture XML et JSON, le packaging et la CI. Les tests obligatoires n'appellent jamais nmap ni le réseau : mocks, fixtures, fichiers temporaires.
- **adsim est fictif** (domaine `LAB.LOCAL`, aucun import réseau) plutôt qu'un vrai Active Directory. Le vrai AD se pratiquera dans le projet final, sur un domaine personnel.
- **nmap uniquement sur `127.0.0.1:8000`**, en démonstration (`nmap -sT -p 8000 -oX - 127.0.0.1`). Aucun autre hôte ni port n'est autorisé dans le lab ; la liste blanche de ToolWrap ne doit pas être élargie.
- **Pas de solutions** : ni code Python d'exercice, ni `.gitlab-ci.yml` complet. Contrats, tests décrits en prose, pistes officielles et indices progressifs uniquement.
- **Chaque MR = une branche `feat/...` + tests automatisés locaux + diff relu** avant fusion. Les tests sont en `unittest` dans `socle`, `toolwrap` et `reconwrap`, et dans `verification.py` dans `portpilot`, `headerscope` et `fileguard` (écart avec une règle uniforme).

## 10. Dépôts GitHub et mode de travail de l'apprenant
- Dépôt de l'outil : https://github.com/nsqzb/cyberatelier (privé), branche de travail `amelioration/fiabilite-parcours`, PR n°1 ouverte vers `main`.
- L'apprenant code dans VS Code sur son Mac, dans `workspaces/<parcours>` (ignoré par ce dépôt), avec un dépôt Git privé par parcours sur son GitHub (`nsqzb/<nom>`). Premier dépôt : `socle-python-git`. Les parcours GitLab de l'école gardent leurs exigences GitLab (CI, MR).
- Le labo se lance sur le Mac avec `python3 labs.py` ; nmap et adsim se lancent via `docker compose exec atelier ...`.

## 11. À faire (pistes non réalisées)
- Alléger la page d'un parcours (objectifs, timeline, labo, prérequis, notes affichés autour des missions) : le format en paliers est fait, pas la page.
- Rééquilibrer les durées : plusieurs paliers de 6 à 8 minutes (MR3 de socle, toolwrap, reconwrap) et des paliers de pipeline/fusion chargés pour 10 minutes.
- Faire suivre chaque parcours de bout en bout par un apprenant (rien n'a été validé en conditions réelles).
- Script de recette navigateur reproductible (aucun test navigateur automatisé dans le dépôt).
- Corriger le repli `portpilot` de `_state_normalize` (écart signalé en section 8) et ajouter un test.
- Déplacer les textes d'accueil en dur de `web/index.html` vers des valeurs calculées.
- Empêcher deux exécutions simultanées côté interface : désactiver les boutons pendant `/api/run`.
- Renommer ou supprimer un fichier depuis l'interface.
- Mémoriser le dossier de travail (cwd) par parcours : `state.cwdByCourse` existe en mémoire seulement, il est perdu au rechargement.
- Afficher une aide claire dans la console en cas d'échec d'une commande interactive (clone SSH).
- Régénérer le PDF PortPilot en tutoiement si la source est retrouvée.
- Décider d'un éventuel 4ᵉ parcours ou d'autres outils (par exemple ffuf ou nuclei) : non tranché.
- Publier un patch (`git diff main > cyberatelier.patch`) ou une archive à chaque livraison.


## Refonte des consignes pour débutant (2026-10-10)

- Les 18 missions gardent leurs identifiants, leurs branches, leurs temps et tous les cas de test / démonstration. Les 153 paliers gardent leurs identifiants : aucune migration de progression.
- `learningGuide` dans `courses.json` contient la méthode et le glossaire. `steps[].learning` décrit le point de départ, le livrable, l’utilité et la commande des tests.
- `paliers[].workspace` indique les fichiers ; `explanation` donne les notions ; `do` contient les actions ; `blocks` remplace `commands` avec `kind`, `title`, `context`, `code`. Ne mélange plus un extrait Python/YAML/Markdown avec une commande shell. Le rendu garde un fallback pour les anciens contenus.
- Les branches MR1 sont créées dans les missions, après la préparation. Le bouton « Lancer les tests » utilise la commande du parcours (unittest pour Socle/ToolWrap/ReconWrap, verification.py pour les autres).
- `scripts/generate_exercises.py` synchronise uniquement la section balisée des six Markdown ; `--check` et un test détectent les divergences. Le contrat avant et les limites après ne sont pas remplacés.
- `scripts/generate_portpilot_pdf.py` reconstruit le PDF depuis le Markdown avec ReportLab (dépendance d’édition uniquement). Le PDF n’a plus de source absente.
- Corrections de guidage : appeler les tests PortPilot explicitement ; lancer unittest.main dans verification.py ; lire echo $? dans la même exécution web ; exemples d’import sans sortie ; erreurs de transport fabriquées sans réseau ; branche et livraison de ReconWrap MR2 explicites ; commandes de conflit exécutables ; ERROR est le niveau logging, ERREUR le statut du contrat.
- La seule précision de livrable en Socle MR1 est l’inclusion du .gitignore déjà demandé par le parcours : caches et fixtures restent exclus.

## Reprise de tous les paliers après retour apprenant (2026-10-10)

- Les 153 paliers ont leurs notions et actions réécrites. Les 88 cas de test, démonstrations, exigences de livraison, ids et durées restent identiques. Les exemples montrent des données attendues ou une notion sur un autre sujet, sans fonction solution.
- `paliers[].rules` est une liste facultative de règles ; `example` contient `input`, `output`, `note`. `blocks[].placement` vaut `before_actions` pour expliquer une notion ou `after_actions` pour les commandes de réalisation. Le rendu web et le générateur Markdown suivent ce même ordre.
- Socle MR1 palier 6 explique champ, positions de liste, dictionnaire, None, puis montre une ligne et son dictionnaire attendu ; S6, S7 et S8 restent obligatoires.
- ReconWrap R5 est partiellement écrit au palier 4 et complété au palier 6 : aucun appel de module n’est annoncé comme déjà vérifié au palier 4. ERROR est le niveau logging, ERREUR le statut du résultat.
- ToolWrap D3 utilise `--delay 1` avec délai 0,01 seconde pour produire le timeout indépendamment du démarrage de Docker. Les outils et tests automatiques ne changent pas.
- Vérification CI Linux : `process_is_running` dans tests/test_server.py traite aussi ProcessLookupError lorsqu’un processus disparaît pendant la lecture de /proc. Un test isolé reproduit ce cas, garde la distinction vivant/zombie et laisse remonter PermissionError. La suite d’infrastructure compte désormais 52 tests ; les 88 cas d’exercice restent identiques.
