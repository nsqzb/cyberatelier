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

Ces exercices sont ton entraînement. Chaque palier explique les notions utiles, montre les données ou les règles attendues, puis te fait écrire et vérifier ton propre code. Les durées sont des repères : avance quand tu comprends le résultat.

1. Lis « Pour comprendre » et l’exemple lorsqu’il y en a un. Repère ce qui entre dans le programme, ce qui doit en sortir et les règles à respecter.
2. Les cartes de tests donnent l’entrée et le résultat attendu. Écris les tests correspondants dans le fichier indiqué ; cocher un palier ne les exécute pas. Avec unittest, « Ran 0 tests » signifie qu’aucun test n’a été exécuté : ce n’est pas une validation. Un cas décrit peut contenir plusieurs valeurs ; le nombre de méthodes Python n’est donc pas forcément le nombre d’identifiants.
3. Suis les actions numérotées, une à la fois. Les exemples servent à apprendre une notion ; tu écris toi-même la solution de l’exercice. Les blocs Terminal donnent les commandes à lancer au moment indiqué.
4. Vérifie le résultat indiqué avant de poursuivre. Un échec attendu (phase rouge, argument refusé ou conflit volontaire) est expliqué dans le palier.
5. Si tu bloques, lis la dernière ligne de l’erreur, compare entrée et attendu, puis demande un seul indice à la fois avec python3 atelier.py indice depuis cyberatelier. Les trois niveaux vont du rappel à un petit exemple ; ils ne donnent pas une fonction corrigée.

### Le bon endroit pour chaque action

Ouvre `workspaces/fileguard` dans VS Code et un terminal du Mac dans ce même dossier. Tu écris et testes le code ici, dans le dépôt Git de l’exercice. Ouvre un second terminal dans `cyberatelier` pour lire les consignes avec `python3 atelier.py voir` et piloter Docker. Le site reste disponible pour la lecture ; l’onglet Coder est facultatif.

Depuis `cyberatelier`, `mkdir -p workspaces/fileguard` puis `cd workspaces/fileguard` permet de rejoindre le dossier du parcours. S’il contient déjà ton exercice, garde ses fichiers, sa branche et son dépôt : ne le reclone pas. La préparation ci-dessous se fait une fois ; la mission crée ensuite sa branche.

Le code Python se place dans VS Code et doit être enregistré avant les tests. Les commandes `docker compose ...` et `python3 atelier.py ...` se lancent depuis `cyberatelier`. Leurs appels Docker entrent dans le conteneur ; `/app/fixtures`, `/app/tools` et `/workspaces` sont des chemins internes à celui-ci. Depuis le dépôt d’exercice sur le Mac, les fixtures fournies sont dans `../../fixtures`.

Le terminal du Mac conserve son `cd` et son activation de venv. Active `.venv` dans chaque nouveau terminal d’exercice ; `python3` utilise alors ce venv, ou appelle `.venv/bin/python` explicitement. Lis `echo $?` immédiatement après le programme dont tu veux le code, avant toute autre commande. Ajoute `.venv/` à `.gitignore` avant `git add`.

PortPilot et HeaderScope exécutés sur le Mac : lance `python3 labs.py` depuis `cyberatelier` dans un autre terminal et garde-le ouvert ; Ctrl+C arrête ce labo Mac. Les outils ToolWrap et les démos ReconWrap tournent dans Docker : `python3 atelier.py labo demarrer`, `labo arreter` et `labo statut` depuis `cyberatelier` pilotent uniquement le labo Docker. Le même numéro 8000 ne relie pas automatiquement les deux environnements.

Un venv créé sur le Mac ne fonctionne pas dans Docker : les démos dans le conteneur utilisent son `python3`. Le dossier hôte `workspaces` doit être monté dans Docker pour que les démos ReconWrap lisent ton code ; conserve le `compose.override.yaml` du mode VS Code. Remplace `main` par `master` si nécessaire. Si une branche existe, reprends-la avec `git switch NOM` sans `-c`. Après chaque fusion, actualise la principale dans le dépôt du parcours avant la mission suivante.

### Préparation sur le Mac

**Vérifier Python**

Terminal du Mac, dans cyberatelier/workspaces/fileguard.

```bash
python3 --version
```

Python 3 doit être installé sur ton Mac. Ce parcours utilise seulement sa bibliothèque standard ; aucun pip install n’est demandé.

**Vérifier Git**

Terminal du Mac, dans cyberatelier/workspaces/fileguard.

```bash
git --version
```

Vérifie Git sur ton Mac. Les commandes du parcours agissent sur ce dépôt d’exercice, distinct du dépôt cyberatelier.

**Configurer ton identité Git (une seule fois)**

Terminal du Mac, dans cyberatelier/workspaces/fileguard.

```bash
git config --global user.name "Prénom Nom" && git config --global user.email "adresse@ecole.example"
```

Remplace les deux valeurs d’exemple par ton nom et l’adresse de ton compte scolaire. Cette configuration globale est enregistrée sur ton Mac ; sans identité, git commit refuse le commit.

**Cloner le dépôt**

Terminal du Mac, dans cyberatelier/workspaces/fileguard.

```bash
git clone <URL_DU_DEPOT> .
```

Depuis le terminal du Mac dans workspaces/fileguard, clone seulement si le dossier est vide et n’a pas encore de dépôt. Remplace <URL_DU_DEPOT> par l’URL autorisée réelle avant exécution ; le point signifie « ici ». Si ton exercice existe déjà, garde-le et passe directement à git status. HTTPS ou SSH peut demander une saisie dans ce terminal.

**Créer le venv**

Terminal du Mac, dans cyberatelier/workspaces/fileguard.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Après le clone, crée ce venv sur le Mac une seule fois ; s’il existe, active-le simplement. L’activation reste valable dans ce terminal. Dans un nouveau terminal, réactive-le ou appelle .venv/bin/python. Ajoute .venv/ à .gitignore avant git add. Aucun paquet pip n’est nécessaire.

**Copier les fixtures fictives (MR2)**

Terminal du Mac, dans cyberatelier/workspaces/fileguard.

```bash
mkdir -p fixtures && cp ../../fixtures/integrity/* fixtures/ && chmod u+w fixtures/*
```

Les originaux sont fournis en lecture seule dans ../../fixtures/integrity ; chmod u+w rend tes copies modifiables, par exemple pour simuler un fichier modifié. Ce sont des données fictives : elles ne remplacent pas les tests sur fichiers temporaires. La source est dans le dépôt cyberatelier sur ton Mac ; /app/fixtures est réservée au conteneur.

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

### MR1 — feat/empreinte (85 min)

Une empreinte décrit les octets d’un fichier ; elle servira à construire le manifeste en MR2. Avance dans l’ordre des paliers et vérifie chaque résultat avant de poursuivre.

**Avant de commencer**

- Point de départ : Un dépôt cloné ; tu disposes de Python 3 et Git. Les tests créeront eux-mêmes leurs fichiers.
- Ce que tu vas produire : fileguard.py, verification.py et .gitlab-ci.yml : calculer et tester une empreinte SHA-256.
- Pourquoi : Une empreinte décrit les octets d’un fichier ; elle servira à construire le manifeste en MR2.
- Commande des tests depuis la racine : `python3 verification.py`. Les cas ci-dessous sont à écrire par toi.

#### Palier 1 — Prépare la branche feat/empreinte (6 min)

Partir d’un dépôt propre, sur une branche dédiée à cette MR.

**Où tu travailles :** Mac · workspaces/fileguard · Dépôt

**Pour comprendre**

- La branche principale (main) contient le travail déjà fusionné. Ta branche feat/... reçoit les changements de cette mission.
- Un dépôt « propre » n’a aucune modification en attente : git status te le confirme.

**Actions dans l’ordre**

1. Ouvre workspaces/fileguard dans VS Code. Dans le terminal du Mac, place-toi dans ce même dossier et active son venv avec source .venv/bin/activate.
2. Si le dépôt n’est pas cloné, fais d’abord la préparation décrite au début du guide.
3. Lis git status ; enregistre ton travail en cours avant de changer de branche.
4. Reviens sur main avec git switch main, mets-la à jour avec git pull --ff-only, puis crée feat/empreinte. Remplace main par master si ton dépôt utilise ce nom.
5. Vérifie le nom de ta branche avec git status. Si elle existe déjà, reprends-la avec git switch sans -c.

**Terminal · Relire l’état du dépôt**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

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

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Une empreinte se développe dans le dépôt FileGuard ; sa branche est indépendante de celle de Cyber Atelier.

</details>

<details>
<summary>Indice 2</summary>

Vérifie le clone, le dossier workspaces/fileguard et main à jour avant de créer feat/empreinte.

</details>

<details>
<summary>Indice 3</summary>

git status dans workspaces/fileguard décrit les fichiers de l’exercice ; le lancer deux dossiers plus haut décrit l’application.

</details>

#### Palier 2 — Des octets, pas du texte (10 min)

Comprendre pourquoi on lit un fichier en mode binaire pour obtenir ses octets exacts.

**Où tu travailles :** Mac · workspaces/fileguard · Terminal : exemple binaire

**Pour comprendre**

- Un octet est une unité du contenu d’un fichier. bytes représente ces octets ; str représente du texte décodé.
- rb lit les octets tels quels ; wb les écrit. Un saut de ligne supplémentaire change aussi le contenu.

**Actions dans l’ordre**

1. Lance l’exemple terminal qui crée un fichier dans un dossier temporaire.
2. Observe b'pomme' et le type bytes. Compare avec "pomme", de type str.
3. Repère wb, rb et with. Vérifie que le dossier temporaire disparaît à la fin de l’exemple.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 -c "from pathlib import Path; from tempfile import TemporaryDirectory
with TemporaryDirectory() as dossier:
    p = Path(dossier) / 'fruits.bin'
    p.write_bytes(b'pomme')
    d = p.read_bytes()
    print(d, type(d))"
```

**Tu sais que c’est bon quand :** Tu vois b'pomme' et le type <class 'bytes'>.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

SHA-256 reçoit des octets ; décoder du texte ou ajouter un saut de ligne change les données calculées.

</details>

<details>
<summary>Indice 2</summary>

Observe bytes, lecture binaire et texte ; garde la lecture du fichier en mode binaire pour le calcul d’empreinte.

</details>

<details>
<summary>Indice 3</summary>

b'abc' contient 3 octets et b'abc\n' en contient 4 : le saut de ligne final est une donnée supplémentaire.

</details>

#### Palier 3 — Premier test rouge, puis premier code vert : F1 (14 min)

Écrire le test avant la fonction, voir l’échec, puis faire passer le test avec le minimum de code.

**Où tu travailles :** Mac · workspaces/fileguard · fileguard.py ; verification.py

**Pour comprendre**

- SHA-256 calcule une empreinte de 64 caractères hexadécimaux à partir des octets. Elle sert à comparer des contenus.
- Un oracle est une valeur attendue connue, écrite dans le test ; on ne la recalcule pas avec la fonction à vérifier.

**Exemple de résultat attendu**

Ce que tu donnes :

```text
Un fichier de zéro octet.
```

Ce que tu dois obtenir :

```text
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

Un fichier vide a une empreinte ; le retour n’est pas vide.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**F1 — Empreinte du fichier vide**
- Entrée : Fichier temporaire de zéro octet
- Résultat attendu : e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

**Actions dans l’ordre**

1. Crée verification.py : classe unittest.TestCase, méthodes test_, unittest.main() sous __main__.
2. Écris F1 : fichier temporaire de zéro octet, empreinte comparée à la constante du cas de test.
3. Lance et comprends le rouge : module ou fonction absente.
4. Crée fileguard.py et calculer_sha256(chemin) : lecture binaire, SHA-256, retour hexadécimal minuscule.
5. Relance F1, vérifie son exécution puis commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

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

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Le fichier vide possède une empreinte définie ; le test doit créer exactement zéro octet.

</details>

<details>
<summary>Indice 2</summary>

Écris F1 dans un dossier temporaire avant empreinte_fichier, puis compare l’hexadécimal complet à l’attendu.

</details>

<details>
<summary>Indice 3</summary>

Path('vide.bin').write_bytes(b'') crée un contenu vide ; écrire une ligne vide dans un éditeur peut créer un octet de saut de ligne.

</details>

#### Palier 4 — F2 : les trois octets abc, sans saut de ligne (14 min)

Vérifier que l’empreinte dépend des octets exacts, sans fin de ligne ajoutée.

**Où tu travailles :** Mac · workspaces/fileguard · fileguard.py ; verification.py

**Pour comprendre**

- b"abc" représente trois octets ; b"abc\n" en représente quatre et aurait une autre empreinte.
- Un nouveau test peut déjà passer : conserve-le même sans modification de code.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**F2 — Empreinte des trois octets abc**
- Entrée : Fichier temporaire contenant exactement b"abc", sans saut de ligne final
- Résultat attendu : ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad

**Actions dans l’ordre**

1. Ajoute F2 : écris exactement b"abc" dans un fichier temporaire en mode binaire.
2. Compare calculer_sha256 à la constante donnée pour F2, sans recalculer l’attendu.
3. En cas d’échec, vérifie les octets et le mode de lecture ; garde la constante intacte.
4. Relance F1 et F2 puis commite ; note si le code n’a pas eu besoin de changer.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add fileguard.py verification.py
git commit -m "Vérifie l’empreinte des trois octets abc"
```

**Tu sais que c’est bon quand :** F1 et F2 passent, et le code n’a pas été modifié pour contourner une constante.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

F2 porte sur les trois octets abc ; l’outil de création du fichier ne doit pas ajouter de caractère.

</details>

<details>
<summary>Indice 2</summary>

Crée le contenu dans le test avec des octets explicites et vérifie la taille avant de comparer l’empreinte connue.

</details>

<details>
<summary>Indice 3</summary>

print('abc') ajoute généralement un retour à la ligne ; write_bytes(b'abc') écrit exactement les trois octets demandés.

</details>

#### Palier 5 — F3 : deux contenus identiques, deux empreintes identiques (14 min)

Écrire un test qui crée lui-même ses fichiers et compare deux résultats.

**Où tu travailles :** Mac · workspaces/fileguard · fileguard.py ; verification.py

**Pour comprendre**

- L’empreinte dépend du contenu, pas du nom du fichier. Deux fichiers aux mêmes octets donnent la même empreinte.
- Le test prépare ses données pour rester indépendant de ton ordinateur.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**F3 — Contenus identiques**
- Entrée : Deux fichiers temporaires contenant les mêmes octets
- Résultat attendu : Empreintes identiques.

**Actions dans l’ordre**

1. Ajoute F3 : deux fichiers de noms différents, mêmes octets, dans un dossier temporaire.
2. Calcule les deux empreintes et compare-les.
3. Vérifie que le test ne lit ni fixture, ni journal, ni fichier personnel.
4. Relance F1 à F3 puis commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add fileguard.py verification.py
git commit -m "Vérifie que deux contenus identiques ont la même empreinte"
```

**Tu sais que c’est bon quand :** F1, F2 et F3 passent ; git log --oneline montre le nouveau commit.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Deux fichiers de même contenu ont la même empreinte, même si leurs noms sont différents.

</details>

<details>
<summary>Indice 2</summary>

Écris F3 avec deux chemins distincts et des octets identiques ; compare les résultats sans inclure les noms dans le calcul.

</details>

<details>
<summary>Indice 3</summary>

note-a.bin et note-b.bin contenant tous deux b'bonjour' doivent avoir la même empreinte ; changer seulement le chemin ne change pas les octets.

</details>

#### Palier 6 — Faire tourner la même suite dans la CI (15 min)

Comprendre ce que la CI exécute, et ce qu’elle ne prouve pas encore.

**Où tu travailles :** Mac · workspaces/fileguard · .gitlab-ci.yml

**Pour comprendre**

- YAML utilise les espaces pour exprimer les niveaux : les commandes script appartiennent à leur job.
- La CI exécute les tests sur un runner ; sa configuration seule ne prouve pas leur exécution.

**Éditeur · Exemple YAML à lire**

VS Code sur le Mac : exemple de syntaxe, à adapter ; ce bloc ne se lance pas dans le terminal.

```yaml
job-bonjour:
  script:
    - echo "bonjour"
```

**Actions dans l’ordre**

1. Lis le job bonjour de l’exemple et repère l’indentation.
2. Rédige .gitlab-ci.yml à la racine : un job lance uniquement python3 verification.py.
3. Ne copie aucune fixture et ne lis aucun chemin du portail dans ce job.
4. Lance la même commande en local et commite la CI. La livraison suivante vérifiera le pipeline.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add .gitlab-ci.yml
git commit -m "Ajoute la CI qui lance la suite locale"
```

**Tu sais que c’est bon quand :** Le fichier est commité. Le pipeline n’est confirmé que lorsque GitLab affiche un job exécuté et vert pour ta branche.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

La CI doit recréer ses fichiers temporaires et exécuter la même suite ; les fixtures du Mac ne sont pas présentes par magie.

</details>

<details>
<summary>Indice 2</summary>

Rédige le job sur les MR, vérifie la commande de tests et ouvre son journal après push.

</details>

<details>
<summary>Indice 3</summary>

Un test utilisant /Users/tonnom/Desktop/exemple.bin échoue ailleurs ; un fichier créé dans TemporaryDirectory peut être recréé sur le runner.

</details>

#### Palier 7 — Livre la MR1 sans confondre test local et fusion (12 min)

Relire le diff, pousser la branche, ouvrir la MR et ne fusionner que le dernier commit vert.

**Où tu travailles :** Mac · workspaces/fileguard · MR GitLab

**Pour comprendre**

- git diff montre les lignes modifiées ; git diff --staged montre celles choisies pour le prochain commit. Le diff de la MR compare toute ta branche à main.
- La demande de fusion (MR dans GitLab, PR dans GitHub) permet de relire le travail avant de l’intégrer à main.

**Actions dans l’ordre**

1. Lance la suite complète avec la commande indiquée au début de la mission.
2. Relis git status et git diff : la livraison doit contenir fileguard.py, verification.py et .gitlab-ci.yml, sans __pycache__, avec les modifications nécessaires de cette mission.
3. Ajoute les fichiers par leur nom, relis git diff --staged, puis commite ce qui ne l’est pas encore.
4. Pousse feat/empreinte et ouvre la demande de fusion vers main.
5. Dans GitLab, ouvre le pipeline du dernier commit : vérifie qu’il a réellement exécuté les tests et qu’il est vert. Un test local réussi ne le remplace pas.
6. Relis le diff et fusionne lorsque le pipeline et les règles de l’école le permettent.
7. Après la fusion, reviens sur main et lance git pull --ff-only avant la mission suivante.

**Terminal · Relire l’état du dépôt**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

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

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Tests locaux, pipeline et autorisation de fusion répondent à des questions différentes.

</details>

<details>
<summary>Indice 2</summary>

Relis les fichiers et le dernier commit vert de la MR, puis mets main à jour seulement après sa fusion.

</details>

<details>
<summary>Indice 3</summary>

Une suite locale verte peut accompagner une MR dont le runner est en attente ; écris cet état précis au lieu d’annoncer la CI réussie.

</details>

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

**Où tu travailles :** Mac · workspaces/fileguard · Dépôt

**Pour comprendre**

- La branche principale (main) contient le travail déjà fusionné. Ta branche feat/... reçoit les changements de cette mission.
- Un dépôt « propre » n’a aucune modification en attente : git status te le confirme.

**Actions dans l’ordre**

1. Ouvre workspaces/fileguard dans VS Code. Dans le terminal du Mac, place-toi dans ce même dossier et active son venv avec source .venv/bin/activate.
2. Vérifie que MR1 est fusionnée et que F1 à F3 passent sur main.
3. Lis git status ; enregistre ton travail en cours avant de changer de branche.
4. Reviens sur main avec git switch main, mets-la à jour avec git pull --ff-only, puis crée feat/manifest. Remplace main par master si ton dépôt utilise ce nom.
5. Vérifie le nom de ta branche avec git status. Si elle existe déjà, reprends-la avec git switch sans -c.

**Terminal · Après la fusion : actualiser la principale**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

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

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Le manifeste réutilise la fonction d’empreinte fusionnée ; MR2 part d’une base verte.

</details>

<details>
<summary>Indice 2</summary>

Actualise main, relance F1 à F3 et crée ou reprends feat/manifest avant d’éditer.

</details>

<details>
<summary>Indice 3</summary>

Si empreinte_fichier manque sur la principale, tu n’as pas encore récupéré la livraison de MR1 ; ajouter le manifeste ne corrige pas cette base.

</details>

#### Palier 2 — Copie les fixtures fictives dans ton dépôt (8 min)

Disposer d’un petit dossier d’exemple, relisible, dans le dépôt.

**Où tu travailles :** Mac · workspaces/fileguard · fixtures/

**Pour comprendre**

- Les fixtures sont trois fichiers fictifs fournis pour les essais ; leurs copies font partie de cette livraison.
- chmod u+w permet de modifier les copies, sans toucher aux originaux.

**Actions dans l’ordre**

1. Sur le Mac, depuis workspaces/fileguard, copie ../../fixtures/integrity dans fixtures/. Les trois fichiers sont copiés directement dans fixtures/ ; /app/fixtures désigne uniquement Docker.
2. Rends les copies modifiables avec chmod u+w.
3. Vérifie README.txt, message.txt et settings.ini avec ls fixtures.
4. Ajoute explicitement ces trois fichiers et commite les copies.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
pwd
```

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs. ../../fixtures est la source sur le Mac ; les copies sont placées dans ton dépôt d’exercice.

```bash
mkdir -p fixtures && cp ../../fixtures/integrity/* fixtures/ && chmod u+w fixtures/*
```

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
ls -l fixtures
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add fixtures
git commit -m "Ajoute les fixtures fictives FileGuard"
```

**Tu sais que c’est bon quand :** ls fixtures affiche README.txt, message.txt et settings.ini ; git log --oneline montre le commit.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Une fixture est un exemple fictif copié dans ton dépôt ; sur le Mac son origine est ../../fixtures.

</details>

<details>
<summary>Indice 2</summary>

Depuis workspaces/fileguard, copie les trois fichiers de ../../fixtures/integrity dans fixtures/ et vérifie leurs noms sans utiliser le chemin Docker /app.

</details>

<details>
<summary>Indice 3</summary>

../../fixtures/integrity remonte de fileguard à workspaces puis à cyberatelier ; ls fixtures doit montrer README.txt, message.txt et settings.ini.

</details>

#### Palier 3 — Un JSON stable : la forme avant le code (10 min)

Savoir écrire exactement le format du contrat, avec un ordre de clés et une fin de ligne stables.

**Où tu travailles :** Mac · workspaces/fileguard · Forme de manifest.json

**Pour comprendre**

- Le manifeste conserve les noms et empreintes à un moment donné. JSON enregistre cette structure dans manifest.json.
- Un nom simple est message.txt, sans dossier ni chemin absolu. L’ordre fait partie du format demandé.

**Exemple de résultat attendu**

Ce que tu donnes :

```text
Un dossier vide.
```

Ce que tu dois obtenir :

```text
{"schema": 1, "files": []}
```

files reste une liste même quand elle est vide.

**Règles à respecter**

- Objet racine : schema vaut 1, puis files contient une liste.
- Chaque entrée a exactement name puis sha256 : nom simple et empreinte de 64 caractères hexadécimaux minuscules.
- Entrées triées par name ; indentation stable, UTF-8, saut de ligne final.
- Pas de chemin absolu ni de donnée secrète ; manifest.json ne contient jamais sa propre empreinte.

**Actions dans l’ordre**

1. Écris à la main un manifeste fictif dans un fichier d’essai, sans encore coder la génération.
2. Compare sa structure aux règles : objet racine, liste files, objets par fichier.
3. Explique pourquoi sort_keys=True changerait l’ordre schema puis files.
4. Retire le fichier d’essai ; un manifeste généré ne sera pas commité.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 -c "import json; print(json.dumps({'b': 1, 'a': 2}, indent=2))"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -c "import json; print(json.dumps({'schema': 1, 'files': []}, indent=2))"
```

**Tu sais que c’est bon quand :** Tu sais dire pourquoi sort_keys=True n’est pas adapté ici : il réordonnerait schema et files, alors que le contrat impose schema puis files.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Un JSON stable impose un ordre, une indentation et une forme de données, pas seulement un texte lisible.

</details>

<details>
<summary>Indice 2</summary>

Dessine schema puis files et les deux clés de chaque entrée ; distingue la liste ordonnée des fichiers de l’objet JSON qui les contient.

</details>

<details>
<summary>Indice 3</summary>

{'schema': 1, 'files': []} représente un inventaire vide ; écrire un chemin absolu au lieu d’un simple name violerait la forme prévue.

</details>

#### Palier 4 — F4 : dossier vide, premier niveau seulement (14 min)

Lister les fichiers réguliers du premier niveau avec pathlib, sans entrer dans les sous-dossiers.

**Où tu travailles :** Mac · workspaces/fileguard · fileguard.py ; verification.py

**Pour comprendre**

- Le premier niveau désigne les fichiers directement dans le dossier donné ; les sous-dossiers ne sont pas parcourus.
- Un dossier vide reste admis et donne une liste vide.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**F4 — Dossier vide**
- Entrée : Dossier temporaire vide
- Résultat attendu : Manifeste valide avec une liste vide.

**Actions dans l’ordre**

1. Ajoute F4 : un dossier temporaire vide donne schema 1 et files vide.
2. Lance et repère la fonction manquante. Choisis son nom et conserve-le dans les tests.
3. Écris la génération minimale pour ce cas, au format du palier précédent.
4. Relance F1 à F4 puis commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

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

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Un dossier vide donne un inventaire vide ; premier niveau signifie qu’on ne descend pas dans les sous-dossiers.

</details>

<details>
<summary>Indice 2</summary>

Écris F4 avec un dossier temporaire neuf et vérifie la structure entière du manifeste, pas seulement son existence.

</details>

<details>
<summary>Indice 3</summary>

Un dossier qui ne contient qu’un sous-dossier sans fichier régulier au premier niveau garde files=[] dans ce périmètre non récursif.

</details>

#### Palier 5 — F5 : trier les noms et écrire le fichier (15 min)

Obtenir le même fichier quel que soit l’ordre de création des fichiers.

**Où tu travailles :** Mac · workspaces/fileguard · fileguard.py ; verification.py

**Pour comprendre**

- Le système ne garantit pas l’ordre de lecture des fichiers. sorted sur les noms rend la liste stable.
- Déterministe signifie ici : mêmes données → même contenu du manifeste.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**F5 — Ordre déterministe**
- Entrée : Fichiers créés dans un ordre non trié
- Résultat attendu : Entrées JSON triées par nom.

**Actions dans l’ordre**

1. Ajoute F5 : crée plusieurs fichiers temporaires dans un ordre non alphabétique ; vérifie les entrées triées par name.
2. Complète l’inventaire des fichiers réguliers du premier niveau, réutilise calculer_sha256 et écris manifest.json en UTF-8 avec un saut de ligne final.
3. Compare deux générations sur les mêmes données.
4. Choisis si creer crée seulement ou remplace un manifeste existant ; note ce choix pour le README.
5. Relance F1 à F5 puis commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

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

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Le tri se fait par nom avant l’écriture ; deux parcours du même dossier doivent produire les mêmes octets.

</details>

<details>
<summary>Indice 2</summary>

Écris F5 avec les trois noms fournis dans un ordre de création différent, puis vérifie l’ordre final et le saut de ligne demandé.

</details>

<details>
<summary>Indice 3</summary>

Créer z.txt avant a.txt ne doit pas donner un manifeste commençant par z.txt si le contrat impose un tri par nom.

</details>

#### Palier 6 — F6 : le manifeste ne se compte pas lui-même (12 min)

Exclure le manifeste de son propre inventaire, même quand il se trouve dans le dossier examiné.

**Où tu travailles :** Mac · workspaces/fileguard · fileguard.py ; verification.py

**Pour comprendre**

- Le manifeste est une sortie de l’inventaire. Se compter lui-même ferait changer son contenu à chaque génération.
- L’exclusion se fait sur le nom simple manifest.json.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**F6 — Exclusion du manifeste**
- Entrée : Manifeste écrit au même endroit que les données
- Résultat attendu : Le manifeste ne figure pas dans ses propres entrées.

**Actions dans l’ordre**

1. Ajoute F6 : place manifest.json dans le dossier temporaire des données, puis relance l’inventaire.
2. Vérifie qu’aucune entrée files ne porte ce nom.
3. Ajoute l’exclusion sans retirer les autres fichiers réguliers.
4. Relance F1 à F6 puis commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

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

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Un manifeste écrit dans le dossier observé ne doit pas calculer sa propre empreinte.

</details>

<details>
<summary>Indice 2</summary>

Écris F6 après avoir créé manifest.json parmi les données ; vérifie son absence dans files et sa stabilité au second passage.

</details>

<details>
<summary>Indice 3</summary>

Si un catalogue inclut son propre fichier catalogue.json, réécrire celui-ci modifie sa propre empreinte et crée un changement artificiel.

</details>

#### Palier 7 — F7 : refuser les liens symboliques (12 min)

Refuser clairement un lien symbolique, et tester ce refus quand le système permet d’en créer.

**Où tu travailles :** Mac · workspaces/fileguard · fileguard.py ; verification.py

**Pour comprendre**

- Un lien symbolique pointe vers un autre chemin : le suivre pourrait sortir du dossier prévu. Le contrat le refuse.
- skipTest indique avec une raison que le système ne permet pas de créer ce lien.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**F7 — Lien symbolique**
- Entrée : Lien symbolique vers un fichier temporaire, si supporté
- Résultat attendu : Refus clair selon le contrat.

**Actions dans l’ordre**

1. Ajoute F7 : crée un fichier temporaire et un lien vers lui dans le dossier à examiner.
2. Si la création du lien n’est pas supportée, utilise skipTest avec une explication.
3. Sinon, attends une exception explicite indiquant le refus du lien. Choisis son type et note-le pour le README.
4. Détecte le lien avant de lire sa cible, relance F1 à F7 puis commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

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

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Un lien symbolique pointe vers une autre entrée ; le refuser évite de suivre un contenu hors périmètre.

</details>

<details>
<summary>Indice 2</summary>

Crée un lien dans le test temporaire et vérifie le refus explicite avant le calcul de son empreinte.

</details>

<details>
<summary>Indice 3</summary>

Path('raccourci').is_symlink() permet de distinguer un lien d’un fichier régulier ; suivre sa cible silencieusement changerait le périmètre.

</details>

#### Palier 8 — Livre la MR2 (8 min)

Relire le diff, pousser feat/manifest, ouvrir la MR et ne pas livrer de fichiers générés.

**Où tu travailles :** Mac · workspaces/fileguard · MR GitLab

**Pour comprendre**

- git diff montre les lignes modifiées ; git diff --staged montre celles choisies pour le prochain commit. Le diff de la MR compare toute ta branche à main.
- La demande de fusion (MR dans GitLab, PR dans GitHub) permet de relire le travail avant de l’intégrer à main.

**Actions dans l’ordre**

1. Lance la suite complète avec la commande indiquée au début de la mission.
2. Écarte manifest.json produit par tes essais. Vérifie les trois fixtures d’origine dans la MR.
3. Relis git status et git diff : la livraison doit contenir fileguard.py, verification.py et fixtures/, avec les modifications nécessaires de cette mission.
4. Ajoute les fichiers par leur nom, relis git diff --staged, puis commite ce qui ne l’est pas encore.
5. Pousse feat/manifest et ouvre la demande de fusion vers main.
6. Dans GitLab, ouvre le pipeline du dernier commit : vérifie qu’il a réellement exécuté les tests et qu’il est vert. Un test local réussi ne le remplace pas.
7. Relis le diff et fusionne lorsque le pipeline et les règles de l’école le permettent.
8. Après la fusion, reviens sur main et lance git pull --ff-only avant la mission suivante.

**Terminal · Relire l’état du dépôt**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

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

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

MR2 livre le manifeste et ses tests sans transformer la démonstration en dépendance du runner.

</details>

<details>
<summary>Indice 2</summary>

Relance F1 à F7 avec leurs dossiers temporaires, relis les fixtures copiées et vérifie le pipeline du dernier commit.

</details>

<details>
<summary>Indice 3</summary>

Un runner peut passer F4 sur un dossier vide temporaire même sans fixtures/integrity ; ce test ne doit pas chercher ton dossier local.

</details>

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

**Où tu travailles :** Mac · workspaces/fileguard · Dépôt

**Pour comprendre**

- La branche principale (main) contient le travail déjà fusionné. Ta branche feat/... reçoit les changements de cette mission.
- Un dépôt « propre » n’a aucune modification en attente : git status te le confirme.

**Actions dans l’ordre**

1. Ouvre workspaces/fileguard dans VS Code. Dans le terminal du Mac, place-toi dans ce même dossier et active son venv avec source .venv/bin/activate.
2. Vérifie que MR2 est fusionnée et que F1 à F7 passent sur main.
3. Lis git status ; enregistre ton travail en cours avant de changer de branche.
4. Reviens sur main avec git switch main, mets-la à jour avec git pull --ff-only, puis crée feat/comparaison. Remplace main par master si ton dépôt utilise ce nom.
5. Vérifie le nom de ta branche avec git status. Si elle existe déjà, reprends-la avec git switch sans -c.

**Terminal · Après la fusion : actualiser la principale**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

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

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

La comparaison s’ajoute au manifeste fusionné ; feat/comparaison doit partir de main à jour.

</details>

<details>
<summary>Indice 2</summary>

Vérifie F1 à F7 avant la nouvelle branche et retrouve la forme schema/files utilisée en MR2.

</details>

<details>
<summary>Indice 3</summary>

Une comparaison qui lit un autre format de manifeste ne teste pas la continuité du projet ; garde le même contrat de fichier.

</details>

#### Palier 2 — Comparer des ensembles de noms (8 min)

Séparer présence et absence des noms, puis comparer les empreintes nom par nom.

**Où tu travailles :** Mac · workspaces/fileguard · Contrat de comparer

**Pour comprendre**

- Le manifeste est la référence de départ ; l’inventaire décrit les fichiers actuels.
- L’intersection contient les noms des deux côtés ; la différence contient les noms d’un seul côté.

**Règles à respecter**

- comparer(manifeste, inventaire) retourne inchange, modifie, supprime et ajoute : listes triées de noms.
- Deux côtés, même empreinte → inchange.
- Deux côtés, empreinte différente → modifie.
- Seulement dans le manifeste → supprime.
- Seulement dans l’inventaire → ajoute.
- manifest.json est exclu de toutes les catégories.

**Actions dans l’ordre**

1. Observe l’exemple d’ensembles sans coder comparer pour l’instant.
2. Classe sur papier des noms présents seulement avant, seulement maintenant et des deux côtés.
3. Pour un nom des deux côtés, compare ensuite les empreintes.
4. Vérifie que tu sais distinguer les quatre catégories et leur tri.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 -c "a = {'pomme', 'poire'}; b = {'poire', 'kiwi'}; print(a - b, b - a, a & b)"
```

**Tu sais que c’est bon quand :** Tu sais dire, pour un nom, s’il est absent d’un côté, ou présent des deux côtés avec des empreintes différentes.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Les ensembles permettent de distinguer noms communs, nouveaux et absents ; les empreintes servent ensuite aux noms communs.

</details>

<details>
<summary>Indice 2</summary>

Dessine deux colonnes, référence et dossier actuel, puis classe les noms avant de comparer leur contenu.

</details>

<details>
<summary>Indice 3</summary>

Référence {a,b} et actuel {b,c} donnent a absent, c nouveau et b commun ; seule l’empreinte de b décidera s’il est modifié.

</details>

#### Palier 3 — F8 : aucun changement (10 min)

Écrire le premier cas de comparaison : tout est inchangé.

**Où tu travailles :** Mac · workspaces/fileguard · fileguard.py ; verification.py

**Pour comprendre**

- Sans différence, les fichiers restent dans le résultat, rangés dans inchange.
- Les quatre clés sont présentes même quand trois listes sont vides.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**F8 — Aucun changement**
- Entrée : Le dossier correspond exactement au manifeste
- Résultat attendu : Tous les fichiers dans inchangé.

**Actions dans l’ordre**

1. Ajoute F8 : dossier temporaire correspondant exactement au manifeste.
2. Vérifie tous les noms dans inchange et trois autres listes vides.
3. Crée comparer(manifeste, inventaire) avec les catégories et le tri prévus.
4. Relance F1 à F8 puis commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add fileguard.py verification.py
git commit -m "Compare un dossier identique à son manifeste"
```

**Tu sais que c’est bon quand :** F1 à F8 passent ; git log --oneline montre le commit.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Un fichier commun avec la même empreinte est inchangé ; le résultat doit contenir les autres catégories aussi.

</details>

<details>
<summary>Indice 2</summary>

Écris F8 sans modifier le dossier entre création et vérification, puis vérifie les quatre catégories et leurs listes attendues.

</details>

<details>
<summary>Indice 3</summary>

Une référence note.txt avec empreinte X et un fichier actuel note.txt avec empreinte X donnent un inchangé et aucune autre catégorie.

</details>

#### Palier 4 — F9 et F10 : modifié et supprimé (10 min)

Distinguer un fichier dont le contenu a changé d’un fichier qui a disparu.

**Où tu travailles :** Mac · workspaces/fileguard · fileguard.py ; verification.py

**Pour comprendre**

- Même nom et nouveaux octets : fichier modifié. Nom disparu de l’inventaire actuel : fichier supprimé.
- La comparaison prend le manifeste comme référence.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**F9 — Fichier modifié**
- Entrée : Même nom, contenu dont l’empreinte diffère
- Résultat attendu : Nom dans modifié.

**F10 — Fichier supprimé**
- Entrée : Nom du manifeste absent du dossier
- Résultat attendu : Nom dans supprimé.

**Actions dans l’ordre**

1. Ajoute F9 : crée le manifeste puis change le contenu du fichier ; attends son nom dans modifie.
2. Ajoute F10 : crée le manifeste puis retire le fichier temporaire ; attends son nom dans supprime.
3. Complète comparer sans confondre les situations ni placer un nom dans deux catégories.
4. Relance F1 à F10 puis commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add fileguard.py verification.py
git commit -m "Classe les fichiers modifiés et supprimés"
```

**Tu sais que c’est bon quand :** F1 à F10 passent.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Modifié signifie nom présent et empreinte différente ; supprimé signifie nom de référence absent du dossier courant.

</details>

<details>
<summary>Indice 2</summary>

Écris F9 et F10 dans deux scénarios temporaires séparés pour observer chaque cause sans mélange.

</details>

<details>
<summary>Indice 3</summary>

note.txt passé d’empreinte X à Y est modifié ; note.txt introuvable est supprimé, même si un autre fichier contient les anciens octets.

</details>

#### Palier 5 — F11 et F12 : ajouté, puis plusieurs catégories (10 min)

Gérer les nouveaux fichiers, puis vérifier que les quatre catégories restent exactes quand elles coexistent.

**Où tu travailles :** Mac · workspaces/fileguard · fileguard.py ; verification.py

**Pour comprendre**

- Un fichier actuel absent du manifeste est ajouté.
- Le cas mixte vérifie que les catégories fonctionnent ensemble et restent exclusives.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**F11 — Fichier ajouté**
- Entrée : Nouveau fichier régulier au premier niveau
- Résultat attendu : Nom dans ajouté.

**F12 — Plusieurs catégories**
- Entrée : Dossier avec cas inchangé, modifié, supprimé et ajouté
- Résultat attendu : Chaque nom dans sa catégorie exacte.

**Actions dans l’ordre**

1. Ajoute F11 : nouveau fichier régulier au premier niveau, nom dans ajoute.
2. Ajoute F12 : un fichier par catégorie, inchangé, modifié, supprimé et ajouté.
3. Compare les listes exactes triées, avec chaque nom seulement dans sa catégorie.
4. Complète le code, relance F1 à F12 puis commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add fileguard.py verification.py
git commit -m "Classe les fichiers ajoutés et les cas mêlés"
```

**Tu sais que c’est bon quand :** F1 à F12 passent.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Un fichier nouveau est ajouté même si son contenu ressemble à un autre ; plusieurs catégories peuvent coexister.

</details>

<details>
<summary>Indice 2</summary>

Écris F11 puis le scénario mixte F12 ; compare chaque liste au lieu de vérifier seulement le nombre total.

</details>

<details>
<summary>Indice 3</summary>

Référence a/b et actuel a changé/c donnent a modifié, b supprimé, c ajouté ; aucun nom ne doit apparaître dans deux catégories incompatibles.

</details>

#### Palier 6 — F13 et F14 : manifeste vide et manifeste exclu (8 min)

Vérifier les cas limites : un manifeste sans entrée, et un manifeste conservé à côté des données.

**Où tu travailles :** Mac · workspaces/fileguard · fileguard.py ; verification.py

**Pour comprendre**

- Sans entrée dans le manifeste, tous les fichiers actuels sont nouveaux.
- manifest.json reste exclu même s’il est conservé avec les données.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**F13 — Manifeste vide**
- Entrée : Manifeste avec zéro entrée et dossier contenant des données
- Résultat attendu : Les fichiers sont ajoutés.

**F14 — Manifeste exclu**
- Entrée : Manifeste conservé à proximité des données
- Résultat attendu : Il n’est jamais signalé comme ajouté ou modifié.

**Actions dans l’ordre**

1. Ajoute F13 : manifeste vide, dossier temporaire contenant des fichiers ; tous dans ajoute.
2. Ajoute F14 avec manifest.json à proximité : il n’est ni ajouté ni modifié.
3. Complète ces limites sans retirer l’exclusion de l’inventaire.
4. Relance F1 à F14 puis commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add fileguard.py verification.py
git commit -m "Gère le manifeste vide et le manifeste exclu"
```

**Tu sais que c’est bon quand :** F1 à F14 passent : les quatorze tests sont verts.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Le manifeste vide reste un point de comparaison valide ; son propre fichier demeure exclu.

</details>

<details>
<summary>Indice 2</summary>

Écris F13 avec files=[] et F14 avec manifest.json présent, puis vérifie que seuls les vrais fichiers de données deviennent ajoutés.

</details>

<details>
<summary>Indice 3</summary>

Un dossier avec seulement manifest.json et une référence vide doit rester sans fichier ajouté ; le manifeste n’est pas une donnée surveillée.

</details>

#### Palier 7 — Commandes simples et affichage par catégorie (8 min)

Relier la création et la vérification à une ligne de commande, sans parcourir le disque.

**Où tu travailles :** Mac · workspaces/fileguard · fileguard.py

**Pour comprendre**

- creer enregistre la référence ; verifier compare l’état actuel à cette référence.
- Un message clair et un code non nul signalent une entrée inutilisable.

**Actions dans l’ordre**

1. Ajoute creer DOSSIER et verifier DOSSIER ; aucun dossier n’est cherché ailleurs automatiquement.
2. creer écrit manifest.json selon ton choix création/remplacement. verifier affiche les quatre catégories, un nom par ligne.
3. Essaie un argument manquant et un dossier inexistant : message clair, code non nul.
4. Relance les tests et commite la CLI.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

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

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Une commande de création et une commande de vérification ont deux effets différents ; l’affichage reprend les catégories calculées.

</details>

<details>
<summary>Indice 2</summary>

Relie les fonctions déjà testées aux commandes simples prévues et garde l’affichage distinct de la logique de comparaison.

</details>

<details>
<summary>Indice 3</summary>

Créer un inventaire enregistre une référence ; vérifier ensuite ne doit pas réécrire cette référence, sinon un changement serait effacé avant comparaison.

</details>

#### Palier 8 — Rédige le README (9 min)

Expliquer le programme et ses limites à quelqu’un qui ne l’a pas écrit.

**Où tu travailles :** Mac · workspaces/fileguard · README.md

**Pour comprendre**

- Le README documente tes décisions : remplacement du manifeste et exception pour les liens.
- Une référence modifiable avec les données ne certifie pas leur origine.

**Actions dans l’ordre**

1. Documente structure du dossier, format schema/files/name/sha256, commandes et catégories.
2. Précise premier niveau seulement, refus des liens et type d’exception choisi.
3. Indique si creer crée ou remplace manifest.json.
4. Explique le besoin d’une référence de confiance et la limite : FileGuard n’est pas un antivirus.
5. Suis les commandes du README puis commite.

**Terminal · Enregistrer le travail vérifié**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
git add README.md
git commit -m "Documente FileGuard dans le README"
```

**Tu sais que c’est bon quand :** Un lecteur qui ne connaît pas le projet sait lancer les commandes, lire le résultat et voir les limites.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Le README précise la confiance dans le manifeste et les limites du premier niveau.

</details>

<details>
<summary>Indice 2</summary>

Donne tes commandes de création/vérification, les quatre catégories et le refus des liens, avec les chemins Mac testés.

</details>

<details>
<summary>Indice 3</summary>

Une empreinte constate une différence par rapport à la référence ; si quelqu’un change à la fois fichier et référence, cette comparaison peut ne rien signaler.

</details>

#### Palier 9 — Démonstration des quatre catégories, puis livraison (12 min)

Montrer les quatre catégories sur un scénario, puis livrer la MR3 et fusionner le dernier commit vert.

**Où tu travailles :** Mac · workspaces/fileguard · Dossier temporaire ; MR GitLab

**Pour comprendre**

- git diff montre les lignes modifiées ; git diff --staged montre celles choisies pour le prochain commit. Le diff de la MR compare toute ta branche à main.
- La demande de fusion (MR dans GitLab, PR dans GitHub) permet de relire le travail avant de l’intégrer à main.

**Actions dans l’ordre**

1. Lance la suite complète avec la commande indiquée au début de la mission.
2. Fais la démo hors tests sur des copies hors du dépôt : crée le manifeste, modifie message.txt, supprime settings.ini, ajoute nouveau.txt. Vérifie ces trois catégories ainsi que README.txt dans inchange. Les changements de démo ne sont pas livrés.
3. Relis git status et git diff : la livraison doit contenir fileguard.py, verification.py et README.md, avec les modifications nécessaires de cette mission.
4. Ajoute les fichiers par leur nom, relis git diff --staged, puis commite ce qui ne l’est pas encore.
5. Pousse feat/comparaison et ouvre la demande de fusion vers main.
6. Dans GitLab, ouvre le pipeline du dernier commit : vérifie qu’il a réellement exécuté les tests et qu’il est vert. Un test local réussi ne le remplace pas.
7. Relis le diff et fusionne lorsque le pipeline et les règles de l’école le permettent.
8. Après la fusion, reviens sur main et lance git pull --ff-only avant la mission suivante.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/fileguard, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

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

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

La démonstration doit observer les quatre catégories avec des modifications explicites puis livrer une suite autonome.

</details>

<details>
<summary>Indice 2</summary>

Garde un fichier, modifie-en un, supprime-en un et ajoute-en un après la référence ; observe les catégories avant les tests et la MR.

</details>

<details>
<summary>Indice 3</summary>

Avec a inchangé, b modifié, c retiré et d créé, un bilan correct place chacun dans sa catégorie ; réécrire la référence trop tôt ferait disparaître ces différences.

</details>

**Avant de livrer**

- Les quatre catégories ont des tests reproductibles et le manifeste lui-même est ignoré.
- Le programme reste limité au dossier choisi, au premier niveau, sans suivre de symlinks.
- Le README indique que le manifeste doit être digne de confiance et que le projet n’est pas un antivirus.

<!-- END GENERATED EXERCISES -->

## Méthode GitLab

Le dossier FileGuard est vide au départ. Clone le dépôt de l’école directement dans le dossier courant avec git clone <URL_DU_DEPOT> . avant de créer les fichiers. Le point signifie « ici ». Fais le clone dans le terminal du Mac, depuis workspaces/fileguard, uniquement si le dépôt n’existe pas encore. Le terminal conserve son cd et son activation de venv ; reste dans le dépôt du parcours pour Git et les tests.

Utilise un dépôt autorisé par l’école, un runner actif sur les MR des branches non protégées et les droits convenus pour les règles de fusion. Pour chaque MR, crée la branche depuis la principale actualisée, exécute la même commande de tests localement et en CI, lis le diff, puis ouvre la MR. Fusionne uniquement le dernier commit vert. Après chaque fusion, actualise la principale avant l’étape suivante.

La CI ne dépend pas d’un dossier de données du portail. Les tests créent leurs propres fichiers temporaires. Les fixtures d’exemple peuvent être copiées par l’apprenant dans son dépôt, mais elles ne remplacent pas les tests temporaires et ne sont pas supposées présentes sur le runner d’école.

## Repères de temps

Préparation GitLab et lecture : 30 min. MR1 empreintes et tests : 85 min. MR2 manifeste et tests : 85 min. MR3 comparaison, affichage et README : 80 min. Relecture et marge : 20 min. Total : 300 min.

## Livrables et limites

Livre fileguard.py, verification.py, un README, les fixtures fictives copiées dans le dépôt, une CI qui exécute les tests temporaires et trois MR successives. Montre un scénario où les quatre catégories sont distinguées, et explique clairement que le manifeste de référence doit lui-même être digne de confiance.

FileGuard est un outil pédagogique d’intégrité, pas un antivirus ni une garantie d’authenticité. SHA-256 permet de constater une différence avec un manifeste de confiance ; une personne capable de modifier les fichiers peut aussi modifier un manifeste conservé à côté. Il ne parcourt pas récursivement, ne suit pas les liens et ne cherche pas de secrets.
