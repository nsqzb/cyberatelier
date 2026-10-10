# Cyber Atelier

Cyber Atelier propose six parcours pour pratiquer Python et Git à ton rythme, jusqu’à assembler un mini-framework. Tu peux suivre les 153 paliers entièrement depuis le terminal du Mac : les consignes, les indices et ta position sont accessibles sans ouvrir le site. Les sujets, tests et exigences restent ceux des six parcours de cinq heures. Aucun corrigé Python ni pipeline d’exercice n’est préinstallé.

## Démarrer dans le terminal du Mac

Depuis le dossier de l’application, lance le lecteur avec Python 3 :

```bash
cd /Users/anas/Documents/cyberatelier
python3 atelier.py
```

Le lecteur montre un seul palier à la fois et retrouve le dernier palier consulté au prochain lancement. Il affiche le dossier de ton exercice, sa branche Git actuelle, la branche demandée et les commandes à lancer. Tu écris et exécutes ton code toi-même dans le terminal du Mac, depuis `workspaces/<parcours>`, avec ton environnement Python local. Les indices se révèlent à ta demande, en trois niveaux.

La progression terminal est enregistrée dans `userdata/terminal.json`, à côté de tes exercices et hors du dépôt Git de l’application. Au premier lancement, si Docker est actif, le lecteur importe les cases et notes déjà enregistrées dans l’atelier. Il reste ensuite utilisable hors ligne ; tes modifications dans le terminal ne remplacent pas la progression du site. Une case cochée indique ce que tu déclares terminé : elle ne prouve pas que des tests ou une CI ont réussi.

Le [guide du terminal Mac](docs/TERMINAL_MAC.md) présente les commandes de navigation, les deux dépôts Git et les laboratoires.

## Démarrer les outils Docker et le site facultatif

Installe Docker Desktop (ou Docker Engine avec le plugin Docker Compose), puis ouvre un terminal dans le dossier du projet. Lance :

```bash
docker compose up --build -d
docker compose ps
```

Ouvre ensuite <http://127.0.0.1:8080>. L’application utilise le port `8080` par défaut. Pour en choisir un autre, crée un fichier `.env` à côté de `compose.yaml` contenant, par exemple, `ATELIER_PORT=8081`, puis relance `docker compose up -d`. L’adresse devient alors <http://127.0.0.1:8081>.

Le service écoute sur `0.0.0.0:8080` à l’intérieur du conteneur afin que Docker puisse lui transmettre les requêtes. La publication côté machine est limitée à `127.0.0.1` : l’application est accessible depuis cette machine, pas depuis le réseau local. Dans le laboratoire, `127.0.0.1` désigne le conteneur lui-même. Le labo écoute sur le port 8000 à l’intérieur du conteneur et n’est pas publié sur l’hôte.

## Parcours et chemin conseillé

Six parcours de cinq heures chacun, trois merge requests par parcours. Pour les objectifs, les branches et les ids de tests, voir `docs/PARCOURS.md`.

- **Socle Python & Git** (`socle`), 5 h : fonctions pures, tests unittest, fichiers et JSON, Git en équipe (conflit, rebase, tag).
- **PortPilot** (`portpilot`), 5 h : scanner TCP limité à 127.0.0.1, validation de ports, pipeline GitLab.
- **HeaderScope** (`headerscope`), 5 h : client HTTP vers le labo local et contrôle de trois en-têtes de sécurité.
- **FileGuard** (`fileguard`), 5 h : empreintes SHA-256, manifeste et comparaison inchangé, modifié, supprimé ou ajouté.
- **ToolWrap** (`toolwrap`), 5 h : lancer un outil externe avec `subprocess`, CLI `argparse`, lecture des sorties nmap et adsim.
- **ReconWrap** (`reconwrap`), 5 h : assembler un mini-framework avec des modules réseau, web et Active Directory, des rapports et une version v0.1.0.

Chemin conseillé : suis l'ordre ci-dessus. Le socle prépare tout le reste. PortPilot et HeaderScope fournissent les modules réseau et web que ReconWrap réutilise ; ToolWrap apprend à piloter les outils dont ReconWrap a besoin. Commence ReconWrap seulement après ToolWrap.

## Outils fournis et leurs limites

- **nmap** : outil réel, installé dans le conteneur. Il sert uniquement à une démonstration sur `127.0.0.1`, port `8000`, labo démarré, par exemple `nmap -sT -p 8000 -oX - 127.0.0.1`. Limite : aucune autre cible ni plage n'est autorisée. Les tests obligatoires n'appellent jamais nmap, car le runner GitLab ne l'a pas : ils lisent des fichiers XML fictifs.
- **adsim** (`/app/tools/adsim.py`) : simulateur **fictif** d'un annuaire Active Directory, domaine `LAB.LOCAL`. Il ne se connecte à aucun annuaire ni à aucun réseau, et ses données sont fixes. Il ne remplace pas un vrai Active Directory : le vrai AD se pratiquera dans le projet final, sur un domaine personnel.
- **Fixtures** : `fixtures/` dans l’application sur ton Mac, ou `/app/fixtures/` dans Docker. Elles contiennent `integrity` pour FileGuard, `socle` (journal de connexions fictif), `nmap` (sorties XML) et `adsim` (sorties JSON et texte). Depuis ton exercice, copie les fichiers demandés depuis `../../fixtures/`. Ce sont des données fictives : elles ne prouvent rien sur un vrai réseau ni sur un vrai domaine.

## Travailler sur les parcours

Chaque exercice a son propre dépôt dans `workspaces/<parcours>`. Fais tes opérations Git et tes tests depuis ce dossier sur le Mac. Le dépôt de l’application est à la racine `cyberatelier` : changer sa branche pour une mise à jour ne change pas celle de ton exercice.

Par exemple, pour reprendre le Socle dans un autre terminal :

```bash
cd /Users/anas/Documents/cyberatelier/workspaces/socle
git status
git branch --show-current
```

Suis ensuite la commande des tests donnée par ton palier. Pour les démonstrations réseau exécutées sur le Mac, lance `python3 labs.py` depuis la racine de l’application dans un terminal séparé. Ce laboratoire écoute sur le `127.0.0.1:8000` du Mac. Les commandes `docker compose ...` se lancent depuis la racine de l’application ; elles exécutent les outils dans Docker, où `127.0.0.1` désigne le conteneur.

### Éditeur et console du site, si tu les utilises

L’onglet Coder permet de créer et modifier les fichiers du projet, puis de lancer de vraies commandes dans ce projet. Une commande lancée depuis l’interface s’arrête au bout de 30 secondes ; utilise le shell interactif décrit ci-dessous pour une opération plus longue. Avant chaque commande, l’éditeur enregistre le fichier ouvert : la commande lit la version affichée. Ce shell reste attaché au conteneur et ne garde pas de session après sa fermeture. Les dossiers `portpilot`, `headerscope` et `fileguard` sont réservés au travail apprenant. Les fixtures fictives de FileGuard sont fournies en lecture seule dans `/app/fixtures/integrity`. Depuis la console du parcours FileGuard, `mkdir -p fixtures && cp /app/fixtures/integrity/* fixtures/ && chmod u+w fixtures/*` les copie dans ton dépôt et rend les copies modifiables. L’onglet Environnement présente les commandes pour le terminal du Mac ; adapte les chemins si tu travailles dans cette console Docker.

Pour les opérations Git interactives, ouvre un shell dans le conteneur :

```bash
docker compose exec atelier bash
cd /workspaces/portpilot
git clone URL_DU_DEPOT_ECOLE .
```

Remplace `URL_DU_DEPOT_ECOLE` par l’URL fournie par ton école. Avant ton premier commit, déclare une fois ton identité Git (elle est conservée dans le volume `home`) :

```bash
git config --global user.name "Prénom Nom"
git config --global user.email "adresse@ecole.example"
```

Tu peux aussi utiliser les dossiers `headerscope` et `fileguard`. Git, bash et le client OpenSSH sont installés. Avec une URL SSH, tu peux créer une clé dans le conteneur avec `ssh-keygen`, puis ajouter son contenu `.pub` à ton compte GitLab scolaire. Le dossier personnel du conteneur est conservé dans un volume Docker pour garder ta configuration Git et SSH entre les redémarrages. La clé privée qui s’y trouve reste un secret : ne l’ajoute jamais à un dépôt ni à une archive partagée. Avec HTTPS, Git peut demander un jeton ; ne colle pas de mot de passe ou de jeton dans les notes de l’atelier, les fichiers du projet ou une commande conservée dans l’historique. L’application ne gère pas les comptes de l’école.

Le labo intégré à Docker démarre avec l’application et écoute sur le port 8000 du conteneur. Depuis le terminal du Mac, `python3 atelier.py labo arreter` et `python3 atelier.py labo demarrer` permettent de contrôler ce labo pour les démonstrations Docker, sans ouvrir le site. Ces commandes ne contrôlent pas le labo Mac lancé avec `python3 labs.py`. Un runner GitLab de l’école est une machine distincte : `127.0.0.1` dans un job désigne ce runner. Les tests automatiques demandés restent autonomes ; les démonstrations avec le labo sont séparées. Un résultat local réussi ne valide pas automatiquement une merge request et ne coche pas sa progression.

## Arrêter et reprendre

Pour arrêter le service tout en gardant tes données :

```bash
docker compose stop
```

Pour le reprendre :

```bash
docker compose start
```

Ou utilise `docker compose down` pour supprimer les conteneurs. Les volumes nommés `workspaces`, `data` et `home` restent présents. Au prochain lancement, `docker compose up -d` les réutilise. `home` conserve la configuration Git et SSH ; `docker compose down -v` supprime aussi ces volumes, y compris cette configuration, ainsi que le code et la progression.

## Mettre à jour Cyber Atelier

Après la fusion d’une MR de l’application dans `main`, lance depuis `cyberatelier` :

```bash
./mettre-a-jour
```

La commande vérifie l’état du dépôt de l’application, sauvegarde le code et les progressions, récupère `main`, construit l’image, puis attend que Docker soit prêt. L’ancien conteneur reste actif pendant la construction. Les sauvegardes se trouvent dans `backups/`. Si le dépôt de l’application contient des modifications suivies non commitées ou un historique incompatible, la commande s’arrête avec une explication.

Pour vérifier les mises à jour disponibles sans changer de branche ni redémarrer Docker :

```bash
./mettre-a-jour --check
```

La version est affichée après la mise à jour et avec `python3 atelier.py version`. Les fichiers, commits et branches de tes exercices, ainsi que les volumes `data` et `home`, sont conservés. N’utilise pas `docker compose down -v` : cette commande supprime les volumes.

## Sauvegarder et restaurer

La progression du terminal et ses notes sont dans `userdata/terminal.json` ; celles du site sont dans le volume Docker `data`. Avec le `compose.override.yaml` fourni, tes projets sont dans `workspaces/` sur le Mac et sont aussi visibles dans Docker. La commande `./mettre-a-jour` archive ces données avant toute mise à jour. Pour une sauvegarde manuelle du code et de la progression du site, depuis le dossier du projet :

```bash
mkdir -p backups
docker compose exec -T atelier tar -czf - -C / workspaces data > backups/cyberatelier-$(date +%Y%m%d-%H%M%S).tar.gz
```

Cette archive manuelle contient tous les projets et la progression du site ; `./mettre-a-jour` ajoute aussi `userdata/terminal.json` s’il existe. Les deux formats excluent le volume `home` qui peut contenir une clé SSH privée. Garde les archives dans un endroit sûr ; les dépôts peuvent contenir tes propres informations. Avant une restauration, sauvegarde l’état actuel et ferme les lecteurs terminal. Depuis le dossier de l’application, restaure uniquement `workspaces` et `data` dans leurs montages Docker :

```bash
docker compose stop
docker compose run --rm --no-deps --no-build --pull never -T --entrypoint tar atelier -xzf - -C / workspaces data < backups/NOM_DE_L_ARCHIVE.tar.gz
docker compose start
```

L’import remplace les chemins présents dans les montages par ceux de l’archive. Pour une sauvegarde créée par `./mettre-a-jour`, vérifie aussi si elle contient la progression terminal :

```bash
tar -tzf backups/NOM_DE_L_ARCHIVE.tar.gz userdata/terminal.json
```

Si ce fichier est listé, restaure-le sur le Mac, en gardant le lecteur fermé :

```bash
mkdir -p userdata backups
if [ -f userdata/terminal.json ]; then
  cp -p userdata/terminal.json backups/terminal-avant-restauration-$(date +%Y%m%d-%H%M%S).json
fi
tar -xzf backups/NOM_DE_L_ARCHIVE.tar.gz -C . userdata/terminal.json
chmod 600 userdata/terminal.json
```

Pour sauvegarder uniquement le code d’un parcours, utilise aussi l’action d’export ZIP dans l’interface. L’export de progression depuis l’interface permet de conserver ou transférer le JSON de progression du site séparément.

## Configuration et limites

Les ports et chemins internes peuvent être ajustés par variables d’environnement : `ATELIER_PORT` choisit le port publié par Compose (8080 par défaut) ; dans le conteneur, `ATELIER_HOST=0.0.0.0`, `ATELIER_PORT=8080`, `WORKSPACES_DIR=/workspaces`, `DATA_DIR=/data` et `LAB_PORT=8000`. Pour un lancement Python natif, le serveur utilise par défaut `ATELIER_HOST=127.0.0.1`.

L’application exécute les commandes et le code de l’apprenant dans le conteneur sous un compte non-root. Elle est destinée à un usage personnel local, pas à être hébergée ou exposée sur un réseau. Le conteneur ne reçoit pas le socket Docker et n’a pas de privilèges administrateur. Les fichiers de l’application sont en lecture seule ; le code, la progression et le dossier personnel sont conservés séparément dans les montages `workspaces`, `data` et `home`. Git, bash, OpenSSH et Python sont disponibles sans installation de dépendances au démarrage.

## Vérifier l’infrastructure

Les tests de l’application (serveur, laboratoire et cohérence des contenus) s’exécutent dans le conteneur :

```bash
docker compose exec -T atelier python -m unittest discover -s tests -p 'test_*.py' -v
```

Ces tests vérifient Cyber Atelier lui-même, pas tes exercices : tes exercices sont testés par tes propres tests (`verification.py` ou `unittest`, selon le parcours).


## Maintenir les énoncés

Les consignes des 18 missions sont définies dans `content/courses.json`. Chaque mission précise son point de départ, son livrable et sa commande de tests ; chaque palier précise les fichiers concernés, les actions dans l’ordre et les blocs typés (`shell`, `python`, `yaml`, `markdown`). Les contrats de programme et les limites restent dans l’introduction et la fin de chaque énoncé Markdown.

Après une modification des missions, synchronise les six énoncés :

```bash
python3 scripts/generate_exercises.py
python3 scripts/generate_exercises.py --check
```

Le second appel vérifie la synchronisation sans écrire. Les tests de contenu font aussi ce contrôle. Édite les missions dans le JSON : les sections Markdown entre `BEGIN GENERATED EXERCISES` et `END GENERATED EXERCISES` sont régénérées.

Pour PortPilot, régénère également le PDF depuis son Markdown avec `python3 scripts/generate_portpilot_pdf.py`. Ce script d’édition utilise ReportLab ; cette dépendance reste hors de l’application et du conteneur d’apprentissage. L’application et les tests de contenu utilisent uniquement la bibliothèque standard.
