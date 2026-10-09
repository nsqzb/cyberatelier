# Cyber Atelier

Cyber Atelier est une application locale pour pratiquer Python et GitLab à son rythme. Elle contient trois parcours guidés de cinq heures. Le code que tu écris et ta progression sont enregistrés dans des volumes Docker persistants. Aucun corrigé Python ni pipeline d’exercice n’est préinstallé.

## Démarrer

Installe Docker Desktop (ou Docker Engine avec le plugin Docker Compose), puis ouvre un terminal dans le dossier du projet. Lance :

```bash
docker compose up --build -d
docker compose ps
```

Ouvre ensuite <http://127.0.0.1:8080>. L’application utilise le port `8080` par défaut. Pour en choisir un autre, crée un fichier `.env` à côté de `compose.yaml` contenant, par exemple, `ATELIER_PORT=8081`, puis relance `docker compose up -d`. L’adresse devient alors <http://127.0.0.1:8081>.

Le service écoute sur `0.0.0.0:8080` à l’intérieur du conteneur afin que Docker puisse lui transmettre les requêtes. La publication côté machine est limitée à `127.0.0.1` : l’application est accessible depuis cette machine, pas depuis le réseau local. Dans le laboratoire, `127.0.0.1` désigne le conteneur lui-même. Le labo écoute sur le port 8000 à l’intérieur du conteneur et n’est pas publié sur l’hôte.

## Travailler sur les parcours

L’onglet Coder permet de créer et modifier les fichiers du projet, puis de lancer de vraies commandes dans ce projet. Une commande lancée depuis l’interface s’arrête au bout de 30 secondes ; utilise le shell interactif décrit ci-dessous pour une opération plus longue. Avant chaque commande, l’éditeur enregistre le fichier ouvert : la commande lit la version affichée. Ce shell reste attaché au conteneur et ne garde pas de session après sa fermeture. Les dossiers `portpilot`, `headerscope` et `fileguard` sont réservés au travail apprenant. Les fixtures fictives de FileGuard sont fournies en lecture seule dans `/app/fixtures/integrity`. Depuis la console du parcours FileGuard, `mkdir -p fixtures && cp /app/fixtures/integrity/* fixtures/ && chmod u+w fixtures/*` les copie dans ton dépôt et rend les copies modifiables (le bouton « Préparer dans la console » de l’onglet Environnement remplit cette commande).

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

Le labo intégré sert de cible locale pour HeaderScope et PortPilot. Il démarre automatiquement avec l’application et écoute sur le port 8000 du conteneur ; le bouton de la page du parcours permet de l’arrêter (pour observer une connexion refusée) ou de le relancer. Il n’est pas nécessaire de démarrer un serveur HTTP séparé. Un runner GitLab de l’école est une machine distincte : `127.0.0.1` dans un job désigne ce runner, et non le conteneur de Cyber Atelier. Les runners, leur configuration, les variables de CI et les droits de fusion sont fournis par l’école. Si le runner n’exécute pas le labo, les tests réseau visant celui-ci ne peuvent pas y réussir ; suis les consignes du parcours pour privilégier les tests autonomes adaptés au runner. Un résultat local réussi ne valide pas automatiquement une merge request et ne coche pas sa progression.

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

Remplace les fichiers de l’application (ou applique le patch fourni), puis reconstruis l’image depuis le dossier du projet :

```bash
docker compose up --build -d
```

Les volumes `workspaces`, `data` et `home` sont réutilisés tels quels : ton code, ta progression et ta configuration Git sont conservés. Fais une sauvegarde (section suivante) avant une mise à jour importante. N’utilise pas `docker compose down -v` pour « repartir proprement » : cette commande supprime les volumes.

## Sauvegarder et restaurer

La progression et les notes sont conservées dans le volume `data`. Les dépôts et fichiers créés dans l’atelier sont dans `workspaces`. Pour en faire une archive sur la machine hôte, depuis le dossier du projet :

```bash
mkdir -p backups
docker compose exec -T atelier tar -czf - -C / workspaces data > backups/cyberatelier-$(date +%Y%m%d-%H%M%S).tar.gz
```

Cette archive contient tous les projets et la progression, mais exclut volontairement le volume `home` qui peut contenir une clé SSH privée. Garde-la dans un endroit sûr ; les dépôts peuvent contenir tes propres informations. Après restauration, configure à nouveau l’accès SSH si nécessaire. Pour restaurer une archive, arrête d’abord le service, puis extrais-la dans les volumes depuis le conteneur :

```bash
docker compose stop
docker compose run --rm --no-deps -T --entrypoint tar atelier -xzf - -C / < backups/NOM_DE_L_ARCHIVE.tar.gz
docker compose start
```

L’import remplace les chemins présents dans les volumes par ceux de l’archive. Pour sauvegarder uniquement le code d’un parcours, utilise aussi l’action d’export ZIP dans l’interface. L’export de progression depuis l’interface permet de conserver ou transférer le JSON de progression séparément.

## Configuration et limites

Les ports et chemins internes peuvent être ajustés par variables d’environnement : `ATELIER_PORT` choisit le port publié par Compose (8080 par défaut) ; dans le conteneur, `ATELIER_HOST=0.0.0.0`, `ATELIER_PORT=8080`, `WORKSPACES_DIR=/workspaces`, `DATA_DIR=/data` et `LAB_PORT=8000`. Pour un lancement Python natif, le serveur utilise par défaut `ATELIER_HOST=127.0.0.1`.

L’application exécute les commandes et le code de l’apprenant dans le conteneur sous un compte non-root. Elle est destinée à un usage personnel local, pas à être hébergée ou exposée sur un réseau. Le conteneur ne reçoit pas le socket Docker et n’a pas de privilèges administrateur. Les fichiers de l’application sont en lecture seule ; le code, la progression et le dossier personnel sont conservés séparément dans les volumes nommés `workspaces`, `data` et `home`. Git, bash, OpenSSH et Python sont disponibles sans installation de dépendances au démarrage.

## Vérifier l’infrastructure

Les tests de l’application (serveur, laboratoire et cohérence des contenus) s’exécutent dans le conteneur :

```bash
docker compose exec -T atelier python -m unittest discover -s tests -p 'test_*.py' -v
```

Ils vérifient Cyber Atelier lui-même, pas tes exercices : ceux-ci sont testés par ton propre `verification.py`.
