# ReconWrap — assembler un mini-framework

**Durée : 5 heures · Niveau débutant · 3 merge requests**

Tu vas assembler un petit framework de reconnaissance modulaire. Il lance des modules (réseau, web, Active Directory) contre le laboratoire local, normalise leurs résultats, produit un rapport JSON et Markdown, puis se documente et se livre comme un vrai projet. Ce parcours de synthèse réutilise ton propre code de PortPilot et de HeaderScope. Il ne demande pas de réécrire ce que tu sais déjà faire : il porte sur l’architecture, l’orchestration et la livraison.

Le périmètre reste strictement local : 127.0.0.1, le laboratoire HTTP sur le port 8000 et les outils fournis dans le conteneur. Aucune cible distante, aucune exploitation.

## Prérequis

- Avoir terminé les parcours Socle et ToolWrap.
- Idéalement avoir fait PortPilot et HeaderScope. Tu relis et adaptes ton propre code avant de le brancher ; tu ne le copies pas à l’aveugle.
- Connaître argparse, json, subprocess, logging, pathlib et unittest au niveau de la bibliothèque standard.
- Savoir créer une branche et une merge request dans le dépôt de l’école.

## Contrat du programme

Le package vit dans le dossier `reconwrap/`. Un module par domaine : `network.py`, `web.py`, `ad.py`. Le contrat commun est dans `core.py` ; la CLI dans `cli.py` ; `__main__.py` permet de lancer `python -m reconwrap`. Tu peux choisir les noms internes, mais garde la séparation suivante : contrat et registre, modules, rapport, CLI.

**Contrat d’un module.** Chaque module expose une fonction qui prend une cible validée et des options. Elle retourne un dict normalisé avec exactement ces clés :

- `module` : le nom du module ;
- `statut` : `OK`, `ERREUR` ou `IGNORE`, et rien d’autre ;
- `donnees` : les informations propres au module ;
- `alertes` : une liste de messages lisibles ;
- `duree_s` : la durée en secondes, positive ou nulle.

Une panne ne doit jamais se propager : le dispatch transforme une exception en résultat `ERREUR`, et les autres modules continuent.

**Cible.** Seule `127.0.0.1` est acceptée. Une autre valeur (adresse externe, nom de domaine, plage, chaîne contenant autre chose) est refusée avant tout appel de module.

**Fixtures pour la CI.** Les modules s’appuient sur les fixtures fournies, copiées dans le dépôt : sorties XML de nmap, sorties JSON et texte d’adsim. Les tests obligatoires lisent ces fichiers. Ils n’appellent ni nmap, ni adsim, ni le laboratoire, ni le réseau, car le runner de l’école n’a pas ces outils. Les démonstrations contre le labo sont à part, hors CI.

**Outils et périmètre.**

- Module réseau : nmap en TCP connect sur le port 8000 uniquement, en démonstration. Le XML est lu avec `xml.etree.ElementTree`.
- Module web : tes règles HeaderScope, sur les quatre chemins du labo : `/fragile`, `/durci`, `/absent`, `/erreur`.
- Module AD : `adsim`, simulateur fictif du domaine `LAB.LOCAL`. Aucun annuaire réel n’est interrogé.

Bibliothèque standard uniquement : pas de dépendance pip, un venv suffit.

## Setup

Le dossier du parcours est vide au départ. Dans la console de Cyber Atelier, prépare l’environnement dans cet ordre :

1. Vérifier Python : `python --version` (utilise `python3` si besoin).
2. Vérifier Git : `git --version`.
3. Configurer ton identité Git une seule fois, avec les informations de ton compte scolaire.
4. Cloner le dépôt directement dans le dossier courant : `git clone <URL_DU_DEPOT> .`. Ce clone est interactif : fais-le dans `docker compose exec atelier bash`, depuis le dossier Cyber Atelier, puis `cd /workspaces/reconwrap`.
5. Créer le venv : `python -m venv .venv`. Dans la console web, chaque commande repart à neuf : une activation (`source .venv/bin/activate`) ne persiste pas. Appelle `.venv/bin/python` explicitement. Ajoute `.venv/` à `.gitignore` dans la MR1, avant ton premier `git add`.
6. Créer la branche de la MR1 : `git switch -c feat/architecture`.

<!-- BEGIN GENERATED EXERCISES -->
## Comment travailler un exercice

Ces exercices sont ton entraînement. Chaque palier explique les notions utiles, montre les données ou les règles attendues, puis te fait écrire et vérifier ton propre code. Les durées sont des repères : avance quand tu comprends le résultat.

1. Lis « Pour comprendre » et l’exemple lorsqu’il y en a un. Repère ce qui entre dans le programme, ce qui doit en sortir et les règles à respecter.
2. Les cartes de tests donnent l’entrée et le résultat attendu. Écris les tests correspondants dans le fichier indiqué ; cocher un palier ne les exécute pas. Avec unittest, « Ran 0 tests » signifie qu’aucun test n’a été exécuté : ce n’est pas une validation. Un cas décrit peut contenir plusieurs valeurs ; le nombre de méthodes Python n’est donc pas forcément le nombre d’identifiants.
3. Suis les actions numérotées, une à la fois. Les exemples servent à apprendre une notion ; tu écris toi-même la solution de l’exercice. Les blocs Terminal donnent les commandes à lancer au moment indiqué.
4. Vérifie le résultat indiqué avant de poursuivre. Un échec attendu (phase rouge, argument refusé ou conflit volontaire) est expliqué dans le palier.
5. Si tu bloques, lis la dernière ligne de l’erreur, compare l’entrée et l’attendu, puis ouvre l’indice. Fais un petit changement et relance.

### Le bon endroit pour chaque action

Sur ton Mac, ouvre `workspaces/reconwrap` dans VS Code. Dans Cyber Atelier, utilise l’éditeur et la console de **Coder**, avec `cwd` sur `.` (la racine du dépôt). Fais la préparation de **Environnement** avant MR1 ; la mission crée ensuite sa branche.

Le code Python se place dans l’éditeur. Les commandes `docker compose ...` se lancent sur ton Mac depuis `cyberatelier` ; `/app/...` existe dans le conteneur. Le laboratoire interrogé doit tourner dans le même environnement que ton programme.

La console web repart à neuf à chaque exécution : un `cd`, une activation de venv ou `echo $?` ne se transmet pas à la commande suivante. Lance le programme et `echo $?` ensemble quand le palier le demande. Le nombre affiché par echo est celui du programme ; la console peut afficher code 0 pour echo lui-même.

Un venv créé sur le Mac ne fonctionne pas dans le conteneur : utilise `python3` dans ce dernier. Remplace `main` par `master` si nécessaire. Si une branche existe déjà, reprends-la avec `git switch NOM` sans `-c`. Après chaque fusion, actualise la branche principale avant la mission suivante.

### Les mots utiles

**Chaîne / champ.** Une chaîne (str) est du texte. Un champ est un morceau de donnée, comme l’utilisateur dans une ligne de journal.

**Liste / position.** Une liste conserve plusieurs valeurs dans un ordre. Sa première position porte le numéro 0, la suivante 1, etc.

**Dictionnaire / clé.** Un dictionnaire associe un nom à une valeur : {"fruit": "pomme"}. fruit est la clé ; pomme est sa valeur.

**None.** Une valeur Python qui représente l’absence de résultat. Dans analyser_ligne, elle signifie que la ligne est refusée. Elle s’écrit sans guillemets.

**split / strip.** split() sans argument découpe une chaîne sur ses espaces. split(".") découpe sur les points. strip() retire les espaces aux bords.

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

### MR1 — feat/architecture (100 min)

Le registre relie un nom à une fonction ; le dispatch appelle cette fonction et isole ses pannes. Avance dans l’ordre des paliers et vérifie chaque résultat avant de poursuivre.

**Avant de commencer**

- Point de départ : Les parcours précédents sont terminés ; un dépôt cloné et un venv sont préparés.
- Ce que tu vas produire : Le package reconwrap, core.py et tests/test_core.py : contrat, cible, registre, dispatch et logging.
- Pourquoi : Le registre relie un nom à une fonction ; le dispatch appelle cette fonction et isole ses pannes.
- Commande des tests depuis la racine : `.venv/bin/python -m unittest -v`. Les cas ci-dessous sont à écrire par toi.

#### Palier 1 — Crée le package et protège le venv (10 min)

Avoir un package reconwrap/ importable, et un .gitignore qui protège le venv avant ton premier commit.

**Où tu travailles :** .gitignore ; reconwrap/__init__.py ; reconwrap/__main__.py

**Pour comprendre**

- La branche principale (main) contient le travail déjà fusionné. Ta branche feat/... reçoit les changements de cette mission.
- Un dépôt « propre » n’a aucune modification en attente : git status te le confirme.

**Actions dans l’ordre**

1. Ouvre workspaces/reconwrap dans VS Code, ou Coder dans Cyber Atelier avec cwd sur « . ».
2. Termine la préparation, notamment le venv de cet environnement.
3. Lis git status ; enregistre ton travail en cours avant de changer de branche.
4. Reviens sur main avec git switch main, mets-la à jour avec git pull --ff-only, puis crée feat/architecture. Remplace main par master si ton dépôt utilise ce nom.
5. Avant git add, crée .gitignore avec .venv/, __pycache__/ et rapports/. Crée reconwrap/__init__.py et reconwrap/__main__.py ; ce dernier peut afficher un simple message en MR1. Vérifie python -m reconwrap sans traceback.
6. Vérifie le nom de ta branche avec git status. Si elle existe déjà, reprends-la avec git switch sans -c.

**Terminal · Relire l’état du dépôt**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git status
git switch main
git pull --ff-only
git switch -c feat/architecture
git branch --show-current
```

**Terminal · Commande à lancer au moment indiqué**

```bash
ls -d .venv   # si le dossier n’existe pas : python3 -m venv .venv
```

**Terminal · Exemple travaillé, sans rapport avec ReconWrap, dans un dossier jetable **

```bash
mkdir exemple_pkg
touch exemple_pkg/__init__.py
echo 'print("Bonjour depuis le paquet")' > exemple_pkg/__main__.py
python3 -m exemple_pkg
rm -r exemple_pkg
```

**Terminal · Relire l’état du dépôt**

```bash
git status
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add .gitignore reconwrap/__init__.py reconwrap/__main__.py
git commit -m "Crée la structure du package reconwrap"
```

**Tu sais que c’est bon quand :** git status n’affiche plus .venv/, et .venv/bin/python -m reconwrap s’exécute sans traceback.

*Indice si tu bloques :* Si .venv/ apparaît encore dans git status, ton .gitignore n’est pas enregistré ou un motif est mal écrit (le point au début de .venv compte). Le message de l’exemple jetable doit venir de ton __main__.py.

#### Palier 2 — La fabrique du résultat (R1) (10 min)

Construire un dict à cinq clés exactes depuis une fonction, avec annotations de type et docstring.

**Où tu travailles :** reconwrap/core.py ; tests/test_core.py

**Pour comprendre**

- Une fabrique est une fonction qui construit le résultat commun aux modules. Chaque module rend cette même structure.
- Les annotations décrivent les types attendus sans les imposer automatiquement. Une docstring est le texte d’aide placé au début d’une fonction.

**Éditeur · Exemple travaillé, sans rapport avec ReconWrap **

Éditeur : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
def doubler(n: int) -> int:
    """Retourne le double de n."""
    return n * 2
```

**Exemple de résultat attendu**

Ce que tu donnes :

```text
Fabrique avec module="faux", statut="OK", donnees={}, alertes=[], duree_s=0.0.
```

Ce que tu dois obtenir :

```text
{"module": "faux", "statut": "OK", "donnees": {}, "alertes": [], "duree_s": 0.0}
```

Tu choisis le nom de la fabrique et gardes les cinq clés pour tous les modules.

**Règles à respecter**

- Cinq clés exactes : module, statut, donnees, alertes, duree_s.
- Statuts finaux admis : OK, ERREUR, IGNORE.
- alertes est une liste et duree_s un nombre positif ou nul.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**R1 — Résultat normalisé**
- Entrée : Fabrique appelée avec module « faux », statut « OK », donnees vide, alertes vide et duree_s 0.0.
- Résultat attendu : Dict aux cinq clés exactes module, statut, donnees, alertes, duree_s ; alertes est une liste et duree_s un nombre positif ou nul.

**Actions dans l’ordre**

1. Crée tests/__init__.py vide et tests/test_core.py.
2. Écris R1 : module "faux", statut "OK", donnees vide, alertes [] et duree_s 0.0. Vérifie les cinq clés exactes, la liste d’alertes et la durée positive ou nulle.
3. Lance : la fabrique manque. Crée-la dans reconwrap/core.py avec des annotations et une docstring.
4. Fais passer R1 sans encore contrôler les statuts : ce sera le palier suivant.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
.venv/bin/python -m unittest -v
```

**Tu sais que c’est bon quand :** R1 passe : le dict a exactement les clés module, statut, donnees, alertes, duree_s.

*Indice si tu bloques :* Commence par écrire le dict littéral, puis relis le contrat. Un test par règle : ici, seule la forme du dict est testée.

#### Palier 3 — Le statut refusé (R2) (10 min)

Refuser tout statut hors de OK, ERREUR et IGNORE, avec une erreur qui explique ce qui ne va pas.

**Où tu travailles :** reconwrap/core.py ; tests/test_core.py

**Pour comprendre**

- Le statut est une valeur de contrat, avec une casse exacte. "ok" n’est pas "OK".
- Refuser un statut inconnu tôt évite de produire un rapport impossible à interpréter.

**Éditeur · Exemple travaillé, sans rapport avec ReconWrap **

Éditeur : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
MENU = ("margherita", "reine")
def commander(plat):
    if plat not in MENU:
        raise ValueError(f"plat inconnu : {plat}")
    return f"Commande : {plat}"
```

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**R2 — Statut refusé**
- Entrée : Statut « FAUX », puis statut « ok » en minuscules.
- Résultat attendu : ValueError avec un message en français qui cite le statut refusé. Aucun dict n’est retourné : les minuscules sont refusées aussi.

**Actions dans l’ordre**

1. Écris R2 séparément pour "FAUX" et "ok".
2. Vérifie ValueError et un message français citant le statut refusé. Aucun dictionnaire ne doit être retourné.
3. Ajoute le contrôle des trois statuts admis dans la fabrique.
4. Relance R1 et R2 puis commite contrat et tests.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
.venv/bin/python -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add reconwrap/core.py tests/__init__.py tests/test_core.py
git commit -m "Ajoute le contrat de résultat normalisé"
```

**Tu sais que c’est bon quand :** R1 et R2 passent. « ok » en minuscules est refusé.

*Indice si tu bloques :* Un tuple de statuts et l’opérateur in comparent exactement : les minuscules sont donc refusées. Le message doit contenir le statut reçu.

#### Palier 4 — La cible loopback seulement (R5) (10 min)

Refuser toute cible qui n’est pas 127.0.0.1 avant qu’un module soit appelé.

**Où tu travailles :** reconwrap/core.py ; tests/test_core.py

**Pour comprendre**

- La validation de la cible est un contrôle avant toute action. Ici, seule la chaîne exacte 127.0.0.1 est admise.
- R5 sera complété quand le dispatch existera, pour prouver aussi qu’un refus ne lance aucun module.

**Éditeur · Exemple travaillé, sans rapport avec ReconWrap **

Éditeur : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
try:
    n = int("abc")
except ValueError as erreur:
    print("pas un nombre :", erreur)
```

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**R5 — Cible loopback seulement**
- Entrée : 127.0.0.1, puis 192.0.2.10, example.com, une chaîne vide, 10.0.0.0/24 et « 127.0.0.1; ls ».
- Résultat attendu : 127.0.0.1 est accepté. Toutes les autres valeurs lèvent ValueError et aucun module n’est appelé.

**Actions dans l’ordre**

1. Commence R5 avec 127.0.0.1 admis, puis les cinq valeurs refusées du cas de test.
2. Écris la validation dans core.py : contrôle du type puis comparaison exacte ; refus par ValueError.
3. Relance les tests de validation.
4. Note que la preuve « aucun module appelé » sera ajoutée au palier 6 ; elle n’est pas encore validée ici.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
.venv/bin/python -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add reconwrap/core.py tests/test_core.py
git commit -m "Valide la cible : seule 127.0.0.1 est acceptée"
```

**Tu sais que c’est bon quand :** La validation accepte 127.0.0.1 et refuse 192.0.2.10, example.com, le texte vide, 10.0.0.0/24 et « 127.0.0.1; ls ». La partie dispatch de R5 reste à compléter au palier 6.

*Indice si tu bloques :* Vérifie d’abord le type, puis compare la chaîne exacte. Une chaîne qui contient autre chose (espace, point-virgule) doit être refusée, pas réparée.

#### Palier 5 — Le registre des modules (R3) (10 min)

Associer un nom de module à sa fonction, et signaler clairement un nom inconnu.

**Où tu travailles :** reconwrap/core.py ; tests/test_core.py

**Pour comprendre**

- Le registre est un dictionnaire : une clé comme network désigne une fonction. Il indique les modules disponibles.
- Un nom inconnu doit être refusé avant d’appeler une fonction du registre.

**Éditeur · Exemple travaillé, sans rapport avec ReconWrap **

Éditeur : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
def dire_bonjour():
    return "bonjour"

ACTIONS = {"bonjour": dire_bonjour}
print(ACTIONS["bonjour"]())
print(sorted(ACTIONS))
```

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**R3 — Nom de module inconnu**
- Entrée : Registre contenant trois faux modules nommés network, web et ad ; demande du module « scanner ».
- Résultat attendu : ValueError qui liste les modules connus. Aucun des trois faux modules n’est appelé.

**Actions dans l’ordre**

1. Écris R3 avec trois faux modules network, web et ad qui enregistrent leurs appels.
2. Demande scanner : attends ValueError listant les modules connus et aucun appel des faux.
3. Écris le registre et la recherche de module dans core.py.
4. Fais passer R3 sans lancer de module réel.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
.venv/bin/python -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add reconwrap/core.py tests/test_core.py
git commit -m "Ajoute le registre des modules"
```

**Tu sais que c’est bon quand :** R3 passe : le nom inconnu donne une erreur qui liste les noms connus, sans appel de module.

*Indice si tu bloques :* Une fonction peut être rangée dans un dictionnaire comme n’importe quelle valeur. Pour la liste des noms connus, sorted() donne un ordre stable.

#### Palier 6 — Le dispatch et l’isolation des pannes (R4) (10 min)

Appeler un module par son nom, et transformer une exception en résultat ERREUR sans rien propager.

**Où tu travailles :** reconwrap/core.py ; tests/test_core.py

**Pour comprendre**

- Le dispatch choisit une fonction dans le registre et l’appelle. Il transforme une panne du module en résultat commun.
- Exception couvre les pannes ordinaires ; BaseException inclurait aussi Ctrl+C, qui doit continuer à interrompre le programme.

**Éditeur · Exemple travaillé, sans rapport avec ReconWrap **

Éditeur : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
def lire_note(texte):
    try:
        return int(texte)
    except ValueError as erreur:
        return f"erreur : {erreur}"

print(lire_note("12"))
print(lire_note("douze"))
```

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**R4 — Exception isolée**
- Entrée : Faux module qui lève RuntimeError avec le message « boom ».
- Résultat attendu : Le dispatch ne propage pas l’exception ; il retourne statut ERREUR, alertes vide, et donnees contient le message d’erreur.

**Actions dans l’ordre**

1. Écris R4 : un faux module lève RuntimeError("boom") ; attends ERREUR, alertes [] et message dans donnees, sans exception propagée.
2. Dans le dispatch, refuse le module inconnu et la cible invalide avant l’appel ; protège ensuite seulement l’exécution du module.
3. Construis le résultat d’erreur avec la fabrique ; attrape Exception, pas BaseException.
4. Complète R5 : pour chaque cible refusée, vérifie que le faux module n’a jamais été appelé.
5. Relance R1 à R5 puis commite le dispatch et ses tests.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
.venv/bin/python -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add reconwrap/core.py tests/test_core.py
git commit -m "Isole les erreurs des modules dans le dispatch"
```

**Tu sais que c’est bon quand :** R1 à R5 passent. Un module qui lève une exception donne un résultat ERREUR, sans traceback.

*Indice si tu bloques :* Le texte de l’exception est dans la variable de l’except (as erreur). Il doit finir dans donnees, pas être affiché.

#### Palier 7 — Un logger par module (10 min)

Ajouter du logging au dispatch sans que les tests dépendent du texte affiché.

**Où tu travailles :** reconwrap/core.py ; tests/test_core.py

**Pour comprendre**

- Un logger porte un nom pour identifier l’origine des messages. Les niveaux sont DEBUG, INFO et ERROR.
- ERROR est le niveau Python du journal ; ERREUR est le statut français du dictionnaire de résultat.

**Éditeur · Exemple travaillé, sans rapport avec ReconWrap **

Éditeur : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
import logging
logging.basicConfig(level=logging.INFO, format="%(name)s %(levelname)s %(message)s")
journal = logging.getLogger("cuisine")
journal.info("four préchauffé")
journal.debug("température lue : 180")
```

**Actions dans l’ordre**

1. Prépare un logger par module, nommé selon ce module.
2. Journalise l’appel en INFO, les détails en DEBUG et les pannes avec journal.error(...).
3. Observe une panne simulée : la ligne doit identifier le module et le niveau ERROR.
4. Ne teste pas le texte exact du journal ; relance R1 à R5 puis commite le logging séparément.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
.venv/bin/python -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add reconwrap/core.py
git commit -m "Ajoute le logging du dispatch"
```

**Tu sais que c’est bon quand :** Une panne simulée produit une ligne de niveau ERROR identifiant le module. Le résultat garde le statut ERREUR ; R1 à R5 passent.

*Indice si tu bloques :* Avec level=INFO, la ligne DEBUG n’apparaît pas : c’est normal. Regarde ce que le format affiche avant de choisir le nom du logger.

#### Palier 8 — Ajouter un module ne touche pas le dispatch (10 min)

Vérifier l’acceptance clé : un nouveau module ne demande que de l’ajouter au registre.

**Où tu travailles :** reconwrap/core.py ; tests/test_core.py

**Pour comprendre**

- Le dispatch dépend du contrat et du registre, pas d’une liste de conditions propres à network/web/ad.
- Un nouveau module doit s’intégrer en étant enregistré, sans modifier le dispatch.

**Actions dans l’ordre**

1. Ajoute dans tests/test_core.py un quatrième faux module, par exemple cloud, conforme au contrat.
2. Ajoute seulement sa fonction au registre de l’essai, puis appelle le dispatch sur cloud.
3. Vérifie que le résultat arrive sans changer la fonction de dispatch.
4. Relis son diff par rapport au palier précédent et conserve ce test pour la livraison.

**Terminal · Relire l’état du dépôt**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git diff reconwrap/core.py
```

**Terminal · Commande à lancer au moment indiqué**

```bash
.venv/bin/python -m unittest -v
```

**Tu sais que c’est bon quand :** Le faux module « cloud » répond via le dispatch, et le diff du dispatch est vide depuis le palier précédent.

*Indice si tu bloques :* Si tu as dû modifier le dispatch pour le faire fonctionner, la structure n’est pas bonne : reviens au registre seul.

#### Palier 9 — Vérifier et committer proprement (10 min)

Contrôler chaque commit avant de le faire : état, diff en zone de préparation, tests, commandes.

**Où tu travailles :** Dépôt ; historique Git

**Pour comprendre**

- git add choisit le contenu du prochain commit ; git diff --staged permet de le relire avant enregistrement.
- Un commit atomique décrit une modification cohérente, par exemple contrat ou logging.

**Actions dans l’ordre**

1. Lance git status, git diff et les tests avant le dernier commit de MR1.
2. Ajoute explicitement le test cloud ainsi que les fichiers nécessaires encore modifiés ; relis le contenu staged.
3. Commite avec un message qui décrit le changement.
4. Relis l’historique : structure, contrat, cible, registre, dispatch et logging doivent être compréhensibles.
5. Lance python -m reconwrap avec le Python de cet environnement et vérifie status propre.

**Terminal · Exemple travaillé dans un dépôt jetable, hors de ReconWrap **

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
mkdir ~/essai-git && cd ~/essai-git && git init -b main
echo bonjour > a.txt
git add a.txt
git diff --staged
git commit -m "Premier essai"
cd - 
```

**Terminal · Relire l’état du dépôt**

```bash
git status
```

**Terminal · Enregistrer le travail vérifié**

```bash
git diff --staged
```

**Terminal · Relire l’état du dépôt**

```bash
git log --oneline
```

**Terminal · Commande à lancer au moment indiqué**

```bash
.venv/bin/python -m reconwrap
```

**Terminal · Commande à lancer au moment indiqué**

```bash
.venv/bin/python -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add tests/test_core.py
git diff --staged
git commit -m "Vérifie l’extension du registre sans modifier le dispatch"
```

**Tu sais que c’est bon quand :** git log --oneline montre les commits atomiques de la MR, git status est propre, et python -m reconwrap ne lève pas d’erreur.

*Indice si tu bloques :* Si un commit contient plusieurs sujets, tu peux le scinder : git reset --soft HEAD~1 annule le dernier commit en gardant les modifications. Demande-toi d’abord si c’est nécessaire.

#### Palier 10 — Pousser la MR1 et la faire relire (10 min)

Pousser la branche, ouvrir la merge request sur le dépôt de l’école, et distinguer ce qui est vérifié de ce qui est autorisé.

**Où tu travailles :** MR GitLab

**Pour comprendre**

- git diff montre les lignes modifiées ; git diff --staged montre celles choisies pour le prochain commit. Le diff de la MR compare toute ta branche à main.
- La demande de fusion (MR dans GitLab, PR dans GitHub) permet de relire le travail avant de l’intégrer à main.

**Actions dans l’ordre**

1. Lance la suite complète avec la commande indiquée au début de la mission.
2. Le fichier de CI arrivera en MR3. Note l’état réel des tests et de la relecture ; la case de progression ne vérifie pas ces conditions.
3. Relis git status et git diff : la livraison doit contenir le package reconwrap/, tests/ et .gitignore, avec les modifications nécessaires de cette mission.
4. Ajoute les fichiers par leur nom, relis git diff --staged, puis commite ce qui ne l’est pas encore.
5. Pousse feat/architecture et ouvre la demande de fusion vers main.
6. Relis le diff dans la demande de fusion. Cette mission n’a pas encore de pipeline : la relecture et les conditions de fusion restent nécessaires.
7. Fusionne après relecture et, pour GitLab de l’école, après son autorisation.
8. Après la fusion, reviens sur main et lance git pull --ff-only avant la mission suivante.

**Terminal · Relire l’état du dépôt**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git status
git log --oneline main..HEAD
```

**Terminal · Publier la branche ou ouvrir la demande de fusion**

```bash
git push -u origin feat/architecture
```

**Terminal · Après la fusion : actualiser la principale**

```bash
git switch main
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git pull --ff-only
```

**Tu sais que c’est bon quand :** La merge request est ouverte avec seulement les fichiers de MR1 ; ton main local est à jour après fusion (git log --oneline).

*Indice si tu bloques :* Si git push se plaint, vérifie d’abord que tu es bien sur feat/architecture (git branch --show-current). Ne fusionne pas sans relecture.

**Avant de livrer**

- python -m reconwrap s’exécute sans traceback, même si aucun module n’est encore branché.
- Les tests R1 à R5 passent localement avec python -m unittest, sans réseau et sans outil externe.
- Ajouter un faux module ne demande aucune modification du dispatch : seul le registre change.
- Le .venv n’est pas suivi par Git, les commits sont atomiques et le diff de la MR a été relu.

### MR2 — feat/orchestration-rapport (100 min)

Tu assembles les composants précédents sans rendre la CI dépendante des outils réels. Avance dans l’ordre des paliers et vérifie chaque résultat avant de poursuivre.

**Avant de commencer**

- Point de départ : MR1 fusionnée ; le contrat et le dispatch sont disponibles, R1 à R5 passent.
- Ce que tu vas produire : Modules network, web et ad, orchestration, CLI et rapports ; tests R6 à R14 et fixtures.
- Pourquoi : Tu assembles les composants précédents sans rendre la CI dépendante des outils réels.
- Commande des tests depuis la racine : `.venv/bin/python -m unittest -v`. Les cas ci-dessous sont à écrire par toi.

#### Palier 1 — Copier les fixtures dans le dépôt (8 min)

Rendre les fixtures nmap et adsim suivies par Git, pour que la CI les lise à la place des vrais outils.

**Où tu travailles :** Dépôt ; fixtures/

**Pour comprendre**

- La branche principale (main) contient le travail déjà fusionné. Ta branche feat/... reçoit les changements de cette mission.
- Un dépôt « propre » n’a aucune modification en attente : git status te le confirme.

**Actions dans l’ordre**

1. Ouvre workspaces/reconwrap dans VS Code, ou Coder dans Cyber Atelier avec cwd sur « . ».
2. Vérifie que MR1 est fusionnée et que R1 à R5 passent.
3. Lis git status ; enregistre ton travail en cours avant de changer de branche.
4. Reviens sur main avec git switch main, mets-la à jour avec git pull --ff-only, puis crée feat/orchestration-rapport. Remplace main par master si ton dépôt utilise ce nom.
5. Copie fixtures/nmap et fixtures/adsim depuis ../../fixtures sur le Mac, ou /app/fixtures dans Docker. Rends les copies modifiables, ajoute-les explicitement et commite ; aucun venv ni rapport ne doit être ajouté.
6. Vérifie le nom de ta branche avec git status. Si elle existe déjà, reprends-la avec git switch sans -c.

**Terminal · Relire l’état du dépôt**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git status
git switch main
git pull --ff-only
git switch -c feat/orchestration-rapport
```

**Terminal · Exemple travaillé, sans rapport avec ReconWrap **

```bash
mkdir -p recettes_copie && cp -r recettes/. recettes_copie/
# le point après recettes/ copie le contenu du dossier, pas le dossier lui-même
```

**Terminal · Commande à lancer au moment indiqué**

Terminal de ton Mac, depuis workspaces/reconwrap. Dans le conteneur, remplace ../../fixtures par /app/fixtures ; garde le reste de la commande. Les copies vont dans ton dépôt.

```bash
mkdir -p fixtures && cp -r ../../fixtures/nmap/. fixtures/nmap/ && cp -r ../../fixtures/adsim/. fixtures/adsim/ && chmod -R u+w fixtures
```

**Terminal · Relire l’état du dépôt**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git status
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add fixtures
git commit -m "Ajoute les fixtures nmap et adsim"
```

**Tu sais que c’est bon quand :** git status a listé les fichiers de fixtures/nmap et fixtures/adsim, et ces fichiers sont dans le commit.

*Indice si tu bloques :* Si cp refuse d’écrire, tu essaies d’écrire dans les originaux : vérifie que ta destination est bien fixtures/ dans ton dépôt.

#### Palier 2 — Lire un XML avec ElementTree (8 min)

Lire un fichier XML et retrouver ses balises et attributs avec la bibliothèque standard.

**Où tu travailles :** fixtures/nmap/open_8000.xml

**Pour comprendre**

- ElementTree lit l’arbre XML. tag est le nom d’une balise ; get lit un attribut de cette balise.
- Un XML mal formé lève ParseError, que le module devra traduire en ERREUR.

**Éditeur · Exemple travaillé, sans rapport avec ReconWrap **

Éditeur : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
import xml.etree.ElementTree as ET
xml = "<rayon><fruit nom='pomme' prix='2'/><fruit nom='poire' prix='3'/></rayon>"
racine = ET.fromstring(xml)
for fruit in racine.findall("fruit"):
    print(fruit.get("nom"), fruit.get("prix"))
try:
    ET.fromstring("<rayon><fruit>")
except ET.ParseError as erreur:
    print("XML cassé :", erreur)
```

**Actions dans l’ordre**

1. Ouvre open_8000.xml et repère la racine ainsi que la balise state du port.
2. Lance la lecture proposée et observe le tag de la racine.
3. Repère portid, protocol et l’attribut state : ils fournissent les données à conserver.
4. Ne code pas encore le module : cette étape prépare la lecture du contrat R12.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
.venv/bin/python -c "import xml.etree.ElementTree as ET; print(ET.parse('fixtures/nmap/open_8000.xml').getroot().tag)"
```

**Tu sais que c’est bon quand :** Tu affiches le tag de la racine de open_8000.xml, et tu as repéré la balise qui porte l’état du port 8000.

*Indice si tu bloques :* Utilise les noms de balises tels qu’ils apparaissent dans le fichier. Les attributs se lisent avec get(), pas avec le texte entre balises.

#### Palier 3 — Le module réseau et le XML nmap (R12) (10 min)

Transformer un XML nmap en résultat du contrat : open, closed, filtered, ou ERREUR si le XML est cassé.

**Où tu travailles :** reconwrap/network.py ; tests/test_network.py

**Pour comprendre**

- Le module réseau retourne la structure commune de MR1. La voie « fichier fourni » remplace la sortie d’un scan réel dans les tests.
- Une fixture rend l’essai stable et indépendant de nmap.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**R12 — Lecture XML nmap**
- Entrée : Fixtures nmap : open_8000.xml, closed_8000.xml, mixed.xml et broken.xml.
- Résultat attendu : Le port 8000 est open dans open_8000.xml et closed dans closed_8000.xml. mixed.xml donne open, closed et filtered. broken.xml donne ERREUR sans exception.

**Actions dans l’ordre**

1. Relis la validation de cible/port de ton PortPilot avant de l’adapter.
2. Écris R12 dans tests/test_network.py avec les quatre fixtures XML : open, closed, mixed et broken. Aucun appel à nmap.
3. Crée network.py avec une entrée permettant de lire le fichier XML fourni et un retour conforme à la fabrique.
4. Conserve les états open/closed/filtered ; transforme ParseError en ERREUR sans exception sortante.
5. Relance les tests puis commite le module réseau.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
.venv/bin/python -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add reconwrap/network.py tests/test_network.py
git commit -m "Ajoute le module réseau et la lecture XML nmap"
```

**Tu sais que c’est bon quand :** R12 passe : open, closed, filtered pour les bons fichiers, ERREUR sans traceback pour broken.xml.

*Indice si tu bloques :* Pour mixed.xml, un port peut avoir un état différent des autres : cherche le port 8000 précisément, pas le premier port du fichier. Pour broken.xml, attrape l’erreur de lecture et retourne ERREUR.

#### Palier 4 — Le module web et le classement hors réseau (R14) (10 min)

Classer une réponse HTTP (code et en-têtes) sans ouvrir de connexion, et distinguer code HTTP, panne et timeout.

**Où tu travailles :** reconwrap/web.py ; tests/test_web.py

**Pour comprendre**

- Le classement web reçoit un code et des en-têtes : c’est une fonction pure testable sans connexion.
- La voie réelle lit la réponse avant ce classement ; code HTTP, panne et timeout restent trois informations différentes.

**Éditeur · Exemple travaillé, sans rapport avec ReconWrap **

Éditeur : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
stock = {"Pommes": 3, "Poires": 0}
stock_min = {nom.lower(): n for nom, n in stock.items()}
print(stock_min["pommes"])
```

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**R14 — Classement web sans réseau**
- Entrée : Statut 404 avec en-têtes quelconques, puis statut 200 avec les trois en-têtes conformes.
- Résultat attendu : 404 : statut ERREUR, code 404 conservé, alertes vide. 200 conforme : zéro alerte. Aucune connexion n’est ouverte.

**Actions dans l’ordre**

1. Relis les trois contrôles et la normalisation des noms dans ton HeaderScope.
2. Écris R14 dans tests/test_web.py : 404 garde son code avec ERREUR et alertes [] ; 200 conforme donne zéro alerte.
3. Adapte le classement au contrat ReconWrap sans appel réseau dans ce test.
4. Garde les quatre chemins du labo seulement et prévois dans donnees un code HTTP ou une panne/timeout distincte.
5. Relance la suite ; ces pannes réelles seront observées en D6.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
.venv/bin/python -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add reconwrap/web.py tests/test_web.py
git commit -m "Ajoute le classement web hors réseau"
```

**Tu sais que c’est bon quand :** R14 passe : 404 donne ERREUR avec le code conservé, 200 conforme donne zéro alerte, et aucune connexion n’est ouverte.

*Indice si tu bloques :* Une fonction pure est plus simple à tester : elle ne fait que transformer ses arguments. Garde la connexion dans une autre fonction, plus tard.

#### Palier 5 — Le module AD et la sortie capturée (R13) (10 min)

Lire une sortie JSON d’adsim capturée et la transformer en résultat du contrat, sans appeler adsim.

**Où tu travailles :** reconwrap/ad.py ; tests/test_ad.py

**Pour comprendre**

- json.load lit un fichier JSON en dictionnaires et listes. JSONDecodeError indique un fichier mal formé.
- adsim reste le simulateur fictif LAB.LOCAL : le test lit une sortie capturée et ne lance pas cet outil.

**Éditeur · Exemple travaillé, sans rapport avec ReconWrap **

Éditeur : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
import json
texte = '{"fruits": [{"nom": "pomme", "stock": 3}, {"nom": "poire", "stock": 0}]}'
donnees = json.loads(texte)
print([f["nom"] for f in donnees["fruits"] if f["stock"] > 0])
try:
    json.loads("{pas du json")
except json.JSONDecodeError as erreur:
    print("JSON invalide :", erreur)
```

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**R13 — Lecture AD depuis fixtures**
- Entrée : Fixtures adsim : users.json, puis broken.json. Le module lit la sortie capturée, il n’appelle pas adsim.
- Résultat attendu : users.json : le nombre de comptes égale count et actifs et inactifs sont distingués. broken.json donne ERREUR avec un message.

**Actions dans l’ordre**

1. Écris R13 dans tests/test_ad.py avec users.json puis broken.json.
2. Vérifie le nombre de comptes égal à count et la distinction actifs/inactifs selon enabled.
3. Crée la lecture dans ad.py et retourne le contrat commun ; pour broken.json, ERREUR avec message.
4. Relance R13 et la suite. Le lancement réel sera ajouté au palier suivant.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
.venv/bin/python -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add reconwrap/ad.py tests/test_ad.py
git commit -m "Ajoute la lecture des sorties adsim capturées"
```

**Tu sais que c’est bon quand :** R13 passe : le nombre de comptes égale count, actifs et inactifs sont séparés, et broken.json donne ERREUR.

*Indice si tu bloques :* Relis la structure de users.json avant d’écrire le code : le nom des champs compte. Compte les comptes à partir de la liste, puis compare à count.

#### Palier 6 — Lancer adsim sans shell (8 min)

Appeler adsim depuis Python de façon sûre : liste d’arguments, délai maximal, et ERREUR en cas de panne.

**Où tu travailles :** reconwrap/ad.py

**Pour comprendre**

- La liste d’arguments de subprocess.run garde chaque valeur séparée, sans interprétation par un shell.
- Le timeout borne l’attente et lève TimeoutExpired lorsqu’il est dépassé.

**Éditeur · Exemple travaillé, sans rapport avec ReconWrap **

Éditeur : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
import subprocess
resultat = subprocess.run(["echo", "a; b"], capture_output=True, text=True, timeout=5)
print(resultat.returncode, resultat.stdout.strip())
```

**Actions dans l’ordre**

1. Branche le lancement d’adsim dans la voie réelle du module AD avec une liste d’arguments et sans shell=True.
2. Transforme un dépassement du délai en résultat ERREUR.
3. Relis la séparation : les tests continuent à lire leurs fixtures, sans passer par ce lancement.
4. Vérifie l’absence de shell=True et relance tous les cas écrits jusqu’ici. D5 vérifiera cette voie réelle dans Docker.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
grep -n "shell=True" reconwrap/*.py   # aucune ligne ne doit s’afficher
```

**Terminal · Commande à lancer au moment indiqué**

```bash
.venv/bin/python -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add reconwrap/ad.py
git commit -m "Lance adsim avec subprocess et délai maximal"
```

**Tu sais que c’est bon quand :** grep ne trouve aucun shell=True, et les tests R1 à R14 passent toujours.

*Indice si tu bloques :* Le chemin d’adsim se construit à partir du dossier du projet (pathlib), pas à partir de l’endroit où tu tapes la commande. Lis la documentation de subprocess.run pour timeout.

#### Palier 7 — L’orchestration : un échec ne bloque pas les autres (R6) (8 min)

Exécuter plusieurs modules dans l’ordre demandé, en isolant chaque échec.

**Où tu travailles :** reconwrap/core.py ; tests/test_orchestration.py

**Pour comprendre**

- L’orchestrateur parcourt les modules demandés et conserve leurs résultats dans le même ordre.
- Le dispatch de MR1 isole chaque panne : l’orchestrateur peut continuer après un échec.

**Éditeur · Exemple travaillé, sans rapport avec ReconWrap **

Éditeur : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
nombres = [1, 2, 3]
carres = [n * n for n in nombres]
print(carres)
```

**Exemple de résultat attendu**

Ce que tu donnes :

```text
Modules demandés : A, B, C ; B plante.
```

Ce que tu dois obtenir :

```text
Résultats : A OK, B ERREUR, C OK.
```

L’échec de B reste dans le rapport et n’empêche pas C de travailler.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**R6 — Échec isolé**
- Entrée : Trois faux modules dans cet ordre : A retourne OK, B lève une exception, C retourne OK.
- Résultat attendu : Trois résultats dans l’ordre demandé : A OK, B ERREUR, C OK. C est bien exécuté après l’échec de B.

**Actions dans l’ordre**

1. Écris R6 dans tests/test_orchestration.py avec A qui rend OK, B qui lève une exception, C qui rend OK.
2. Vérifie trois résultats dans l’ordre A OK, B ERREUR, C OK, et l’appel effectif de C.
3. Crée la boucle d’orchestration en utilisant le dispatch, sans dupliquer son traitement d’erreur.
4. Relance la suite et commite l’orchestrateur.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
.venv/bin/python -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add reconwrap/core.py tests/test_orchestration.py
git commit -m "Exécute plusieurs modules en isolant les échecs"
```

**Tu sais que c’est bon quand :** R6 passe : résultats dans l’ordre A OK, B ERREUR, C OK ; C est bien exécuté après l’échec de B.

*Indice si tu bloques :* L’ordre des résultats suit l’ordre de la liste reçue, pas celui du dictionnaire ni celui de l’exécution.

#### Palier 8 — La CLI argparse et les modules inconnus (R7) (8 min)

Lire les options de la ligne de commande et refuser un module inconnu avec le code de sortie 2.

**Où tu travailles :** reconwrap/cli.py ; tests/test_cli.py

**Pour comprendre**

- La CLI valide l’ensemble des options avant de lancer les modules ou d’écrire un rapport.
- argparse écrit les erreurs d’usage sur stderr et termine avec 2 ; --help termine avec 0.

**Éditeur · Exemple travaillé, sans rapport avec ReconWrap **

Éditeur : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
import argparse
parser = argparse.ArgumentParser(prog="repas")
parser.add_argument("--plat", choices=["soupe", "salade"], default="soupe")
print(parser.parse_args(["--plat", "salade"]).plat)
parser.parse_args(["--plat", "pizza"])   # erreur : code 2 et SystemExit
```

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**R7 — Module inconnu en CLI**
- Entrée : --modules network,scanner, dans un dossier temporaire.
- Résultat attendu : Code de sortie 2, message d’erreur sur stderr, aucun rapport écrit.

**Actions dans l’ordre**

1. Crée reconwrap/cli.py avec --modules, --cible (défaut 127.0.0.1), --chemin, --format json/md et --sortie.
2. Relie reconwrap/__main__.py à la CLI pour python -m reconwrap.
3. Écris R7 dans tests/test_cli.py avec --modules network,scanner dans un dossier temporaire.
4. Capture le code 2 et le message sur stderr, puis vérifie qu’aucun rapport n’a été écrit.
5. Valide tous les noms avant l’orchestration, relance la suite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
.venv/bin/python -m unittest -v
```

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs. Lance le programme et echo $? ensemble : le nombre affiché est le code du programme ; la console peut afficher code 0 pour echo lui-même.

```bash
.venv/bin/python -m reconwrap --modules scanner; echo $?
```

**Terminal · Enregistrer le travail vérifié**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git add reconwrap/cli.py reconwrap/__main__.py tests/test_cli.py
git commit -m "Ajoute la CLI argparse et le refus des modules inconnus"
```

**Tu sais que c’est bon quand :** R7 passe, et la commande avec un module inconnu affiche 2 après le message d’erreur.

*Indice si tu bloques :* Pour tester une sortie avec code 2, attends une exception SystemExit dans le test (assertRaises) et vérifie son code.

#### Palier 9 — La cible refusée en CLI (R8) et git stash (10 min)

Refuser une cible autre que 127.0.0.1 dans la CLI avant tout appel, et pratiquer git stash et git restore.

**Où tu travailles :** reconwrap/cli.py ; tests/test_cli.py

**Pour comprendre**

- La CLI doit réutiliser la validation de MR1. Refuser la cible signifie ne lancer aucun module et ne produire aucun fichier.
- stash met un changement de côté ; pop le restaure. restore efface un changement non commité : essaie-le seulement sur un fichier jetable.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**R8 — Cible refusée en CLI**
- Entrée : --cible 192.0.2.10, dans un dossier temporaire.
- Résultat attendu : Code de sortie 2, aucun module appelé, aucun fichier écrit.

**Actions dans l’ordre**

1. Écris R8 : --cible 192.0.2.10 dans un dossier temporaire ; code 2, aucun module appelé, aucun fichier écrit.
2. Branche la validation de core.py dans la CLI et relance R8.
3. Commite le travail utile avant l’essai Git. Ajoute un commentaire temporaire dans cli.py, fais stash puis observe status propre et stash list.
4. Fais stash pop et observe le commentaire revenu ; retire uniquement ce commentaire.
5. Pour observer restore, crée et commite un fichier dans un dépôt d’essai hors du projet, modifie-le puis restaure ce seul fichier. Vérifie stash list vide dans le vrai dépôt.

**Terminal · Exemple jetable **

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
cd ~/essai-git && echo "ligne en trop" >> a.txt
git restore a.txt
cat a.txt
cd -
```

**Terminal · Commande à lancer au moment indiqué**

```bash
.venv/bin/python -m unittest -v
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git stash push -m "essai"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git stash pop
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add reconwrap/cli.py tests/test_cli.py
git commit -m "Refuse une cible autre que 127.0.0.1 dans la CLI"
```

**Tu sais que c’est bon quand :** R8 passe ; tu as vu git stash mettre tes modifications de côté et les rendre (git stash list est vide).

*Indice si tu bloques :* Une cible refusée doit échouer avant le lancement de tout module : le contrôle se fait en tête de la CLI.

#### Palier 10 — Rapports JSON et Markdown (R9, R10, R11) (12 min)

Écrire un rapport JSON et Markdown déterministe, dans un dossier dédié, avec des noms de fichiers sûrs.

**Où tu travailles :** reconwrap/rapport.py ; tests/test_rapport.py

**Pour comprendre**

- Un rapport déterministe garde les mêmes octets quand les résultats et la date sont identiques. La date doit donc pouvoir être fournie par le test.
- Le dossier de sortie et le nom de fichier sont deux valeurs distinctes : le nom ne doit pas créer de sous-chemin.
- Markdown est un texte structuré avec titres et listes, lisible sans outil spécial.

**Éditeur · Exemple travaillé, sans rapport avec ReconWrap **

Éditeur : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
import json
print(json.dumps({"b": 1, "a": 2}, sort_keys=True, ensure_ascii=False))
from pathlib import Path
print(Path("dossier/courses.txt").name)
```

**Éditeur · Exemple travaillé dans un dossier temporaire, sans rapport avec ReconWrap **

```python
import tempfile
from pathlib import Path
with tempfile.TemporaryDirectory() as dossier:
    chemin = Path(dossier) / "liste.txt"
    chemin.write_text("lait\npain\n", encoding="utf-8")
    print(chemin.read_text(encoding="utf-8").split())
```

**Règles à respecter**

- Le JSON conserve la date injectée et, pour chaque module, module, statut et alertes.
- Deux écritures des mêmes entrées donnent des JSON identiques octet pour octet.
- Les noms de fichiers restent dans le dossier demandé.
- Markdown conserve ordre des modules et rattachement de leurs alertes.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**R9 — Rapport JSON déterministe**
- Entrée : Mêmes résultats écrits deux fois, avec la date injectée 2026-01-05T08:00:00, dans deux dossiers temporaires.
- Résultat attendu : Les deux fichiers JSON sont identiques octet pour octet. Ils contiennent la date injectée et, pour chaque module, les clés module, statut et alertes.

**R10 — Nom de fichier sûr**
- Entrée : Nom de rapport « ../../evil » puis « rapport final/v1 », dans un dossier temporaire.
- Résultat attendu : Le nom est refusé ou nettoyé. Aucun fichier n’est créé en dehors du dossier demandé, et aucun nom ne contient de séparateur de chemin.

**R11 — Rapport Markdown**
- Entrée : Un résultat OK sans alerte, puis un résultat ERREUR avec deux alertes.
- Résultat attendu : Un titre, une ligne par module avec son statut, les alertes listées sous leur module, dans l’ordre des résultats.

**Actions dans l’ordre**

1. Écris R9 : injecte 2026-01-05T08:00:00, écris les mêmes résultats dans deux dossiers temporaires et compare les octets JSON.
2. Écris R10 pour ../../evil et rapport final/v1 : refuse ou nettoie le nom, sans fichier hors du dossier ni séparateur restant. Documente ton choix dans la docstring.
3. Écris R11 : titre, ligne par module avec statut, puis alertes sous leur module, dans l’ordre des résultats.
4. Crée les fonctions d’écriture de rapport JSON et Markdown en respectant ces cas.
5. Documente le code de sortie choisi pour la commande, relance R9 à R11 et la suite, puis commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
.venv/bin/python -m unittest -v
```

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs. rapport_a et rapport_b désignent les deux dossiers que tu crées pour ton essai ; adapte leurs noms aux sorties de ton programme.

```bash
cmp rapport_a/rapport.json rapport_b/rapport.json   # sans sortie : fichiers identiques
```

**Terminal · Enregistrer le travail vérifié**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git add reconwrap/rapport.py tests/test_rapport.py
git commit -m "Ajoute les rapports JSON et Markdown"
```

**Tu sais que c’est bon quand :** R9, R10 et R11 passent ; deux écritures donnent des JSON identiques ; aucun fichier ne sort du dossier demandé.

*Indice si tu bloques :* Passe la date en argument de la fonction et écris le JSON avec sort_keys=True. Pour R11, lis les résultats dans l’ordre reçu et construis les lignes au fur et à mesure.

#### Palier 11 — Démonstrations contre le labo (hors CI) (8 min)

Prouver, à un moment donné et labo démarré, que D1 à D6 se comportent comme attendu. Ce ne sont pas des tests.

**Où tu travailles :** Outils réels dans Docker ; MR GitLab

**Pour comprendre**

- Les six démos lancent les voies réelles. Le pipeline futur continuera à lire des fixtures et des données injectées.
- Dans Docker, utilise python3 ; un venv créé sur le Mac n’est pas réutilisable dans le conteneur.

**Actions dans l’ordre**

1. Démarre le labo intégré. Ouvre le conteneur et place-toi dans /workspaces/reconwrap.
2. D1 : réseau, port 8000 open. D2 : web /fragile, trois alertes. D3 : web /durci, zéro alerte.
3. D4 : /absent puis /erreur, ERREUR avec les codes 404 puis 500 conservés.
4. D5 : adsim, comptes fictifs LAB.LOCAL. D6 : arrête le labo, observe une panne web sans code HTTP et un rapport tout de même écrit ; relance ensuite le labo.
5. Note les résultats dans les notes du parcours, puis relance les tests et relis le diff contre main.
6. Commite le travail nécessaire, pousse feat/orchestration-rapport et ouvre MR2 dans GitLab. Fusionne après relecture et autorisation de l’école ; la CI arrive en MR3. Mets main à jour.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -m reconwrap --modules network --cible 127.0.0.1 --format json --sortie rapports/   # D1
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -m reconwrap --modules web --chemin /fragile --format md --sortie rapports/   # D2
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -m reconwrap --modules web --chemin /durci --format md --sortie rapports/   # D3
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -m reconwrap --modules web --chemin /absent --format md --sortie rapports/   # D4 (puis --chemin /erreur)
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -m reconwrap --modules ad --format json --sortie rapports/   # D5, dans le conteneur
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -m reconwrap --modules network,web,ad --format json --sortie rapports/   # D6, labo arrêté
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -m unittest -v
```

**Terminal · Relire l’état du dépôt**

```bash
git status
git diff main --stat
```

**Terminal · Publier la branche ou ouvrir la demande de fusion**

```bash
git push -u origin feat/orchestration-rapport
```

**Terminal · Après la fusion : actualiser la principale**

```bash
git switch main
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git pull --ff-only
```

**Tu sais que c’est bon quand :** D1 : port 8000 open. D2 : trois alertes. D3 : zéro alerte. D4 : ERREUR avec 404, puis 500. D5 : comptes LAB.LOCAL. D6 : panne web distincte d’un code HTTP, et le rapport est écrit.

*Indice si tu bloques :* Si une démonstration donne un résultat inattendu, vérifie d’abord que le labo est démarré (son bouton) avant de changer le code.

**Démonstrations manuelles (hors CI)**

Ces essais utilisent le laboratoire ou les outils réels. Ils sont séparés des tests obligatoires.

**D1 — Réseau contre le labo**
- Entrée : Labo démarré avec son bouton. python -m reconwrap --modules network --cible 127.0.0.1 --format json --sortie rapports/
- Résultat attendu : Le port 8000 est signalé open dans le rapport JSON.

**D2 — Web : chemin fragile**
- Entrée : Labo démarré. --modules web --chemin /fragile --format md
- Résultat attendu : Trois alertes, une par en-tête absent ou non conforme.

**D3 — Web : chemin durci**
- Entrée : Labo démarré. --modules web --chemin /durci --format md
- Résultat attendu : Zéro alerte.

**D4 — Erreurs HTTP 404 et 500**
- Entrée : Labo démarré. --modules web avec --chemin /absent, puis --chemin /erreur.
- Résultat attendu : Statut ERREUR avec le code 404, puis avec le code 500 ; alertes vide dans les deux cas.

**D5 — Active Directory avec adsim**
- Entrée : python -m reconwrap --modules ad --format json --sortie rapports/ (dans le conteneur).
- Résultat attendu : Les comptes du domaine LAB.LOCAL apparaissent avec leur état actif ou inactif. Aucun annuaire réel n’est contacté.

**D6 — Labo arrêté**
- Entrée : Arrête le labo avec son bouton, puis lance --modules network,web,ad.
- Résultat attendu : Le module web signale une panne de connexion, distincte d’un code HTTP. Les autres modules produisent quand même leur résultat et le rapport est écrit.

**Avant de livrer**

- Les neuf tests R6 à R14 passent localement avec python -m unittest, sans nmap, sans labo et sans réseau.
- Un module en échec ne bloque ni les autres modules ni l’écriture du rapport. Le code de sortie choisi est documenté et identique à chaque lancement.
- Toute cible autre que 127.0.0.1 est refusée avant l’appel d’un module. Le code n’utilise jamais shell=True.
- Les démonstrations D1 à D6 sont consignées à part, avec le labo démarré explicitement. Elles ne figurent pas dans la CI.

### MR3 — feat/doc-qualite (70 min)

Tu livres une version qu’une autre personne peut lancer et étendre avec le contrat existant. Avance dans l’ordre des paliers et vérifie chaque résultat avant de poursuivre.

**Avant de commencer**

- Point de départ : MR2 fusionnée ; les trois modules, la CLI et les rapports fonctionnent.
- Ce que tu vas produire : Documentation, tests de contrat et d’aide, CI, CHANGELOG, docs/PROJET_FINAL.md et tag v0.1.0.
- Pourquoi : Tu livres une version qu’une autre personne peut lancer et étendre avec le contrat existant.
- Commande des tests depuis la racine : `.venv/bin/python -m unittest -v`. Les cas ci-dessous sont à écrire par toi.

#### Palier 1 — Relire le diff et documenter l’API (10 min)

Relire ton diff comme si c’était celui d’un autre, puis ajouter docstrings et annotations à l’API publique.

**Où tu travailles :** reconwrap/

**Pour comprendre**

- La branche principale (main) contient le travail déjà fusionné. Ta branche feat/... reçoit les changements de cette mission.
- Un dépôt « propre » n’a aucune modification en attente : git status te le confirme.

**Éditeur · Exemple travaillé, sans rapport avec ReconWrap **

Éditeur : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
def compter_mots(texte: str) -> int:
    """Retourne le nombre de mots d’un texte."""
    return len(texte.split())
```

**Actions dans l’ordre**

1. Ouvre workspaces/reconwrap dans VS Code, ou Coder dans Cyber Atelier avec cwd sur « . ».
2. Vérifie que MR2 est fusionnée.
3. Lis git status ; enregistre ton travail en cours avant de changer de branche.
4. Reviens sur main avec git switch main, mets-la à jour avec git pull --ff-only, puis crée feat/doc-qualite. Remplace main par master si ton dépôt utilise ce nom.
5. Écris une checklist hors du dépôt : noms, erreurs, effets de bord, chemins, tests. Relis le code avec elle ; ajoute aux fonctions publiques des annotations et une docstring décrivant action, paramètres et retour. Relance les tests.
6. Vérifie le nom de ta branche avec git status. Si elle existe déjà, reprends-la avec git switch sans -c.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git switch main && git pull --ff-only && git switch -c feat/doc-qualite
```

**Terminal · Relire l’état du dépôt**

```bash
git diff main --stat
git diff main
```

**Terminal · Commande à lancer au moment indiqué**

```bash
.venv/bin/python -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add reconwrap/
git commit -m "Ajoute docstrings et annotations de type"
```

**Tu sais que c’est bon quand :** Chaque fonction publique a une docstring exacte et des annotations ; les tests passent toujours.

*Indice si tu bloques :* Relis en te mettant à la place de quelqu’un qui n’a pas écrit le code : si un nom ou un message ne dit pas ce qu’il fait, corrige le nom ou la docstring.

#### Palier 2 — Écrire le README (10 min)

Écrire un README qu’une personne sans aide peut suivre pour installer, lancer et étendre l’outil.

**Où tu travailles :** README.md

**Pour comprendre**

- Un README utilisable donne les commandes exactes et les dossiers où les exécuter.
- Ajouter un module suit le contrat : fonction, inscription dans le registre, tests ; le dispatch reste identique.

**Éditeur · Exemple travaillé, sans rapport avec ReconWrap **

Éditeur : exemple de syntaxe, à adapter ; ce bloc ne se lance pas dans le terminal.

````markdown
# Recettes
## Installation
```bash
python3 -m venv .venv
```
````

**Actions dans l’ordre**

1. Rédige installation avec venv, lancement, cinq options CLI et commande des tests.
2. Décris l’architecture par domaine et les trois gestes d’ajout d’un module.
3. Précise le périmètre loopback et les limites éthiques/légales.
4. Suis le README dans un clone temporaire propre : crée son venv, lance tests et aide.
5. Corrige chaque instruction qui demandait de deviner un chemin ou une option, puis commite.

**Terminal · Enregistrer le travail vérifié**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git add README.md
git commit -m "Rédige le README"
```

**Tu sais que c’est bon quand :** Tu as suivi le README dans un dossier propre et tu lances les tests et l’aide sans rien devoir deviner.

*Indice si tu bloques :* Pour chaque étape du README, écris la commande exacte puis le résultat attendu. Une phrase qui ne correspond à rien dans le code doit être corrigée.

#### Palier 3 — Contrat des trois modules et aide CLI (R15, R17) (8 min)

Vérifier que les trois modules respectent le contrat hors ligne, et que l’aide de la CLI est complète.

**Où tu travailles :** tests/test_contrat.py ; tests/test_cli.py

**Pour comprendre**

- Le contrat commun permet de vérifier les trois domaines avec les mêmes critères. subTest nomme chaque sous-cas sans arrêter les suivants.
- Tester l’aide confirme que l’entrée publique fonctionne sans démarrer de module.

**Éditeur · Exemple travaillé, sans rapport avec ReconWrap **

Éditeur : place ce code dans un fichier d’exemple jetable, puis lance ce fichier avec python3. Un extrait avec self se place dans une méthode de test.

```python
import unittest
class TestCarres(unittest.TestCase):
    def test_carres(self):
        for n, attendu in [(2, 4), (3, 9)]:
            with self.subTest(n=n):
                self.assertEqual(n * n, attendu)
```

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**R15 — Contrat des trois modules hors ligne**
- Entrée : Résultats de network (fixture XML), ad (fixture JSON) et web (classement injecté), relus avec la fabrique de résultat de MR1.
- Résultat attendu : Les trois résultats ont les cinq clés, un statut OK, ERREUR ou IGNORE, et une liste d’alertes.

**R17 — Aide de la CLI**
- Entrée : python -m reconwrap --help
- Résultat attendu : Code de sortie 0. L’aide affiche les options --modules, --cible, --chemin, --format et --sortie.

**Actions dans l’ordre**

1. Écris R15 dans tests/test_contrat.py : network depuis XML, ad depuis JSON, web depuis code/en-têtes injectés.
2. Pour chaque résultat, vérifie les cinq clés, un statut OK/ERREUR/IGNORE et la liste d’alertes avec la fabrique de MR1.
3. Écris R17 : python -m reconwrap --help rend 0 et affiche --modules, --cible, --chemin, --format, --sortie.
4. Utilise subTest si utile pour identifier les trois domaines, relance puis commite les tests.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
.venv/bin/python -m unittest -v
```

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs. Lance le programme et echo $? ensemble : le nombre affiché est le code du programme ; la console peut afficher code 0 pour echo lui-même.

```bash
.venv/bin/python -m reconwrap --help; echo $?
```

**Terminal · Enregistrer le travail vérifié**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git add tests/test_contrat.py tests/test_cli.py
git commit -m "Ajoute les tests de contrat et d’aide CLI"
```

**Tu sais que c’est bon quand :** R15 et R17 passent, et l’aide affiche les cinq options.

*Indice si tu bloques :* Pour un module hors ligne, passe-lui le fichier de fixture au lieu de le lancer : le test reste rapide et sans réseau.

#### Palier 4 — Le pipeline GitLab et la suite complète (R16) (10 min)

Écrire le pipeline qui lance les tests sur chaque merge request, et prouver que la suite passe sans labo ni nmap.

**Où tu travailles :** .gitlab-ci.yml

**Pour comprendre**

- GitLab exécute le fichier .gitlab-ci.yml depuis la racine du dépôt sur son runner. Le job doit utiliser un environnement Python.
- La suite est indépendante de nmap, adsim et du labo ; les démonstrations ne doivent pas entrer dans ce job.

**Éditeur · Exemple YAML sans rapport avec ReconWrap **

Éditeur : exemple de syntaxe, à adapter ; ce bloc ne se lance pas dans le terminal.

```yaml
courses:
  - lait
  - pain
```

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**R16 — Suite complète sans labo**
- Entrée : python -m unittest lancé depuis la racine, labo arrêté et nmap absent du système.
- Résultat attendu : Code de sortie 0. Les tests R1 à R15 sont découverts, et aucun test ne se connecte à 127.0.0.1:8000 ni n’appelle nmap ou adsim.

**Actions dans l’ordre**

1. Lis l’exemple YAML pour repérer les niveaux d’indentation, puis rédige la CI toi-même.
2. Prévois une image Python et un job limité aux MR, qui lance python -m unittest depuis la racine.
3. R16 : arrête le labo, vérifie que R1 à R15 sont découverts et que la suite sort avec 0 sans appel réseau, nmap ou adsim.
4. Relis les tests pour confirmer l’usage des fixtures, données injectées et faux.
5. Commite, pousse et ouvre MR3 ; attends son pipeline. S’il manque un runner, note cet état au lieu d’annoncer la CI validée.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs. Lance le programme et echo $? ensemble : le nombre affiché est le code du programme ; la console peut afficher code 0 pour echo lui-même.

```bash
.venv/bin/python -m unittest; echo $?
```

**Terminal · Enregistrer le travail vérifié**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git add .gitlab-ci.yml
git commit -m "Ajoute le pipeline GitLab qui lance unittest"
```

**Terminal · Publier la branche ou ouvrir la demande de fusion**

```bash
git push -u origin feat/doc-qualite
```

**Tu sais que c’est bon quand :** La commande du pipeline est celle que tu as testée en local, depuis la racine, et elle sort avec 0. Le statut du pipeline dans GitLab est noté tel qu’il est.

*Indice si tu bloques :* Le piège fréquent : une commande qui marche depuis un sous-dossier, mais pas depuis la racine. Tu lances tes tests depuis la racine, comme le pipeline.

#### Palier 5 — Le CHANGELOG de la version 0.1.0 (8 min)

Écrire l’historique de la version 0.1.0 : ce qui est ajouté et ce qui reste limité.

**Où tu travailles :** CHANGELOG.md

**Pour comprendre**

- Le CHANGELOG décrit les changements visibles d’une version. Il permet de comprendre ce qui est livré et ses limites.
- Un ajout annoncé doit déjà exister ; une idée future va dans les pistes, pas dans les fonctionnalités livrées.

**Éditeur · Exemple travaillé, sans rapport avec ReconWrap **

Éditeur : exemple de syntaxe, à adapter ; ce bloc ne se lance pas dans le terminal.

```markdown
## 0.1.0
### Ajouté
- Recette de crêpes.
### Limites connues
- Pas de version sans gluten.
```

**Actions dans l’ordre**

1. Crée CHANGELOG.md avec une section 0.1.0.
2. Liste les ajouts en phrases courtes du point de vue de l’utilisateur.
3. Ajoute les limites connues, notamment outils fictifs et périmètre local.
4. Vérifie chaque affirmation contre le code puis commite.

**Terminal · Enregistrer le travail vérifié**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git add CHANGELOG.md
git commit -m "Ajoute le CHANGELOG pour la version 0.1.0"
```

**Tu sais que c’est bon quand :** CHANGELOG.md contient une section 0.1.0 avec des ajouts et des limites connues.

*Indice si tu bloques :* Une limite connue est une information utile : par exemple, le module AD ne tourne que sur le domaine fictif.

#### Palier 6 — La page sur le projet final (8 min)

Rédiger un bilan honnête : ce qui est fait, ce qui reste à apprendre, et les autorisations nécessaires.

**Où tu travailles :** docs/PROJET_FINAL.md

**Pour comprendre**

- Le bilan distingue compétences pratiquées, idées de futur projet et compétences encore à apprendre.
- Le module AD réel reste une idée de projet : adsim n’est pas un annuaire réel.

**Actions dans l’ordre**

1. Crée docs/PROJET_FINAL.md avec ce que tu ferais, ce que tu ne ferais pas et ce qui reste à apprendre.
2. Dans les idées, décris un module AD réel sur un domaine autorisé et une interface graphique optionnelle.
3. Précise l’accord écrit, daté, du propriétaire nécessaire pour travailler sur un vrai domaine.
4. Distingue clairement réalisé et envisagé, puis commite le document.

**Terminal · Enregistrer le travail vérifié**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git add docs/PROJET_FINAL.md
git commit -m "Rédige la page sur le projet final"
```

**Tu sais que c’est bon quand :** docs/PROJET_FINAL.md distingue fait, à faire, et autorisation nécessaire.

*Indice si tu bloques :* Un projet qui touche à un vrai réseau ou un vrai annuaire demande une autorisation écrite avant le premier test, même pour un essai rapide.

#### Palier 7 — Un conflit et un revert dans des branches jetables (8 min)

Résoudre un conflit en lisant les marqueurs, et annuler un commit avec git revert, sans toucher à la branche principale.

**Où tu travailles :** README.md dans les branches jetables

**Pour comprendre**

- Un conflit demande de choisir le contenu final. Un revert enregistre un commit inverse sans effacer l’historique.
- Les trois branches sont locales et jetables ; aucune n’est poussée.

**Actions dans l’ordre**

1. Commite tout le travail utile de feat/doc-qualite ; git status doit être propre.
2. Depuis main, crée jetable-conflit-a puis jetable-conflit-b ; remplace la première ligne README par Variante A ou B et commite dans chacune.
3. Fusionne A dans B. Résous le conflit, enlève les marqueurs, ajoute et commite ; observe le fichier et le graphe avant nettoyage.
4. Depuis main, crée jetable-revert : ajoute une ligne d’essai, commite puis lance git revert HEAD --no-edit. Observe erreur et inverse dans l’historique.
5. Reviens sur feat/doc-qualite et supprime uniquement ces trois branches. -D abandonne leur historique local non fusionné.
6. Relance la suite sur la vraie branche.

**Terminal · Relire l’état du dépôt**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git status
git switch main
git pull --ff-only
git switch -c jetable-conflit-a
```

**Terminal · Commande à lancer au moment indiqué**

```bash
# Après modification de la première ligne :
git add README.md
git commit -m "Essai A"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git switch main
git switch -c jetable-conflit-b
```

**Terminal · Commande à lancer au moment indiqué**

```bash
# Après modification de la même ligne :
git add README.md
git commit -m "Essai B"
git merge jetable-conflit-a
```

**Terminal · Commande à lancer au moment indiqué**

```bash
# Après résolution dans l’éditeur :
git add README.md
git commit -m "Résout le conflit d’essai"
git log --oneline --graph -5
grep -n "<<<<<<<\|=======\|>>>>>>>" README.md
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git switch main
git switch -c jetable-revert
```

**Terminal · Commande à lancer au moment indiqué**

```bash
# Après ajout de la ligne d’essai :
git add README.md
git commit -m "Commit de test"
git revert HEAD --no-edit
git log --oneline -3
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git switch feat/doc-qualite
git branch -D jetable-conflit-a jetable-conflit-b jetable-revert
git branch
.venv/bin/python -m unittest -v
```

**Tu sais que c’est bon quand :** Avant nettoyage, tu as observé un conflit résolu sans marqueurs et un commit suivi de son revert. Après nettoyage, tu es sur feat/doc-qualite, les branches jetables ont disparu et les tests passent.

*Indice si tu bloques :* Ne garde jamais les marqueurs. Pour annuler, utilise git revert sur une branche jetable, pas git reset. git branch -D ne sert qu’aux branches jetables.

#### Palier 8 — Ouvrir la MR3, la fusionner et poser le tag v0.1.0 (8 min)

Faire relire la MR3, la fusionner si l’école l’autorise, puis poser le tag annoté v0.1.0 sur la principale.

**Où tu travailles :** MR GitLab ; tag v0.1.0

**Pour comprendre**

- Le tag annoté fige la version livrée avec message et auteur. Il doit désigner le main mis à jour après fusion.
- Un pipeline vert, l’autorisation de fusion et la présence du tag sont des vérifications différentes.

**Actions dans l’ordre**

1. Relis le diff de MR3 avec la checklist du palier 1. Commite et pousse les derniers changements.
2. Ouvre ou actualise MR3, puis attends le pipeline du dernier commit.
3. Fusionne seulement si le pipeline et l’école le permettent ; sinon conserve l’état réel comme non validé.
4. Après fusion, mets main à jour et crée le tag annoté v0.1.0 avec un message.
5. Compare git show v0.1.0 au commit de main, puis pousse le tag séparément.

**Terminal · Relire l’état du dépôt**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git status
```

**Terminal · Publier la branche ou ouvrir la demande de fusion**

```bash
git push -u origin feat/doc-qualite
```

**Terminal · Après la fusion : actualiser la principale**

```bash
git switch main && git pull --ff-only
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git tag -a v0.1.0 -m "ReconWrap 0.1.0"
```

**Terminal · Publier la branche ou ouvrir la demande de fusion**

```bash
git push origin v0.1.0
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git show --stat v0.1.0
```

**Tu sais que c’est bon quand :** git tag --list affiche v0.1.0, et git show v0.1.0 pointe sur le même commit que main après fusion.

*Indice si tu bloques :* Si la fusion n’a pas eu lieu, ne pose pas le tag. Un tag annoté a son propre message : écris-le court.

**Avant de livrer**

- Une personne qui n’a pas écrit le code peut installer et lancer l’outil en suivant le README, sans aide extérieure.
- Le pipeline de la MR lance python -m unittest et passe. Si l’instance de l’école n’a pas de runner, note-le au lieu de déclarer la CI validée.
- Le tag v0.1.0 pointe sur le commit fusionné de la principale. Le conflit et le revert ont été faits dans des branches jetables, supprimées ensuite.
- docs/PROJET_FINAL.md distingue ce qui est fait, ce qui reste à apprendre, et précise l’autorisation nécessaire pour tout test sur un vrai domaine.

<!-- END GENERATED EXERCISES -->

## Méthode GitLab

Utilise un dépôt autorisé par ton école. Vérifie que le runner est actif sur les branches de merge request et que tu as les droits d’ouverture et de fusion. Pour chaque étape : pars de la branche principale à jour, écris le code et les tests, lance `python -m unittest` en local, relis le diff, pousse, ouvre la merge request, attends un pipeline vert, puis fusionne. Après chaque fusion, mets la principale à jour avant de créer la branche suivante.

**Quatre résultats à ne pas confondre :**

- les tests locaux que tu lances toi-même ;
- le pipeline GitLab réellement exécuté sur le runner ;
- l’autorisation effective de fusion donnée par les règles de l’école ;
- la case cochée dans Cyber Atelier, qui est déclarative et ne vérifie rien.

Les démonstrations D1 à D6 ne sont pas des tests de la CI : elles prouvent seulement que le labo réagit comme attendu, à un moment donné.

## Repères de temps

Préparation (Python, Git, venv, lecture du contrat) : 20 min. MR1 architecture, contrat et registre : 100 min. MR2 modules, CLI et rapports : 100 min. MR3 documentation, qualité et release : 70 min. Marge et relecture finale : 10 min. Total : 300 min.

## Livrables et limites

**Livrables.** Un package `reconwrap/` fonctionnel, des fixtures copiées dans le dépôt, une suite de tests unittest, un `.gitlab-ci.yml` qui lance cette suite, un README complet, un `CHANGELOG.md`, le tag `v0.1.0`, trois merge requests successives, les démonstrations D1 à D6 consignées séparément, et un bilan honnête.

**Limites.**

- Le périmètre est loopback : 127.0.0.1 uniquement. Pas de scan de plage, pas de cible distante, pas d’exploitation.
- Les tests de CI s’appuient sur des fixtures : ils valident la logique, pas le comportement sur un vrai réseau. Les démonstrations exigent le labo démarré.
- `adsim` est un simulateur fictif (domaine `LAB.LOCAL`) : le module AD n’est pas testé contre un annuaire réel dans ce parcours.
- Un framework d’outils de sécurité ne vaut pas audit. Tout usage hors d’un cadre autorisé par écrit est interdit et engage ta responsabilité légale.
