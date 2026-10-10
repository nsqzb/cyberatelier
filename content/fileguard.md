# FileGuard — manifeste d’intégrité SHA-256

**Durée : 5 heures · Niveau débutant · 3 merge requests**

Tu vas créer puis vérifier un manifeste d’intégrité pour quelques fichiers fictifs. Tu utiliseras hashlib, pathlib et json, avec un petit dossier de fixtures copié dans ton dépôt. Le périmètre reste simple : fichiers réguliers au premier niveau, sans parcours récursif.

## Contrat du manifeste

Ton programme se nomme fileguard.py. Le dossier à examiner est un chemin explicite fourni au programme ou défini comme constante. Le manifeste est un fichier JSON déterministe nommé manifest.json, placé hors du dossier surveillé ou exclu explicitement de son inventaire. Il ne doit jamais contenir sa propre empreinte.

Pour chaque fichier régulier directement dans le dossier, calcule SHA-256 sur les octets lus en mode binaire. Le format exact est un objet JSON avec une clé schema dont la valeur est 1, puis une clé files qui contient une liste d’objets. Chaque objet de files a exactement deux clés : name, le nom simple du fichier, et sha256, l’empreinte hexadécimale minuscule de 64 caractères. Exemple de forme, sans données à utiliser comme solution :

    {"schema": 1, "files": [{"name": "message.txt", "sha256": "…"}]}

La liste des entrées est triée par name. Le JSON est écrit avec une indentation stable, des clés dans l’ordre schema puis files et, dans chaque entrée, name puis sha256, ainsi qu’un saut de ligne final. Ne stocke pas de chemin absolu ni de donnée secrète.

À la vérification, compare l’inventaire courant au manifeste et distingue exactement les catégories inchangé, modifié, supprimé et ajouté. Les nouveaux fichiers réguliers du premier niveau sont signalés comme ajoutés. Les fichiers présents dans le manifeste mais absents du dossier sont supprimés. Un nom présent des deux côtés avec des empreintes différentes est modifié. Le manifeste lui-même est exclu.

Les liens symboliques sont hors périmètre : refuse-les clairement, comme recommandé ici, et teste ce choix. Les sous-dossiers ne sont pas parcourus. Le format de manifeste ne certifie pas son origine : un manifeste stocké à côté des fichiers peut être modifié par la même personne.

<!-- BEGIN GENERATED EXERCISES -->
## Comment travailler un exercice

Chaque mission construit une partie du projet. Commence par « Avant de commencer », puis avance palier par palier. Les durées sont des repères : prends le temps de comprendre chaque résultat.

1. Lis l’objectif et les fichiers concernés. Un fichier indiqué comme « à créer » n’est pas fourni : c’est toi qui l’écris.
2. Les cartes de tests donnent l’entrée et le résultat attendu. Écris les tests correspondants dans le fichier indiqué ; cocher un palier ne les exécute pas. Avec unittest, « Ran 0 tests » signifie qu’aucun test n’a été exécuté : ce n’est pas une validation. Un cas décrit peut contenir plusieurs valeurs ; le nombre de méthodes Python n’est donc pas forcément le nombre d’identifiants.
3. Suis les actions numérotées. Les blocs Python se placent dans l’éditeur ; les commandes se lancent au moment demandé. Relis les blocs Git : des modifications et des actions dans GitHub/GitLab peuvent être nécessaires entre deux commandes.
4. Vérifie le résultat indiqué avant de poursuivre. Un échec attendu (phase rouge, argument refusé ou conflit volontaire) est expliqué dans le palier.
5. Si tu bloques, lis la dernière ligne de l’erreur, compare l’entrée et l’attendu, puis ouvre l’indice. Fais un petit changement et relance.

### Le bon endroit pour chaque action

Sur ton Mac, ouvre `workspaces/fileguard` dans VS Code. Dans Cyber Atelier, utilise l’éditeur et la console de **Coder**, avec `cwd` sur `.` (la racine du dépôt). Fais la préparation de **Environnement** avant MR1 ; la mission crée ensuite sa branche.

Le code Python se place dans l’éditeur. Les commandes `docker compose ...` se lancent sur ton Mac depuis `cyberatelier` ; `/app/...` existe dans le conteneur. Le laboratoire interrogé doit tourner dans le même environnement que ton programme.

La console web repart à neuf à chaque exécution : un `cd`, une activation de venv ou `echo $?` ne se transmet pas à la commande suivante. Lance le programme et `echo $?` ensemble quand le palier le demande. Le nombre affiché par echo est celui du programme ; la console peut afficher code 0 pour echo lui-même.

Un venv créé sur le Mac ne fonctionne pas dans le conteneur : utilise `python3` dans ce dernier. Remplace `main` par `master` si nécessaire. Si une branche existe déjà, reprends-la avec `git switch NOM` sans `-c`. Après chaque fusion, actualise la branche principale avant la mission suivante.

### Les mots utiles

**Contrat.** Les règles à respecter : arguments reçus, valeur retournée, erreurs et cas limites. Tu choisis le code qui respecte ces règles.

**Test à écrire.** Une entrée et un résultat attendu à transformer en vérification Python. Les identifiants S1, T1, etc. désignent des cas à couvrir, pas des tests déjà installés.

**Rouge puis vert.** Écris la vérification, lance-la et comprends son échec. Écris ensuite le code, relance et garde les vérifications précédentes. Un nouveau cas peut déjà passer : ne casse pas le code pour le rendre rouge.

**Fonction pure.** Une fonction qui calcule son résultat depuis ses arguments, sans accéder au réseau ou au disque et sans modifier les données reçues.

**Exception.** Une erreur signalée par Python, par exemple ValueError. « Lever » signale l’erreur ; « attraper » la traite avec except. Si le contrat attend une exception, la voir est une réussite du test.

**Fixture.** Un fichier de données fictives fourni pour rendre un essai reproductible. Une fixture XML ou JSON remplace la sortie d’un outil réel dans les tests.

**Mock.** Un faux temporaire qui remplace un appel pendant le test. Il permet de choisir le résultat et de vérifier les arguments sans lancer de réseau ou de processus réel.

**CLI.** L’interface en ligne de commande : tu lances un programme avec des arguments. --help décrit les options ; argparse les lit et vérifie leur forme.

**Code de sortie.** Le nombre rendu au terminal quand le programme se termine. 0 signifie réussite ; une valeur non nulle signale un échec ou un usage incorrect selon le contrat.

**Commit.** Un point enregistré dans l’historique Git. git add choisit les fichiers ; git diff --staged montre le contenu choisi ; git commit l’enregistre.

**PR / MR.** Une demande de fusion de ta branche vers la principale. GitHub dit pull request (PR), GitLab merge request (MR). L’ouvrir, la relire et la fusionner sont trois actions distinctes.

**Pipeline / job.** GitLab exécute le pipeline : un ensemble de tâches, appelées jobs. La CI est cette exécution automatique. Un fichier de configuration présent ne prouve pas qu’un job a tourné.

**Artefact.** Un fichier conservé par un job GitLab après son exécution, par exemple le ZIP de livraison.

**Empreinte / manifeste.** L’empreinte SHA-256 est calculée à partir des octets d’un fichier. Le manifeste mémorise des noms et leurs empreintes pour comparer plus tard.

**Parser.** Lire un format structuré pour obtenir des données Python. JSON donne des dictionnaires et listes ; XML donne un arbre de balises et d’attributs.

**Package / venv.** Un package regroupe des modules Python dans un dossier. Un venv est un environnement Python séparé, que tu ne livres pas dans Git.

**Déterministe.** Avec les mêmes entrées, le résultat est identique. Pour tester un rapport daté, le test fournit la date au lieu de lire l’heure actuelle.

**stderr / stdout.** Deux sorties du programme : stdout porte le résultat normal, stderr les messages d’erreur et les traces. Le code de sortie reste un nombre séparé.

**Loopback.** L’adresse de la machine où tourne le programme. 127.0.0.1 dans Docker désigne le conteneur ; sur le Mac, elle désigne le Mac ; dans la CI, elle désigne le runner.

## Les trois MR

Les durées sont des repères compris dans les 300 minutes du parcours.

### MR1 — feat/empreinte (85 min)

Une empreinte décrit les octets d’un fichier ; elle servira à construire le manifeste en MR2. Avance dans l’ordre des paliers et vérifie chaque résultat avant de poursuivre.

**Avant de commencer**

- Point de départ : Un dépôt cloné ; tu disposes de Python 3 et Git. Les tests créeront eux-mêmes leurs fichiers.
- Ce que tu vas produire : fileguard.py, verification.py et .gitlab-ci.yml : calculer et tester une empreinte SHA-256.
- Pourquoi : Une empreinte décrit les octets d’un fichier ; elle servira à construire le manifeste en MR2.
- Commande des tests depuis la racine : `python3 verification.py`. Les cas ci-dessous sont à écrire par toi.

#### Palier 1 — Prépare la branche feat/empreinte (6 min)

Partir d’un dépôt propre, sur une branche dédiée à cette MR.

**Où tu travailles :** Dépôt

**Actions dans l’ordre**

1. Ouvre le dossier workspaces/fileguard dans le terminal de VS Code (ou, dans le conteneur, docker compose exec atelier bash puis cd /workspaces/fileguard).
2. Si le dépôt n’est pas encore cloné, fais d’abord l’étape « Cloner le dépôt » de l’onglet Environnement.
3. Crée la branche de MR1 depuis la branche principale, puis vérifie où tu es.

**Terminal · Relire l’état du dépôt**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git status
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git switch -c feat/empreinte
```

**Terminal · Relire l’état du dépôt**

```bash
git status
```

**Tu sais que c’est bon quand :** git status affiche « On branch feat/empreinte » et « nothing to commit ».

*Indice si tu bloques :* Si Git répond « not a git repository », tu n’es pas dans le dossier du dépôt. Si la branche existe déjà, utilise git switch feat/empreinte, sans -c.

#### Palier 2 — Des octets, pas du texte (10 min)

Comprendre pourquoi on lit un fichier en mode binaire pour obtenir ses octets exacts.

**Où tu travailles :** Terminal : exemple binaire

**Actions dans l’ordre**

1. Un fichier est une suite d’octets. Le mode texte (par défaut) décode le contenu et peut traiter les fins de ligne ; le mode binaire (rb, wb) donne les octets tels quels.
2. Lance l’exemple ci-dessous dans le terminal : il crée un dossier temporaire, écrit un fichier de fruits, le relit en octets et le supprime à la sortie du bloc with.
3. Compare b"pomme" à "pomme" : le premier est de type bytes, le second de type str. Aucun fichier ne reste dans ton dépôt.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -c "from pathlib import Path; from tempfile import TemporaryDirectory
with TemporaryDirectory() as dossier:
    p = Path(dossier) / 'fruits.bin'
    p.write_bytes(b'pomme')
    d = p.read_bytes()
    print(d, type(d))"
```

**Tu sais que c’est bon quand :** Tu vois b'pomme' et le type <class 'bytes'>.

*Indice si tu bloques :* Le préfixe b devant les guillemets désigne des octets. Une chaîne de texte (str) n’est pas acceptée par hashlib : il faut des octets.

#### Palier 3 — Premier test rouge, puis premier code vert : F1 (14 min)

Écrire le test avant la fonction, voir l’échec, puis faire passer le test avec le minimum de code.

**Où tu travailles :** fileguard.py ; verification.py

**Pour comprendre**

- Notion : un fichier temporaire est créé par tempfile et supprimé à la fin du bloc with. Exemple sans rapport avec l’exercice : un dossier temporaire contenant un fichier de fruits.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**F1 — Empreinte du fichier vide**
- Entrée : Fichier temporaire de zéro octet
- Résultat attendu : e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

**Actions dans l’ordre**

1. Dans verification.py, importe unittest, crée une classe héritant de unittest.TestCase et des méthodes commençant par test_. Ajoute le point d’entrée unittest.main() sous la garde if __name__ == "__main__". Sans ce lancement, python3 verification.py peut finir avec 0 sans exécuter aucun test.
2. Crée verification.py avec une classe de test unittest. Ajoute le test F1 : un fichier de zéro octet, dans un dossier temporaire créé par le test, comparé à l’oracle du fichier vide écrit en constante dans le test.
3. Lance le test : il échoue, parce que fileguard.py n’existe pas encore. C’est la phase rouge, elle est normale.
4. Crée fileguard.py avec une fonction calculer_sha256(chemin) (ce nom est proposé ; tu peux le garder). Elle ouvre le fichier en mode binaire, calcule le SHA-256 des octets et renvoie l’empreinte en hexadécimal minuscule. Relance : F1 passe (phase verte).
5. Commit de ce palier.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -c "import tempfile, pathlib; d = tempfile.TemporaryDirectory(); p = pathlib.Path(d.name) / 'fruits.txt'; p.write_bytes(b'pomme'); print(p.read_bytes())"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add fileguard.py verification.py
git commit -m "Calcule l’empreinte SHA-256 du fichier vide"
```

**Tu sais que c’est bon quand :** F1 passe ; python3 verification.py se termine sans erreur ; git log --oneline montre le nouveau commit.

*Indice si tu bloques :* Phase rouge : une erreur du type ImportError ou NameError est l’échec attendu. Pour la phase verte, la documentation de hashlib et celle d’open donnent les deux outils dont tu as besoin ; l’oracle reste une constante du test.

#### Palier 4 — F2 : les trois octets abc, sans saut de ligne (14 min)

Vérifier que l’empreinte dépend des octets exacts, sans fin de ligne ajoutée.

**Où tu travailles :** fileguard.py ; verification.py

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**F2 — Empreinte des trois octets abc**
- Entrée : Fichier temporaire contenant exactement b"abc", sans saut de ligne final
- Résultat attendu : ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad

**Actions dans l’ordre**

1. Ajoute le test F2 : un fichier temporaire qui contient exactement les octets de « abc », sans saut de ligne final. Compare à l’oracle abc, écrit en constante dans le test.
2. Lance les tests. S’il passe tout de suite, c’est possible : écris le test quand même et note-le dans ton message de commit.
3. Si F2 échoue, relis comment ton fichier est ouvert et écrit. Ne change jamais la constante de l’oracle pour faire passer le test.
4. Une fois F1 et F2 verts, commit.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add fileguard.py verification.py
git commit -m "Vérifie l’empreinte des trois octets abc"
```

**Tu sais que c’est bon quand :** F1 et F2 passent, et le code n’a pas été modifié pour contourner une constante.

*Indice si tu bloques :* Pour écrire exactement trois octets, utilise un littéral b suivi de guillemets, sans \n. Vérifie que le test lit les octets sans conversion de texte.

#### Palier 5 — F3 : deux contenus identiques, deux empreintes identiques (14 min)

Écrire un test qui crée lui-même ses fichiers et compare deux résultats.

**Où tu travailles :** fileguard.py ; verification.py

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**F3 — Contenus identiques**
- Entrée : Deux fichiers temporaires contenant les mêmes octets
- Résultat attendu : Empreintes identiques.

**Actions dans l’ordre**

1. Ajoute le test F3 : dans un même dossier temporaire, crée deux fichiers qui ont les mêmes octets, calcule leurs empreintes et compare-les.
2. Le test ne lit ni le dossier personnel, ni un journal, ni une fixture : tout ce dont il a besoin est créé dans le dossier temporaire.
3. Lance les tests, vérifie que F1, F2 et F3 passent, puis commit.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add fileguard.py verification.py
git commit -m "Vérifie que deux contenus identiques ont la même empreinte"
```

**Tu sais que c’est bon quand :** F1, F2 et F3 passent ; git log --oneline montre le nouveau commit.

*Indice si tu bloques :* Écris les mêmes octets dans deux noms différents, puis compare les deux résultats de ta fonction avec assertEqual.

#### Palier 6 — Faire tourner la même suite dans la CI (15 min)

Comprendre ce que la CI exécute, et ce qu’elle ne prouve pas encore.

**Où tu travailles :** .gitlab-ci.yml

**Actions dans l’ordre**

1. Crée .gitlab-ci.yml à la racine du dépôt, avec un seul job dont la ligne script lance uniquement python3 verification.py. Le job ne copie aucune fixture et ne lit aucun chemin du portail.
2. Le YAML se lit à l’indentation (deux espaces par niveau). Exemple sans rapport avec l’exercice : un job qui affiche un mot.
3. Lance la même commande en local avant de pousser.
4. Distingue quatre niveaux : test local réussi ; pipeline GitLab réellement exécuté ; fusion autorisée par les règles de l’école ; case cochée dans Cyber Atelier, qui ne vérifie rien. Un fichier .gitlab-ci.yml présent ne prouve pas qu’un pipeline a tourné.
5. Commit ce fichier.

**Éditeur · Exemple YAML à lire**

Éditeur : exemple de syntaxe, à adapter ; ce bloc ne se lance pas dans le terminal.

```yaml
job-bonjour:
  script:
    - echo "bonjour"
```

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add .gitlab-ci.yml
git commit -m "Ajoute la CI qui lance la suite locale"
```

**Tu sais que c’est bon quand :** Le fichier est commité. Le pipeline n’est confirmé que lorsque GitLab affiche un job exécuté et vert pour ta branche.

*Indice si tu bloques :* Si GitLab ne lance aucun pipeline, vérifie que le fichier est à la racine du dépôt, que la branche est poussée et que le runner de l’école est actif sur les branches non protégées.

#### Palier 7 — Livre la MR1 sans confondre test local et fusion (12 min)

Relire le diff, pousser la branche, ouvrir la MR et ne fusionner que le dernier commit vert.

**Où tu travailles :** MR GitLab

**Actions dans l’ordre**

1. Regarde ce que tu livres : fichiers modifiés et historique. La MR doit contenir fileguard.py, verification.py et .gitlab-ci.yml, sans __pycache__.
2. Pousse la branche et ouvre la merge request vers main.
3. Relis le diff comme s’il était écrit par quelqu’un d’autre.
4. Fusionne seulement si le dernier commit a passé le pipeline GitLab et que les règles de l’école l’autorisent. Vert en local ne suffit pas.
5. Après la fusion, reviens sur main et mets-la à jour avant MR2.

**Terminal · Relire l’état du dépôt**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git status
git diff main --stat
```

**Terminal · Publier la branche ou ouvrir la demande de fusion**

```bash
git push -u origin feat/empreinte
```

**Terminal · Après la fusion : actualiser la principale**

```bash
git switch main
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git pull --ff-only
```

**Tu sais que c’est bon quand :** La MR ne contient que les trois fichiers attendus, et ta branche main locale contient la fusion (git log --oneline).

*Indice si tu bloques :* Si le push est refusé, vérifie le nom de la branche avec git branch. Ne fusionne pas avant d’avoir relu le diff et vu le pipeline.

**Avant de livrer**

- La fonction lit les octets et renvoie une empreinte SHA-256 hexadécimale minuscule.
- Les tests comparent aux deux oracles fixes fournis ; la fonction testée ne calcule pas elle-même les valeurs attendues.
- Les tests ne dépendent pas du dossier personnel, d’un journal ou d’une fixture externe.
- La CI exécute uniquement la suite locale (python3 verification.py), sans service distant ni chemin du portail.

### MR2 — feat/manifest (85 min)

Le manifeste mémorise l’état de référence qui sera comparé au dossier en MR3. Avance dans l’ordre des paliers et vérifie chaque résultat avant de poursuivre.

**Avant de commencer**

- Point de départ : MR1 fusionnée ; F1 à F3 passent.
- Ce que tu vas produire : L’inventaire et l’écriture de manifest.json dans fileguard.py ; F4 à F7 ; copies des fixtures.
- Pourquoi : Le manifeste mémorise l’état de référence qui sera comparé au dossier en MR3.
- Commande des tests depuis la racine : `python3 verification.py`. Les cas ci-dessous sont à écrire par toi.

#### Palier 1 — Repars de main à jour et crée feat/manifest (6 min)

Partir de la MR1 fusionnée, pas d’une branche ancienne.

**Où tu travailles :** Dépôt

**Actions dans l’ordre**

1. Reviens sur main et mets-la à jour, puis crée la branche de MR2.
2. Vérifie que ton dépôt est propre avant de commencer.

**Terminal · Après la fusion : actualiser la principale**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git switch main
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git pull --ff-only
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git switch -c feat/manifest
```

**Terminal · Relire l’état du dépôt**

```bash
git status
```

**Tu sais que c’est bon quand :** git status affiche « On branch feat/manifest » et « nothing to commit ».

*Indice si tu bloques :* Si git pull --ff-only refuse, c’est que main a divergé : ne force rien, demande de l’aide avant de continuer.

#### Palier 2 — Copie les fixtures fictives dans ton dépôt (8 min)

Disposer d’un petit dossier d’exemple, relisible, dans le dépôt.

**Où tu travailles :** fixtures/

**Actions dans l’ordre**

1. Sur le Mac, reste dans workspaces/fileguard : ../../ remonte jusqu’au projet Cyber Atelier, où se trouve fixtures/integrity. Dans le conteneur, remplace ../../fixtures par /app/fixtures.
2. La commande crée fixtures/, copie les trois fichiers fictifs, puis rend les copies modifiables (chmod u+w). Les originaux restent en lecture seule.
3. Vérifie le résultat, puis commit les copies : elles font partie de la MR2.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
pwd
```

**Terminal · Commande à lancer au moment indiqué**

Terminal de ton Mac, depuis workspaces/fileguard. Dans le conteneur, remplace ../../fixtures par /app/fixtures ; garde le reste de la commande. Les copies vont dans ton dépôt.

```bash
mkdir -p fixtures && cp ../../fixtures/integrity/* fixtures/ && chmod u+w fixtures/*
```

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
ls -l fixtures
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add fixtures
git commit -m "Ajoute les fixtures fictives FileGuard"
```

**Tu sais que c’est bon quand :** ls fixtures affiche README.txt, message.txt et settings.ini ; git log --oneline montre le commit.

*Indice si tu bloques :* Si cp répond « No such file or directory », pwd te dit où tu es : la commande doit être lancée depuis workspaces/fileguard. Les fixtures ne sont pas présumées présentes sur le runner : les tests, eux, créent leurs propres fichiers.

#### Palier 3 — Un JSON stable : la forme avant le code (10 min)

Savoir écrire exactement le format du contrat, avec un ordre de clés et une fin de ligne stables.

**Où tu travailles :** Forme de manifest.json

**Pour comprendre**

- Notion : json.dumps écrit un dictionnaire dans l’ordre où ses clés ont été ajoutées. Avec indent=2, la sortie est lisible et stable. Exemple sans rapport avec l’exercice : un panier de fruits.

**Actions dans l’ordre**

1. Contrat : un objet JSON avec la clé schema (valeur 1), puis la clé files : une liste d’objets. Chaque objet a exactement deux clés, name (nom simple) puis sha256 (64 caractères hexadécimaux minuscules). Le fichier se termine par un saut de ligne.
2. Tu n’as rien à coder à ce palier : écris à la main, sur un exemple fictif, un JSON qui respecte ce contrat, puis compare-le avec la forme donnée dans le guide.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -c "import json; print(json.dumps({'b': 1, 'a': 2}, indent=2))"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -c "import json; print(json.dumps({'schema': 1, 'files': []}, indent=2))"
```

**Tu sais que c’est bon quand :** Tu sais dire pourquoi sort_keys=True n’est pas adapté ici : il réordonnerait schema et files, alors que le contrat impose schema puis files.

*Indice si tu bloques :* Ne mets pas de chemin absolu dans le JSON. L’empreinte n’est pas encore calculée : ce palier ne sert qu’à fixer la forme.

#### Palier 4 — F4 : dossier vide, premier niveau seulement (14 min)

Lister les fichiers réguliers du premier niveau avec pathlib, sans entrer dans les sous-dossiers.

**Où tu travailles :** fileguard.py ; verification.py

**Pour comprendre**

- Notion : pathlib.Path(dossier).iterdir() donne les entrées directes d’un dossier. Exemple sans rapport : lister les fichiers d’un dossier fruits.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**F4 — Dossier vide**
- Entrée : Dossier temporaire vide
- Résultat attendu : Manifeste valide avec une liste vide.

**Actions dans l’ordre**

1. Ajoute le test F4 : un dossier temporaire vide donne un manifeste valide avec une liste vide. Lance-le, il échoue parce que la fonction n’existe pas encore.
2. Écris le plus petit code qui fait passer F4. Ne parcours aucun sous-dossier.
3. Commit ce palier.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -c "from pathlib import Path; [print(c.name, c.is_file()) for c in Path('.').iterdir()]"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add fileguard.py verification.py
git commit -m "Produit un manifeste vide pour un dossier vide"
```

**Tu sais que c’est bon quand :** F1 à F4 passent ; git log --oneline montre le commit.

*Indice si tu bloques :* Un sous-dossier apparaît dans iterdir() mais n’est pas un fichier régulier. Vérifie-le avant de l’ajouter à l’inventaire.

#### Palier 5 — F5 : trier les noms et écrire le fichier (15 min)

Obtenir le même fichier quel que soit l’ordre de création des fichiers.

**Où tu travailles :** fileguard.py ; verification.py

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**F5 — Ordre déterministe**
- Entrée : Fichiers créés dans un ordre non trié
- Résultat attendu : Entrées JSON triées par nom.

**Actions dans l’ordre**

1. Ajoute le test F5 : crée plusieurs fichiers dans un ordre non trié, génère le manifeste, puis vérifie que les entrées sont triées par nom.
2. Trie les noms avant l’écriture, avec sorted(). Écris le fichier en UTF-8 et ajoute un saut de ligne final, puis vérifie que le contenu correspond au contrat.
3. Le nom de fichier du manifeste est manifest.json. Ce palier ne règle pas encore l’exclusion : elle viendra à F6.
4. Le guide demande de décider et de documenter si la commande crée ou remplace le manifeste. Note ta décision maintenant ; tu la rédigeras dans le README en MR3.
5. Commit ce palier.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -c "print(sorted(['zeta.txt', 'alpha.txt']))"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add fileguard.py verification.py
git commit -m "Trie les entrées du manifeste par nom"
```

**Tu sais que c’est bon quand :** F1 à F5 passent ; le contenu du manifeste est identique d’un lancement à l’autre sur le même dossier.

*Indice si tu bloques :* Trie les noms, pas les empreintes. json.dump n’écrit pas de saut de ligne final : ajoute-le toi-même.

#### Palier 6 — F6 : le manifeste ne se compte pas lui-même (12 min)

Exclure le manifeste de son propre inventaire, même quand il se trouve dans le dossier examiné.

**Où tu travailles :** fileguard.py ; verification.py

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**F6 — Exclusion du manifeste**
- Entrée : Manifeste écrit au même endroit que les données
- Résultat attendu : Le manifeste ne figure pas dans ses propres entrées.

**Actions dans l’ordre**

1. Ajoute le test F6 : écris le manifeste dans le même dossier que les données, relance l’inventaire, et vérifie que manifest.json n’apparaît pas dans ses propres entrées.
2. Écris le plus petit code qui fait passer F6. La comparaison se fait sur le nom simple du fichier, pas sur un chemin complet.
3. Commit ce palier.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -c "from pathlib import Path; print(Path('dossier/manifest.json').name)"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add fileguard.py verification.py
git commit -m "Exclut le manifeste de son propre inventaire"
```

**Tu sais que c’est bon quand :** F1 à F6 passent ; manifest.json n’apparaît jamais dans les entrées.

*Indice si tu bloques :* Le nom simple d’un fichier est accessible via l’attribut name d’un Path. Compare-le à la constante du nom du manifeste.

#### Palier 7 — F7 : refuser les liens symboliques (12 min)

Refuser clairement un lien symbolique, et tester ce refus quand le système permet d’en créer.

**Où tu travailles :** fileguard.py ; verification.py

**Pour comprendre**

- Notion : os.symlink(cible, lien) crée un lien dans un dossier temporaire. Exemple sans rapport : un raccourci vers un fichier de fruits. Pathlib.is_symlink() dit si une entrée est un lien.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**F7 — Lien symbolique**
- Entrée : Lien symbolique vers un fichier temporaire, si supporté
- Résultat attendu : Refus clair selon le contrat.

**Actions dans l’ordre**

1. Ajoute le test F7 : crée un lien vers un fichier temporaire. Si le système refuse de créer le lien, le test se termine proprement avec skipTest et un message clair.
2. Écris le code qui refuse le lien avec une erreur explicite dont le message indique qu’un lien symbolique est refusé. Pour le contrat, choisis un type d’exception et documente-le dans le README en MR3.
3. Vérifie que le test passe quand le lien existe, et que l’inventaire ne le suit pas. Commit.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -c "import os, tempfile, pathlib; d = tempfile.mkdtemp(); os.symlink(pathlib.Path(d) / 'a', pathlib.Path(d) / 'lien'); print(pathlib.Path(d, 'lien').is_symlink())"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add fileguard.py verification.py
git commit -m "Refuse les liens symboliques dans l’inventaire"
```

**Tu sais que c’est bon quand :** F1 à F7 passent ; la sortie de l’exemple est True pour le lien.

*Indice si tu bloques :* Vérifie is_symlink() avant is_file() : is_file() suit le lien et répondrait sur la cible. Un test qui ne peut pas créer de lien doit être ignoré avec un message, pas réussir silencieusement.

#### Palier 8 — Livre la MR2 (8 min)

Relire le diff, pousser feat/manifest, ouvrir la MR et ne pas livrer de fichiers générés.

**Où tu travailles :** MR GitLab

**Actions dans l’ordre**

1. Regarde le diff : fileguard.py, verification.py, fixtures/. Un manifest.json généré par tes essais ne doit pas être commité.
2. Pousse la branche et ouvre la merge request vers main.
3. Attends le pipeline vert dans GitLab, puis fusionne seulement si les règles de l’école l’autorisent. Vert en local ne suffit pas.
4. Après la fusion, reviens sur main et mets-la à jour avant MR3.

**Terminal · Relire l’état du dépôt**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git status
git diff main --stat
```

**Terminal · Publier la branche ou ouvrir la demande de fusion**

```bash
git push -u origin feat/manifest
```

**Terminal · Après la fusion : actualiser la principale**

```bash
git switch main
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git pull --ff-only
```

**Tu sais que c’est bon quand :** git status ne montre aucun manifest.json non suivi à commiter ; la MR contient les fichiers attendus ; main locale contient la fusion.

*Indice si tu bloques :* Si git status montre manifest.json, ajoute-le à .gitignore plutôt que de le commiter, ou supprime-le avant le commit.

**Avant de livrer**

- Chaque entrée désigne un fichier régulier directement dans le dossier et ne contient aucun chemin absolu.
- Le manifeste est déterministe et exclu de l’inventaire.
- Aucun lien n’est suivi et aucun sous-dossier n’est parcouru.
- Les fixtures fictives (README.txt, settings.ini, message.txt) sont copiées dans le dépôt, avec des droits d’écriture pour tes copies.

### MR3 — feat/comparaison (80 min)

Tu distingues inchangé, modifié, supprimé et ajouté puis vérifies le résultat en démonstration. Avance dans l’ordre des paliers et vérifie chaque résultat avant de poursuivre.

**Avant de commencer**

- Point de départ : MR2 fusionnée ; l’inventaire produit un manifeste conforme.
- Ce que tu vas produire : La comparaison, les commandes creer et verifier, F8 à F14 et README.md.
- Pourquoi : Tu distingues inchangé, modifié, supprimé et ajouté puis vérifies le résultat en démonstration.
- Commande des tests depuis la racine : `python3 verification.py`. Les cas ci-dessous sont à écrire par toi.

#### Palier 1 — Repars de main à jour et crée feat/comparaison (5 min)

Partir de la MR2 fusionnée, pour que la comparaison s’appuie sur le bon code.

**Où tu travailles :** Dépôt

**Actions dans l’ordre**

1. Reviens sur main, mets-la à jour, puis crée la branche de MR3.
2. Vérifie que ton dépôt est propre.

**Terminal · Après la fusion : actualiser la principale**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git switch main
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git pull --ff-only
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git switch -c feat/comparaison
```

**Terminal · Relire l’état du dépôt**

```bash
git status
```

**Tu sais que c’est bon quand :** git status affiche « On branch feat/comparaison » et « nothing to commit ».

*Indice si tu bloques :* Si la branche existe déjà, utilise git switch feat/comparaison, sans -c. Vérifie d’abord que MR2 apparaît bien dans git log.

#### Palier 2 — Comparer des ensembles de noms (8 min)

Séparer présence et absence des noms, puis comparer les empreintes nom par nom.

**Où tu travailles :** Contrat de comparer

**Pour comprendre**

- Notion : un set ne contient que des valeurs distinctes ; la différence ensembliste donne ce qui est dans l’un et pas dans l’autre. Exemple sans rapport : deux paniers de fruits.

**Actions dans l’ordre**

1. Contrat proposé pour la comparaison : une fonction comparer(manifeste, inventaire) qui renvoie un dictionnaire aux clés inchange, modifie, supprime et ajoute, chacune avec une liste triée de noms. Un nom présent des deux côtés avec une empreinte différente est modifié.
2. Le manifeste lui-même est ignoré : aucune entrée qui le concerne ne peut apparaître dans une catégorie.
3. Pas de code à ce palier : vérifie sur l’exemple de commande que tu sais ce qu’est une différence et une intersection.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -c "a = {'pomme', 'poire'}; b = {'poire', 'kiwi'}; print(a - b, b - a, a & b)"
```

**Tu sais que c’est bon quand :** Tu sais dire, pour un nom, s’il est absent d’un côté, ou présent des deux côtés avec des empreintes différentes.

*Indice si tu bloques :* Garde deux vues séparées : l’ensemble des noms d’un côté, un dictionnaire nom vers empreinte de l’autre. Compare les empreintes seulement pour les noms présents des deux côtés.

#### Palier 3 — F8 : aucun changement (10 min)

Écrire le premier cas de comparaison : tout est inchangé.

**Où tu travailles :** fileguard.py ; verification.py

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**F8 — Aucun changement**
- Entrée : Le dossier correspond exactement au manifeste
- Résultat attendu : Tous les fichiers dans inchangé.

**Actions dans l’ordre**

1. Ajoute le test F8 : un dossier temporaire dont chaque fichier correspond exactement au manifeste. Tous les noms doivent être dans inchange, et les autres catégories vides.
2. Lance le test : il échoue tant que comparer n’existe pas. Écris le plus petit code qui fait passer F8.
3. Commit ce palier.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add fileguard.py verification.py
git commit -m "Compare un dossier identique à son manifeste"
```

**Tu sais que c’est bon quand :** F1 à F8 passent ; git log --oneline montre le commit.

*Indice si tu bloques :* Crée le manifeste avec ta fonction de MR2 dans le dossier temporaire, puis compare : tu n’as pas besoin d’écrire les empreintes à la main.

#### Palier 4 — F9 et F10 : modifié et supprimé (10 min)

Distinguer un fichier dont le contenu a changé d’un fichier qui a disparu.

**Où tu travailles :** fileguard.py ; verification.py

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**F9 — Fichier modifié**
- Entrée : Même nom, contenu dont l’empreinte diffère
- Résultat attendu : Nom dans modifié.

**F10 — Fichier supprimé**
- Entrée : Nom du manifeste absent du dossier
- Résultat attendu : Nom dans supprimé.

**Actions dans l’ordre**

1. Ajoute le test F9 : même nom, contenu différent, donc une empreinte différente. Le nom doit être dans modifie.
2. Ajoute le test F10 : un nom présent dans le manifeste mais absent du dossier. Le nom doit être dans supprime.
3. Lance les tests, écris le code qui les fait passer, puis commit.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add fileguard.py verification.py
git commit -m "Classe les fichiers modifiés et supprimés"
```

**Tu sais que c’est bon quand :** F1 à F10 passent.

*Indice si tu bloques :* Pour F10, le manifeste garde le nom du fichier supprimé : l’inventaire courant, lui, ne le contient plus. Compare les deux ensembles de noms avant de comparer les empreintes.

#### Palier 5 — F11 et F12 : ajouté, puis plusieurs catégories (10 min)

Gérer les nouveaux fichiers, puis vérifier que les quatre catégories restent exactes quand elles coexistent.

**Où tu travailles :** fileguard.py ; verification.py

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**F11 — Fichier ajouté**
- Entrée : Nouveau fichier régulier au premier niveau
- Résultat attendu : Nom dans ajouté.

**F12 — Plusieurs catégories**
- Entrée : Dossier avec cas inchangé, modifié, supprimé et ajouté
- Résultat attendu : Chaque nom dans sa catégorie exacte.

**Actions dans l’ordre**

1. Ajoute le test F11 : un nouveau fichier régulier au premier niveau, absent du manifeste. Son nom doit être dans ajoute.
2. Ajoute le test F12 : un dossier qui contient un cas inchangé, un modifié, un supprimé et un ajouté. Chaque nom doit être dans sa catégorie exacte, et nulle part ailleurs.
3. Lance les tests, écris le code qui les fait passer, puis commit.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add fileguard.py verification.py
git commit -m "Classe les fichiers ajoutés et les cas mêlés"
```

**Tu sais que c’est bon quand :** F1 à F12 passent.

*Indice si tu bloques :* Un nom ne doit jamais apparaître dans deux catégories à la fois. Vérifie-le dans F12 avec un assertEqual sur chaque liste.

#### Palier 6 — F13 et F14 : manifeste vide et manifeste exclu (8 min)

Vérifier les cas limites : un manifeste sans entrée, et un manifeste conservé à côté des données.

**Où tu travailles :** fileguard.py ; verification.py

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**F13 — Manifeste vide**
- Entrée : Manifeste avec zéro entrée et dossier contenant des données
- Résultat attendu : Les fichiers sont ajoutés.

**F14 — Manifeste exclu**
- Entrée : Manifeste conservé à proximité des données
- Résultat attendu : Il n’est jamais signalé comme ajouté ou modifié.

**Actions dans l’ordre**

1. Ajoute le test F13 : un manifeste sans entrée et un dossier qui contient des fichiers. Tous les fichiers doivent être dans ajoute.
2. Ajoute le test F14 : le manifeste est conservé à côté des données. Il ne doit jamais être signalé comme ajouté ou modifié.
3. Écris le code qui fait passer les deux tests, puis commit.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add fileguard.py verification.py
git commit -m "Gère le manifeste vide et le manifeste exclu"
```

**Tu sais que c’est bon quand :** F1 à F14 passent : les quatorze tests sont verts.

*Indice si tu bloques :* Pour F14, l’exclusion doit s’appliquer à l’inventaire courant avant toute comparaison, pas seulement à l’affichage.

#### Palier 7 — Commandes simples et affichage par catégorie (8 min)

Relier la création et la vérification à une ligne de commande, sans parcourir le disque.

**Où tu travailles :** fileguard.py

**Pour comprendre**

- Notion : sys.argv contient les arguments de la ligne de commande. Exemple sans rapport : un petit script qui affiche le premier argument.

**Actions dans l’ordre**

1. Ajoute deux commandes : creer DOSSIER (écrit manifest.json) et verifier DOSSIER (affiche les quatre catégories, un nom par ligne). Le dossier est toujours explicite ; le programme ne cherche rien ailleurs.
2. Vérifie qu’un argument manquant ou un dossier inexistant donne un message clair et un code de sortie non nul.
3. Commit ce palier.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -c "import sys; print(sys.argv)" creer dossier
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 fileguard.py creer fixtures
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 fileguard.py verifier fixtures
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add fileguard.py
git commit -m "Ajoute les commandes creer et verifier"
```

**Tu sais que c’est bon quand :** Les deux commandes s’exécutent sur le dossier donné et affichent les quatre catégories.

*Indice si tu bloques :* Lis sys.argv[1] pour le nom de la commande, puis sys.argv[2] pour le dossier. Vérifie l’existence du dossier avant de rien écrire.

#### Palier 8 — Rédige le README (9 min)

Expliquer le programme et ses limites à quelqu’un qui ne l’a pas écrit.

**Où tu travailles :** README.md

**Actions dans l’ordre**

1. Le README contient : la structure du dossier, le format du manifeste (schema 1, files, name, sha256), les commandes, le comportement des liens symboliques et des sous-dossiers, le sens du résultat et les limites.
2. Indique si creer crée ou remplace manifest.json, et quelle exception est levée pour un lien symbolique.
3. Écris que le manifeste doit être digne de confiance, puisqu’une personne qui modifie les fichiers peut modifier un manifeste conservé à côté, et que le projet n’est pas un antivirus.
4. Commit le README.

**Terminal · Enregistrer le travail vérifié**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git add README.md
git commit -m "Documente FileGuard dans le README"
```

**Tu sais que c’est bon quand :** Un lecteur qui ne connaît pas le projet sait lancer les commandes, lire le résultat et voir les limites.

*Indice si tu bloques :* Relis le contrat du guide et vérifie que chaque point du README correspond à ce que ton code fait réellement.

#### Palier 9 — Démonstration des quatre catégories, puis livraison (12 min)

Montrer les quatre catégories sur un scénario, puis livrer la MR3 et fusionner le dernier commit vert.

**Où tu travailles :** Dossier temporaire ; MR GitLab

**Actions dans l’ordre**

1. Démonstration (hors tests) : copie les fixtures dans un dossier de démonstration hors du dépôt, crée le manifeste, modifie un fichier, supprime-en un autre, ajoute un nouveau fichier, puis vérifie. Tu dois voir un fichier dans chaque catégorie, et README.txt inchangé.
2. Relis le diff de la MR3, pousse la branche, puis ouvre la troisième merge request vers main.
3. Attends le pipeline vert dans GitLab et fusionne seulement si les règles de l’école l’autorisent. La démonstration locale n’est pas une preuve de fusion.
4. Après la fusion, mets main à jour : la série de trois MR est terminée.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
cp -r fixtures ~/demo_fileguard
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 fileguard.py creer ~/demo_fileguard
```

**Terminal · Commande à lancer au moment indiqué**

```bash
echo "modification" >> ~/demo_fileguard/message.txt
```

**Terminal · Commande à lancer au moment indiqué**

```bash
rm ~/demo_fileguard/settings.ini
```

**Terminal · Commande à lancer au moment indiqué**

```bash
echo "nouveau" > ~/demo_fileguard/nouveau.txt
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 fileguard.py verifier ~/demo_fileguard
```

**Terminal · Relire l’état du dépôt**

```bash
git status
git diff main --stat
```

**Terminal · Publier la branche ou ouvrir la demande de fusion**

```bash
git push -u origin feat/comparaison
```

**Terminal · Après la fusion : actualiser la principale**

```bash
git switch main
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git pull --ff-only
```

**Tu sais que c’est bon quand :** La sortie de verifier range message.txt dans modifie, settings.ini dans supprime, nouveau.txt dans ajoute et README.txt dans inchange ; la MR3 est fusionnée après un pipeline vert.

*Indice si tu bloques :* Si verifier ne trouve pas de manifeste, vérifie que creer a bien écrit manifest.json dans ~/demo_fileguard. Ne fusionne pas avant d’avoir relu le diff et vu le pipeline.

**Avant de livrer**

- Les quatre catégories ont des tests reproductibles et le manifeste lui-même est ignoré.
- Le programme reste limité au dossier choisi, au premier niveau, sans suivre de symlinks.
- Le README indique que le manifeste doit être digne de confiance et que le projet n’est pas un antivirus.

<!-- END GENERATED EXERCISES -->

## Méthode GitLab

Le dossier FileGuard est vide au départ. Clone le dépôt de l’école directement dans le dossier courant avec git clone <URL_DU_DEPOT> . avant de créer les fichiers. Le point signifie « ici ». Le terminal web repart du dossier courant explicite pour chaque commande ; un cd seul ne persiste pas. Pour Git interactif, utilise docker compose exec atelier bash depuis le dossier Cyber Atelier.

Utilise un dépôt autorisé par l’école, un runner actif sur les MR des branches non protégées et les droits convenus pour les règles de fusion. Pour chaque MR, crée la branche depuis la principale actualisée, exécute la même commande de tests localement et en CI, lis le diff, puis ouvre la MR. Fusionne uniquement le dernier commit vert. Après chaque fusion, actualise la principale avant l’étape suivante.

La CI ne dépend pas d’un dossier de données du portail. Les tests créent leurs propres fichiers temporaires. Les fixtures d’exemple peuvent être copiées par l’apprenant dans son dépôt, mais elles ne remplacent pas les tests temporaires et ne sont pas supposées présentes sur le runner d’école.

## Repères de temps

Préparation GitLab et lecture : 30 min. MR1 empreintes et tests : 85 min. MR2 manifeste et tests : 85 min. MR3 comparaison, affichage et README : 80 min. Relecture et marge : 20 min. Total : 300 min.

## Livrables et limites

Livre fileguard.py, verification.py, un README, les fixtures fictives copiées dans le dépôt, une CI qui exécute les tests temporaires et trois MR successives. Montre un scénario où les quatre catégories sont distinguées, et explique clairement que le manifeste de référence doit lui-même être digne de confiance.

FileGuard est un outil pédagogique d’intégrité, pas un antivirus ni une garantie d’authenticité. SHA-256 permet de constater une différence avec un manifeste de confiance ; une personne capable de modifier les fichiers peut aussi modifier un manifeste conservé à côté. Il ne parcourt pas récursivement, ne suit pas les liens et ne cherche pas de secrets.
