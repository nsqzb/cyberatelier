# Socle Python & Git — bases, tests et premier travail en équipe

**Durée : 5 heures · Niveau débutant · 3 merge requests**

Ce parcours est le point d’entrée de Cyber Atelier. Tu connais déjà les variables, les listes et les fonctions. Ici, tu vas écrire de petites fonctions pures, les tester avec unittest, lire un journal de connexions fictif, puis livrer le tout avec Git comme le ferait une équipe. Les données sont entièrement fictives : aucune cible réseau, aucun outil offensif. Le but est d’arriver à PortPilot, HeaderScope et FileGuard avec les réflexes en place.

Les exercices ne donnent aucune solution. Tu trouveras des contrats précis (entrées, sorties, erreurs, cas limites), des tests décrits en prose et des indices progressifs. Pratique chaque commande Git sur ton propre dépôt : le guide ne remplace pas le cours.

## Contrat du programme

Le programme final tient en trois fichiers Python et un README :

- `outils.py` : fonctions pures de validation et de comptage (MR1) ;
- `journal.py` : lecture de fichier, erreurs, JSON et rapport de données (MR2) ;
- `analyseur.py` : affichage du rapport et point d’entrée en ligne de commande (MR3).

Chaque fichier a son fichier de tests : `test_outils.py`, `test_journal.py`, `test_analyseur.py`. Tous utilisent unittest, lancé avec `python3 -m unittest` depuis le dossier du projet. Aucun `pip install`, aucun pytest.

Le journal fictif est `fixtures/socle/auth.log`. Tu le copies depuis le terminal du Mac dans workspaces/socle avec la commande de préparation ; les originaux sont en lecture seule, la copie est modifiable. Il n’est jamais versionné : ton `.gitignore` l’exclut.

Le format d’une ligne de journal est :

`AAAA-MM-JJ HH:MM:SS EVENEMENT utilisateur ip`

Par exemple : `2026-01-05 08:12:44 LOGIN_OK alice 192.0.2.10`. Les événements acceptés sont `LOGIN_OK` et `LOGIN_FAIL`. Une ligne qui ne respecte pas ce format est « malformée » : elle est comptée, pas une raison de planter.

<!-- BEGIN GENERATED EXERCISES -->
## Comment travailler un exercice

Ces exercices sont ton entraînement. Chaque palier explique les notions utiles, montre les données ou les règles attendues, puis te fait écrire et vérifier ton propre code. Les durées sont des repères : avance quand tu comprends le résultat.

1. Lis « Pour comprendre » et l’exemple lorsqu’il y en a un. Repère ce qui entre dans le programme, ce qui doit en sortir et les règles à respecter.
2. Les cartes de tests donnent l’entrée et le résultat attendu. Écris les tests correspondants dans le fichier indiqué ; cocher un palier ne les exécute pas. Avec unittest, « Ran 0 tests » signifie qu’aucun test n’a été exécuté : ce n’est pas une validation. Un cas décrit peut contenir plusieurs valeurs ; le nombre de méthodes Python n’est donc pas forcément le nombre d’identifiants.
3. Suis les actions numérotées, une à la fois. Les exemples servent à apprendre une notion ; tu écris toi-même la solution de l’exercice. Les blocs Terminal donnent les commandes à lancer au moment indiqué.
4. Vérifie le résultat indiqué avant de poursuivre. Un échec attendu (phase rouge, argument refusé ou conflit volontaire) est expliqué dans le palier.
5. Si tu bloques, lis la dernière ligne de l’erreur, compare entrée et attendu, puis demande un seul indice à la fois avec python3 atelier.py indice depuis cyberatelier. Les trois niveaux vont du rappel à un petit exemple ; ils ne donnent pas une fonction corrigée.

### Le bon endroit pour chaque action

Ouvre `workspaces/socle` dans VS Code et un terminal du Mac dans ce même dossier. Tu écris et testes le code ici, dans le dépôt Git de l’exercice. Ouvre un second terminal dans `cyberatelier` pour lire les consignes avec `python3 atelier.py voir` et piloter Docker. Le site reste disponible pour la lecture ; l’onglet Coder est facultatif.

Depuis `cyberatelier`, `mkdir -p workspaces/socle` puis `cd workspaces/socle` permet de rejoindre le dossier du parcours. S’il contient déjà ton exercice, garde ses fichiers, sa branche et son dépôt : ne le reclone pas. La préparation ci-dessous se fait une fois ; la mission crée ensuite sa branche.

Le code Python se place dans VS Code et doit être enregistré avant les tests. Les commandes `docker compose ...` et `python3 atelier.py ...` se lancent depuis `cyberatelier`. Leurs appels Docker entrent dans le conteneur ; `/app/fixtures`, `/app/tools` et `/workspaces` sont des chemins internes à celui-ci. Depuis le dépôt d’exercice sur le Mac, les fixtures fournies sont dans `../../fixtures`.

Le terminal du Mac conserve son `cd` et son activation de venv. Active `.venv` dans chaque nouveau terminal d’exercice ; `python3` utilise alors ce venv, ou appelle `.venv/bin/python` explicitement. Lis `echo $?` immédiatement après le programme dont tu veux le code, avant toute autre commande. Ajoute `.venv/` à `.gitignore` avant `git add`.

PortPilot et HeaderScope exécutés sur le Mac : lance `python3 labs.py` depuis `cyberatelier` dans un autre terminal et garde-le ouvert ; Ctrl+C arrête ce labo Mac. Les outils ToolWrap et les démos ReconWrap tournent dans Docker : `python3 atelier.py labo demarrer`, `labo arreter` et `labo statut` depuis `cyberatelier` pilotent uniquement le labo Docker. Le même numéro 8000 ne relie pas automatiquement les deux environnements.

Un venv créé sur le Mac ne fonctionne pas dans Docker : les démos dans le conteneur utilisent son `python3`. Le dossier hôte `workspaces` doit être monté dans Docker pour que les démos ReconWrap lisent ton code ; conserve le `compose.override.yaml` du mode VS Code. Remplace `main` par `master` si nécessaire. Si une branche existe, reprends-la avec `git switch NOM` sans `-c`. Après chaque fusion, actualise la principale dans le dépôt du parcours avant la mission suivante.

### Préparation sur le Mac

**Vérifier Python**

Terminal du Mac, dans cyberatelier/workspaces/socle.

```bash
python3 --version
```

Python 3 doit être installé sur ton Mac. Ce parcours utilise seulement sa bibliothèque standard ; aucun pip install n’est demandé.

**Vérifier Git**

Terminal du Mac, dans cyberatelier/workspaces/socle.

```bash
git --version
```

Vérifie Git sur ton Mac. Les commandes du parcours agissent sur ce dépôt d’exercice, distinct du dépôt cyberatelier.

**Configurer ton identité Git (une seule fois)**

Terminal du Mac, dans cyberatelier/workspaces/socle.

```bash
git config --global user.name "Prénom Nom" && git config --global user.email "adresse@ecole.example"
```

Remplace les deux valeurs d’exemple par ton nom et l’adresse de ton compte scolaire. Cette configuration globale est enregistrée sur ton Mac ; sans identité, git commit refuse le commit.

**Cloner le dépôt**

Terminal du Mac, dans cyberatelier/workspaces/socle.

```bash
git clone <URL_DU_DEPOT> .
```

Depuis le terminal du Mac dans workspaces/socle, clone seulement si le dossier est vide et n’a pas encore de dépôt. Remplace <URL_DU_DEPOT> par l’URL autorisée réelle avant exécution ; le point signifie « ici ». Si ton exercice existe déjà, garde-le et passe directement à git status. HTTPS ou SSH peut demander une saisie dans ce terminal.

**Créer le venv**

Terminal du Mac, dans cyberatelier/workspaces/socle.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Après le clone, crée ce venv sur le Mac une seule fois ; s’il existe, active-le simplement. L’activation reste valable dans ce terminal. Dans un nouveau terminal, réactive-le ou appelle .venv/bin/python. Ajoute .venv/ à .gitignore avant git add. Aucun paquet pip n’est nécessaire.

**Vérifier le dépôt cloné**

Terminal du Mac, dans cyberatelier/workspaces/socle.

```bash
git status
```

Vérifie que tu es sur la branche principale (main ou master) et que le dépôt est propre.

**Copier les fixtures du parcours**

Terminal du Mac, dans cyberatelier/workspaces/socle.

```bash
mkdir -p fixtures/socle && cp -r ../../fixtures/socle/. fixtures/socle/ && chmod -R u+w fixtures/socle
```

Copie le journal fictif auth.log dans ton dossier de travail. Les originaux sont en lecture seule ; la copie est modifiable. Ne l’ajoute pas à Git : le .gitignore de MR1 l’exclut. La source est dans le dépôt cyberatelier sur ton Mac ; /app/fixtures est réservée au conteneur.

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

### MR1 — feat/bases (100 min)

Tu vas écrire quatre fonctions pures de validation, d’analyse de ligne et de comptage. Tu construis leurs tests au fil des paliers, puis tu livres le tout dans ta première demande de fusion.

**Avant de commencer**

- Point de départ : Un dépôt cloné, Python 3 et Git disponibles. Aucun fichier Python de cet exercice n’est fourni.
- Ce que tu vas produire : outils.py et test_outils.py : valider un nom, analyser une ligne, compter les événements et les échecs.
- Pourquoi : Ces fonctions seront réutilisées pour lire le journal en MR2.
- Commande des tests depuis la racine : `python3 -m unittest -v`. Les cas ci-dessous sont à écrire par toi.

#### Palier 1 — Prépare ton dépôt et ta branche (10 min)

Avoir un dossier propre, relié à GitHub, sur la branche de la mission.

**Où tu travailles :** Mac · workspaces/socle · Dépôt et .gitignore

**Pour comprendre**

- La branche principale (main) contient le travail déjà fusionné. Ta branche feat/... reçoit les changements de cette mission.
- Un dépôt « propre » n’a aucune modification en attente : git status te le confirme.

**Actions dans l’ordre**

1. Ouvre workspaces/socle dans VS Code. Dans le terminal du Mac, place-toi dans ce même dossier et active son venv avec source .venv/bin/activate.
2. Termine la préparation décrite au début du guide : le dépôt doit déjà être cloné.
3. Lis git status ; enregistre ton travail en cours avant de changer de branche.
4. Reviens sur main avec git switch main, mets-la à jour avec git pull --ff-only, puis crée feat/bases. Remplace main par master si ton dépôt utilise ce nom.
5. Crée .gitignore avec __pycache__/, .venv/ et fixtures/, un motif par ligne. Commite ce fichier ; git status doit ensuite être propre.
6. Vérifie le nom de ta branche avec git status. Si elle existe déjà, reprends-la avec git switch sans -c.

**Terminal · Relire l’état du dépôt**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
git status
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git switch -c feat/bases
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add .gitignore
git commit -m "Prépare les exclusions du parcours"
```

**Terminal · Relire l’état du dépôt**

```bash
git status
```

**Tu sais que c’est bon quand :** git status affiche « On branch feat/bases » et « nothing to commit, working tree clean ».

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Une branche Git conserve une version du dépôt ; le dossier courant décide quel dépôt reçoit tes commandes.

</details>

<details>
<summary>Indice 2</summary>

Compare le chemin donné par pwd au dossier workspaces/socle, puis lis la branche dans git status avant de la créer.

</details>

<details>
<summary>Indice 3</summary>

Dans un dépôt d’essai, git switch -c feat/carnet crée la branche ; git switch feat/carnet reprend une branche déjà créée.

</details>

#### Palier 2 — Écris ton tout premier test (10 min)

Comprendre à quoi sert un test avant d’en écrire pour de vrai.

**Où tu travailles :** Mac · workspaces/socle · exemple.py (jetable)

**Pour comprendre**

- Un test appelle une fonction puis compare sa réponse à une valeur prévue. assertEqual compare deux valeurs ; un écart fait échouer le test.
- unittest.TestCase regroupe les vérifications. Chaque méthode dont le nom commence par test_ est découverte par unittest.

**Éditeur · Exemple Python à lire ou essayer**

VS Code sur le Mac : place ce code dans un fichier d’exemple jetable, puis lance ce fichier avec python3. Un extrait avec self se place dans une méthode de test.

```python
import unittest

def doubler(n):
    return n * 2

class TestDoubler(unittest.TestCase):
    def test_doubler_un_nombre(self):
        self.assertEqual(doubler(4), 8)

if __name__ == "__main__":
    unittest.main()
```

**Actions dans l’ordre**

1. Crée exemple.py, fichier jetable, et recopie l’exemple doubler ci-dessous.
2. Lance-le : 4 doublé doit donner 8, donc le test affiche OK.
3. Change uniquement l’attendu 8 en 9, relance et lis FAILED : le test détecte maintenant l’écart.
4. Remets 8, vérifie OK, puis supprime exemple.py sans le commiter.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 exemple.py -v
```

**Tu sais que c’est bon quand :** Tu as vu « OK » avec 8, puis « FAIL » avec 9, et tu sais lire la ligne « AssertionError: 8 != 9 ».

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Un test compare un résultat obtenu à un résultat attendu ; unittest découvre les méthodes dont le nom commence par test_.

</details>

<details>
<summary>Indice 2</summary>

Observe l’exemple doubler : repère l’appel, la valeur attendue et la classe TestCase avant de créer ton propre fichier d’essai.

</details>

<details>
<summary>Indice 3</summary>

Si tripler(3) retourne 9, assertEqual(tripler(3), 9) passe ; attendre 8 produit un échec qui montre les deux valeurs.

</details>

#### Palier 3 — Un test d’abord, puis la fonction : les noms valides (15 min)

Écrire un test AVANT le code (il échoue), puis le minimum de code pour le faire passer.

**Où tu travailles :** Mac · workspaces/socle · outils.py ; test_outils.py

**Pour comprendre**

- Une chaîne (str) est du texte ; True et False sont des booléens qui expriment « accepté » ou « refusé ».
- La fonction reçoit un nom et retourne sa décision. Ton test vérifie ce retour ; afficher le nom avec print ne suffit pas.

**Exemple de résultat attendu**

Ce que tu donnes :

```text
valider_nom_utilisateur("Alice_01")
```

Ce que tu dois obtenir :

```text
True
```

Les guillemets indiquent une chaîne. Le booléen True ne prend pas de guillemets.

**Règles à respecter**

- Le nom est du texte ; un autre type doit lever TypeError.
- Retire les espaces au début et à la fin avant de vérifier.
- Longueur admise après ce retrait : de 3 à 16 caractères inclus.
- Le premier caractère est une lettre ASCII : A à Z ou a à z.
- Les autres caractères sont des lettres ASCII, des chiffres, _ ou -.
- Retour : True pour un nom admis, False pour un texte refusé.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**S1 — Nom valide simple**
- Entrée : « alice », « Alice_01 », « a-b-c »
- Résultat attendu : True pour les trois.

**Actions dans l’ordre**

1. Crée test_outils.py avec une classe unittest qui importe valider_nom_utilisateur depuis outils.
2. Écris S1 : alice, Alice_01 et a-b-c doivent chacun donner True. Lance les tests et comprends l’erreur de fonction ou module absent.
3. Crée outils.py et valider_nom_utilisateur(nom). Fais passer S1 avec une logique qui accepte ces noms.
4. Relance la suite, puis commite outils.py et test_outils.py. Les autres règles seront testées aux deux paliers suivants.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add outils.py test_outils.py
git commit -m "Ajoute valider_nom_utilisateur pour les noms valides"
```

**Tu sais que c’est bon quand :** python3 -m unittest -v affiche 1 test OK, et git log --oneline montre ton nouveau commit.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

La phase rouge prouve que le test observe une fonction absente ou incorrecte ; le vert vient après son écriture.

</details>

<details>
<summary>Indice 2</summary>

Commence seulement par les noms valides de S1, puis vérifie que les noms ressortent inchangés.

</details>

<details>
<summary>Indice 3</summary>

Pour un validateur de couleur, une entrée « bleu » acceptée ressort « bleu » ; ne la remplace pas par une valeur constante pour satisfaire un seul exemple.

</details>

#### Palier 4 — Les limites : longueur et caractères (15 min)

Faire échouer un test, puis compléter la fonction règle par règle.

**Où tu travailles :** Mac · workspaces/socle · outils.py ; test_outils.py

**Pour comprendre**

- len(texte) donne le nombre de caractères. « Inclus » signifie que les deux bornes sont autorisées.
- ASCII désigne ici les lettres A–Z et a–z. isalpha() accepte aussi des lettres accentuées : ce seul contrôle ne respecte pas le contrat.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**S2 — Bornes de longueur**
- Entrée : « abc » (3 caractères), une chaîne valide de 16 caractères, « ab » (2), une chaîne valide de 17 caractères
- Résultat attendu : True pour 3 et 16 caractères, False pour 2 et 17.

**S3 — Premier caractère et caractères interdits**
- Entrée : « 1alice », « _alice », « ali ce », « ali.ce », « alicé », chaîne vide
- Résultat attendu : False pour les six cas.

**Actions dans l’ordre**

1. Ajoute S2 : des noms de 3 et 16 caractères sont acceptés ; des noms de 2 et 17 sont refusés.
2. Ajoute S3 : 1alice, _alice, ali ce, ali.ce, alicé et le texte vide sont refusés, chacun dans un cas distinct.
3. Lance les tests, puis complète les contrôles de longueur, du premier caractère et des caractères suivants.
4. Relance S1 à S3 et commite lorsque tout passe.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add outils.py test_outils.py
git commit -m "Contrôle la longueur et les caractères des noms"
```

**Tu sais que c’est bon quand :** S1, S2 et S3 passent.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

ASCII est un ensemble de caractères précis ; les méthodes isalpha et isalnum acceptent aussi des lettres accentuées.

</details>

<details>
<summary>Indice 2</summary>

Examine séparément la longueur, le premier caractère et les autres caractères ; teste chaque limite sans convertir l’entrée.

</details>

<details>
<summary>Indice 3</summary>

« é » est une lettre pour isalpha(), mais « é ».isascii() vaut False ; un test de longueur peut comparer deux textes de tailles voisines.

</details>

#### Palier 5 — Espaces et mauvais types (12 min)

Gérer deux cas limites, dont une erreur levée volontairement.

**Où tu travailles :** Mac · workspaces/socle · outils.py ; test_outils.py

**Pour comprendre**

- strip() enlève les espaces aux bords du texte ; les espaces au milieu restent présents.
- TypeError signale que l’argument n’est pas du type demandé. assertRaises vérifie qu’une exception attendue est bien levée.

**Éditeur · Exemple Python à lire ou essayer**

VS Code sur le Mac : place ce code dans un fichier d’exemple jetable, puis lance ce fichier avec python3. Un extrait avec self se place dans une méthode de test.

```python
with self.assertRaises(ValueError):
    int("abc")
```

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**S4 — Espaces de bord**
- Entrée : « bob » entouré d’espaces, puis « b » entouré d’espaces
- Résultat attendu : True pour « bob » après retrait des espaces ; False pour « b », qui fait 1 caractère.

**S5 — Type non chaîne**
- Entrée : None, puis 42
- Résultat attendu : Les deux appels lèvent TypeError (assertRaises).

**Actions dans l’ordre**

1. Ajoute S4 : " bob " donne True et " b " donne False après retrait des espaces.
2. Ajoute S5 avec assertRaises(TypeError), séparément pour None et 42.
3. Contrôle le type avant d’utiliser une méthode de chaîne, puis applique les règles au texte nettoyé.
4. Relance S1 à S5. L’exception attendue doit être TypeError ; une autre exception ne valide pas S5.
5. Commite les changements.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add outils.py test_outils.py
git commit -m "Gère les espaces et les types invalides"
```

**Tu sais que c’est bon quand :** S1 à S5 passent.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Le type de l’entrée doit être vérifié avant une méthode de chaîne ; strip enlève seulement les espaces aux bords.

</details>

<details>
<summary>Indice 2</summary>

Compare un nom entouré d’espaces à un nom avec un espace au milieu, puis vérifie qu’un entier produit ValueError.

</details>

<details>
<summary>Indice 3</summary>

«  livre  ».strip() donne « livre », tandis que « li vre ».strip() garde l’espace intérieur ; 42 n’a pas de méthode strip().

</details>

#### Palier 6 — Lire une ligne de journal (15 min)

Passer d’une ligne de journal fictif à cinq informations nommées, et refuser les lignes incorrectes.

**Où tu travailles :** Mac · workspaces/socle · outils.py ; test_outils.py

**Pour comprendre**

- Un journal est un texte qui raconte des événements. Ici, une ligne représente une connexion fictive : date, heure, événement, utilisateur et adresse IP. Tu travailles sur cette chaîne, sans lire de fichier à ce palier.
- Un champ est un morceau de la ligne. split() sans argument sépare le texte sur les espaces et produit une liste ; ses positions commencent à 0.
- Un dictionnaire associe une clé à une valeur : la clé utilisateur permet de retrouver le nom sans se souvenir d’une position.
- None est la valeur Python qui signifie ici « ligne refusée ». Ce n’est ni le texte "None", ni un dictionnaire vide, ni une exception.

**Éditeur · Découper un ticket de courses (exemple à part)**

À lire ou essayer dans un fichier jetable, puis supprimer. Ce petit exemple explique split ; il ne résout pas analyser_ligne.

```python
ticket = "pain 2 EUR"
morceaux = ticket.split()
print(morceaux)       # ['pain', '2', 'EUR']
print(morceaux[0])    # pain : première position
print(morceaux[1])    # 2 : c’est encore une chaîne
print(morceaux[2])    # EUR
```

**Exemple de résultat attendu**

Ce que tu donnes :

```text
"2026-01-05 08:12:44 LOGIN_OK alice 192.0.2.10"
```

Ce que tu dois obtenir :

```text
{
  "date": "2026-01-05",
  "heure": "08:12:44",
  "evenement": "LOGIN_OK",
  "utilisateur": "alice",
  "ip": "192.0.2.10"
}
```

Tu écris la fonction qui produit ce résultat. Cet exemple montre les données attendues, pas son code.

**Règles à respecter**

- La fonction s’appelle analyser_ligne(ligne) et reçoit une chaîne.
- Une ligne admise contient exactement cinq champs, dans l’ordre date, heure, événement, utilisateur, IP. Les valeurs du dictionnaire restent des chaînes.
- L’événement admis est LOGIN_OK ou LOGIN_FAIL.
- L’IP contient exactement quatre nombres entiers séparés par des points, chacun entre 0 et 255 inclus.
- Ligne vide après retrait des espaces aux bords → None.
- Nombre de champs différent de cinq → None.
- Événement différent de LOGIN_OK et LOGIN_FAIL → None.
- IP qui ne respecte pas la règle ci-dessus → None.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**S6 — Ligne de journal nominale**
- Entrée : « 2026-01-05 08:12:44 LOGIN_OK alice 192.0.2.10 »
- Résultat attendu : Dictionnaire exact : date « 2026-01-05 », heure « 08:12:44 », evenement « LOGIN_OK », utilisateur « alice », ip « 192.0.2.10 ».

**S7 — Lignes refusées par la structure ou l’événement**
- Entrée : Chaîne vide ; ligne à 4 champs ; ligne à 6 champs ; événement « LOGIN_BOOM »
- Résultat attendu : None pour les quatre cas.

**S8 — Adresse invalide**
- Entrée : ip « 192.0.2.300 », ip « 192.0.2 », ip « abc.def.ghi.jkl »
- Résultat attendu : None pour les trois lignes.

**Actions dans l’ordre**

1. Dans test_outils.py, écris S6 avec la ligne affichée ci-dessus. Compare le retour à tout le dictionnaire attendu, avec ses cinq clés et ses cinq valeurs.
2. Dans outils.py, crée analyser_ligne(ligne). Découpe le texte et associe chaque champ à la bonne clé. Fais passer S6.
3. Ajoute S7 : une ligne vide, une ligne de quatre champs, une de six champs, puis une avec LOGIN_BOOM donnent toutes None. Complète ces refus.
4. Ajoute S8 : remplace seulement l’IP d’une ligne valide par 192.0.2.300, puis 192.0.2, puis abc.def.ghi.jkl. Chaque cas donne None.
5. Complète la vérification de l’IP, puis relance S1 à S8. Garde le même retour pour tous les cas refusés.
6. Commite outils.py et test_outils.py une fois la suite verte.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add outils.py test_outils.py
git commit -m "Ajoute analyser_ligne"
```

**Tu sais que c’est bon quand :** S1 à S8 passent.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

split() donne une liste de champs ; un dictionnaire associe chaque donnée à une clé ; None indique ici une ligne refusée.

</details>

<details>
<summary>Indice 2</summary>

Vérifie d’abord les cinq champs, puis l’événement et les quatre morceaux d’IP ; construis le dictionnaire après ces contrôles.

</details>

<details>
<summary>Indice 3</summary>

« pain 2 EUR ».split() donne ['pain', '2', 'EUR'] : la position 1 reste du texte, et int('2') permet ensuite une comparaison numérique.

</details>

#### Palier 7 — Compter les événements (13 min)

Parcourir une liste avec une boucle et construire des dictionnaires.

**Où tu travailles :** Mac · workspaces/socle · outils.py ; test_outils.py

**Pour comprendre**

- Une liste d’événements contient les dictionnaires construits au palier précédent. Une boucle permet d’en lire un à la fois.
- Un compteur commence à zéro et augmente pour chaque événement concerné. Compter ne doit ni retirer ni modifier les événements reçus.

**Exemple de résultat attendu**

Ce que tu donnes :

```text
Deux échecs pour alice, seulement une réussite pour bob, un échec pour carol.
```

Ce que tu dois obtenir :

```text
{"alice": 2, "carol": 1}
```

C’est le retour de echecs_par_utilisateur. Bob est absent du résultat.

**Règles à respecter**

- compter_evenements retourne toujours les deux clés LOGIN_OK et LOGIN_FAIL, avec des compteurs entiers ; les deux valent zéro pour une liste vide.
- echecs_par_utilisateur compte uniquement LOGIN_FAIL. Un utilisateur sans échec n’apparaît pas ; une liste vide donne {}.
- Les fonctions laissent la liste et les dictionnaires reçus intacts.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**S9 — Comptage des événements**
- Entrée : Liste vide, puis deux LOGIN_OK et un LOGIN_FAIL. Vérifier aussi que la liste d’entrée est identique avant et après l’appel.
- Résultat attendu : Liste vide : LOGIN_OK 0 et LOGIN_FAIL 0. Deuxième cas : LOGIN_OK 2 et LOGIN_FAIL 1. Liste inchangée.

**S10 — Échecs par utilisateur**
- Entrée : Liste vide ; alice avec deux LOGIN_FAIL ; bob avec un seul LOGIN_OK ; carol avec un LOGIN_FAIL
- Résultat attendu : Liste vide : {}. Cas mixte : {"alice": 2, "carol": 1}, sans bob.

**Actions dans l’ordre**

1. Écris S9 pour compter_evenements : liste vide, puis deux LOGIN_OK et un LOGIN_FAIL. Conserve une copie de l’entrée et vérifie qu’elle n’a pas changé après l’appel.
2. Crée compter_evenements(evenements) dans outils.py et fais passer S9.
3. Écris S10 pour echecs_par_utilisateur : liste vide, puis alice avec deux échecs, bob avec seulement une réussite et carol avec un échec.
4. Crée echecs_par_utilisateur(evenements), relance S1 à S10 et commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add outils.py test_outils.py
git commit -m "Ajoute le comptage des événements et des échecs"
```

**Tu sais que c’est bon quand :** Les 10 tests S1 à S10 passent.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Un compteur augmente pour chaque occurrence ; un dictionnaire permet de garder plusieurs compteurs nommés.

</details>

<details>
<summary>Indice 2</summary>

Traite d’abord la liste vide, puis une liste mélangée ; distingue le total par événement du comptage des échecs par utilisateur.

</details>

<details>
<summary>Indice 3</summary>

Pour les fruits ['pomme', 'poire', 'pomme'], un comptage par nom donne {'pomme': 2, 'poire': 1} ; les valeurs comptent les occurrences.

</details>

#### Palier 8 — Livre ta pull request (10 min)

Relire ton travail, le pousser sur GitHub et le fusionner proprement.

**Où tu travailles :** Mac · workspaces/socle · Branche feat/bases et PR GitHub

**Pour comprendre**

- git diff montre les lignes modifiées ; git diff --staged montre celles choisies pour le prochain commit. Le diff de la MR compare toute ta branche à main.
- La demande de fusion (MR dans GitLab, PR dans GitHub) permet de relire le travail avant de l’intégrer à main.

**Actions dans l’ordre**

1. Lance la suite complète avec la commande indiquée au début de la mission.
2. Dans GitHub, vérifie que la PR n’inclut ni fixtures/ ni caches Python. Si gh n’est pas installé, ouvre la PR depuis le site : cet outil est facultatif.
3. Relis git status et git diff : la livraison doit contenir outils.py, test_outils.py et .gitignore, avec les modifications nécessaires de cette mission.
4. Ajoute les fichiers par leur nom, relis git diff --staged, puis commite ce qui ne l’est pas encore.
5. Pousse feat/bases et ouvre la demande de fusion vers main.
6. Relis le diff dans la demande de fusion. Cette mission n’a pas encore de pipeline : la relecture et les conditions de fusion restent nécessaires.
7. Fusionne après relecture et, pour GitLab de l’école, après son autorisation.
8. Après la fusion, reviens sur main et lance git pull --ff-only avant la mission suivante.

**Terminal · Relire l’état du dépôt**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
git status
git diff main --stat
```

**Terminal · Publier la branche ou ouvrir la demande de fusion**

```bash
git push -u origin feat/bases
gh pr create --base main --title "Bases : validation et analyse de journal" --body "Ajoute outils.py et ses tests S1 à S10."
```

**Terminal · Après la fusion : actualiser la principale**

```bash
git switch main
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git pull --ff-only
```

**Tu sais que c’est bon quand :** La pull request contient outils.py, test_outils.py et le .gitignore de préparation, et ton main local contient la fusion (git log --oneline).

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Une PR présente les commits de ta branche pour relecture ; un test local ne fusionne rien.

</details>

<details>
<summary>Indice 2</summary>

Vérifie les fichiers choisis avec git diff --staged et les changements contre main ; pousse feat/bases avant d’ouvrir la PR.

</details>

<details>
<summary>Indice 3</summary>

Une PR de carnet peut afficher README.md et carnet.py ; un dossier de cache affiché dans son diff révèle qu’il a été ajouté à Git.

</details>

**Avant de livrer**

- python3 -m unittest -v affiche OK pour S1 à S10.
- git log --oneline montre un commit par palier de code (au moins cinq).
- La pull request contient outils.py, test_outils.py et le .gitignore de préparation, sans __pycache__ ni fixtures.

### MR2 — feat/fichiers-erreurs (100 min)

Tu vas construire journal.py et test_journal.py : lire les lignes, compter les lignes malformées, construire et sauvegarder un rapport. Avance dans l’ordre des paliers et vérifie chaque résultat avant de poursuivre.

**Avant de commencer**

- Point de départ : MR1 fusionnée : outils.py et ses tests sont sur la branche principale.
- Ce que tu vas produire : journal.py et test_journal.py : lire les lignes, compter les lignes malformées, construire et sauvegarder un rapport.
- Pourquoi : Tu prépares les données que l’analyseur affichera en MR3.
- Commande des tests depuis la racine : `python3 -m unittest -v`. Les cas ci-dessous sont à écrire par toi.

#### Palier 1 — Repars d’une base à jour (8 min)

Partir de main à jour, sur une branche neuve, avant d’écrire la moindre ligne.

**Où tu travailles :** Mac · workspaces/socle · Dépôt ; journal.py ; test_journal.py

**Pour comprendre**

- La branche principale (main) contient le travail déjà fusionné. Ta branche feat/... reçoit les changements de cette mission.
- Un dépôt « propre » n’a aucune modification en attente : git status te le confirme.

**Actions dans l’ordre**

1. Ouvre workspaces/socle dans VS Code. Dans le terminal du Mac, place-toi dans ce même dossier et active son venv avec source .venv/bin/activate.
2. Vérifie que MR1 est fusionnée et que outils.py est présent sur main.
3. Lis git status ; enregistre ton travail en cours avant de changer de branche.
4. Reviens sur main avec git switch main, mets-la à jour avec git pull --ff-only, puis crée feat/fichiers-erreurs. Remplace main par master si ton dépôt utilise ce nom.
5. Crée journal.py et test_journal.py, puis lance les tests déjà écrits : ils doivent tous passer.
6. Vérifie le nom de ta branche avec git status. Si elle existe déjà, reprends-la avec git switch sans -c.

**Terminal · Après la fusion : actualiser la principale**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
git switch main
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git pull --ff-only
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git switch -c feat/fichiers-erreurs
```

**Terminal · Relire l’état du dépôt**

```bash
git log --oneline
```

**Terminal · Commande à lancer au moment indiqué**

```bash
touch journal.py test_journal.py
```

**Terminal · Relire l’état du dépôt**

```bash
git status
```

**Tu sais que c’est bon quand :** git status affiche « On branch feat/fichiers-erreurs » et deux fichiers non suivis : journal.py et test_journal.py.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Chaque mission part de la précédente fusionnée ; git pull --ff-only accepte une simple avance sans créer de fusion locale.

</details>

<details>
<summary>Indice 2</summary>

Vérifie outils.py sur main et une suite verte avant de créer feat/fichiers-erreurs ; reprends la branche si elle existe déjà.

</details>

<details>
<summary>Indice 3</summary>

Si origin/main contient un commit de plus, pull --ff-only avance main ; si les deux historiques divergent, la commande refuse et le graphe aide à comprendre.

</details>

#### Palier 2 — Refuser un chemin vide, sans toucher au disque (10 min)

Écrire un test pour une fonction qui valide une entrée, puis la faire passer.

**Où tu travailles :** Mac · workspaces/socle · journal.py ; test_journal.py

**Pour comprendre**

- Un chemin est le texte qui désigne un fichier, par exemple dossier/auth.log. Vérifier sa forme et vérifier son existence sont deux opérations différentes.
- ValueError signale ici une valeur vide ou inutilisable, même si son type est une chaîne.

**Éditeur · Exemple Python à lire ou essayer**

VS Code sur le Mac : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
def diviser(a, b):
    if b == 0:
        raise ZeroDivisionError("b ne doit pas être zéro")
    return a / b
```

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**S13 — Chemin vide ou blanc**
- Entrée : Chaîne vide, une chaîne de trois espaces, puis « dossier/auth.log »
- Résultat attendu : ValueError pour les deux premiers cas ; aucune exception pour le troisième, sans accès au disque.

**Actions dans l’ordre**

1. Dans test_journal.py, écris S13 avant les tests de lecture : texte vide et espaces seuls doivent lever ValueError.
2. Ajoute un cas non vide, dossier/auth.log : il est admis même si le fichier n’existe pas.
3. Dans journal.py, écris verifier_chemin(chemin) pour contrôler ce texte sans ouvrir le fichier.
4. Relance la suite ; commite quand S13 passe.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add journal.py test_journal.py
git commit -m "Ajoute verifier_chemin et refuse les chemins vides"
```

**Tu sais que c’est bon quand :** S13 passe, et git log --oneline montre ton nouveau commit. Le test passe sans fichier présent : aucun accès au disque.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Valider un chemin vide est une règle pure : elle se teste sans créer de fichier.

</details>

<details>
<summary>Indice 2</summary>

Écris S11 avec une chaîne vide et une chaîne d’espaces ; demande ValueError avant toute ouverture de fichier.

</details>

<details>
<summary>Indice 3</summary>

Un champ de dossier «   » devient vide après strip() ; tester ce refus n’a pas besoin d’un disque ni d’un fichier fictif.

</details>

#### Palier 3 — Lire un fichier UTF-8 et nettoyer ses lignes (14 min)

Lire un fichier avec pathlib, puis écarter les lignes vides et les espaces de bord.

**Où tu travailles :** Mac · workspaces/socle · journal.py ; test_journal.py

**Pour comprendre**

- open(..., encoding="utf-8") lit un fichier texte ; with garantit sa fermeture. UTF-8 permet de lire notamment les accents.
- Un dossier temporaire est créé par le test et supprimé à sa fin. Le test écrit lui-même les données dont il a besoin.

**Éditeur · Exemple Python à lire ou essayer**

VS Code sur le Mac : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
import pathlib
import tempfile

with tempfile.TemporaryDirectory() as dossier:
    chemin = pathlib.Path(dossier) / "courses.txt"
    chemin.write_text("pain\nlait\n", encoding="utf-8")
    print(chemin.read_text(encoding="utf-8").splitlines())
```

**Exemple de résultat attendu**

Ce que tu donnes :

```text
Un fichier contenant "  première  \n\n deuxième\n troisième \n"
```

Ce que tu dois obtenir :

```text
["première", "deuxième", "troisième"]
```

Le résultat est une liste de chaînes ; les lignes vides ne deviennent pas des événements.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**S11 — Lecture nettoyée**
- Entrée : Fichier temporaire de trois lignes, une ligne vide et des espaces en fin de ligne
- Résultat attendu : Liste de trois chaînes, dans l’ordre, sans espaces de bord et sans ligne vide.

**Actions dans l’ordre**

1. Écris S11 : dans un dossier temporaire, crée un fichier avec trois lignes non vides, des lignes vides et des espaces aux bords.
2. Vérifie que lire_journal renvoie les trois lignes nettoyées, dans le même ordre.
3. Dans journal.py, écris lire_journal(chemin) : appelle verifier_chemin, ouvre en UTF-8, nettoie les lignes et écarte celles devenues vides.
4. Relance tous les tests puis commite. Le test ne lit pas la fixture auth.log.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add journal.py test_journal.py
git commit -m "Ajoute lire_journal avec nettoyage des lignes"
```

**Tu sais que c’est bon quand :** S11 et S13 passent. Le fichier temporaire disparaît tout seul : git status ne montre aucun fichier de test.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

UTF-8 décrit comment convertir les octets en texte ; une ligne peut finir par un saut de ligne.

</details>

<details>
<summary>Indice 2</summary>

Utilise un fichier temporaire contenant des lignes normales, vides et entourées d’espaces ; compare précisément la liste renvoyée.

</details>

<details>
<summary>Indice 3</summary>

Un fichier de courses contenant «  pain  » puis une ligne blanche permet de voir la différence entre nettoyer une ligne et conserver une ligne vide.

</details>

#### Palier 4 — Laisser remonter l’erreur de fichier absent (8 min)

Comprendre qu’une erreur qui n’est pas attrapée remonte jusqu’à l’appelant.

**Où tu travailles :** Mac · workspaces/socle · journal.py ; test_journal.py

**Pour comprendre**

- FileNotFoundError est l’erreur Python pour un fichier absent. À ce niveau, lire_journal la laisse remonter : la CLI la traduira plus tard en message utilisateur.
- Un chemin dans un dossier temporaire permet de tester cette absence sans dépendre du contenu de ton ordinateur.

**Éditeur · Exemple Python à lire ou essayer**

VS Code sur le Mac : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
try:
    int("abc")
except ValueError:
    print("ce n’est pas un nombre")
```

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**S12 — Fichier absent**
- Entrée : Chemin inexistant dans un dossier temporaire
- Résultat attendu : lire_journal lève FileNotFoundError (assertRaises).

**Actions dans l’ordre**

1. Ajoute S12 : fabrique le chemin d’un fichier absent dans un dossier temporaire.
2. Avec assertRaises(FileNotFoundError), appelle lire_journal sur ce chemin.
3. Lance la suite. Si S12 passe déjà, garde le test : aucune modification du code n’est nécessaire.
4. Vérifie que lire_journal ne transforme pas cette erreur en liste vide, puis commite le test.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add test_journal.py
git commit -m "Teste le fichier absent (FileNotFoundError)"
```

**Tu sais que c’est bon quand :** S12 passe, et journal.py ne contient aucun except autour de la lecture du fichier.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Une exception peut remonter sans être remplacée ; FileNotFoundError indique un chemin absent.

</details>

<details>
<summary>Indice 2</summary>

Choisis un chemin inexistant dans un dossier temporaire et vérifie le type exact de l’exception, sans créer ce fichier.

</details>

<details>
<summary>Indice 3</summary>

Ouvrir absent.txt dans un dossier neuf lève FileNotFoundError ; remplacer cela par [] ferait croire qu’un fichier vide a été lu.

</details>

#### Palier 5 — Séparer les lignes valides des malformées (14 min)

Parcourir des lignes avec une boucle, compter les refusées, et renvoyer un couple.

**Où tu travailles :** Mac · workspaces/socle · journal.py ; test_journal.py

**Pour comprendre**

- Une fonction peut réutiliser une autre fonction : analyser_ligne connaît déjà les règles d’une ligne.
- Un tuple peut rendre deux résultats à la fois : la liste des événements admis et le nombre de lignes refusées.

**Éditeur · Exemple Python à lire ou essayer**

VS Code sur le Mac : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
def separer_pairs(nombres):
    pairs = []
    autres = 0
    for n in nombres:
        if n % 2 == 0:
            pairs.append(n)
        else:
            autres += 1
    return pairs, autres

print(separer_pairs([1, 2, 4, 7]))
```

**Exemple de résultat attendu**

Ce que tu donnes :

```text
charger_evenements([])
```

Ce que tu dois obtenir :

```text
([], 0)
```

Les parenthèses regroupent les deux résultats ; tu peux les récupérer dans deux variables.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**S14 — Lignes valides et malformées**
- Entrée : Quatre lignes dont deux invalides (une mauvaise structure, un événement inconnu), puis une liste vide
- Résultat attendu : Deux événements dans l’ordre d’arrivée et malformees = 2 ; liste vide : ([], 0).

**Actions dans l’ordre**

1. Écris S14 : quatre lignes dont deux refusées doivent donner deux événements dans l’ordre et le compteur 2. Vérifie aussi l’entrée vide.
2. Crée charger_evenements(lignes) dans journal.py en important analyser_ligne depuis outils.
3. Pour chaque ligne, conserve le dictionnaire obtenu ou augmente le compteur si le retour vaut None.
4. Retourne les deux résultats ensemble, relance la suite et commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add journal.py test_journal.py
git commit -m "Ajoute charger_evenements et compte les lignes malformees"
```

**Tu sais que c’est bon quand :** S11 à S14 passent. Une liste vide donne ([], 0).

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Une ligne vide et une ligne malformée sont deux situations différentes ; analyser_ligne fournit le verdict sur une ligne non vide.

</details>

<details>
<summary>Indice 2</summary>

Sépare les lignes ignorées des lignes comptées ; garde les dictionnaires des lignes valides et le nombre de lignes non vides refusées.

</details>

<details>
<summary>Indice 3</summary>

Sur trois lignes de tickets, une ligne blanche ignorée, une ligne lisible et une ligne cassée donnent une donnée valide et une malformée, pas trois erreurs.

</details>

#### Palier 6 — Construire le rapport (14 min)

Assembler un dictionnaire de résultats à partir de fonctions déjà testées.

**Où tu travailles :** Mac · workspaces/socle · journal.py ; test_journal.py

**Pour comprendre**

- Le rapport rassemble les compteurs déjà calculés ; il ne relit pas les fichiers.
- Réutiliser compter_evenements et echecs_par_utilisateur évite de maintenir plusieurs versions des mêmes règles.

**Éditeur · Exemple Python à lire ou essayer**

VS Code sur le Mac : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
rapport = {"nom": "pain", "quantite": 2}
print(rapport["quantite"])
```

**Éditeur · Import à ajouter dans journal.py**

VS Code sur le Mac : cette ligne se place en haut de journal.py. Elle réutilise tes fonctions de MR1 ; ce n’est pas un exemple jetable.

```python
from outils import compter_evenements, echecs_par_utilisateur
```

**Exemple de résultat attendu**

Ce que tu donnes :

```text
construire_rapport([], 0)
```

Ce que tu dois obtenir :

```text
{"lignes_valides": 0, "login_ok": 0, "login_fail": 0, "lignes_malformees": 0, "echecs_par_utilisateur": {}}
```

Même sans données, les cinq clés sont présentes.

**Règles à respecter**

- Le rapport a les clés lignes_valides, login_ok, login_fail, lignes_malformees et echecs_par_utilisateur.
- Les quatre premiers champs sont des compteurs ; le dernier est le dictionnaire des échecs par utilisateur.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**S15 — Construction du rapport**
- Entrée : Trois LOGIN_OK, deux LOGIN_FAIL dont deux pour alice, et un nombre de lignes malformées de 1
- Résultat attendu : lignes_valides 5, login_ok 3, login_fail 2, lignes_malformees 1, echecs_par_utilisateur {"alice": 2}.

**S18 — Journal vide**
- Entrée : construire_rapport([], 0)
- Résultat attendu : lignes_valides 0, login_ok 0, login_fail 0, lignes_malformees 0, echecs_par_utilisateur {} ; aucune exception.

**Actions dans l’ordre**

1. Écris d’abord S18 : aucun événement et zéro ligne malformée donnent le rapport vide décrit ci-dessus.
2. Écris S15 : trois réussites, deux échecs pour alice et une ligne malformée donnent 5, 3, 2, 1 et {"alice": 2}.
3. Crée construire_rapport(evenements, malformees) avec les fonctions de outils.py.
4. Compare les dictionnaires entiers dans les tests, relance toute la suite et commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add journal.py test_journal.py
git commit -m "Ajoute construire_rapport"
```

**Tu sais que c’est bon quand :** S11 à S15 et S18 passent.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Un rapport rassemble des résultats déjà calculés ; les compteurs doivent rester cohérents avec les événements reçus.

</details>

<details>
<summary>Indice 2</summary>

Réutilise les fonctions de MR1 plutôt que recopier leurs boucles, puis teste un cas vide et un cas avec plusieurs utilisateurs.

</details>

<details>
<summary>Indice 3</summary>

Un rapport de commandes peut contenir total=3 et par_client={'lea': 2, 'sam': 1} : la somme des clients retrouve le total.

</details>

#### Palier 7 — Sauver et relire le JSON (14 min)

Écrire un rapport en JSON, le relire, et transformer un JSON abîmé en message clair.

**Où tu travailles :** Mac · workspaces/socle · journal.py ; test_journal.py

**Pour comprendre**

- JSON est un format de fichier pour conserver des dictionnaires et des listes. dump écrit dans un fichier ; load lit depuis un fichier.
- JSONDecodeError signifie que le fichier existe mais que son texte n’est pas un JSON valide. Ce cas diffère d’un fichier absent.

**Éditeur · Exemple Python à lire ou essayer**

VS Code sur le Mac : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
import json

with open("panier.json", "w", encoding="utf-8") as f:
    json.dump({"fruit": "pomme"}, f, ensure_ascii=False, indent=2)

with open("panier.json", encoding="utf-8") as f:
    print(json.load(f))
```

**Éditeur · Exemple Python à lire ou essayer**

```python
try:
    json.loads("[1, 2")
except json.JSONDecodeError as exc:
    print("erreur :", exc)
```

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**S16 — Aller-retour JSON avec accents**
- Entrée : Rapport contenant la clé « échecs » et une valeur accentuée, sauvegardé puis rechargé
- Résultat attendu : Le rapport rechargé est égal à l’original, et le fichier est relu sans erreur par json.load.

**S17 — Erreurs de chargement JSON**
- Entrée : Fichier contenant « {pas du json » ; chemin absent
- Résultat attendu : ValueError pour le fichier corrompu ; FileNotFoundError pour le chemin absent.

**Actions dans l’ordre**

1. Essaie l’exemple panier.json dans un fichier jetable ; observe l’écriture et la relecture, puis nettoie ces fichiers d’essai.
2. Écris S16 : sauvegarde un rapport avec des accents dans un dossier temporaire, recharge-le et compare au rapport initial.
3. Crée sauvegarder_rapport(chemin, rapport) et charger_rapport(chemin). Ouvre les fichiers en UTF-8 et utilise ensure_ascii=False pour écrire ; garde le même ordre d’arguments dans tes tests.
4. Écris S17 : JSON cassé → ValueError avec message français citant le fichier ; fichier absent → FileNotFoundError conservée.
5. Attrape uniquement JSONDecodeError dans le chargement, puis relance la suite et commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add journal.py test_journal.py
git commit -m "Ajoute sauvegarder_rapport et charger_rapport en JSON"
```

**Tu sais que c’est bon quand :** S11 à S18 passent. Le fichier panier.json de l’exemple n’est pas dans git status (supprime-le après l’exemple).

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

JSON conserve des données structurées ; relire le fichier permet de vérifier ce qui a réellement été écrit.

</details>

<details>
<summary>Indice 2</summary>

Écris dans un dossier temporaire, recharge avec json.load et compare le dictionnaire ; observe aussi indentation et saut de ligne demandés.

</details>

<details>
<summary>Indice 3</summary>

json.loads('{"produit": "café", "quantite": 2}') donne un dictionnaire avec un entier ; le texte JSON seul ne prouve pas que le fichier est lisible.

</details>

#### Palier 8 — Git de rattrapage : commit fautif, revert, stash, restore (10 min)

Défaire un commit sans réécrire l’historique, mettre une modification de côté, et jeter un brouillon.

**Où tu travailles :** Mac · workspaces/socle · journal.py ; test_journal.py

**Pour comprendre**

- git revert crée un nouveau commit qui annule un commit précédent : l’erreur et sa correction restent visibles dans l’historique.
- git stash met des modifications non commitées de côté ; pop les remet. git restore efface les changements non committés du fichier nommé.

**Actions dans l’ordre**

1. Commence avec un dépôt propre et tous les tests verts. Introduis une erreur dans verifier_chemin, sans changer les tests.
2. Lance les tests, observe l’échec et commite uniquement cette erreur volontaire.
3. Lance git revert HEAD --no-edit : les tests doivent redevenir verts. Relis les deux commits dans git log.
4. Ajoute seulement un commentaire # brouillon dans journal.py ; lance stash push, observe status propre et stash list, puis stash pop.
5. Vérifie que le commentaire est revenu. Utilise restore uniquement pour retirer ce brouillon, puis vérifie status propre et stash list vide.

**Terminal · Enregistrer le travail vérifié**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
git add journal.py
git commit -m "Casse verifier_chemin (exercice)"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -m unittest -v
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git revert HEAD --no-edit
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -m unittest -v
```

**Terminal · Commande à lancer au moment indiqué**

```bash
echo "# brouillon" >> journal.py
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git stash push -m brouillon
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git stash list
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git stash pop
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git restore journal.py
```

**Terminal · Relire l’état du dépôt**

```bash
git status
git log --oneline
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git stash list
```

**Tu sais que c’est bon quand :** git log --oneline montre « Casse verifier_chemin (exercice) » puis son revert ; git status est propre ; git stash list est vide.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

revert crée un commit inverse ; stash met une modification de côté ; restore reprend une version d’un fichier.

</details>

<details>
<summary>Indice 2</summary>

Identifie le commit fautif avant revert et les fichiers modifiés avant stash/restore ; suis les essais sans jeter de travail utile.

</details>

<details>
<summary>Indice 3</summary>

Si un commit ajoute une ligne « brouillon », revert ajoute un second commit qui la retire : les deux restent visibles dans git log.

</details>

#### Palier 9 — Démonstration, pull request (8 min)

Vérifier le rapport sur le journal fictif, puis livrer la MR.

**Où tu travailles :** Mac · workspaces/socle · fixtures/socle/auth.log ; PR GitHub

**Pour comprendre**

- git diff montre les lignes modifiées ; git diff --staged montre celles choisies pour le prochain commit. Le diff de la MR compare toute ta branche à main.
- La demande de fusion (MR dans GitLab, PR dans GitHub) permet de relire le travail avant de l’intégrer à main.

**Actions dans l’ordre**

1. Lance la suite complète avec la commande indiquée au début de la mission.
2. Avant la livraison, fais D1 avec une copie locale du journal fictif : lire → charger les événements → construire le rapport. Le nombre de lignes non vides doit égaler lignes_valides + lignes_malformees. Ne commite pas la fixture ni un rapport d’essai.
3. Relis git status et git diff : la livraison doit contenir journal.py et test_journal.py, avec les modifications nécessaires de cette mission.
4. Ajoute les fichiers par leur nom, relis git diff --staged, puis commite ce qui ne l’est pas encore.
5. Pousse feat/fichiers-erreurs et ouvre la demande de fusion vers main.
6. Relis le diff dans la demande de fusion. Cette mission n’a pas encore de pipeline : la relecture et les conditions de fusion restent nécessaires.
7. Fusionne après relecture et, pour GitLab de l’école, après son autorisation.
8. Après la fusion, reviens sur main et lance git pull --ff-only avant la mission suivante.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 -c "from journal import lire_journal, charger_evenements, construire_rapport; lignes = lire_journal('fixtures/socle/auth.log'); evenements, malformees = charger_evenements(lignes); print(construire_rapport(evenements, malformees))"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
grep -c "[^[:space:]]" fixtures/socle/auth.log
```

**Terminal · Relire l’état du dépôt**

```bash
git status
git diff main --stat
```

**Terminal · Publier la branche ou ouvrir la demande de fusion**

```bash
git push -u origin feat/fichiers-erreurs
gh pr create --base main --title "Fichiers, erreurs et JSON" --body "Ajoute journal.py et ses tests S11 à S18."
```

**Tu sais que c’est bon quand :** lignes_valides + lignes_malformees est égal au nombre affiché par grep. La pull request ne contient que journal.py et test_journal.py (et outils.py si tu l’as modifié, avec une raison).

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

La démonstration utilise un vrai fichier local ; les tests restent reproductibles avec leurs fichiers temporaires.

</details>

<details>
<summary>Indice 2</summary>

Retrouve fixtures/socle/auth.log depuis le dépôt du parcours et vérifie que lignes_valides + lignes_malformees retrouve les lignes non vides.

</details>

<details>
<summary>Indice 3</summary>

Pour un journal de 7 lignes non vides avec 2 refusées, les compteurs doivent donner 5 valides et 2 malformées ; une ligne blanche n’ajoute rien.

</details>

**Démonstrations manuelles (hors CI)**

Ces essais lisent des fichiers locaux ou utilisent le labo et les outils réels, selon le parcours. Ils sont séparés des tests obligatoires.

**D1 — Rapport sur la copie du journal fictif**
- Entrée : Script local (hors tests) qui lit fixtures/socle/auth.log avec lire_journal, charger_evenements et construire_rapport
- Résultat attendu : Aucune trace d’erreur. lignes_valides + lignes_malformees est égal au nombre de lignes non vides du fichier, que tu comptes avec une commande de ton choix.

**Avant de livrer**

- python -m unittest passe pour S1 à S18 ; les tests de MR1 (S1 à S10) restent verts.
- Les tests créent leurs fichiers dans un dossier temporaire et ne laissent rien dans le dépôt.
- git log --oneline montre le commit fautif et son revert ; git stash list est vide à la fin.
- Le diff de la MR est relu et ne contient que journal.py, test_journal.py et les modifications éventuelles de outils.py justifiées.
- Chaque palier de code a son commit, avec le message donné dans le palier.

### MR3 — feat/analyseur (70 min)

Tu vas construire analyseur.py, test_analyseur.py et README.md : un programme utilisable en terminal, avec messages et codes de retour. Avance dans l’ordre des paliers et vérifie chaque résultat avant de poursuivre.

**Avant de commencer**

- Point de départ : MR2 fusionnée : outils.py et journal.py sont disponibles et leurs tests passent.
- Ce que tu vas produire : analyseur.py, test_analyseur.py et README.md : un programme utilisable en terminal, avec messages et codes de retour.
- Pourquoi : Tu livres un premier programme complet et pratiques conflit, rebase et tag.
- Commande des tests depuis la racine : `python3 -m unittest -v`. Les cas ci-dessous sont à écrire par toi.

#### Palier 1 — Repars de main et crée la branche (5 min)

Partir d’une base à jour, avant d’écrire le programme complet.

**Où tu travailles :** Mac · workspaces/socle · Dépôt

**Pour comprendre**

- La branche principale (main) contient le travail déjà fusionné. Ta branche feat/... reçoit les changements de cette mission.
- Un dépôt « propre » n’a aucune modification en attente : git status te le confirme.

**Actions dans l’ordre**

1. Ouvre workspaces/socle dans VS Code. Dans le terminal du Mac, place-toi dans ce même dossier et active son venv avec source .venv/bin/activate.
2. Vérifie que MR2 est fusionnée : outils.py et journal.py doivent être présents.
3. Lis git status ; enregistre ton travail en cours avant de changer de branche.
4. Reviens sur main avec git switch main, mets-la à jour avec git pull --ff-only, puis crée feat/analyseur. Remplace main par master si ton dépôt utilise ce nom.
5. Lance la suite existante avant de créer analyseur.py : cette base doit être verte.
6. Vérifie le nom de ta branche avec git status. Si elle existe déjà, reprends-la avec git switch sans -c.

**Terminal · Après la fusion : actualiser la principale**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
git switch main
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git pull --ff-only
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git switch -c feat/analyseur
```

**Terminal · Relire l’état du dépôt**

```bash
git log --oneline
git status
```

**Tu sais que c’est bon quand :** git status affiche « On branch feat/analyseur » et « nothing to commit, working tree clean ».

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

L’analyseur assemble les fonctions déjà fusionnées ; sa nouvelle branche doit repartir d’une base testée.

</details>

<details>
<summary>Indice 2</summary>

Retrouve outils.py et journal.py sur main, lance les tests existants, puis crée ou reprends feat/analyseur.

</details>

<details>
<summary>Indice 3</summary>

Dans un projet de recettes, un assembleur utilise les modules ingrédients et portions existants ; les recréer ailleurs casse la continuité du projet.

</details>

#### Palier 2 — Formater le rapport : le cas complet (7 min)

Séparer le calcul du texte et son affichage : une fonction qui renvoie une chaîne, sans rien afficher.

**Où tu travailles :** Mac · workspaces/socle · analyseur.py ; test_analyseur.py

**Pour comprendre**

- Formater signifie transformer des données en un texte lisible. return rend ce texte au programme qui appelle ; print l’affiche immédiatement.
- Les clés d’un dictionnaire ne donnent pas forcément l’ordre souhaité : sorted permet un ordre alphabétique stable.

**Éditeur · Exemple Python à lire ou essayer**

VS Code sur le Mac : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
def afficher_panier(articles):
    lignes = []
    for nom in sorted(articles):
        lignes.append(f"{nom} : {articles[nom]}")
    return "\n".join(lignes)

print(afficher_panier({"pomme": 3, "banane": 1}))
```

**Règles à respecter**

- Les quatre libellés sont, dans cet ordre : Lignes valides :, Connexions réussies :, Échecs de connexion :, Lignes malformées :.
- Les lignes d’utilisateurs suivent, triées par nom.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**S19 — Formatage complet**
- Entrée : Rapport avec 5 lignes valides, 3 connexions réussies, 2 échecs répartis entre bob (1) et alice (1), 1 malformée
- Résultat attendu : Les quatre lignes de compteurs ont leurs valeurs ; la ligne alice apparaît avant la ligne bob.

**Actions dans l’ordre**

1. Écris S19 dans test_analyseur.py avec le rapport décrit dans le cas de test.
2. Vérifie les quatre libellés de compteurs dans l’ordre imposé, puis alice avant bob pour les échecs par utilisateur.
3. Crée formater_rapport(rapport) dans analyseur.py : elle retourne une chaîne et n’affiche rien.
4. Réutilise les données du rapport ; relance tous les tests puis commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add analyseur.py test_analyseur.py
git commit -m "Ajoute formater_rapport avec le cas complet"
```

**Tu sais que c’est bon quand :** S19 passe. Lance python3 analyseur.py : il n’affiche encore rien d’utile, et ce n’est pas grave à ce stade.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Le formatage transforme un dictionnaire en texte ; l’ordre et les retours à la ligne font partie du résultat.

</details>

<details>
<summary>Indice 2</summary>

Écris S18 en comparant la chaîne entière, puis construis l’affichage depuis les données sans relire le journal.

</details>

<details>
<summary>Indice 3</summary>

Un bilan « Total : 2\nPain : 1\nRiz : 1 » diffère de « Total: 2 » ; compare des chaînes complètes pour repérer espaces et sauts de ligne.

</details>

#### Palier 3 — Formater le rapport : sans échec (6 min)

Traiter le cas où personne n’a échoué.

**Où tu travailles :** Mac · workspaces/socle · analyseur.py ; test_analyseur.py

**Pour comprendre**

- Un dictionnaire vide {} signifie qu’aucun utilisateur n’a d’échec enregistré. Les autres compteurs du rapport restent utiles.
- Un cas vide est un comportement à prévoir, pas une raison de faire disparaître tout le rapport.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**S20 — Formatage sans échec**
- Entrée : echecs_par_utilisateur vide
- Résultat attendu : La chaîne contient « Aucun échec » et aucune ligne d’utilisateur.

**Actions dans l’ordre**

1. Ajoute S20 avec echecs_par_utilisateur égal à {}.
2. Vérifie la présence de « Aucun échec », l’absence de lignes utilisateur et la conservation des quatre compteurs.
3. Complète formater_rapport pour ce cas, puis relance S19 et S20 avec le reste de la suite.
4. Commite quand tous les tests passent.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add analyseur.py test_analyseur.py
git commit -m "Affiche Aucun échec quand il n’y a pas d’échec"
```

**Tu sais que c’est bon quand :** S19 et S20 passent.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Le cas sans échec doit avoir un affichage prévu ; une collection vide n’est pas une erreur.

</details>

<details>
<summary>Indice 2</summary>

Écris S19 avec le rapport sans échec et compare sa chaîne entière au texte attendu, sans laisser une ligne de classement inventée.

</details>

<details>
<summary>Indice 3</summary>

Pour une liste de retards vide, une phrase « Aucun retard » est plus claire qu’un titre suivi d’une zone vide ; le test doit exiger la forme choisie par le contrat.

</details>

#### Palier 4 — Codes de retour : usage et fichier absent (10 min)

Faire renvoyer un code de retour à main, sans jamais quitter le programme soi-même.

**Où tu travailles :** Mac · workspaces/socle · analyseur.py ; test_analyseur.py

**Pour comprendre**

- argv est ici une liste d’arguments, sans le nom du script. main(argv) la reçoit et rend un entier : les tests peuvent l’appeler comme une fonction.
- stdout porte le résultat ; stderr porte les erreurs. redirect_stdout et redirect_stderr permettent au test de lire ces sorties dans StringIO.

**Éditeur · Exemple Python à lire ou essayer**

VS Code sur le Mac : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
import sys

def signaler(message):
    print(message, file=sys.stderr)
    return 2

print(signaler("usage : exemple FICHIER"))
```

**Éditeur · Exemple Python à lire ou essayer**

```python
try:
    with open("inexistant.txt", encoding="utf-8") as f:
        print(f.read())
except FileNotFoundError:
    print("fichier introuvable")
```

**Exemple de résultat attendu**

Ce que tu donnes :

```text
main([])
```

Ce que tu dois obtenir :

```text
Retour : 2 ; stdout : vide ; stderr : message d’usage.
```

Le retour est un nombre. Le message est écrit sur un canal séparé.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**S21 — Usage sans argument**
- Entrée : main([])
- Résultat attendu : Code 2 ; message sur la sortie d’erreur ; rien sur la sortie standard.

**S22 — Fichier absent**
- Entrée : main avec un chemin inexistant dans un dossier temporaire
- Résultat attendu : Code 1 ; message clair ; aucune exception ne sort de main.

**Actions dans l’ordre**

1. Écris S21 : main([]) rend 2, écrit l’usage sur stderr et laisse stdout vide.
2. Écris S22 avec un chemin temporaire absent : main rend 1 et un message clair, sans laisser sortir l’exception.
3. Crée main(argv). Vérifie les arguments avant la lecture ; traite FileNotFoundError et ValueError au niveau de la CLI.
4. Capture les sorties dans les tests, relance la suite et commite. N’appelle pas sys.exit dans main.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add analyseur.py test_analyseur.py
git commit -m "Ajoute main avec les codes de retour 2 et 1"
```

**Tu sais que c’est bon quand :** S19 à S22 passent. Aucun sys.exit n’apparaît dans analyseur.py à ce stade.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

main reçoit des arguments et retourne un code ; stderr et stdout sont distincts de ce nombre.

</details>

<details>
<summary>Indice 2</summary>

Sépare le refus d’usage du fichier absent et teste chaque code attendu sans dépendre du véritable sys.argv du terminal.

</details>

<details>
<summary>Indice 3</summary>

Une commande de catalogue sans argument peut rendre 2 pour usage, alors qu’un fichier demandé mais absent peut rendre 1 ; les causes doivent rester distinguables.

</details>

#### Palier 5 — Codes de retour : succès avec une ligne malformée (10 min)

Faire afficher le rapport et renvoyer 0 quand le fichier est valide.

**Où tu travailles :** Mac · workspaces/socle · analyseur.py ; test_analyseur.py

**Pour comprendre**

- La fonction principale coordonne les étapes que tu as déjà écrites. Elle ne réécrit ni l’analyse ni le comptage.
- Le fichier de S23 est construit par le test : aucune fixture personnelle ni journal système n’est nécessaire.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**S23 — Fichier valide avec une ligne malformée**
- Entrée : Fichier temporaire de deux lignes valides et une malformée, passé à main
- Résultat attendu : Code 0 ; la sortie contient « Lignes valides : 2 » et « Lignes malformées : 1 ».

**Actions dans l’ordre**

1. Écris S23 : dans un dossier temporaire, crée un journal de deux lignes valides et une malformée.
2. Vérifie main([chemin]) : retour 0, texte avec « Lignes valides : 2 » et « Lignes malformées : 1 ».
3. Relie lire_journal → charger_evenements → construire_rapport → formater_rapport, puis affiche le texte dans main.
4. Relance S21 à S23 et toute la suite, puis commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add analyseur.py test_analyseur.py
git commit -m "Affiche le rapport et renvoie 0 en cas de succes"
```

**Tu sais que c’est bon quand :** S19 à S23 passent.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Une ligne malformée tolérée n’empêche pas forcément un rapport réussi ; le contrat choisit le code final.

</details>

<details>
<summary>Indice 2</summary>

Teste un fichier temporaire mélangeant ligne valide et ligne malformée, puis vérifie le rapport et le code 0 ensemble.

</details>

<details>
<summary>Indice 3</summary>

Une liste de courses avec un élément illisible peut produire un bilan avec « ignorés : 1 » et réussir ; un refus de fichier entier est une autre situation.

</details>

#### Palier 6 — Point d’entrée et import sans effet (8 min)

Lancer le programme en ligne de commande, sans qu’importer le module l’exécute.

**Où tu travailles :** Mac · workspaces/socle · analyseur.py ; test_analyseur.py

**Pour comprendre**

- Importer un module rend ses fonctions disponibles. Cela ne doit pas lancer le programme complet.
- La garde if __name__ == "__main__" distingue lancement direct et import. sys.argv[1:] retire le nom du script ; sys.exit transmet le retour au terminal.

**Éditeur · Exemple Python à lire ou essayer**

VS Code sur le Mac : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
import sys

def saluer():
    print("Bonjour")
    return 0

if __name__ == "__main__":
    sys.exit(saluer())
```

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**S24 — Import sans effet de bord**
- Entrée : Import du module analyseur dans le test, sortie redirigée
- Résultat attendu : Aucune sortie : le bloc __main__ ne s’exécute pas à l’import.

**Actions dans l’ordre**

1. Écris S24 : importe analyseur dans un nouvel interpréteur ou recharge-le pour vérifier l’absence de sortie. Un import déjà en cache ne suffit pas à le prouver.
2. Sous la garde du script seulement, appelle main avec sys.argv[1:] et transmets son retour à sys.exit.
3. Relance les tests. Fais D2 avec la copie locale du journal : résultat et code 0.
4. Lance sans argument : usage et code 2. Dans le terminal du Mac, lis echo $? immédiatement après le programme, avant toute autre commande.
5. Commite quand les tests passent.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
python3 -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add analyseur.py test_analyseur.py
git commit -m "Ajoute le point d’entrée en ligne de commande"
```

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs. Lis le code de sortie immédiatement après le programme, avant toute autre commande.

```bash
python3 analyseur.py fixtures/socle/auth.log; echo $?
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 analyseur.py; echo $?
```

**Tu sais que c’est bon quand :** S19 à S24 passent. Le premier cas affiche le rapport et renvoie 0 ; le second affiche le message d’usage et renvoie 2.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

La garde __main__ distingue lancement direct et import ; sys.exit transmet le code de main au terminal.

</details>

<details>
<summary>Indice 2</summary>

Cherche les appels et affichages exécutés au niveau du module ; vérifie l’import dans un interpréteur neuf et lis echo $? juste après le programme.

</details>

<details>
<summary>Indice 3</summary>

importer un module de calcul doit rendre ses fonctions disponibles sans afficher « Calcul terminé » ; lancer son script peut afficher ce message.

</details>

#### Palier 7 — README et .gitignore (6 min)

Documenter l’usage, les codes de retour et les limites du programme.

**Où tu travailles :** Mac · workspaces/socle · README.md ; .gitignore

**Pour comprendre**

- Le README est le mode d’emploi pour quelqu’un qui découvre ton dépôt. Une commande documentée doit fonctionner depuis la racine.
- Les codes de sortie permettent aussi à un autre programme de savoir si l’analyse a réussi.

**Actions dans l’ordre**

1. Rédige README.md : objectif, forme des cinq champs d’une ligne, commande de lancement et commande des tests.
2. Explique les codes 0 (réussite), 1 (lecture/analyse impossible) et 2 (usage incorrect).
3. Précise le périmètre : journal fictif local, sans réseau.
4. Vérifie .gitignore : caches et fixtures d’essai exclus. Relance les tests et commite le README.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
cat .gitignore
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -m unittest -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add README.md .gitignore
git commit -m "Ajoute le README et complete le .gitignore"
```

**Tu sais que c’est bon quand :** git status est propre, et le README contient les trois codes de retour et la mention des données fictives.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Le README explique comment utiliser le programme ; .gitignore ne retire pas les fichiers déjà suivis par Git.

</details>

<details>
<summary>Indice 2</summary>

Reprends les commandes réellement vérifiées, explique les codes 0/1/2 et relis git status pour les caches et fixtures d’essai.

</details>

<details>
<summary>Indice 3</summary>

Une documentation « python3 carnet.py notes.txt » permet de reproduire un lancement ; « lance le code » ne dit ni le fichier ni l’argument attendu.

</details>

#### Palier 8 — Provoquer un conflit de fusion et le résoudre (10 min)

Lire les marqueurs de conflit, choisir la ligne voulue, et conclure la fusion à la main.

**Où tu travailles :** Mac · workspaces/socle · README.md dans les branches exercice/

**Pour comprendre**

- Un conflit arrive quand Git ne peut pas choisir entre deux modifications de la même ligne. Les marqueurs montrent les deux versions à départager.
- Les branches exercice/conflit-a et exercice/conflit-b sont des essais locaux. Elles ne sont pas poussées sur GitHub.

**Actions dans l’ordre**

1. Commite d’abord tout le travail de feat/analyseur ; git status doit être propre.
2. Crée les deux branches d’essai depuis feat/analyseur et remplace la première ligne de README.md différemment dans chacune. Commite chaque version.
3. Fusionne la seconde dans la première : lis le conflit attendu, puis ouvre README.md.
4. Choisis le texte final, enlève <<<<<<<, ======= et >>>>>>>, ajoute le fichier et commite la résolution.
5. Vérifie l’absence de marqueurs et observe le graphe Git avant le nettoyage.
6. Reviens sur feat/analyseur et supprime uniquement les deux branches d’essai ; -D abandonne leur historique local non fusionné.

**Terminal · Commande à lancer au moment indiqué**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
git switch feat/analyseur
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git switch -c exercice/conflit-a
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add README.md
git commit -m "Exercice : variante A du titre"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git switch feat/analyseur
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git switch -c exercice/conflit-b
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add README.md
git commit -m "Exercice : variante B du titre"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git switch exercice/conflit-a
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git merge exercice/conflit-b
```

**Terminal · Relire l’état du dépôt**

```bash
git status
```

**Terminal · Commande à lancer au moment indiqué**

```bash
grep -n "<<<<<<<\|=======\|>>>>>>>" README.md
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add README.md
git commit -m "Resout le conflit du titre (exercice)"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
grep -c "<<<<<<<\|=======\|>>>>>>>" README.md
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git switch feat/analyseur
```

**Terminal · Relire l’état du dépôt**

```bash
git branch -D exercice/conflit-b
git branch -D exercice/conflit-a
git branch
```

**Tu sais que c’est bon quand :** La dernière commande grep ne trouve aucun marqueur dans README.md et git branch ne montre plus les branches exercice/. Pourquoi -D : git branch -d refuse de supprimer une branche dont les commits ne sont pas dans feat/analyseur ; tu le sais, et tu supprimes exprès, car c’est un exercice jetable.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

Un conflit apparaît quand deux branches changent la même zone ; les marqueurs délimitent les deux versions.

</details>

<details>
<summary>Indice 2</summary>

Lis les deux variantes du README et garde une version cohérente ; supprime tous les marqueurs avant d’ajouter le fichier résolu.

</details>

<details>
<summary>Indice 3</summary>

Deux branches qui remplacent « Titre A » par « Titre B » et « Titre C » exigent un choix humain ; laisser <<<<<<< dans le fichier ne résout rien.

</details>

#### Palier 9 — Rebase local, tag v0.1.0 et pull request (8 min)

Replacer ta branche au-dessus d’un main qui a avancé, poser un tag annoté, puis ouvrir la MR.

**Où tu travailles :** Mac · workspaces/socle · Historique Git ; PR GitHub

**Pour comprendre**

- Un rebase rejoue les commits de ta branche sur une base qui a avancé. Il peut changer leurs identifiants : fais cet exercice avant le premier push.
- Un tag annoté associe un nom de version, un message et un auteur à un commit précis.

**Actions dans l’ordre**

1. Commence avec un dépôt propre. Sur main local, ajoute le commentaire d’exercice à outils.py et commite-le ; ce commit sera inclus dans la PR, sans push direct de main.
2. Reviens sur feat/analyseur et rebase sur main. En cas de conflit : corrige, git add, puis rebase --continue ; rebase --abort annule l’opération.
3. Relance tous les tests et observe le graphe des commits après le rebase.
4. Crée le tag annoté v0.1.0 avec un message, puis vérifie le commit désigné avec git show.
5. Relis le diff contre origin/main, pousse feat/analyseur et ouvre la PR. Mentionne le rebase et le commentaire d’exercice.
6. Pousse le tag séparément lorsqu’il est autorisé, puis fusionne après relecture et mets main à jour.

**Terminal · Après la fusion : actualiser la principale**

Terminal du Mac, dans cyberatelier/workspaces/socle, venv Mac activé. Exécute chaque ligne au moment indiqué, avec les modifications manuelles entre les blocs.

```bash
git switch main
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add outils.py
git commit -m "Ajoute un commentaire d’en-tete a outils.py"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git switch feat/analyseur
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git rebase main
```

**Terminal · Relire l’état du dépôt**

```bash
git log --oneline --graph
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git tag -a v0.1.0 -m "Analyseur de journal, version 0.1.0"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git tag -l
```

**Terminal · Relire l’état du dépôt**

```bash
git diff origin/main --stat
```

**Terminal · Publier la branche ou ouvrir la demande de fusion**

```bash
git push -u origin feat/analyseur
gh pr create --base main --title "Analyseur de journal" --body "Ajoute analyseur.py, test_analyseur.py et le README (S19 à S24)."
```

**Tu sais que c’est bon quand :** git log --oneline --graph montre feat/analyseur posée au-dessus du commit de main ; git tag -l affiche v0.1.0 ; le README ne contient plus de marqueur de conflit.

**Indices progressifs**

Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.

<details>
<summary>Indice 1</summary>

rebase rejoue des commits sur une nouvelle base ; un tag annoté nomme un commit de livraison.

</details>

<details>
<summary>Indice 2</summary>

Termine la relecture et les essais Git, reviens sur la branche utile, puis vérifie le commit visé par le tag après la fusion.

</details>

<details>
<summary>Indice 3</summary>

git show v0.2.0 dans un dépôt d’essai permet de voir le message du tag et le commit nommé ; le nom de tag seul ne garantit pas le bon contenu.

</details>

**Démonstrations manuelles (hors CI)**

Ces essais lisent des fichiers locaux ou utilisent le labo et les outils réels, selon le parcours. Ils sont séparés des tests obligatoires.

**D2 — Analyseur en ligne de commande**
- Entrée : python analyseur.py fixtures/socle/auth.log, puis python analyseur.py sans argument ; vérifie le code avec echo $?
- Résultat attendu : Premier cas : rapport affiché et code 0. Second cas : message d’usage et code 2.

**Avant de livrer**

- python -m unittest passe pour S1 à S24, et les tests créent leurs fichiers dans un dossier temporaire.
- Le conflit de fusion a été résolu à la main : aucun marqueur <<<<<<< , ======= ou >>>>>>> ne reste dans README.md.
- git log --oneline --graph montre la branche rebasée sur main ; le tag v0.1.0 est présent dans git tag -l.
- La merge request vers la branche principale a été relue ; les branches exercice/ ont été supprimées et ne figurent pas sur GitLab.
- Chaque palier de code a son commit, avec le message donné dans le palier.

<!-- END GENERATED EXERCISES -->

## Méthode GitLab et Git

Chaque MR suit le même cycle, que tu dois pratiquer sur ton dépôt :

1. mettre la branche principale à jour (`git switch main`, `git pull`) ;
2. créer la branche de la MR (`git switch -c feat/...`) ;
3. écrire le code et les tests, puis lancer `python3 -m unittest` ;
4. contrôler `git status` et `git diff` avant chaque commit ;
5. commiter avec un message clair, puis relire `git log --oneline` ;
6. pousser, ouvrir la MR, relire son diff avant de la déclarer prête.

Quatre résultats différents ne se confondent pas : les tests locaux (ce que tu lances sur ta machine), le pipeline GitLab réellement exécuté, l’autorisation effective de fusion, et une case cochée dans Cyber Atelier (déclarative, sans vérification).

## Repères de temps

| Étape | Minutes |
| --- | --- |
| Préparer le poste, Git et les fixtures | 20 |
| MR1 — fonctions pures, unittest, premier push | 100 |
| MR2 — fichiers, erreurs, JSON, Git de rattrapage | 100 |
| MR3 — analyseur complet, conflit, rebase, tag | 70 |
| Relecture et marge | 10 |
| **Total** | **300** |

## Préparation (20 min)

Dans le terminal du Mac depuis `workspaces/socle`, vérifie Python et Git, configure ton identité avec tes propres valeurs et clone le dépôt seulement s’il n’existe pas encore. Crée et active le venv Mac, puis copie les fixtures depuis `../../fixtures/socle`. La section « Préparation sur le Mac » donne les commandes ; MR1 crée ensuite `feat/bases`. Ton exercice existant conserve ses fichiers et sa branche : ne le reclone pas.

## Livrables

- Dépôt contenant `outils.py`, `journal.py`, `analyseur.py`, leurs tests unittest, `README.md` et `.gitignore`.
- Trois MR successives, chacune créée depuis la branche principale à jour et relue avant fusion.
- Tests S1 à S24 exécutés localement avec `python3 -m unittest` ; démonstrations D1 et D2 faites à la main, hors CI.
- Tag `v0.1.0` posé, avec conflit et rebase réalisés sur des branches locales.

## Limites

- Données entièrement fictives (`fixtures/socle`, adresses 192.0.2.0/24) ; aucun réseau, aucune cible, aucun outil offensif.
- Les tests obligatoires n’ouvrent pas `fixtures/` et n’ont besoin d’aucun service : ils tournent sur un runner sans labo. La lecture de `auth.log` reste une démonstration locale.
- Le parcours n’introduit ni pytest, ni packaging, ni CI complète : ce sont des étapes ultérieures.
- Le conflit et le rebase sont provoqués sur des branches locales jetables, jamais sur la branche principale.

## Bilan honnête

À la fin de ce parcours, tu dois être capable d’écrire une petite fonction pure avec ses cas limites, de la tester avec unittest, de lire un fichier en gérant les erreurs, de manipuler JSON, et de livrer une MR propre avec Git : branche, commit, push, relecture, conflit résolu, tag.

Ce que ce parcours ne fait pas encore : écrire un package installable, utiliser `subprocess` ou `argparse` dans un vrai programme de sécurité, mettre en place une CI complète sur ton propre runner. Tu les rencontreras dans PortPilot, HeaderScope et FileGuard, puis dans le framework. Ne compte pas sur ce parcours pour être autonome sur ces sujets : il te donne les fondations, la pratique reste à faire.
