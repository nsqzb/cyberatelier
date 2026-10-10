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

Chaque mission construit une partie du projet. Commence par « Avant de commencer », puis avance palier par palier. Les durées sont des repères : prends le temps de comprendre chaque résultat.

1. Lis l’objectif et les fichiers concernés. Un fichier indiqué comme « à créer » n’est pas fourni : c’est toi qui l’écris.
2. Les cartes de tests donnent l’entrée et le résultat attendu. Écris les tests correspondants dans le fichier indiqué ; cocher un palier ne les exécute pas. Avec unittest, « Ran 0 tests » signifie qu’aucun test n’a été exécuté : ce n’est pas une validation. Un cas décrit peut contenir plusieurs valeurs ; le nombre de méthodes Python n’est donc pas forcément le nombre d’identifiants.
3. Suis les actions numérotées. Les blocs Python se placent dans l’éditeur ; les commandes se lancent au moment demandé. Relis les blocs Git : des modifications et des actions dans GitHub/GitLab peuvent être nécessaires entre deux commandes.
4. Vérifie le résultat indiqué avant de poursuivre. Un échec attendu (phase rouge, argument refusé ou conflit volontaire) est expliqué dans le palier.
5. Si tu bloques, lis la dernière ligne de l’erreur, compare l’entrée et l’attendu, puis ouvre l’indice. Fais un petit changement et relance.

### Le bon endroit pour chaque action

Sur ton Mac, ouvre `workspaces/toolwrap` dans VS Code. Dans Cyber Atelier, utilise l’éditeur et la console de **Coder**, avec `cwd` sur `.` (la racine du dépôt). Fais la préparation de **Environnement** avant MR1 ; la mission crée ensuite sa branche.

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

- Une branche est une ligne de travail séparée de main : main ne bouge pas tant que tu ne fusionnes pas.

**Actions dans l’ordre**

1. Ouvre le dossier workspaces/toolwrap dans VS Code, puis un terminal (Terminal > New Terminal).
2. Si git status répond « not a git repository », fais d’abord « Cloner le dépôt » dans l’onglet Environnement. Clone directement dans workspaces/toolwrap avec le point final ; n’imbrique pas un second workspaces/toolwrap dans ce dossier.
3. Vérifie que python3 et git répondent, puis crée la branche de la MR1 depuis main à jour.

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

**Actions dans l’ordre**

1. Une liste d’arguments : le premier élément est le programme, les suivants sont ses arguments. Python ne les interprète pas : un point-virgule ou un guillemet reste une simple lettre.
2. Le shell, lui, interprète « ; » comme un séparateur de commandes. C’est ce que tu évites en ne passant jamais une chaîne à un shell avec une entrée utilisateur.
3. Lis la documentation de subprocess.run : retiens seulement capture_output, text et returncode.
4. Lance l’exemple ci-dessous. Il est sans rapport avec ton outil : il lance Python lui-même.

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

**Actions dans l’ordre**

1. adsim est un simulateur fictif, sans réseau. Il tourne dans le conteneur : depuis ton Mac, tu le lances avec docker compose exec, depuis le dossier du projet Cyber Atelier (celui qui contient compose.yaml), et non depuis workspaces/toolwrap.
2. Lance les trois commandes ci-dessous et note, pour chacune, le code de sortie et le canal du message (stdout ou stderr).
3. Code 0 : succès. Code 3 : échec simulé par --fail. Code 2 : argument inconnu, refusé avant tout traitement.
4. Garde stderr visible : le message d’argument inconnu fait partie de l’observation. Si tu es déjà dans la console du conteneur, lance python3 /app/tools/adsim.py directement, sans docker compose exec.

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

- Un mock est un faux objet qui remplace une fonction pendant un test. unittest.mock.patch le pose le temps du bloc with.

**Actions dans l’ordre**

1. Règle essentielle : on patche le nom tel que le module qui appelle la fonction le voit, pas là où la fonction est définie.
2. Crée l’exemple dans un dossier jetable hors du dépôt, lance-le, puis supprime-le.
3. assert_called_once_with vérifie les arguments reçus par le faux.

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

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**W1 — Succès normalisé**
- Entrée : Résultat simulé : code 0, stdout « ok », stderr vide ; appel lancer_outil(['echo', 'ok'], 2)
- Résultat attendu : Dictionnaire avec returncode 0, stdout « ok », stderr vide et erreur None. Aucune exception.

**Actions dans l’ordre**

1. Crée toolwrap.py (le wrapper) et tests/test_toolwrap.py (les tests). Les tests vivent dans tests/ et importent toolwrap.
2. Écris le test W1 : patche subprocess.run à l’endroit où toolwrap.py l’utilise, puis fais renvoyer au faux un résultat subprocess.CompletedProcess avec returncode 0, stdout « ok » et stderr vide.
3. Lance les tests : ils échouent, c’est la phase rouge. Le message te dit ce qui manque.
4. Écris lancer_outil(args, timeout) : liste d’arguments, capture_output, text, timeout transmis, check à False. Retourne les quatre clés returncode, stdout, stderr et erreur.
5. Fais passer W1 sans rien ajouter d’autre, puis commit.

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

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**W3 — Délai dépassé**
- Entrée : subprocess.run lève TimeoutExpired ; délai demandé : 2 secondes
- Résultat attendu : returncode None et erreur non vide qui mentionne le délai ; le timeout de 2 secondes est bien transmis à subprocess.run.

**W4 — Outil introuvable**
- Entrée : subprocess.run lève FileNotFoundError
- Résultat attendu : returncode None et erreur « outil introuvable » ou un message équivalent court ; aucune exception ne remonte.

**Actions dans l’ordre**

1. Exemple sans rapport d’abord : une exception se rattrape avec try / except. TimeoutExpired est l’exception que subprocess.run lève quand le délai est dépassé.
2. W3 : le faux lève TimeoutExpired. Vérifie que le délai de 2 secondes est bien transmis à subprocess.run, et que erreur mentionne le délai.
3. W4 : le faux lève FileNotFoundError. Vérifie que returncode vaut None et que erreur dit que l’outil est introuvable.
4. Dans lancer_outil, attrape les deux exceptions séparément. Aucune ne doit sortir de la fonction.
5. Lance les tests, puis commit.

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

- Un code de retour non nul n’est pas une exception : subprocess.run renvoie quand même un résultat, avec returncode 3 par exemple. Tu conserves returncode et stderr, et tu remplis erreur.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**W2 — Code de retour non nul**
- Entrée : Résultat simulé : code 3, stderr « erreur simulée »
- Résultat attendu : returncode 3 et stderr conservés ; erreur est une chaîne non vide ; aucune exception. Un code 0 n’est pas une erreur.

**W5 — Liste d’arguments intacte**
- Entrée : ['echo', 'Ana; echo piraté']
- Résultat attendu : subprocess.run reçoit exactement cette liste de deux éléments, sans shell=True (absent ou False). Le texte après le point-virgule reste dans un seul argument.

**Actions dans l’ordre**

1. W2 : un code 0 n’est jamais une erreur ; un code 3 donne erreur non vide, et stderr reste renseigné.
2. W5 : vérifie que le faux reçoit exactement la liste ['echo', 'Ana; echo piraté'], sans shell=True. Les arguments d’un appel se lisent dans call_args.
3. Lance les tests : W1 à W5 doivent tous passer. Puis commit.

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

**Actions dans l’ordre**

1. Crée un fichier .gitignore contenant une ligne __pycache__/ : Python y range ses caches, ils ne doivent pas être commités.
2. Relance les tests, puis regarde git status : __pycache__ ne doit plus apparaître.
3. Relis le diff avant chaque add. Le .gitignore fait l’objet de son propre commit.

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

**Actions dans l’ordre**

1. Ici, aucun pipeline ne tourne : un test local réussi n’est pas une fusion autorisée. Tu relis le diff toi-même, puis tu fusionnes.
2. Pousse la branche, ouvre la pull request, puis relis le diff dans GitHub comme si c’était le code de quelqu’un d’autre.
3. Fusionne avec « Merge pull request » dans GitHub, puis reviens sur main à jour.

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

**Actions dans l’ordre**

1. Vérifie que toolwrap.py est présent sur main : c’est la preuve que la MR1 est fusionnée.
2. Crée la branche de la MR2 depuis main à jour.

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

**Actions dans l’ordre**

1. argparse lit une liste d’arguments et produit un objet dont les champs sont les valeurs reçues. En test, tu lui passes la liste ; en ligne de commande, il lit sys.argv.
2. Une sous-commande est un mot qui choisit une branche du programme. Chacune a ses propres arguments.
3. Lance l’exemple sans rapport : une petite calculatrice. Lis ce que --help affiche.

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

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**W6 — Sous-commande reseau**
- Entrée : ['reseau', '127.0.0.1', '--port', '8000']
- Résultat attendu : Sous-commande reseau, cible 127.0.0.1, port 8000 sous forme d’entier. Sans --port, la valeur par défaut 8000 est retenue.

**W7 — Aide**
- Entrée : ['--help']
- Résultat attendu : SystemExit de code 0 ; la sortie affichée mentionne les sous-commandes reseau et ad.

**Actions dans l’ordre**

1. Crée cli.py. Mets la construction du parseur dans une fonction construire_parseur(), et écris main(argv) qui reçoit une liste d’arguments (pas sys.argv) : les tests passent une liste.
2. Sous-commande reseau : une cible obligatoire et --port entier, 8000 par défaut.
3. Sous-commande ad : un sujet parmi users, groups et computers, puis --format json ou text.
4. W6 vérifie les valeurs obtenues. W7 vérifie que --help sort avec SystemExit de code 0 : utilise assertRaises(SystemExit).
5. Lance python3 cli.py --help à la main, puis les tests, puis commit.

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

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**W8 — Liste blanche**
- Entrée : « 127.0.0.1 » puis « 127.0.0.2 », « 8.8.8.8 », « localhost », « 127.0.0.1/32 »
- Résultat attendu : 127.0.0.1 accepté ; les quatre autres refusés par ValueError avec un message clair en français. Aucune résolution de nom n’est tentée.

**Actions dans l’ordre**

1. ipaddress lit une chaîne comme une adresse IP. Si ce n’est pas une adresse, elle lève ValueError : c’est un moyen de refuser « localhost » sans consulter le DNS.
2. Liste blanche : une constante unique dans cli.py, qui ne contient que l’adresse autorisée dans le labo. Une adresse loopback n’est pas autorisée par défaut : seule celle de la liste l’est.
3. Écris W8 d’abord : 127.0.0.1 est accepté ; 127.0.0.2, 8.8.8.8, localhost et 127.0.0.1/32 sont refusés avec un message en français.
4. Écris la validation, fais passer W8, puis commit.

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

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**W9 — Cible refusée sans lancement**
- Entrée : ['reseau', '8.8.8.8'] avec lancer_outil remplacé par un faux
- Résultat attendu : main retourne 2, un message d’erreur est écrit sur stderr et lancer_outil n’est jamais appelé.

**Actions dans l’ordre**

1. Dans main, valide la cible avant tout appel à lancer_outil. Si elle est refusée : message sur stderr, code de retour 2.
2. Dans W9, remplace lancer_outil par un faux dans le module cli (cli.lancer_outil), comme dans l’exemple de mock de la MR1. Il ne doit jamais être appelé.
3. Pour lire stderr dans le test, capture-le avec contextlib.redirect_stderr.
4. Écris W9, fais-le passer, puis commit.

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

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**W10 — Codes de retour de main**
- Entrée : ['ad', 'users'] avec lancer_outil simulé : une fois code 0, une fois code 3 (ou erreur)
- Résultat attendu : main retourne 0 dans le premier cas et 1 dans le second. Le sujet users est transmis à l’outil.

**Actions dans l’ordre**

1. Code 0 : l’outil a réussi. Code 1 : échec (returncode non nul ou erreur renseignée). Code 2 : arguments invalides ou cible refusée, déjà fait.
2. logging écrit des messages sur un canal choisi. Ici, le canal est stderr : le résultat reste sur stdout, les traces sur stderr.
3. W10 : utilise mock.patch avec side_effect et une liste, pour que le faux renvoie d’abord un succès, puis un code 3. main doit renvoyer 0 puis 1, et le sujet users doit être transmis à l’outil.
4. Écris main avec logging, fais passer W10, puis commit.

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

**Actions dans l’ordre**

1. Les branches essai/conflit-a et essai/conflit-b partent de main. Elles servent uniquement à l’exercice : tu les supprimes à la fin.
2. Chaque branche écrit une ligne différente dans README.md. Si README.md n’existe pas encore sur main, le conflit porte sur un fichier créé des deux côtés ; s’il existe déjà, c’est un conflit de contenu. Dans les deux cas, la méthode est la même.
3. Git écrit les deux versions entre les marqueurs <<<<<<<, ======= et >>>>>>>. Tu choisis le texte final, tu retires les trois marqueurs, puis tu commites.
4. Ne lance pas ces commandes sur feat/cli-perimetre.

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

**Actions dans l’ordre**

1. Un rebase rejoue tes commits sur une nouvelle base. Pour que l’exercice ne touche pas main, la base évoluée est une branche jetable essai/base-evoluee, créée depuis main.
2. La copie jetable essai/rebase reprend ta branche feat/cli-perimetre. Tu rebases cette copie, pas la vraie branche.
3. Pendant le rebase, Git s’arrête à chaque conflit : lis son message, corrige le fichier, git add, puis git rebase --continue. git rebase --abort annule tout.
4. Dans la vraie MR2, si main a avancé avant ta livraison, la même commande s’applique à feat/cli-perimetre. Si la branche est déjà poussée, ne rebase pas sans prévenir : un rebase réécrit l’historique et impose un push forcé, à mentionner dans la PR.

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

**Actions dans l’ordre**

1. Dans README.md, ajoute une section « CLI » : codes 0, 1 et 2, liste blanche (127.0.0.1 seulement), commande des tests.
2. Relis le diff : seuls cli.py, tests/test_cli.py et README.md doivent apparaître. Aucune ligne d’essai ne doit subsister.
3. Pousse la branche, ouvre la pull request, puis fusionne après relecture. Il n’y a toujours pas de pipeline : la fusion reste ta décision.

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

**Actions dans l’ordre**

1. Crée la branche de la MR3 depuis main à jour.
2. Copie les fixtures nmap et adsim depuis le dossier fixtures/ du projet Cyber Atelier dans ton dépôt.
3. Ouvre fixtures/nmap/open_8000.xml, closed_8000.xml et mixed.xml : repère l’hôte, le port (portid), le protocole et l’état (state).

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

- Un XML est un arbre d’éléments avec des attributs. xml.etree.ElementTree le charge et permet de parcourir cet arbre.

**Actions dans l’ordre**

1. findall('article') ne cherche que les enfants directs de l’élément. get('nom') lit un attribut.
2. Une chaîne mal formée lève ParseError : tu la rattraperas plus tard pour les fichiers cassés.

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

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**W11 — XML ouvert**
- Entrée : Fixture open_8000.xml
- Résultat attendu : Un élément : source nmap, nom « 8000/tcp », statut « open », erreur None.

**Actions dans l’ordre**

1. Crée parsing.py (les parseurs) et tests/test_parsing.py. Le test W11 lit fixtures/nmap/open_8000.xml.
2. Construis le chemin de la fixture à partir de __file__ (le fichier de test), pas à partir du dossier courant : les tests passent ainsi depuis n’importe où.
3. W11 : un élément, source nmap, nom « 8000/tcp », statut « open », erreur None. Lance les tests : rouge.
4. Écris l’analyse nmap : un élément par port de l’hôte, avec les clés source, type, nom, statut et details. Vert, puis commit.

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

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**W12 — XML mixte, ordre conservé**
- Entrée : Fixture mixed.xml, qui contient trois ports : open, closed et filtered
- Résultat attendu : Trois éléments dans l’ordre du fichier, de statuts open, closed puis filtered ; erreur None.

**W13 — XML cassé**
- Entrée : Fixture broken.xml
- Résultat attendu : Aucune exception ; items vide ; erreur est une chaîne non vide.

**Actions dans l’ordre**

1. W12 : mixed.xml donne trois éléments dans l’ordre du fichier, de statuts open, closed puis filtered ; erreur None.
2. W13 : broken.xml ne lève aucune exception : items est vide et erreur est une chaîne non vide.
3. Chaque analyse renvoie toujours la même forme : un dictionnaire avec items et erreur.
4. Écris les tests, fais-les passer, puis commit.

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

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**W14 — JSON adsim valide**
- Entrée : Fixture users.json
- Résultat attendu : Nombre d’éléments égal au champ count du fichier ; statut « actif » ou « inactif » selon enabled ; groupes conservés, liste vide si l’utilisateur n’a aucun groupe.

**Actions dans l’ordre**

1. json.loads transforme une chaîne JSON en dictionnaire Python. Les données de adsim sont dans fixtures/adsim/users.json.
2. Ouvre users.json : les champs count et items. Chaque item a name, enabled et groups.
3. Format commun : source, type, nom, statut, details. Pour adsim : statut « actif » ou « inactif » selon enabled, et details contient les groupes (liste vide si aucun).
4. W14 : le nombre d’éléments est égal au champ count, les statuts et les groupes sont conservés. Écris le test, rouge, puis vert, commit.

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

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**W15 — JSON invalide**
- Entrée : Fixture broken.json
- Résultat attendu : items vide ; erreur non vide ; aucune exception.

**Actions dans l’ordre**

1. json.loads lève JSONDecodeError sur une chaîne invalide. C’est une sous-classe de ValueError : rattrape-la au moment de l’analyse.
2. W15 : broken.json donne items vide, erreur non vide, et aucune exception.
3. Crée dans README.md une section « Statuts » qui liste open, closed, filtered, actif et inactif, avec leur sens.

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

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**W16 — Rapport texte**
- Entrée : Trois éléments normalisés (deux open, un closed), puis une liste vide
- Résultat attendu : Une ligne par élément dans l’ordre, puis un total cohérent (3 éléments, 2 open, 1 closed) ; pour la liste vide, un message indique qu’aucun élément n’a été trouvé.

**Actions dans l’ordre**

1. Exemple sans rapport ci-dessous : une boucle, un compteur, et sum avec une condition.
2. W16 : trois éléments (deux open, un closed) donnent une ligne par élément dans l’ordre, puis un total de 3, 2 ouverts et 1 fermé. Une liste vide donne un message qui dit qu’aucun élément n’a été trouvé.
3. Écris une fonction qui renvoie le texte (et ne l’affiche pas) : le test compare une chaîne. L’affichage sur stdout se fait ensuite, dans main.

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

**Actions dans l’ordre**

1. Les démonstrations ne font pas partie de unittest discover : elles montrent le comportement réel, sans remplacer les tests.
2. D1 : démarre le labo HTTP avec son bouton dans l’interface Cyber Atelier (127.0.0.1:8000). Lance nmap réel avec lancer_outil, depuis le dossier du projet, puis passe la sortie XML à ton analyse.
3. D2 : lance adsim réel avec lancer_outil et passe sa sortie JSON à ton analyse. Le nombre doit égaler count.
4. D3 : lance adsim avec --fail (code 3), puis avec un délai de 0,01 seconde : le démarrage de docker dépasse ce délai, ce qui doit donner une erreur de timeout.
5. Note dans le bilan ce que tu observes : port open quand le labo tourne, et résultat différent quand il est arrêté.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -c "import sys; sys.path.insert(0, 'workspaces/toolwrap'); from toolwrap import lancer_outil; print(lancer_outil(['docker', 'compose', 'exec', '-T', 'atelier', 'nmap', '-sT', '-p', '8000', '-oX', '-', '127.0.0.1'], 30))"
```

**Terminal · Commande à lancer au moment indiqué**

Console ou shell du conteneur, à la racine du parcours. /app contient les fichiers fournis par Cyber Atelier ; ce chemin n’existe pas sur le Mac.

```bash
python3 -c "import sys; sys.path.insert(0, 'workspaces/toolwrap'); from toolwrap import lancer_outil; print(lancer_outil(['docker', 'compose', 'exec', '-T', 'atelier', 'python', '/app/tools/adsim.py', 'users', '--fail'], 30))"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -c "import sys; sys.path.insert(0, 'workspaces/toolwrap'); from toolwrap import lancer_outil; print(lancer_outil(['docker', 'compose', 'exec', '-T', 'atelier', 'python', '/app/tools/adsim.py', 'users'], 0.01))"
```

**Tu sais que c’est bon quand :** D1 donne le port 8000 en open quand le labo tourne. D2 donne un nombre d’éléments égal à count. D3 donne une erreur normalisée pour le code 3 et une erreur de timeout, sans trace Python.

*Indice si tu bloques :* Commande vide ou « no such service » : vérifie depuis le dossier du projet avec docker compose ps. Port closed : démarre le labo depuis l’interface. Les démonstrations n’ajoutent rien aux tests : garde-les dans le bilan.

#### Palier 9 — Bilan du README et livraison de la MR3 (8 min)

Finir le README avec un bilan honnête, puis livrer la MR3 sans y mettre les fichiers de démonstration.

**Où tu travailles :** README.md ; PR GitHub

**Actions dans l’ordre**

1. Dans README.md, complète : périmètre, codes de sortie, commandes de tests, démonstrations séparées de la CI, puis un bilan en trois listes : ce que les tests prouvent, ce que les démonstrations montrent, ce qui reste à faire.
2. Ajoute à l’index uniquement les fichiers de test et les fixtures d’origine. Les fichiers demo_*.xml et demo_*.json ne sont pas livrés.
3. Pousse la branche, ouvre la pull request, relis le diff dans GitHub, puis fusionne. Un test local réussi reste distinct d’une fusion autorisée.

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
