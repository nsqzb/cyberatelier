# Journal de la livraison

Ce journal décrit la livraison sur la branche `amelioration/fiabilite-parcours`, au-dessus de `main` (commit `6734f3f`). Elle comprend le commit `3c38487` (« Fiabilise l'éditeur et étend le programme à 6 parcours (30 h) », 2026-10-10 00:59) et des modifications non commitées décrites en section 8. Chaque point a été vérifié dans le code à la date du 2026-10-10.

## 1. Correctifs de l'éditeur (`web/app.js`)

- **Enregistrement avant exécution** : `runCommand` enregistre le fichier ouvert si son brouillon est modifié, puis lance la commande. Si l'enregistrement échoue, la commande n'est pas lancée. Si le fichier change pendant l'enregistrement, l'utilisateur est invité à enregistrer puis à relancer.
- **Console conservée par parcours** : la sortie est gardée dans `consoleByCourse` et réaffichée au retour dans l'onglet Coder.
- **Code de sortie annoncé** : chaque sortie se termine par `[code N · durée · cwd]`, avec un message de succès ou d'échec. Un délai dépassé est signalé, avec le conseil d'utiliser le shell interactif.
- **Flush à la fermeture** : `pagehide` envoie la progression non sauvegardée avec `fetch` en `keepalive`. Limite : 64 Ko.
- **Avertissement de fermeture** : `beforeunload` demande confirmation si des modifications ne sont pas enregistrées ou si la dernière sauvegarde de progression a échoué (`state.saveError`).

## 2. Accessibilité et mise en page

- **Tailles de police** : le plus petit corps de texte passe à 11 px (les anciennes valeurs de 9 et 10 px ont disparu de `web/styles.css`).
- **Focus** : `focusView` place le focus sur le titre de la vue à chaque changement de vue, puis remonte la page en haut.
- **`aria-current`** : posé sur l'élément de navigation actif (`web/app.js`).
- **Bouton ⚙ mobile** : `#settings-open-mobile` ouvre « Progression & sauvegarde » sous 760 px (classe `mobile-only`). Le bouton de la barre latérale « Progression & sauvegarde » reste présent dans l'interface.
- **Messages** : la zone `#alert-region` est en `role="status"` (`role="alert"` pour les erreurs).
- **Mise en page** : pas de défilement horizontal à 375 px (vérifié lors de la passation, parcours navigateur non reproductible par un script du dépôt).

## 3. Contenu (`content/`)

- **Identité Git** : la commande `git config --global user.name` / `user.email` figure dans les consignes de `socle`, `portpilot`, `headerscope`, `fileguard` et `reconwrap` ; `toolwrap` demande seulement de vérifier cette identité (`git config --global --get`). Elle est conservée dans le volume `home`.
- **Clone interactif** : l'étape `git clone <URL_DU_DEPOT> .` est marquée `interactive` dans les 6 parcours, avec la consigne d'utiliser `docker compose exec atelier bash`, car elle peut demander un jeton ou la confirmation d'une empreinte SSH.
- **PortPilot** : la création de branche (`git switch -c feat/validation`) est une étape séparée, après `git status`.
- **FileGuard** : étape de copie des fixtures (`cp /app/fixtures/integrity/*` puis `chmod u+w`), pour que les copies soient modifiables.
- **HeaderScope MR3** : les anciens tests H11 à H13 deviennent des démonstrations D1 à D3 (`demos`), hors tests automatisés. Le runner GitLab ne peut pas les atteindre : `127.0.0.1` y désigne le runner.
- **Guide GitLab** : nouvelle section « Quatre résultats à ne pas confondre » (tests locaux, pipeline réel, autorisation de fusion, case cochée).
- **Ids** : aucun id de mission n'a été renommé. Les ids des parcours existants (`portpilot-mr1..3`, `headerscope-mr1..3`, `fileguard-mr1..3`) sont inchangés.

## 4. Extension du programme

- **Trois parcours ajoutés** : `socle` (5 h, débutant), `toolwrap` (5 h) et `reconwrap` (5 h). Le programme passe de 15 h à 30 h et de 9 à 18 missions. Ordre : socle, portpilot, headerscope, fileguard, toolwrap, reconwrap.
- **Fichiers ajoutés** : `content/socle.md`, `content/toolwrap.md`, `content/reconwrap.md`.
- **Outils** : `tools/adsim.py` (simulateur fictif d'Active Directory, domaine `LAB.LOCAL`, aucun import réseau) ; `fixtures/adsim/`, `fixtures/nmap/` et `fixtures/socle/` (données fictives).
- **Image** : le `Dockerfile` installe `nmap` (paquet Debian). `.dockerignore` exclut `drafts/`, qui contient les ébauches de rédaction.
- **Tests** : `tests/test_content.py` (7 tests : ids, durées, cas de test, liens, fixtures, absence de dépendance au labo dans les tests obligatoires) et `tests/test_tools.py` (26 tests : adsim, codes de sortie, fixtures, absence d'import réseau). Au total, 46 tests (13 d'origine).

## 5. Changements de format de données

- **Progression : aucune migration nécessaire.** Les anciennes progressions restent valides : leurs ids de mission sont inchangés, et les clés de notes manquantes (`socle`, `toolwrap`, `reconwrap`) sont ajoutées vides par `_state_normalize` (`server.py`) et par `normalizeProgression` (`web/app.js`).
- **`selectedCourse` par défaut** : `socle` dans `DEFAULT_STATE` (`server.py`) et dans l'état initial de l'interface (`web/app.js`).
- **Écart** : sans la clé `selectedCourse`, `_state_normalize` retient `portpilot` (valeur de repli codée en dur). L'import JSON dans l'interface, lui, rejette un fichier sans `selectedCourse`. Ces deux comportements ne concordent pas avec le défaut `socle`. Non corrigé dans cette livraison.
- **Textes d'accueil en dur** : `#side-info` (« 30 h · 6 parcours · 18 missions ») et le paragraphe d'accueil de `web/index.html` sont écrits en dur. Les compteurs calculés (`renderProgress`) sont corrects.

## 6. Limites et points non vérifiés

- **PDF PortPilot** (`web/downloads/PortPilot.pdf`) : il vouvoie l'apprenant, propose `git clone <URL>` sans point final et une démonstration avec `python -m http.server 8000`, alors que le labo occupe déjà le port 8000. La source ReportLab est absente : non modifié.
- **Références en ligne** : les URL des `references` ne sont pas ouvertes ni vérifiées par ce travail. Elles sont limitées à `docs.python.org`, `git-scm.com` et `docs.gitlab.com` (contrôle de forme par `test_content.py`, pas d'accès réseau).
- **Parcours relus mais non menés de bout en bout** : `socle`, `toolwrap` et `reconwrap` ont été relus, mais aucun apprenant ne les a suivis entièrement. Ce point vient de la passation, il n'a pas été vérifié ici.
- **MR3 de 70 min** : jugée serrée dans `socle`, `toolwrap` et `reconwrap`. À confirmer au premier retour.
- **Hints** : `portpilot`, `headerscope` et `fileguard` ont un indice unique ; `socle`, `toolwrap` et `reconwrap` ont trois niveaux (format du cahier des charges).
- **Tests de Cyber Atelier** : 46 tests. Passage local hors Docker le 2026-10-10 : 46 OK (macOS, Python 3.14). Le passage dans Docker est signalé dans la passation, non rejoué ici. Sur macOS, les tests de mort de processus (`process_is_running` lit `/proc`) passent sans prouver grand-chose.
- **Démonstrations** : les ids `D1`… sont réutilisés d'un parcours à l'autre. Les démonstrations nécessitent le labo démarré et ne sont pas exécutées par la CI.
- **Décision à revoir** : `drafts/OUTILS.md` cite le port 8080 comme cible nmap. La décision retenue est `127.0.0.1:8000` uniquement, et aucun contenu livré n'utilise 8080.

## 7. Prochaines pistes

- Corriger le repli `portpilot` de `_state_normalize` et ajouter un test.
- Remplacer les textes d'accueil en dur par des valeurs calculées.
- Désactiver les boutons d'exécution pendant `/api/run`, pour éviter les doubles lancements côté interface.
- Mémoriser le dossier de travail (cwd) par parcours entre deux rechargements.
- Ajouter un script de recette navigateur reproductible.
- Décider d'un éventuel quatrième parcours ou d'autres outils (par exemple ffuf ou nuclei).

## 8. Hors commit (état constaté à 01:03)

Ces changements ne figurent pas dans `3c38487` :
- **`labs.py`** : bloc `if __name__ == "__main__":` ajouté. `python3 labs.py` lance le labo sur `127.0.0.1:8000` de la machine hôte (utile pour coder dans VS Code), jusqu'à Ctrl+C. Le code du labo n'est pas modifié.
- **`compose.override.yaml`** (nouveau) : mode « je code dans VS Code ». Compose le charge automatiquement et monte `./workspaces` de l'hôte à la place du volume nommé `workspaces`. Pour revenir au volume, retirer ce fichier ; le volume existant n'est pas supprimé.
- **`.gitignore`** (nouveau) : ignore `workspaces/`, `backups/`, `.env`, les caches Python, `.venv/` et `.DS_Store`.
- **Documentation** : `CLAUDE.md`, `README.md`, `docs/`.
- **Ébauches** : `drafts/socle/`, `drafts/toolwrap/`, `drafts/reconwrap/` (non suivies).

Points à traiter avant de documenter le mode VS Code auprès de l'apprenant : `README.md` décrit encore les volumes nommés `workspaces`, `data` et `home` sans mentionner `compose.override.yaml` ni `python3 labs.py`.
