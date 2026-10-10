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

<!-- BEGIN GENERATED EXERCISES -->
## Comment travailler un exercice

Ces exercices sont ton entraînement. Chaque palier explique les notions utiles, montre les données ou les règles attendues, puis te fait écrire et vérifier ton propre code. Les durées sont des repères : avance quand tu comprends le résultat.

1. Lis « Pour comprendre » et l’exemple lorsqu’il y en a un. Repère ce qui entre dans le programme, ce qui doit en sortir et les règles à respecter.
2. Les cartes de tests donnent l’entrée et le résultat attendu. Écris les tests correspondants dans le fichier indiqué ; cocher un palier ne les exécute pas. Avec unittest, « Ran 0 tests » signifie qu’aucun test n’a été exécuté : ce n’est pas une validation. Un cas décrit peut contenir plusieurs valeurs ; le nombre de méthodes Python n’est donc pas forcément le nombre d’identifiants.
3. Suis les actions numérotées, une à la fois. Les exemples servent à apprendre une notion ; tu écris toi-même la solution de l’exercice. Les blocs Terminal donnent les commandes à lancer au moment indiqué.
4. Vérifie le résultat indiqué avant de poursuivre. Un échec attendu (phase rouge, argument refusé ou conflit volontaire) est expliqué dans le palier.
5. Si tu bloques, lis la dernière ligne de l’erreur, compare l’entrée et l’attendu, puis ouvre l’indice. Fais un petit changement et relance.

### Le bon endroit pour chaque action

Sur ton Mac, ouvre `workspaces/toolwrap` dans VS Code. Dans Cyber Atelier, utilise l’éditeur et la console de **Coder**, avec `cwd` sur `.` (la racine du dépôt). Fais la préparation de **Environnement** avant MR1 ; la mission crée ensuite sa branche.

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

### MR1 — feat/subprocess (100 min)

Le wrapper sera appelé par la CLI en MR2, puis ses sorties seront analysées en MR3. Avance dans l’ordre des paliers et vérifie chaque résultat avant de poursuivre.

**Avant de commencer**

- Point de départ : Un dépôt cloné. Les outils réels sont observés dans Docker ; les tests les remplacent par des faux.
- Ce que tu vas produire : toolwrap.py et tests/test_toolwrap.py : lancer_outil, ses quatre clés de résultat et W1 à W5.
- Pourquoi : Le wrapper sera appelé par la CLI en MR2, puis ses sorties seront analysées en MR3.
- Commande des tests depuis la racine : `python3 -m unittest discover -s tests -v`. Les cas ci-dessous sont à écrire par toi.

#### Palier 1 — Branche et repères (10 min)

Travailler sur une branche dédiée à la MR1 et savoir où tu te trouves avant d’écrire une ligne.

**Où tu travailles :** Dépôt

**Pour comprendre**

- La branche principale (main) contient le travail déjà fusionné. Ta branche feat/... reçoit les changements de cette mission.
- Un dépôt « propre » n’a aucune modification en attente : git status te le confirme.

**Actions dans l’ordre**

1. Ouvre workspaces/toolwrap dans VS Code, ou Coder dans Cyber Atelier avec cwd sur « . ».
2. Termine la préparation de l’onglet Environnement avant de commencer.
3. Lis git status ; enregistre ton travail en cours avant de changer de branche.
4. Reviens sur main avec git switch main, mets-la à jour avec git pull --ff-only, puis crée feat/subprocess. Remplace main par master si ton dépôt utilise ce nom.
5. Vérifie le nom de ta branche avec git status. Si elle existe déjà, reprends-la avec git switch sans -c.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 --version
git --version
```

**Terminal · Après la fusion : actualiser la principale**

```bash
git switch main
git pull --ff-only
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git switch -c feat/subprocess
```

**Terminal · Relire l’état du dépôt**

```bash
git status
```

**Tu sais que c’est bon quand :** git status affiche « On branch feat/subprocess » et « nothing to commit, working tree clean ».

*Indice si tu bloques :* Si la branche existe déjà, utilise git switch feat/subprocess sans -c. Si git pull --ff-only refuse, ne force rien : regarde d’abord ce que contient ta branche avec git log --oneline.

#### Palier 2 — Lancer un programme sans shell (12 min)

Comprendre pourquoi on passe une liste d’arguments à subprocess.run, et ce que le shell ferait sinon.

**Où tu travailles :** Terminal : exemple subprocess

**Pour comprendre**

- subprocess.run lance un autre programme. Dans la liste d’arguments, le premier élément est le programme ; chaque élément suivant est un argument distinct.
- Sans shell, le point-virgule reste du texte dans un argument. Un shell pourrait l’interpréter comme un séparateur de commandes.
- capture_output récupère les sorties ; text les donne en chaînes ; returncode est le code de fin du programme.

**Actions dans l’ordre**

1. Lis l’aide de subprocess.run en te concentrant sur capture_output, text et returncode.
2. Lance le premier exemple : observe code 0, stdout avec "5\n" et stderr vide.
3. Lance le second : le texte "Ana; echo piraté" est affiché en entier, sans seconde commande exécutée.
4. Repère la différence entre la liste Python d’arguments et une commande de shell.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -c "import subprocess; r = subprocess.run(['python3', '-c', 'print(2 + 3)'], capture_output=True, text=True); print(r.returncode, repr(r.stdout), repr(r.stderr))"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -c "import subprocess; print(subprocess.run(['echo', 'Bonjour', 'Ana; echo piraté'], capture_output=True, text=True).stdout)"
```

**Tu sais que c’est bon quand :** La première commande affiche « 0 '5\n' '' ». La seconde affiche « Bonjour Ana; echo piraté » : le point-virgule reste dans l’argument, rien n’est exécuté en plus.

*Indice si tu bloques :* Une liste s’écrit avec des crochets et des guillemets. Si Python répond par une erreur, lis la dernière ligne : elle dit ce qui ne va pas.

#### Palier 3 — Observer les codes de sortie d’adsim (12 min)

Voir comment un outil signale le succès, l’échec simulé et l’erreur d’utilisation, par son code de retour et ses canaux.

**Où tu travailles :** Outil adsim dans Docker

**Pour comprendre**

- adsim simule un outil Active Directory ; il lit des données fictives et ne contacte aucun réseau.
- stdout et stderr sont deux canaux séparés ; le code de sortie est un nombre indépendant du message.

**Actions dans l’ordre**

1. Sur le Mac, place-toi dans cyberatelier pour les commandes docker compose. Dans la console du conteneur, utilise directement python3 /app/tools/adsim.py.
2. Lance la commande normale et note le canal du résultat ainsi que le code 0.
3. Lance avec --fail : observe l’erreur simulée et le code 3.
4. Lance avec un argument inconnu : observe le message sur stderr et le code 2.
5. Lis le code avec echo $? dans la même exécution et garde stderr visible.

**Terminal · Commande à lancer au moment indiqué**

Terminal de ton Mac, depuis le dossier cyberatelier contenant compose.yaml. Cette commande entre dans le conteneur ; ne la lance pas depuis sa console web.

```bash
docker compose exec atelier python /app/tools/adsim.py users --format json; echo "code=$?"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
docker compose exec atelier python /app/tools/adsim.py users --format json --fail; echo "code=$?"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
docker compose exec atelier python /app/tools/adsim.py users --inconnu; echo "code=$?"
```

**Tu sais que c’est bon quand :** Tu as noté 0 pour la première, 3 pour --fail, 2 pour l’argument inconnu, et tu sais dire quel canal porte le message d’erreur.

*Indice si tu bloques :* Si docker compose répond « no such service », tu n’es pas dans le dossier du projet. Si le conteneur ne tourne pas, lance docker compose up -d.

#### Palier 4 — Un exemple de mock : patcher le bon nom (12 min)

Remplacer un appel réel par un faux pendant un test, pour que le test ne dépende ni du hasard ni de l’extérieur.

**Où tu travailles :** de.py ; test_de.py (jetables)

**Pour comprendre**

- Un mock remplace un appel par un faux pendant le test. Tu choisis sa réponse et tu peux vérifier comment il a été appelé.
- patch remplace le nom utilisé par le module testé : si de.py a importé randint, le nom à remplacer est de.randint.

**Éditeur · Code d’exemple à placer dans de.py**

Éditeur : crée de.py dans le dossier d’exemple jetable indiqué. Exécute-le au moment demandé ; ne colle pas ce code dans la console.

```python
# de.py
from random import randint

def lancer_de():
    return randint(1, 6)
```

**Éditeur · Code d’exemple à placer dans test_de.py**

Éditeur : crée test_de.py dans le dossier d’exemple jetable indiqué. Exécute-le au moment demandé ; ne colle pas ce code dans la console.

```python
# test_de.py
import unittest
from unittest import mock
import de

class TestLancerDe(unittest.TestCase):
    def test_de_renvoie_la_valeur_du_faux(self):
        with mock.patch('de.randint', return_value=6) as faux:
            self.assertEqual(de.lancer_de(), 6)
            faux.assert_called_once_with(1, 6)

if __name__ == '__main__':
    unittest.main()
```

**Actions dans l’ordre**

1. Dans un dossier jetable hors du dépôt, crée de.py et test_de.py avec les deux exemples.
2. Lance le test : le faux doit rendre 6 et recevoir les arguments 1 et 6, une seule fois.
3. Change seulement return_value en 2, relance et observe l’échec de la comparaison à 6.
4. Rétablis 6, puis supprime le dossier d’exemple. Aucun de ces fichiers n’est un livrable de ToolWrap.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
mkdir -p ~/exemple_mock && cd ~/exemple_mock
# crée de.py et test_de.py ici, puis :
python3 -m unittest -v
```

**Terminal · Commande à lancer au moment indiqué**

```bash
cd - && rm -r ~/exemple_mock
```

**Tu sais que c’est bon quand :** Le test passe. Si tu remplaces return_value=6 par 2, il échoue : le faux impose bien la valeur.

*Indice si tu bloques :* Si le patch n’a aucun effet, vérifie le nom : 'de.randint' fonctionne parce que de.py fait from random import randint ; 'random.randint' ne le toucherait pas.

#### Palier 5 — Premier cas réussi : lancer_outil (W1) (12 min)

Écrire le premier test, le voir échouer, puis écrire le minimum de lancer_outil pour le faire passer.

**Où tu travailles :** toolwrap.py ; tests/test_toolwrap.py

**Pour comprendre**

- Le wrapper transforme le résultat du programme externe en une forme que le reste de ton code peut toujours lire.
- CompletedProcess représente un programme terminé : returncode, stdout et stderr. Le mock permet d’en fournir un sans lancer le programme.

**Exemple de résultat attendu**

Ce que tu donnes :

```text
lancer_outil(["echo", "ok"], 2), avec le résultat simulé de W1.
```

Ce que tu dois obtenir :

```text
{"returncode": 0, "stdout": "ok", "stderr": "", "erreur": None}
```

Le texte "ok" est choisi par le faux du test, sans lancement réel du programme echo.

**Règles à respecter**

- Retour toujours aux quatre clés returncode, stdout, stderr et erreur.
- Succès : code 0, sorties conservées, erreur None.
- Les sorties sont des chaînes ; une sortie absente est vide.
- Une liste vide ne lance rien et rend une erreur normalisée.
- Les échecs prévus seront traités aux deux paliers suivants.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**W1 — Succès normalisé**
- Entrée : Résultat simulé : code 0, stdout « ok », stderr vide ; appel lancer_outil(['echo', 'ok'], 2)
- Résultat attendu : Dictionnaire avec returncode 0, stdout « ok », stderr vide et erreur None. Aucune exception.

**Actions dans l’ordre**

1. Crée toolwrap.py et tests/test_toolwrap.py.
2. Écris W1 : patche subprocess.run là où toolwrap l’utilise et retourne un CompletedProcess simulé (0, "ok", stderr vide).
3. Appelle lancer_outil(["echo", "ok"], 2) et compare le dictionnaire entier. Lance et comprends le rouge.
4. Crée lancer_outil(args, timeout) avec liste d’arguments, capture_output=True, text=True, délai transmis et check=False.
5. Fais passer W1, relance la suite et commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -m unittest discover -s tests -v
```

**Terminal · Relire l’état du dépôt**

```bash
git status
git diff
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add toolwrap.py tests/test_toolwrap.py
git commit -m "Ajoute lancer_outil et le cas de succès"
```

**Tu sais que c’est bon quand :** python3 -m unittest discover -s tests -v affiche W1 en ok, et git log --oneline affiche ton nouveau commit.

*Indice si tu bloques :* Le dictionnaire garde toujours les mêmes quatre clés. Le nom à patcher est celui que toolwrap.py utilise pour subprocess.run : même logique que l’exemple de mock.

#### Palier 6 — Délai dépassé et outil introuvable (W3, W4) (12 min)

Traiter deux exceptions de subprocess.run sans les laisser remonter à l’appelant.

**Où tu travailles :** toolwrap.py ; tests/test_toolwrap.py

**Pour comprendre**

- side_effect permet au mock de lever une exception au lieu de retourner une valeur.
- TimeoutExpired signale que le délai est dépassé ; FileNotFoundError que le programme à lancer est introuvable.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**W3 — Délai dépassé**
- Entrée : subprocess.run lève TimeoutExpired ; délai demandé : 2 secondes
- Résultat attendu : returncode None et erreur non vide qui mentionne le délai ; le timeout de 2 secondes est bien transmis à subprocess.run.

**W4 — Outil introuvable**
- Entrée : subprocess.run lève FileNotFoundError
- Résultat attendu : returncode None et erreur « outil introuvable » ou un message équivalent court ; aucune exception ne remonte.

**Actions dans l’ordre**

1. Écris W3 : le faux lève TimeoutExpired ; vérifie aussi que timeout=2 est transmis à subprocess.run.
2. Attends returncode None et une erreur mentionnant le délai.
3. Écris W4 : le faux lève FileNotFoundError ; attends returncode None et un message court « outil introuvable ».
4. Traite ces deux exceptions séparément dans lancer_outil, sans les laisser sortir.
5. Relance W1, W3 et W4 puis commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -c "import subprocess
try:
    subprocess.run(['python3', '-c', 'import time; time.sleep(3)'], timeout=1)
except subprocess.TimeoutExpired as exc:
    print('trop long, délai :', exc.timeout)"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -m unittest discover -s tests -v
```

**Terminal · Relire l’état du dépôt**

```bash
git status
git diff
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add toolwrap.py tests/test_toolwrap.py
git commit -m "Gère le délai dépassé et l’outil introuvable"
```

**Tu sais que c’est bon quand :** W1, W3 et W4 passent. Dans ces cas, aucune exception ne sort de lancer_outil.

*Indice si tu bloques :* Pour faire lever une exception à un faux, regarde le paramètre side_effect de mock.patch. Le message d’erreur doit être court et en français.

#### Palier 7 — Code de retour non nul et liste intacte (W2, W5) (12 min)

Distinguer un code de retour non nul d’une exception, et vérifier que la liste reçue arrive intacte.

**Où tu travailles :** toolwrap.py ; tests/test_toolwrap.py

**Pour comprendre**

- Un code non nul signifie que le programme a terminé en échec ; il garde tout de même ses sorties utiles.
- call_args permet de lire les arguments reçus par le mock et de vérifier l’absence de shell.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**W2 — Code de retour non nul**
- Entrée : Résultat simulé : code 3, stderr « erreur simulée »
- Résultat attendu : returncode 3 et stderr conservés ; erreur est une chaîne non vide ; aucune exception. Un code 0 n’est pas une erreur.

**W5 — Liste d’arguments intacte**
- Entrée : ['echo', 'Ana; echo piraté']
- Résultat attendu : subprocess.run reçoit exactement cette liste de deux éléments, sans shell=True (absent ou False). Le texte après le point-virgule reste dans un seul argument.

**Actions dans l’ordre**

1. Écris W2 : code 3 et stderr "erreur simulée" ; vérifie leur conservation et une erreur non vide. Code 0 doit garder erreur None.
2. Écris W5 : liste ["echo", "Ana; echo piraté"] transmise intacte, en deux éléments.
3. Vérifie shell absent ou False dans l’appel ; jamais shell=True.
4. Complète le traitement du code non nul, relance W1 à W5 puis commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -c "from unittest import mock
m = mock.Mock()
m(['echo', 'x'], shell=False)
print(m.call_args)
print(m.call_args.args, m.call_args.kwargs)"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -m unittest discover -s tests -v
```

**Terminal · Relire l’état du dépôt**

```bash
git status
git diff
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add toolwrap.py tests/test_toolwrap.py
git commit -m "Gère le code de retour non nul et vérifie la liste d’arguments"
```

**Tu sais que c’est bon quand :** python3 -m unittest discover -s tests -v affiche cinq tests OK (W1 à W5).

*Indice si tu bloques :* Le code 0 ne doit pas remplir erreur. Pour W5, lis les arguments tels que le faux les a reçus, pas une version que tu reconstruis.

#### Palier 8 — Pas de fichiers parasites : .gitignore et diff (10 min)

Ne livrer que tes fichiers, et relire le diff avant chaque commit.

**Où tu travailles :** .gitignore

**Pour comprendre**

- Python crée des caches dans __pycache__. Ils sont reconstruits automatiquement et ne font pas partie de ta source.
- .gitignore empêche Git de proposer ces fichiers non suivis ; le diff reste à relire pour choisir la livraison.

**Actions dans l’ordre**

1. Crée .gitignore avec __pycache__/ sur une ligne.
2. Relance les tests, puis vérifie que git status ne propose plus ces caches.
3. Relis le diff et commite .gitignore séparément.
4. Observe git log --oneline : chaque message décrit le changement enregistré.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
printf '__pycache__/\n' > .gitignore
```

**Terminal · Relire l’état du dépôt**

```bash
git status
git diff
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add .gitignore
git commit -m "Ignore les caches __pycache__"
```

**Terminal · Relire l’état du dépôt**

```bash
git log --oneline
```

**Tu sais que c’est bon quand :** git status ne montre plus __pycache__, et git log --oneline montre les commits de la MR1 avec des messages clairs.

*Indice si tu bloques :* Si __pycache__ apparaît encore, il a déjà été ajouté : git rm -r --cached __pycache__ le retire de l’index sans supprimer les fichiers sur disque.

#### Palier 9 — Livrer la MR1 : pull request et retour sur main (8 min)

Relire ce que tu livres, le pousser et le fusionner après ta propre vérification.

**Où tu travailles :** PR GitHub

**Pour comprendre**

- git diff montre les lignes modifiées ; git diff --staged montre celles choisies pour le prochain commit. Le diff de la MR compare toute ta branche à main.
- La demande de fusion (MR dans GitLab, PR dans GitHub) permet de relire le travail avant de l’intégrer à main.

**Actions dans l’ordre**

1. Lance la suite complète avec la commande indiquée au début de la mission.
2. Relis git status et git diff : la livraison doit contenir toolwrap.py, tests/test_toolwrap.py et .gitignore, avec les modifications nécessaires de cette mission.
3. Ajoute les fichiers par leur nom, relis git diff --staged, puis commite ce qui ne l’est pas encore.
4. Pousse feat/subprocess et ouvre la demande de fusion vers main.
5. Relis le diff dans la demande de fusion. Cette mission n’a pas encore de pipeline : la relecture et les conditions de fusion restent nécessaires.
6. Fusionne après relecture et, pour GitLab de l’école, après son autorisation.
7. Après la fusion, reviens sur main et lance git pull --ff-only avant la mission suivante.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -m unittest discover -s tests -v
```

**Terminal · Relire l’état du dépôt**

```bash
git status
git diff main --stat
```

**Terminal · Publier la branche ou ouvrir la demande de fusion**

```bash
git push -u origin feat/subprocess
gh pr create --base main --title "ToolWrap MR1 : lancer_outil" --body "Ajoute lancer_outil et les tests W1 à W5, sans outil réel."
```

**Terminal · Après la fusion : actualiser la principale**

```bash
git switch main
git pull --ff-only
```

**Tu sais que c’est bon quand :** La pull request ne contient que toolwrap.py, tests/test_toolwrap.py et .gitignore. Après fusion, main est à jour sur ta machine.

*Indice si tu bloques :* Si gh n’est pas disponible, ouvre la pull request depuis l’interface GitHub de ton dépôt. Si git push est refusé, vérifie le nom de la branche avec git branch.

**Avant de livrer**

- Les tests W1 à W5 sont découverts par unittest et passent sans outil réel, sans nmap et sans réseau.
- Aucun appel à subprocess.run n’utilise shell=True, et W5 vérifie que la liste est transmise intacte.
- lancer_outil retourne toujours les quatre clés, y compris en cas de délai dépassé ou d’outil absent.
- L’historique git log --oneline montre des commits au message clair, et la MR ne contient ni __pycache__ ni fichier non voulu.

### MR2 — feat/cli-perimetre (100 min)

Tu apprends à refuser une entrée avant tout lancement d’outil. Avance dans l’ordre des paliers et vérifie chaque résultat avant de poursuivre.

**Avant de commencer**

- Point de départ : MR1 fusionnée ; lancer_outil et W1 à W5 passent.
- Ce que tu vas produire : cli.py, tests/test_cli.py et README.md : sous-commandes, cible autorisée, logging et codes de retour.
- Pourquoi : Tu apprends à refuser une entrée avant tout lancement d’outil.
- Commande des tests depuis la racine : `python3 -m unittest discover -s tests -v`. Les cas ci-dessous sont à écrire par toi.

#### Palier 1 — Branche depuis main à jour (10 min)

Partir d’une main qui contient la MR1 fusionnée, sur une branche dédiée à la CLI.

**Où tu travailles :** Dépôt

**Pour comprendre**

- La branche principale (main) contient le travail déjà fusionné. Ta branche feat/... reçoit les changements de cette mission.
- Un dépôt « propre » n’a aucune modification en attente : git status te le confirme.

**Actions dans l’ordre**

1. Ouvre workspaces/toolwrap dans VS Code, ou Coder dans Cyber Atelier avec cwd sur « . ».
2. Vérifie que MR1 est fusionnée : toolwrap.py est présent et W1 à W5 passent.
3. Lis git status ; enregistre ton travail en cours avant de changer de branche.
4. Reviens sur main avec git switch main, mets-la à jour avec git pull --ff-only, puis crée feat/cli-perimetre. Remplace main par master si ton dépôt utilise ce nom.
5. Vérifie le nom de ta branche avec git status. Si elle existe déjà, reprends-la avec git switch sans -c.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git switch main
git pull --ff-only
git switch -c feat/cli-perimetre
```

**Terminal · Relire l’état du dépôt**

```bash
git status
ls toolwrap.py
```

**Tu sais que c’est bon quand :** git status affiche « On branch feat/cli-perimetre » et toolwrap.py est présent.

*Indice si tu bloques :* Si git pull --ff-only refuse, ta main locale a divergé. Ne tape rien d’autre : regarde d’abord git log --oneline --graph.

#### Palier 2 — Un exemple argparse : sous-commandes et aide (10 min)

Comprendre comment argparse découpe une ligne de commande en sous-commandes, avec leurs propres options.

**Où tu travailles :** calc.py (jetable)

**Pour comprendre**

- argparse transforme une liste de textes en valeurs nommées. type=int convertit un argument numérique en entier.
- Une sous-commande choisit une action, comme additionner dans l’exemple. --help décrit les arguments sans exécuter cette action.

**Éditeur · Code d’exemple à placer dans calc.py**

Éditeur : crée calc.py dans le dossier d’exemple jetable indiqué. Exécute-le au moment demandé ; ne colle pas ce code dans la console.

```python
# calc.py
import argparse

def construire_parseur():
    parseur = argparse.ArgumentParser(prog='calc')
    sous = parseur.add_subparsers(dest='commande', required=True)
    add = sous.add_parser('additionner', help='additionne deux nombres')
    add.add_argument('a', type=int)
    add.add_argument('b', type=int)
    return parseur

if __name__ == '__main__':
    print(construire_parseur().parse_args())
```

**Actions dans l’ordre**

1. Crée calc.py avec l’exemple de calculatrice dans un dossier d’essai.
2. Lance --help et repère la sous-commande additionner.
3. Lance additionner avec deux nombres ; observe commande, a et b dans l’objet retourné.
4. Repère add_subparsers, add_argument et parse_args, puis retire le fichier d’essai.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 calc.py --help
python3 calc.py additionner 2 3
```

**Tu sais que c’est bon quand :** python3 calc.py --help liste la sous-commande additionner. La seconde commande affiche un objet contenant commande='additionner'.

*Indice si tu bloques :* Si argparse affiche une erreur, la dernière ligne dit quel argument manque. Une erreur d’usage fait sortir avec le code 2 par défaut.

#### Palier 3 — Le parseur de cli.py : reseau et ad (W6, W7) (12 min)

Construire les deux sous-commandes du programme et les tester sans lancer aucun processus.

**Où tu travailles :** cli.py ; tests/test_cli.py

**Pour comprendre**

- construire_parseur prépare les règles des arguments ; parse_args les applique. En test, tu fournis une liste sans le nom du script.
- L’aide termine avec SystemExit(0) : pour W7, cette exception est le comportement attendu.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**W6 — Sous-commande reseau**
- Entrée : ['reseau', '127.0.0.1', '--port', '8000']
- Résultat attendu : Sous-commande reseau, cible 127.0.0.1, port 8000 sous forme d’entier. Sans --port, la valeur par défaut 8000 est retenue.

**W7 — Aide**
- Entrée : ['--help']
- Résultat attendu : SystemExit de code 0 ; la sortie affichée mentionne les sous-commandes reseau et ad.

**Actions dans l’ordre**

1. Crée cli.py avec construire_parseur() et main(argv).
2. Ajoute reseau : cible obligatoire, --port entier avec défaut 8000.
3. Ajoute ad : sujet users/groups/computers, --format json/text.
4. Écris W6 avec --port 8000 puis sans --port ; vérifie les champs et le type entier.
5. Écris W7 avec ["--help"] : capture l’aide, attends SystemExit de code 0 et les noms reseau et ad.
6. Essaie aussi python3 cli.py --help, relance les tests et commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 cli.py --help
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -m unittest discover -s tests -v
```

**Terminal · Relire l’état du dépôt**

```bash
git status
git diff
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add cli.py tests/test_cli.py
git commit -m "Ajoute les sous-commandes reseau et ad"
```

**Tu sais que c’est bon quand :** W6 et W7 passent, et python3 cli.py --help mentionne reseau et ad.

*Indice si tu bloques :* Pour W7, argparse écrit l’aide puis lève SystemExit. Si tu veux lire ce texte dans le test, contextlib.redirect_stdout capture ce qui est affiché.

#### Palier 4 — Valider une cible avec ipaddress (W8) (12 min)

Refuser toute cible qui n’est pas une adresse IP autorisée, sans jamais résoudre un nom.

**Où tu travailles :** cli.py ; tests/test_cli.py

**Pour comprendre**

- ipaddress lit une adresse sous forme de texte sans résoudre de nom DNS. localhost et une plage ne sont pas des adresses admises ici.
- La liste blanche contient les cibles explicitement autorisées : appartenir au loopback ne suffit pas.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**W8 — Liste blanche**
- Entrée : « 127.0.0.1 » puis « 127.0.0.2 », « 8.8.8.8 », « localhost », « 127.0.0.1/32 »
- Résultat attendu : 127.0.0.1 accepté ; les quatre autres refusés par ValueError avec un message clair en français. Aucune résolution de nom n’est tentée.

**Actions dans l’ordre**

1. Écris les cinq cas de W8 : 127.0.0.1 accepté ; 127.0.0.2, 8.8.8.8, localhost et 127.0.0.1/32 refusés.
2. Crée une constante unique de liste blanche dans cli.py, avec 127.0.0.1 seulement.
3. Écris la validation avec ipaddress puis la liste blanche. Transforme les refus en ValueError avec message français.
4. Vérifie qu’aucune résolution de nom n’est tentée, relance les tests et commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -c "import ipaddress; print(ipaddress.ip_address('192.168.1.10'))"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -c "import ipaddress; ipaddress.ip_address('bonjour')"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -m unittest discover -s tests -v
```

**Terminal · Relire l’état du dépôt**

```bash
git status
git diff
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add cli.py tests/test_cli.py
git commit -m "Valide la cible avec ipaddress et une liste blanche"
```

**Tu sais que c’est bon quand :** W8 passe : les cinq valeurs donnent exactement le résultat attendu.

*Indice si tu bloques :* La première commande affiche une adresse, la seconde lève ValueError : c’est ce comportement que tu exploites pour refuser. Le message d’erreur ne doit contenir aucune résolution de nom.

#### Palier 5 — Refus sans lancement (W9) (12 min)

Faire en sorte qu’une cible refusée ne lance jamais l’outil, et renvoyer le code 2.

**Où tu travailles :** cli.py ; tests/test_cli.py

**Pour comprendre**

- Valider avant de lancer permet de refuser une cible sans exécuter d’outil.
- redirect_stderr capture le message d’erreur ; assert_not_called vérifie que le faux n’a jamais été utilisé.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**W9 — Cible refusée sans lancement**
- Entrée : ['reseau', '8.8.8.8'] avec lancer_outil remplacé par un faux
- Résultat attendu : main retourne 2, un message d’erreur est écrit sur stderr et lancer_outil n’est jamais appelé.

**Actions dans l’ordre**

1. Écris W9 avec main(["reseau", "8.8.8.8"]) et le faux cli.lancer_outil.
2. Capture stderr ; attends retour 2, message d’erreur et zéro appel du faux.
3. Dans main, appelle la validation avant lancer_outil et traite le refus à ce niveau.
4. Relance W1 à W9 et commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -c "import io, contextlib, sys
buf = io.StringIO()
with contextlib.redirect_stderr(buf):
    print('erreur simulée', file=sys.stderr)
print(repr(buf.getvalue()))"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -m unittest discover -s tests -v
```

**Terminal · Relire l’état du dépôt**

```bash
git status
git diff
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add cli.py tests/test_cli.py
git commit -m "Refuse une cible hors liste blanche avant tout lancement"
```

**Tu sais que c’est bon quand :** W9 passe : main renvoie 2 et le faux n’a jamais été appelé.

*Indice si tu bloques :* Vérifie l’absence d’appel avec assert_not_called(). Le patch vise le nom utilisé dans cli.py.

#### Palier 6 — Codes de retour et logging (W10) (10 min)

Traduire le résultat de l’outil en code 0 ou 1, et tracer la commande lancée sur stderr.

**Où tu travailles :** cli.py ; tests/test_cli.py

**Pour comprendre**

- logging écrit des traces de déroulement et d’erreur. Ici, elles vont sur stderr pour laisser le résultat sur stdout.
- Une liste dans side_effect donne plusieurs réponses successives au mock.

**Règles à respecter**

- 0 : outil réussi.
- 1 : outil en échec, code non nul ou erreur renseignée.
- 2 : arguments invalides ou cible refusée.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**W10 — Codes de retour de main**
- Entrée : ['ad', 'users'] avec lancer_outil simulé : une fois code 0, une fois code 3 (ou erreur)
- Résultat attendu : main retourne 0 dans le premier cas et 1 dans le second. Le sujet users est transmis à l’outil.

**Actions dans l’ordre**

1. Écris W10 : pour main(["ad", "users"]), le faux rend d’abord un succès puis un code 3 ou une erreur.
2. Vérifie retour 0 puis 1, et le sujet users transmis à l’outil.
3. Complète main et le logging sur stderr, puis relance W1 à W10.
4. Commite quand la suite passe.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -c "import logging, sys
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(levelname)s %(message)s')
logging.info('recette lancée : %s', 'ouvrir fichier')"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -m unittest discover -s tests -v
```

**Terminal · Relire l’état du dépôt**

```bash
git status
git diff
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add cli.py tests/test_cli.py
git commit -m "Ajoute les codes de retour de main et le logging"
```

**Tu sais que c’est bon quand :** W1 à W10 passent. Avec le faux, main(['ad', 'users']) renvoie 0 puis 1.

*Indice si tu bloques :* Le dictionnaire renvoyé par lancer_outil a toujours quatre clés : c’est sur returncode et erreur que tu décides du code à renvoyer.

#### Palier 7 — Conflit de fusion guidé (branches jetables) (12 min)

Provoquer puis résoudre un conflit de fusion, dans des branches qui ne seront jamais livrées.

**Où tu travailles :** README.md dans les branches essai/

**Pour comprendre**

- Git signale un conflit quand deux branches changent la même zone du fichier. Les marqueurs contiennent les versions concurrentes.
- L’exercice se fait sur deux branches locales d’essai, sans toucher feat/cli-perimetre.

**Actions dans l’ordre**

1. Commite d’abord le travail de ta vraie branche ; git status doit être propre.
2. Depuis main, crée essai/conflit-a et essai/conflit-b. Écris une ligne différente dans README.md et commite dans chacune.
3. Fusionne la seconde dans la première ; observe le conflit attendu, qu’il s’agisse d’un fichier nouveau ou déjà présent.
4. Choisis le texte final, retire les trois marqueurs, git add puis commit.
5. Vérifie README sans marqueurs et le graphe avant de quitter l’essai.
6. Reviens sur main, supprime uniquement ces branches jetables puis reprends feat/cli-perimetre.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git switch main
git pull --ff-only
git switch -c essai/conflit-a
printf 'Titre : version A\n' > README.md
git add README.md
git commit -m "Essai conflit : version A"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git switch main
git switch -c essai/conflit-b
printf 'Titre : version B\n' > README.md
git add README.md
git commit -m "Essai conflit : version B"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git merge essai/conflit-a
```

**Terminal · Relire l’état du dépôt**

```bash
git status
cat README.md
```

**Terminal · Commande à lancer au moment indiqué**

```bash
# Dans VS Code, ouvre README.md : garde une seule ligne (par exemple « Titre : version finale »), supprime les marqueurs, puis :
git add README.md
git commit -m "Résout le conflit de titre"
```

**Terminal · Après la fusion : actualiser la principale**

```bash
git switch main
git branch -D essai/conflit-a essai/conflit-b
git branch
```

**Tu sais que c’est bon quand :** Avant de quitter la branche d’essai, git log --oneline --graph montre la fusion et README.md n’a plus de marqueurs. Après retour sur main et nettoyage, git branch ne montre plus les deux branches essai/conflit-*. Le résultat de l’exercice reste dans la branche jetable jusqu’à sa suppression.

*Indice si tu bloques :* Si Git refuse la fusion avant le conflit, tu as sans doute des modifications non commitées : lance git status d’abord. Pour annuler une fusion en cours, git merge --abort revient à l’état d’avant.

#### Palier 8 — Rebase guidé sur une base qui a avancé (12 min)

Poser des commits au-dessus d’une base mise à jour, et lire l’historique avant de pousser.

**Où tu travailles :** Historique dans les branches essai/

**Pour comprendre**

- Un rebase rejoue tes commits sur une base plus récente. Cet essai utilise une copie de ta branche.
- Sur une branche déjà poussée, le rebase change l’historique partagé : il faut prévenir avant un éventuel push forcé.

**Actions dans l’ordre**

1. Depuis main, crée essai/base-evoluee, ajoute le changement d’essai et commite-le.
2. Crée essai/rebase depuis feat/cli-perimetre ; rebase cette copie sur essai/base-evoluee.
3. En cas de conflit, lis le message, corrige, git add puis rebase --continue. rebase --abort annule l’essai.
4. Observe le graphe, lance les tests de la copie, puis reviens sur feat/cli-perimetre et supprime les branches d’essai.
5. Pour la vraie livraison, si main a avancé, applique ce principe avant le push ; ne réécris pas une branche déjà partagée sans prévenir.

**Terminal · Relire l’état du dépôt**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git status
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git switch -c essai/rebase feat/cli-perimetre
git switch -c essai/base-evoluee main
printf 'Note : base évoluée\n' > NOTE_BASE.txt
git add NOTE_BASE.txt
git commit -m "Essai : la base avance"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git switch essai/rebase
git rebase essai/base-evoluee
```

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs. Remplace CHEMIN_DU_FICHIER par le chemin indiqué par git status, avant de lancer git add.

```bash
# en cas de conflit : corrige le fichier indiqué, puis
git add CHEMIN_DU_FICHIER
git rebase --continue
```

**Terminal · Relire l’état du dépôt**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git log --oneline --graph
python3 -m unittest discover -s tests -v
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git switch feat/cli-perimetre
git branch -D essai/rebase essai/base-evoluee
git branch
```

**Terminal · Commande à lancer au moment indiqué**

```bash
# Pour la vraie MR2, si main a avancé :
git switch main
git pull --ff-only
git switch feat/cli-perimetre
git rebase main
```

**Tu sais que c’est bon quand :** git log --oneline --graph montre tes commits posés au-dessus de la base, les tests passent dans la copie, et les branches jetables ont disparu.

*Indice si tu bloques :* Un rebase sans conflit est normal ici : lis quand même le graphe. Ne supprime une branche jetable qu’une fois la copie vérifiée.

#### Palier 9 — Livrer la MR2 : README, PR et fusion (10 min)

Documenter les codes, la liste blanche et les tests, puis livrer la MR après ta relecture.

**Où tu travailles :** README.md ; PR GitHub

**Pour comprendre**

- git diff montre les lignes modifiées ; git diff --staged montre celles choisies pour le prochain commit. Le diff de la MR compare toute ta branche à main.
- La demande de fusion (MR dans GitLab, PR dans GitHub) permet de relire le travail avant de l’intégrer à main.

**Actions dans l’ordre**

1. Lance la suite complète avec la commande indiquée au début de la mission.
2. Avant de livrer, ajoute au README une section CLI : codes 0/1/2, cible unique 127.0.0.1 et commande des tests. Vérifie qu’aucun texte d’essai Git ne subsiste.
3. Relis git status et git diff : la livraison doit contenir cli.py, tests/test_cli.py et README.md, avec les modifications nécessaires de cette mission.
4. Ajoute les fichiers par leur nom, relis git diff --staged, puis commite ce qui ne l’est pas encore.
5. Pousse feat/cli-perimetre et ouvre la demande de fusion vers main.
6. Relis le diff dans la demande de fusion. Cette mission n’a pas encore de pipeline : la relecture et les conditions de fusion restent nécessaires.
7. Fusionne après relecture et, pour GitLab de l’école, après son autorisation.
8. Après la fusion, reviens sur main et lance git pull --ff-only avant la mission suivante.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -m unittest discover -s tests -v
python3 cli.py --help
```

**Terminal · Relire l’état du dépôt**

```bash
git status
git diff main --stat
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add README.md
git commit -m "Documente la CLI, les codes de sortie et la liste blanche"
```

**Terminal · Publier la branche ou ouvrir la demande de fusion**

```bash
git push -u origin feat/cli-perimetre
gh pr create --base main --title "ToolWrap MR2 : CLI et périmètre" --body "Ajoute la CLI argparse, la liste blanche ipaddress et les tests W6 à W10, sans outil réel."
```

**Terminal · Après la fusion : actualiser la principale**

```bash
git switch main
git pull --ff-only
```

**Tu sais que c’est bon quand :** La pull request ne contient que cli.py, tests/test_cli.py et README.md. Après fusion, main est à jour sur ta machine.

*Indice si tu bloques :* Si la PR contient une ligne « Titre : version » venue de l’exercice de conflit, elle a été commitée par erreur sur feat/cli-perimetre : git log --oneline te montrera le commit à retirer.

**Avant de livrer**

- python3 -m unittest discover -s tests passe avec W1 à W10, sans outil réel.
- --help fonctionne ; les codes 0, 1 et 2 ainsi que la liste blanche sont documentés dans le README.
- Un refus de cible n’appelle jamais lancer_outil.
- Le conflit a été résolu puis la branche jetable supprimée ; après rebase, git log --oneline --graph montre un historique lisible par rapport à la branche principale.

### MR3 — feat/parsing (70 min)

Tu transformes les sorties d’outils en données communes, puis fais les démonstrations séparément. Avance dans l’ordre des paliers et vérifie chaque résultat avant de poursuivre.

**Avant de commencer**

- Point de départ : MR2 fusionnée ; la CLI est disponible et W1 à W10 passent.
- Ce que tu vas produire : parsing.py, tests/test_parsing.py, fixtures et README.md : lecture XML/JSON et rapport texte.
- Pourquoi : Tu transformes les sorties d’outils en données communes, puis fais les démonstrations séparément.
- Commande des tests depuis la racine : `python3 -m unittest discover -s tests -v`. Les cas ci-dessous sont à écrire par toi.

#### Palier 1 — Branche et fixtures copiées (6 min)

Préparer la branche de la MR3 et copier les fixtures : les originaux restent en lecture seule.

**Où tu travailles :** Dépôt ; fixtures/

**Pour comprendre**

- La branche principale (main) contient le travail déjà fusionné. Ta branche feat/... reçoit les changements de cette mission.
- Un dépôt « propre » n’a aucune modification en attente : git status te le confirme.

**Actions dans l’ordre**

1. Ouvre workspaces/toolwrap dans VS Code, ou Coder dans Cyber Atelier avec cwd sur « . ».
2. Vérifie que MR2 est fusionnée et que W1 à W10 passent.
3. Lis git status ; enregistre ton travail en cours avant de changer de branche.
4. Reviens sur main avec git switch main, mets-la à jour avec git pull --ff-only, puis crée feat/parsing. Remplace main par master si ton dépôt utilise ce nom.
5. Copie les fixtures nmap et adsim dans ton dépôt. Ouvre open_8000.xml, closed_8000.xml et mixed.xml : repère hôte, portid, protocole et état.
6. Vérifie le nom de ta branche avec git status. Si elle existe déjà, reprends-la avec git switch sans -c.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git switch main
git pull --ff-only
git switch -c feat/parsing
```

**Terminal · Commande à lancer au moment indiqué**

Terminal de ton Mac, depuis workspaces/toolwrap. Dans le conteneur, remplace ../../fixtures par /app/fixtures ; garde le reste de la commande. Les copies vont dans ton dépôt.

```bash
mkdir -p fixtures && cp -R ../../fixtures/nmap fixtures/ && cp -R ../../fixtures/adsim fixtures/ && chmod -R u+w fixtures
```

**Terminal · Relire l’état du dépôt**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git status
```

**Tu sais que c’est bon quand :** git status affiche « On branch feat/parsing » et les fichiers copiés apparaissent sous fixtures/.

*Indice si tu bloques :* Depuis workspaces/toolwrap, le projet est deux dossiers plus haut : d’où ../... Les fixtures sont des données de test : tu les commiteras avec les tests.

#### Palier 2 — Exemple ElementTree sans rapport (8 min)

Lire un document XML : racine, enfants, attributs, et erreur de syntaxe.

**Où tu travailles :** Terminal : exemple XML

**Pour comprendre**

- XML représente un arbre de balises. Un attribut, comme nom="pain", est une valeur attachée à une balise.
- ElementTree.fromstring lit le texte ; findall cherche les éléments ; get lit un attribut. Un texte XML cassé lève ParseError.

**Actions dans l’ordre**

1. Lance l’exemple du panier fourni : observe pain 2 puis lait 1.
2. Repère la racine, les enfants article et leurs attributs. findall("article") cherche ici les enfants directs.
3. Observe l’erreur pour le XML mal formé et le except ParseError.
4. Ouvre à nouveau la fixture nmap et repère les mêmes éléments de structure.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -c "import xml.etree.ElementTree as ET
racine = ET.fromstring('<panier><article nom=\"pain\" prix=\"2\"/><article nom=\"lait\" prix=\"1\"/></panier>')
for article in racine.findall('article'):
    print(article.get('nom'), article.get('prix'))"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -c "import xml.etree.ElementTree as ET
try:
    ET.fromstring('<panier><article>')
except ET.ParseError as exc:
    print('erreur :', exc)"
```

**Tu sais que c’est bon quand :** Tu vois « pain 2 » puis « lait 1 », puis une ligne « erreur : ... » pour le XML cassé.

*Indice si tu bloques :* Si findall ne trouve rien, vérifie le nom de la balise. Pour descendre plus bas dans l’arbre, la documentation d’ElementTree explique la syntaxe des chemins.

#### Palier 3 — Un port ouvert dans le XML (W11) (8 min)

Transformer un port de nmap en élément commun, en écrivant le test sur fixture avant le code.

**Où tu travailles :** parsing.py ; tests/test_parsing.py

**Pour comprendre**

- Parser signifie lire un format structuré pour en extraire des données. Le parseur ne lance pas nmap.
- __file__ désigne le fichier de test ; un chemin construit depuis lui ne dépend pas du dossier où tu lances la commande.

**Exemple de résultat attendu**

Ce que tu donnes :

```text
Fixture open_8000.xml.
```

Ce que tu dois obtenir :

```text
items : un élément pour 8000/tcp, statut open ; erreur : None.
```

Ce sont des données lues depuis la fixture ; aucun scan réel n’est nécessaire.

**Règles à respecter**

- Chaque parseur retourne {"items": [...], "erreur": ...}.
- Chaque élément possède source, type, nom, statut et details.
- Pour nmap : source nmap, nom port/protocole et statut fourni par le XML.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**W11 — XML ouvert**
- Entrée : Fixture open_8000.xml
- Résultat attendu : Un élément : source nmap, nom « 8000/tcp », statut « open », erreur None.

**Actions dans l’ordre**

1. Crée parsing.py et tests/test_parsing.py ; construis le chemin des fixtures à partir de __file__.
2. Écris W11 avec open_8000.xml : un élément, source nmap, nom "8000/tcp", statut "open", erreur None.
3. Lance, puis écris le parseur XML avec un élément normalisé par port de l’hôte.
4. Compare aussi la forme du résultat au contrat, relance W11 et commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -m unittest discover -s tests -v
```

**Terminal · Relire l’état du dépôt**

```bash
git status
git diff
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add parsing.py tests/test_parsing.py
git commit -m "Analyse le XML nmap pour un port ouvert"
```

**Tu sais que c’est bon quand :** W11 passe, et le commit contient parsing.py et tests/test_parsing.py.

*Indice si tu bloques :* Le statut se lit sur l’élément state de chaque port. La structure que tu as ouverte au premier palier est la meilleure documentation : relis-la si un nom ne sort pas.

#### Palier 4 — Ordre des ports et XML cassé (W12, W13) (8 min)

Garder l’ordre du fichier, et ne jamais laisser une erreur d’analyse remonter.

**Où tu travailles :** parsing.py ; tests/test_parsing.py

**Pour comprendre**

- L’ordre des ports dans le XML reste l’ordre de la liste items. Trier cette liste changerait le contrat.
- Une erreur de lecture est rendue dans erreur ; elle ne s’échappe pas sous forme d’exception.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**W12 — XML mixte, ordre conservé**
- Entrée : Fixture mixed.xml, qui contient trois ports : open, closed et filtered
- Résultat attendu : Trois éléments dans l’ordre du fichier, de statuts open, closed puis filtered ; erreur None.

**W13 — XML cassé**
- Entrée : Fixture broken.xml
- Résultat attendu : Aucune exception ; items vide ; erreur est une chaîne non vide.

**Actions dans l’ordre**

1. Écris W12 : mixed.xml donne open, closed, filtered dans l’ordre du fichier et erreur None.
2. Écris W13 : broken.xml donne items vide et erreur non vide, sans exception.
3. Complète la boucle de ports et le traitement de ParseError, en gardant toujours les deux clés de retour.
4. Relance W11 à W13 avec le reste de la suite, puis commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -m unittest discover -s tests -v
```

**Terminal · Relire l’état du dépôt**

```bash
git status
git diff
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add parsing.py tests/test_parsing.py
git commit -m "Garde l’ordre des ports et gère le XML cassé"
```

**Tu sais que c’est bon quand :** W11, W12 et W13 passent.

*Indice si tu bloques :* Un XML mal formé lève ParseError dès l’analyse. Rattrape-la autour de l’analyse elle-même, et non dans la boucle qui lit les ports.

#### Palier 5 — JSON adsim et format commun (W14) (8 min)

Lire un JSON avec json.loads, et définir un format commun pour nmap et adsim.

**Où tu travailles :** parsing.py ; tests/test_parsing.py

**Pour comprendre**

- json.loads transforme du texte JSON en dictionnaires et listes Python. Le champ items contient ici les utilisateurs ; count indique leur nombre.
- Normaliser permet d’exposer les mêmes clés pour des outils aux formats différents.

**Règles à respecter**

- source : adsim.
- statut : actif si enabled est vrai, inactif sinon.
- Les groupes restent dans details, y compris une liste vide.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**W14 — JSON adsim valide**
- Entrée : Fixture users.json
- Résultat attendu : Nombre d’éléments égal au champ count du fichier ; statut « actif » ou « inactif » selon enabled ; groupes conservés, liste vide si l’utilisateur n’a aucun groupe.

**Actions dans l’ordre**

1. Ouvre users.json et repère count, items, name, enabled et groups.
2. Écris W14 : nombre d’éléments égal à count, statut selon enabled et groupes conservés.
3. Écris le parseur adsim en utilisant les mêmes cinq clés par élément que pour nmap.
4. Place les groupes dans details, avec liste vide pour un utilisateur sans groupe.
5. Relance la suite puis commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -c "import json
donnees = json.loads('{\"fruits\": [\"pomme\", \"poire\"], \"count\": 2}')
print(donnees['count'], donnees['fruits'][0])"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -m unittest discover -s tests -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add parsing.py tests/test_parsing.py
git commit -m "Analyse le JSON adsim des utilisateurs"
```

**Tu sais que c’est bon quand :** W14 passe, et les éléments adsim ont les mêmes clés que les éléments nmap.

*Indice si tu bloques :* Le nombre attendu est écrit dans le fichier (champ count) : ton test le compare à cette valeur, il ne la recalcule pas.

#### Palier 6 — JSON invalide (W15) et statuts documentés (8 min)

Capturer une erreur de JSON et documenter les valeurs de statut.

**Où tu travailles :** parsing.py ; tests/test_parsing.py

**Pour comprendre**

- JSONDecodeError signale un texte JSON invalide. Il faut la traiter dans le parseur pour garder le retour normalisé.
- Les statuts viennent de deux domaines : états de ports nmap et activité de comptes adsim.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**W15 — JSON invalide**
- Entrée : Fixture broken.json
- Résultat attendu : items vide ; erreur non vide ; aucune exception.

**Actions dans l’ordre**

1. Écris W15 avec broken.json : items [], erreur non vide et aucune exception.
2. Attrape JSONDecodeError dans le parseur JSON ; garde la même forme de retour que pour le XML cassé.
3. Documente open, closed, filtered, actif et inactif dans une section Statuts du README.
4. Relance W11 à W15 et commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -c "import json
try:
    json.loads('{\"count\": ')
except json.JSONDecodeError as exc:
    print('erreur :', exc)"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -m unittest discover -s tests -v
```

**Terminal · Relire l’état du dépôt**

```bash
git status
git diff
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add parsing.py tests/test_parsing.py README.md
git commit -m "Gère le JSON invalide et documente les statuts"
```

**Tu sais que c’est bon quand :** W11 à W15 passent, et README.md contient la section Statuts.

*Indice si tu bloques :* Rattrape JSONDecodeError autour de json.loads, pas autour de la lecture du reste du fichier.

#### Palier 7 — Rapport texte (W16) (8 min)

Afficher une ligne par élément, des totaux cohérents, et un message clair pour une liste vide.

**Où tu travailles :** parsing.py ; tests/test_parsing.py

**Pour comprendre**

- Le rapport transforme les éléments normalisés en texte et compte leurs statuts ; il ne relance pas les outils.
- Retourner une chaîne permet de la tester ; main s’occupe de l’afficher sur stdout.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**W16 — Rapport texte**
- Entrée : Trois éléments normalisés (deux open, un closed), puis une liste vide
- Résultat attendu : Une ligne par élément dans l’ordre, puis un total cohérent (3 éléments, 2 open, 1 closed) ; pour la liste vide, un message indique qu’aucun élément n’a été trouvé.

**Actions dans l’ordre**

1. Observe l’exemple de boucle et de compteur fourni.
2. Écris W16 avec trois éléments, deux open et un closed : ligne par élément dans l’ordre, puis total 3 / open 2 / closed 1.
3. Ajoute le cas vide : message indiquant qu’aucun élément n’a été trouvé.
4. Crée la fonction de rapport sans print, puis branche son affichage dans main.
5. Relance W1 à W16 et commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -c "items = [{'nom': 'a', 'statut': 'open'}, {'nom': 'b', 'statut': 'closed'}, {'nom': 'c', 'statut': 'open'}]
for item in items:
    print(item['nom'], item['statut'])
print('total :', len(items))
print('ouverts :', sum(1 for i in items if i['statut'] == 'open'))"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -m unittest discover -s tests -v
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add parsing.py tests/test_parsing.py
git commit -m "Ajoute le rapport texte"
```

**Tu sais que c’est bon quand :** W1 à W16 passent : python3 -m unittest discover -s tests -v se termine par un total sans échec.

*Indice si tu bloques :* Un message pour une liste vide est une phrase, pas une ligne vide. Vérifie que tes totaux sont calculés à partir de la liste et non écrits en dur.

#### Palier 8 — Démonstrations réelles, hors tests (D1 à D3) (8 min)

Passer les vraies sorties de nmap et d’adsim dans ton code, sans que ces démonstrations entrent dans les tests.

**Où tu travailles :** Outils réels dans Docker

**Pour comprendre**

- Les démonstrations lancent les outils réels ; les tests restent fondés sur mocks et fixtures.
- Pour vérifier un timeout réel, l’outil doit attendre plus longtemps que le délai autorisé : --delay le rend reproductible avec adsim.

**Actions dans l’ordre**

1. Les commandes proposées se lancent sur le Mac depuis cyberatelier, qui contient compose.yaml et workspaces/toolwrap. Elles utilisent Docker pour l’outil réel et ton wrapper du Mac pour le pilotage.
2. D1 : active le labo dans Docker. Lance nmap via lancer_outil sur 127.0.0.1:8000 seulement, puis parse sa sortie XML. Attends open ; compare avec le labo arrêté.
3. D2 : lance adsim users en JSON via lancer_outil et parse sa sortie ; le nombre d’éléments égale count.
4. D3 : lance adsim avec --fail et observe l’erreur normalisée pour le code 3.
5. Pour le timeout de D3, utilise --delay 1 avec un délai de 0,01 seconde ; attends une erreur de délai, sans trace Python.
6. Garde ces appels hors des tests et note les résultats dans le bilan.

**Terminal · D1 : nmap via ton wrapper**

Terminal du Mac, depuis cyberatelier (le dossier de compose.yaml). Le wrapper est importé depuis workspaces/toolwrap ; l’outil réel est exécuté dans Docker. Fais les observations demandées entre les commandes.

```bash
python3 -c "import sys; sys.path.insert(0, 'workspaces/toolwrap'); from toolwrap import lancer_outil; print(lancer_outil(['docker', 'compose', 'exec', '-T', 'atelier', 'nmap', '-sT', '-p', '8000', '-oX', '-', '127.0.0.1'], 30))"
```

**Terminal · D2 : adsim en JSON via ton wrapper**

```bash
python3 -c "import sys; sys.path.insert(0, 'workspaces/toolwrap'); from toolwrap import lancer_outil; print(lancer_outil(['docker', 'compose', 'exec', '-T', 'atelier', 'python', '/app/tools/adsim.py', 'users', '--format', 'json'], 30))"
```

**Terminal · D3 : échec simulé avec --fail**

```bash
python3 -c "import sys; sys.path.insert(0, 'workspaces/toolwrap'); from toolwrap import lancer_outil; print(lancer_outil(['docker', 'compose', 'exec', '-T', 'atelier', 'python', '/app/tools/adsim.py', 'users', '--fail'], 30))"
```

**Terminal · D3 : délai d’une seconde, timeout de 0,01 seconde**

```bash
python3 -c "import sys; sys.path.insert(0, 'workspaces/toolwrap'); from toolwrap import lancer_outil; print(lancer_outil(['docker', 'compose', 'exec', '-T', 'atelier', 'python', '/app/tools/adsim.py', 'users', '--delay', '1'], 0.01))"
```

**Tu sais que c’est bon quand :** D1 donne le port 8000 en open quand le labo tourne. D2 donne un nombre d’éléments égal à count. D3 donne une erreur normalisée pour le code 3 et une erreur de timeout, sans trace Python.

*Indice si tu bloques :* Commande vide ou « no such service » : vérifie depuis le dossier du projet avec docker compose ps. Port closed : démarre le labo depuis l’interface. Les démonstrations n’ajoutent rien aux tests : garde-les dans le bilan.

#### Palier 9 — Bilan du README et livraison de la MR3 (8 min)

Finir le README avec un bilan honnête, puis livrer la MR3 sans y mettre les fichiers de démonstration.

**Où tu travailles :** README.md ; PR GitHub

**Pour comprendre**

- git diff montre les lignes modifiées ; git diff --staged montre celles choisies pour le prochain commit. Le diff de la MR compare toute ta branche à main.
- La demande de fusion (MR dans GitLab, PR dans GitHub) permet de relire le travail avant de l’intégrer à main.

**Actions dans l’ordre**

1. Lance la suite complète avec la commande indiquée au début de la mission.
2. Complète le README : périmètre, codes de sortie, tests, démonstrations séparées et bilan (ce que les tests prouvent, ce que les démos montrent, ce qui reste à faire). Ne livre pas demo_*.xml ou demo_*.json.
3. Relis git status et git diff : la livraison doit contenir parsing.py, les tests, README.md et les fixtures d’origine nécessaires, avec les modifications nécessaires de cette mission.
4. Ajoute les fichiers par leur nom, relis git diff --staged, puis commite ce qui ne l’est pas encore.
5. Pousse feat/parsing et ouvre la demande de fusion vers main.
6. Relis le diff dans la demande de fusion. Cette mission n’a pas encore de pipeline : la relecture et les conditions de fusion restent nécessaires.
7. Fusionne après relecture et, pour GitLab de l’école, après son autorisation.
8. Après la fusion, reviens sur main et lance git pull --ff-only avant la mission suivante.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -m unittest discover -s tests -v
```

**Terminal · Relire l’état du dépôt**

```bash
git status
git diff main --stat
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add README.md parsing.py tests/test_parsing.py fixtures/nmap/open_8000.xml fixtures/nmap/closed_8000.xml fixtures/nmap/mixed.xml fixtures/nmap/broken.xml fixtures/adsim/users.json fixtures/adsim/groups.json fixtures/adsim/computers.json fixtures/adsim/broken.json
git commit -m "Termine le README et le bilan de la MR3"
```

**Terminal · Publier la branche ou ouvrir la demande de fusion**

```bash
git push -u origin feat/parsing
gh pr create --base main --title "ToolWrap MR3 : parseurs et rapport" --body "Ajoute l’analyse XML nmap, l’analyse JSON adsim, le rapport texte et les tests W11 à W16 sur fixtures."
```

**Terminal · Après la fusion : actualiser la principale**

```bash
git switch main
git pull --ff-only
```

**Tu sais que c’est bon quand :** La pull request ne contient ni demo_reel.xml ni demo_users.json. Le README distingue les tests, les démonstrations et les limites.

*Indice si tu bloques :* Si git status montre les fichiers demo_*, c’est normal : ils restent hors commit. Tu peux les ajouter au .gitignore si ça te gêne.

**Démonstrations manuelles (hors CI)**

Ces essais utilisent le laboratoire ou les outils réels. Ils sont séparés des tests obligatoires.

**D1 — nmap réel sur le labo**
- Entrée : Labo HTTP démarré avec son bouton sur 127.0.0.1:8000 ; lancer_outil sur nmap -sT -p 8000 -oX - 127.0.0.1, puis sortie XML passée au parseur
- Résultat attendu : Le port 8000 est au statut open. Si le labo est arrêté, le résultat doit être différent (closed ou erreur) : explique la différence dans le bilan.

**D2 — adsim réel, sortie JSON**
- Entrée : python /app/tools/adsim.py users --format json passé par lancer_outil, puis sortie passée au parseur
- Résultat attendu : Éléments normalisés, erreur None, nombre égal au champ count de la sortie réelle.

**D3 — Erreurs réelles d’adsim**
- Entrée : adsim avec --fail (code 3), puis adsim avec un délai supérieur au timeout de lancer_outil
- Résultat attendu : Le code 3 est normalisé en erreur sans trace Python ; le délai dépassé est normalisé en erreur de timeout.

**Avant de livrer**

- Les tests W11 à W16 passent avec les fixtures seules, sans nmap, sans réseau et sans adsim.
- Un XML ou un JSON cassé ne fait jamais planter le programme : il produit une erreur normalisée.
- Les démonstrations D1 à D3 sont exécutées dans le conteneur, hors unittest discover, et leurs sorties réelles sont consignées dans le README ou le bilan.
- Le bilan distingue tests unitaires (fixtures et mocks), démonstrations réelles (nmap sur le labo, adsim fictif) et limites.

<!-- END GENERATED EXERCISES -->

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
