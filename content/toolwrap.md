# ToolWrap — piloter un outil externe

**Durée : 5 heures · Niveau débutant · 3 merge requests**

Tu vas écrire le cœur du framework de pentest : un wrapper, c’est-à-dire un petit programme Python qui lance un outil en ligne de commande, le pilote (délai, code de retour, erreurs) et transforme sa sortie en données exploitables. Le framework final aura un module réseau piloté par nmap et un module Active Directory piloté par un outil AD. Ici, nmap ne sert qu’en démonstration sur le labo local, et adsim est un simulateur fictif qui joue le rôle de l’outil AD. Tout est un wrapper : c’est la compétence que tu travailles ici.

## Pourquoi ce parcours

Le framework appellera des outils différents, avec des sorties différentes (XML pour nmap, JSON ou texte pour adsim). Trois idées tiennent le parcours :

1. Lancer un outil sans shell, avec une liste d’arguments, pour qu’une entrée utilisateur ne soit jamais interprétée comme une commande.
2. Normaliser le résultat, même en cas d’échec, pour que chaque module traite les erreurs de la même façon.
3. Limiter le périmètre : une CLI qui refuse toute cible hors de la liste blanche avant de lancer quoi que ce soit.

## Périmètre et règles

- Outils : nmap, installé dans le conteneur, utilisé seulement en démonstration sur 127.0.0.1:8000 ; adsim, simulateur FICTIF du domaine LAB.LOCAL, lancé par `python /app/tools/adsim.py <sujet> [options]`.
- Cible réseau : 127.0.0.1 uniquement. Aucune cible externe, aucune plage, aucun exploit.
- Tests obligatoires : unittest, avec unittest.mock sur subprocess.run et des fixtures locales. Aucun processus réel, aucun nmap, aucun réseau dans ces tests.
- Bibliothèque standard uniquement. Pas de pip.
- Git : une branche par MR, créée depuis la branche principale à jour, des commits atomiques, `git status`, `git diff` et `git log --oneline` avant chaque commit.

## Prérequis

- Le Socle : unittest, fichiers, JSON, exceptions, Git de base (branche, commit, diff).
- Idéalement PortPilot et HeaderScope.
- Python 3 et Git dans le conteneur Cyber Atelier.

## Mise en place

Dans la console du parcours, dans l’ordre :

1. `python3 --version` et `git --version` pour vérifier les outils.
2. `git config --global --get user.name && git config --global --get user.email` pour vérifier ton identité Git. Si une valeur manque, reprends la configuration des parcours précédents.
3. Clone interactif, dans `docker compose exec atelier bash` depuis le dossier Cyber Atelier : `git clone <URL_DU_DEPOT> .`, puis `cd /workspaces/toolwrap`.
4. Copie des fixtures nmap : `mkdir -p fixtures && cp -r /app/fixtures/nmap/. fixtures/nmap/ && chmod -R u+w fixtures/nmap`.
5. Copie des fixtures adsim : `mkdir -p fixtures && cp -r /app/fixtures/adsim/. fixtures/adsim/ && chmod -R u+w fixtures/adsim`.
6. Création de la première branche : `git switch -c feat/subprocess`.

Les originaux sont en lecture seule. Tes copies sont modifiables, mais les tests ne doivent pas dépendre de modifications manuelles.

## Contrat du programme

Écris le wrapper et l’analyse dans `toolwrap.py`, la CLI dans `cli.py`, les tests dans `tests/`. Tu choisis les noms internes, mais garde séparés le wrapper, les parseurs, le rapport et la CLI.

**Wrapper `lancer_outil(args, timeout)`** : reçoit une liste d’arguments (le premier élément est le programme) et un délai en secondes. Il retourne toujours un dictionnaire aux quatre clés :

- `returncode` : code de retour, ou None si le programme n’a pas terminé (délai dépassé, outil introuvable) ;
- `stdout` et `stderr` : sorties texte capturées, vides si rien n’a été produit ;
- `erreur` : None en cas de succès ; une chaîne courte en français sinon (délai dépassé, outil introuvable, code de retour non nul).

Aucune exception ne remonte à l’appelant pour ces trois cas. Une liste vide ne lance rien et retourne une erreur normalisée.

**Parseurs** : chaque parseur retourne un dictionnaire `{"items": [...], "erreur": ...}`. Un élément normalisé a les clés `source` (nmap ou adsim), `type`, `nom`, `statut` et `details`. Pour nmap, un port donne par exemple `nom` « 8000/tcp » et `statut` « open », « closed » ou « filtered ». Pour adsim, un utilisateur donne `statut` « actif » ou « inactif » selon `enabled`, et ses groupes sont dans `details`. Un XML ou un JSON invalide donne `items` vide et une erreur non vide.

**CLI `cli.py`** : deux sous-commandes.

- `reseau` : une cible obligatoire et `--port` (8000 par défaut).
- `ad` : un sujet parmi `users`, `groups` et `computers`, puis `--format json` ou `text`.

Codes de sortie : 0 succès, 1 échec de l’outil, 2 arguments invalides ou cible refusée. La liste blanche est une constante unique, documentée dans le README : dans le labo, seule l’adresse 127.0.0.1 est autorisée. Une valeur qui n’est pas une adresse IP, comme `localhost`, est refusée sans résolution de nom.

## Les trois MR

### MR1 — feat/subprocess (100 min)

**Mission.** Écris `lancer_outil(args, timeout)`. Il lance l’outil avec `subprocess.run`, capture stdout et stderr en texte, applique le délai et retourne le dictionnaire normalisé décrit plus haut.

**Règle à comprendre.** Ne passe jamais une chaîne à un shell avec une entrée utilisateur. Exemple sans rapport avec ton outil : un script salue quelqu’un en composant la chaîne « echo Bonjour » suivie du prénom, puis la donne à un shell. Si le prénom saisi est « Ana; echo piraté », le shell exécute deux commandes au lieu d’une : c’est une injection de commande. Avec la liste `['echo', 'Bonjour', 'Ana; echo piraté']`, le texte reste un seul argument et rien n’est interprété.

**Tâches**

1. Entraîne-toi avec `echo` et `python3 -c` dans le terminal. Observe stdout, stderr et le code de retour, puis lis la documentation de `subprocess.run` (capture_output, text, returncode).
2. Entraîne-toi sur adsim : `python /app/tools/adsim.py users --format json`, puis la même commande avec `--fail`, puis un argument invalide. Note les trois codes de sortie et le canal de chaque message.
3. Écris `lancer_outil` : pas de shell, capture_output, text, timeout transmis, check laissé à False. Les quatre clés existent même si le programme n’a jamais démarré.
4. Traite séparément le délai dépassé, le programme introuvable et le code de retour non nul. Chaque cas remplit `erreur` avec un message court.
5. Écris les tests W1 à W5 avec `unittest.mock.patch` sur `subprocess.run`. Vérifie la liste d’arguments et le délai reçus par le mock. Aucun processus réel.
6. Ajoute un `.gitignore` pour `__pycache__/`, puis relis `git status` et `git diff`, fais des commits atomiques et relis `git log --oneline`.

**Tests**

- **W1, succès normalisé** : résultat simulé code 0, stdout « ok » ; appel `lancer_outil(['echo', 'ok'], 2)`. Attendu : returncode 0, stdout « ok », stderr vide, erreur None, aucune exception.
- **W2, code de retour non nul** : résultat simulé code 3, stderr « erreur simulée ». Attendu : returncode 3, stderr conservé, erreur non vide, aucune exception. Un code 0 n’est pas une erreur.
- **W3, délai dépassé** : `subprocess.run` lève TimeoutExpired, délai demandé 2 secondes. Attendu : returncode None, erreur non vide qui mentionne le délai, timeout de 2 secondes transmis à `subprocess.run`.
- **W4, outil introuvable** : `subprocess.run` lève FileNotFoundError. Attendu : returncode None, erreur « outil introuvable » ou équivalent court, aucune exception.
- **W5, liste intacte** : entrée `['echo', 'Ana; echo piraté']`. Attendu : `subprocess.run` reçoit exactement cette liste de deux éléments, sans `shell=True` (absent ou False).

**Acceptance**

- W1 à W5 sont découverts par unittest et passent sans outil réel, sans nmap et sans réseau.
- Aucun appel n’utilise `shell=True`.
- `lancer_outil` retourne toujours les quatre clés.
- L’historique montre des commits au message clair, sans `__pycache__` ni fichier non voulu.

**Indice.** Le dictionnaire doit toujours avoir les mêmes quatre clés, même quand le programme n’a jamais démarré. Pense à ce que `subprocess.run` lève dans chaque cas d’échec. Dans les tests, le patch doit viser le nom tel qu’il est utilisé dans ton module (voir « where to patch » dans la documentation de unittest.mock).

### MR2 — feat/cli-perimetre (100 min)

**Mission.** Ajoute la CLI argparse avec les sous-commandes `reseau` et `ad`, la validation de cible par `ipaddress` et la liste blanche de périmètre, un logging basique et des codes de sortie cohérents. Tu pratiques aussi le conflit de fusion et le rebase.

**Tâches**

1. Lis la documentation argparse (sous-commandes, aide). Crée le parseur sans rien lancer et vérifie `python3 cli.py --help`. Respecte les options décrites dans le contrat.
2. Valide la cible avec `ipaddress`. Une valeur refusée donne un message en français ; la liste blanche est une constante documentée.
3. Branche les sous-commandes sur `lancer_outil`. Ajoute les codes 0, 1 et 2, et un logging basique sur stderr : commande lancée, code retourné.
4. Écris les tests W6 à W10 : passe des listes à `main`, remplace `lancer_outil` par un faux pour ne jamais lancer d’outil, et capture stderr avec `contextlib`.
5. Conflit guidé, dans une branche jetable hors MR : modifie la même ligne de `README.md` sur deux branches, fusionne, observe les marqueurs de conflit, résous-le, puis `git add` et `git commit`. Supprime la branche jetable une fois résolue.
6. Rebase : après une évolution de la branche principale, place `feat/cli-perimetre` dessus avec `git rebase`, résous les conflits éventuels et relis `git log --oneline --graph`.

**Tests**

- **W6, sous-commande reseau** : `['reseau', '127.0.0.1', '--port', '8000']`. Attendu : cible 127.0.0.1, port 8000 sous forme d’entier. Sans `--port`, 8000 par défaut.
- **W7, aide** : `['--help']`. Attendu : SystemExit de code 0, aide qui mentionne `reseau` et `ad`.
- **W8, liste blanche** : « 127.0.0.1 » est accepté ; « 127.0.0.2 », « 8.8.8.8 », « localhost » et « 127.0.0.1/32 » sont refusés par ValueError avec un message clair. Aucune résolution de nom.
- **W9, cible refusée sans lancement** : `['reseau', '8.8.8.8']` avec `lancer_outil` remplacé par un faux. Attendu : `main` retourne 2, message sur stderr, `lancer_outil` jamais appelé.
- **W10, codes de retour de main** : `['ad', 'users']` avec `lancer_outil` simulé, une fois code 0, une fois code 3 ou erreur. Attendu : 0 puis 1. Le sujet users est transmis à l’outil.

**Acceptance**

- `python3 -m unittest discover -s tests` passe avec W1 à W10, sans outil réel.
- `--help` fonctionne ; les codes 0, 1 et 2 ainsi que la liste blanche sont documentés dans le README.
- Un refus de cible n’appelle jamais `lancer_outil`.
- Le conflit est résolu, la branche jetable supprimée, et `git log --oneline --graph` reste lisible après rebase.

**Indice.** Une adresse loopback n’est pas automatiquement autorisée : le contrat de la liste blanche dit exactement laquelle. `ipaddress` lève ValueError pour une chaîne qui n’est pas une adresse IP. Pendant le conflit, Git entoure les zones contestées de marqueurs `<<<<<<<`, `=======` et `>>>>>>>` ; tu choisis le texte final.

### MR3 — feat/parsing (70 min)

**Mission.** Analyse la sortie XML de nmap avec `xml.etree.ElementTree` et la sortie JSON d’adsim avec `json.loads`. Normalise les deux dans le format commun, produis un rapport texte sur stdout, écris les tests sur fixtures sans nmap ni réseau, puis exécute les démonstrations hors tests avec les sorties réelles.

**Tâches**

1. Ouvre `fixtures/nmap/open_8000.xml`, `closed_8000.xml` et `mixed.xml`, repère l’hôte, les ports, le protocole et l’état. Écris l’analyse XML sur ces trois fichiers.
2. Traite `broken.xml` : l’erreur d’analyse est capturée et renvoyée comme erreur normalisée, sans plantage.
3. Analyse les JSON adsim (`users.json`, `groups.json`, `computers.json`) avec `json.loads`. Repère les champs `count` et `items`. Traite `broken.json` comme une erreur normalisée.
4. Normalise tous les éléments avec les mêmes clés (source, type, nom, statut, details). Documente les valeurs de statut dans le README.
5. Écris le rapport texte : une ligne par élément, des totaux cohérents, un message clair pour une liste vide. Écris les tests W11 à W16 sur fixtures.
6. Termine le README : périmètre, codes de sortie, tests, démonstrations séparées de la CI, et bilan honnête (ce qui est prouvé par les tests, ce qui est seulement démontré, ce qui reste à faire).

**Tests**

- **W11, XML ouvert** : `open_8000.xml`. Attendu : un élément, source nmap, nom « 8000/tcp », statut « open », erreur None.
- **W12, XML mixte** : `mixed.xml`, trois ports open, closed, filtered. Attendu : trois éléments dans l’ordre du fichier, avec ces trois statuts ; erreur None.
- **W13, XML cassé** : `broken.xml`. Attendu : aucune exception, items vide, erreur non vide.
- **W14, JSON adsim valide** : `users.json`. Attendu : nombre d’éléments égal au champ `count` du fichier ; statut « actif » ou « inactif » selon `enabled` ; groupes conservés, liste vide si aucun groupe.
- **W15, JSON invalide** : `broken.json`. Attendu : items vide, erreur non vide, aucune exception.
- **W16, rapport** : trois éléments normalisés (deux open, un closed), puis liste vide. Attendu : une ligne par élément dans l’ordre, total cohérent (3 éléments, 2 open, 1 closed) ; pour la liste vide, un message indique qu’aucun élément n’a été trouvé.

**Démonstrations (hors tests, dans le conteneur)**

- **D1, nmap réel sur le labo** : démarre le labo HTTP avec son bouton (127.0.0.1:8000), lance `nmap -sT -p 8000 -oX - 127.0.0.1` via `lancer_outil`, puis passe la sortie XML au parseur. Attendu : le port 8000 est open. Si le labo est arrêté, le résultat doit être différent (closed ou erreur) ; explique la différence dans le bilan.
- **D2, adsim réel, sortie JSON** : lance `python /app/tools/adsim.py users --format json` via `lancer_outil`, puis passe la sortie au parseur. Attendu : éléments normalisés, erreur None, nombre égal au champ `count` de la sortie réelle.
- **D3, erreurs réelles d’adsim** : adsim avec `--fail` (code 3), puis adsim avec un délai supérieur au timeout de `lancer_outil`. Attendu : le code 3 est normalisé en erreur sans trace Python ; le délai dépassé est normalisé en erreur de timeout.

**Acceptance**

- W11 à W16 passent avec les fixtures seules, sans nmap, sans réseau et sans adsim.
- Un XML ou un JSON cassé ne fait jamais planter le programme.
- D1 à D3 sont exécutées dans le conteneur, hors `unittest discover`, et leurs sorties réelles sont consignées dans le README ou le bilan.
- Le bilan distingue tests unitaires, démonstrations réelles et limites.

**Indice.** Les fixtures sont la meilleure documentation : ouvre-les avant d’écrire la moindre recherche d’élément. Décide une seule fois les clés communes, écris-les dans le README, puis fais passer nmap et adsim par ce même format.

## Méthode Git

Chaque MR vient d’une branche créée depuis la branche principale à jour : `git switch main`, `git pull --ff-only`, puis `git switch -c NOM_BRANCHE`. Avant chaque commit, relis `git status` et `git diff`, puis ajoute explicitement les fichiers prévus. Lance les tests localement (`python3 -m unittest discover -s tests`) avant de pousser. Une fois la MR ouverte, relis le diff et fusionne uniquement quand le dernier commit est vert, si ton école fournit un runner. Un test local réussi ne prouve pas que GitLab autorise la fusion.

Le conflit et le rebase de la MR2 se pratiquent sur ton propre dépôt, dans une branche jetable ou sur ta branche de MR avant la fusion. Ne réécris jamais l’historique d’une branche déjà partagée sans le dire.

## Repères de temps

Préparation du dépôt, vérifications et lecture du contrat : 20 min. MR1 subprocess et tests : 100 min. MR2 CLI, liste blanche, conflit et rebase : 100 min. MR3 parsing, rapport, démonstrations et bilan : 70 min. Marge de débogage et bilan honnête : 10 min. Total : 300 min.

## Livrables et limites

Livre `toolwrap.py`, `cli.py`, les tests dans `tests/`, les fixtures copiées, un `.gitignore`, un README clair, trois MR successives et un bilan honnête. Ce bilan doit distinguer ce que les tests prouvent (la logique du wrapper et des parseurs, sur des données contrôlées), ce que les démonstrations montrent (nmap sur le labo, adsim fictif) et ce qui reste à faire.

Limites à garder en tête :

- adsim est un simulateur FICTIF (domaine LAB.LOCAL). Il ne se connecte à aucun annuaire réel. Le vrai Active Directory sera traité dans le projet final, sur un domaine qui t’appartient.
- La cible reste 127.0.0.1. La liste blanche ne doit pas être élargie pendant ce parcours.
- Les tests mockent `subprocess.run` : ils prouvent la logique du wrapper, pas le comportement réel de nmap ou d’adsim. C’est le rôle des démonstrations.
- nmap n’est pas disponible sur un runner GitLab : les tests obligatoires ne l’appellent jamais.
- Un port open ne prouve ni la nature du service ni une vulnérabilité. Une sortie fictive ne prouve rien sur un vrai domaine.
