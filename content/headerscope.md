# HeaderScope — vérifier trois en-têtes HTTP

**Durée : 5 heures · Niveau débutant · 3 merge requests**

Tu vas écrire un petit client qui demande une ressource au laboratoire local et évalue trois en-têtes de réponse. Le travail porte sur la lecture et la normalisation des en-têtes, les réponses HTTP et les erreurs de connexion. Aucun exploit, parcours de liens ou hôte distant n’est utilisé.

## Contrat du programme

Écris ton programme dans headerscope.py et tes tests dans verification.py. Tu peux choisir les noms de fonctions, mais garde séparées les règles pures, le classement des réponses HTTP, le client et l’orchestration. La bibliothèque standard urllib.request suffit. Le programme n’a pas besoin de classes ou de fixtures avancées ; les classes unittest restent utilisées dans les tests. Une fonction pure classer_reponse(statut, entetes) reçoit un code de statut entier et un mapping d’en-têtes : pour 200 elle retourne le statut, l’état HTTP_OK et les alertes calculées par les règles ; pour 404 ou 500 elle retourne le statut, l’état HTTP_ERREUR et une liste d’alertes vide. L’orchestration appelle cette fonction après avoir obtenu la réponse du client. Une panne de transport ou un timeout n’a pas de code HTTP et reste un résultat distinct, hors de classer_reponse.

Les contrôles attendus sont :

- Content-Security-Policy existe et sa valeur, après retrait des espaces au début et à la fin, n’est pas vide ;
- X-Content-Type-Options, après retrait des espaces et comparaison sans tenir compte de la casse, vaut nosniff ;
- X-Frame-Options, après retrait des espaces et comparaison sans tenir compte de la casse, vaut DENY ou SAMEORIGIN.

Les noms d’en-tête sont insensibles à la casse. La valeur CSP est seulement vérifiée comme non vide ; les deux autres valeurs sont normalisées avec espaces retirés et casse ignorée. Retourne une alerte lisible par contrôle en échec ; une réponse conforme produit zéro alerte. Garde le nombre et le contenu des alertes prévisibles afin que les tests puissent les vérifier.

La fonction pure classer_reponse(statut, entetes) retourne un triplet (statut, resultat, alertes). Pour 200, resultat vaut HTTP_OK et alertes contient les résultats des trois règles. Pour 404 et 500, resultat vaut HTTP_ERREUR et alertes est vide ; le statut reste dans le triplet. La fonction ne fait aucun accès réseau. Une panne de connexion ou un timeout survient avant le classement et doit être rendu comme un résultat distinct sans code HTTP.

Le laboratoire local répond aux chemins /fragile, /durci, /absent et /erreur sur 127.0.0.1:8000. /fragile répond 200 sans aucun des trois en-têtes contrôlés et doit produire trois alertes. /durci renvoie les trois en-têtes conformes et doit produire zéro alerte. /absent produit une erreur HTTP 404 et /erreur une erreur HTTP 500.

<!-- BEGIN GENERATED EXERCISES -->
## Comment travailler un exercice

Ces exercices sont ton entraînement. Chaque palier explique les notions utiles, montre les données ou les règles attendues, puis te fait écrire et vérifier ton propre code. Les durées sont des repères : avance quand tu comprends le résultat.

1. Lis « Pour comprendre » et l’exemple lorsqu’il y en a un. Repère ce qui entre dans le programme, ce qui doit en sortir et les règles à respecter.
2. Les cartes de tests donnent l’entrée et le résultat attendu. Écris les tests correspondants dans le fichier indiqué ; cocher un palier ne les exécute pas. Avec unittest, « Ran 0 tests » signifie qu’aucun test n’a été exécuté : ce n’est pas une validation. Un cas décrit peut contenir plusieurs valeurs ; le nombre de méthodes Python n’est donc pas forcément le nombre d’identifiants.
3. Suis les actions numérotées, une à la fois. Les exemples servent à apprendre une notion ; tu écris toi-même la solution de l’exercice. Les blocs Terminal donnent les commandes à lancer au moment indiqué.
4. Vérifie le résultat indiqué avant de poursuivre. Un échec attendu (phase rouge, argument refusé ou conflit volontaire) est expliqué dans le palier.
5. Si tu bloques, lis la dernière ligne de l’erreur, compare l’entrée et l’attendu, puis ouvre l’indice. Fais un petit changement et relance.

### Le bon endroit pour chaque action

Sur ton Mac, ouvre `workspaces/headerscope` dans VS Code. Dans Cyber Atelier, utilise l’éditeur et la console de **Coder**, avec `cwd` sur `.` (la racine du dépôt). Fais la préparation de **Environnement** avant MR1 ; la mission crée ensuite sa branche.

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

### MR1 — feat/regles-entetes (85 min)

Ces règles seront réutilisées sur une réponse HTTP en MR2. Avance dans l’ordre des paliers et vérifie chaque résultat avant de poursuivre.

**Avant de commencer**

- Point de départ : Un dépôt cloné ; tu n’as pas besoin de démarrer le laboratoire pour cette mission.
- Ce que tu vas produire : headerscope.py, verification.py et .gitlab-ci.yml : vérifier les trois en-têtes sur des dictionnaires fabriqués.
- Pourquoi : Ces règles seront réutilisées sur une réponse HTTP en MR2.
- Commande des tests depuis la racine : `python3 verification.py`. Les cas ci-dessous sont à écrire par toi.

#### Palier 1 — Prépare ton dépôt et ta branche (10 min)

Partir d’une branche de travail propre, dédiée à cette MR.

**Où tu travailles :** Dépôt

**Pour comprendre**

- La branche principale (main) contient le travail déjà fusionné. Ta branche feat/... reçoit les changements de cette mission.
- Un dépôt « propre » n’a aucune modification en attente : git status te le confirme.

**Actions dans l’ordre**

1. Ouvre workspaces/headerscope dans VS Code, ou Coder dans Cyber Atelier avec cwd sur « . ».
2. Termine la préparation de l’onglet Environnement : Python, Git et dépôt cloné.
3. Lis git status ; enregistre ton travail en cours avant de changer de branche.
4. Reviens sur main avec git switch main, mets-la à jour avec git pull --ff-only, puis crée feat/regles-entetes. Remplace main par master si ton dépôt utilise ce nom.
5. Vérifie le nom de ta branche avec git status. Si elle existe déjà, reprends-la avec git switch sans -c.

**Terminal · Relire l’état du dépôt**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git status
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git switch -c feat/regles-entetes
```

**Terminal · Relire l’état du dépôt**

```bash
git status
```

**Tu sais que c’est bon quand :** git status affiche « On branch feat/regles-entetes » et « nothing to commit, working tree clean ».

*Indice si tu bloques :* Si Git répond « not a git repository », tu n’es pas dans workspaces/headerscope. Si la branche n’existe pas, reviens sur main à jour (git switch main puis git pull --ff-only) puis crée-la avec git switch -c feat/regles-entetes.

#### Palier 2 — Un premier unittest et le code de sortie (10 min)

Savoir lire un test qui passe ou échoue, et comprendre pourquoi la CI se fie au code de sortie.

**Où tu travailles :** exemple.py (jetable)

**Pour comprendre**

- unittest découvre les méthodes test_ dans une classe qui hérite de TestCase. assertEqual compare le résultat au texte attendu.
- unittest.main() lance les vérifications ; sans lancement, un fichier peut terminer avec 0 sans avoir testé quoi que ce soit.

**Éditeur · Exemple Python à lire ou essayer**

Éditeur : place ce code dans un fichier d’exemple jetable, puis lance ce fichier avec python3. Un extrait avec self se place dans une méthode de test.

```python
import unittest

def saluer(prenom):
    return 'Bonjour ' + prenom + ' !'

class TestSaluer(unittest.TestCase):
    def test_saluer_une_personne(self):
        self.assertEqual(saluer('Ada'), 'Bonjour Ada !')

if __name__ == '__main__':
    unittest.main()
```

**Actions dans l’ordre**

1. Crée exemple.py avec l’exemple saluer. Lance le fichier puis echo $? dans la même exécution.
2. Observe OK et 0 avec l’attendu correct.
3. Change seulement l’attendu en « Bonjour Ada !! » : observe FAILED et 1.
4. Rétablis l’attendu correct, puis supprime exemple.py sans le livrer.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 exemple.py
```

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs. Lance le programme et echo $? ensemble : le nombre affiché est le code du programme ; la console peut afficher code 0 pour echo lui-même.

```bash
python3 exemple.py; echo $?
```

**Tu sais que c’est bon quand :** Avec la bonne valeur, tu vois « OK » et echo affiche 0. Avec la mauvaise, tu vois « FAILED » et echo affiche 1.

*Indice si tu bloques :* unittest.main() lance les tests du fichier. Le code de sortie 0 signifie succès ; toute autre valeur signifie qu’un test a échoué. Lis les messages d’échec de bas en haut : la dernière ligne dit ce qui ne va pas.

#### Palier 3 — Dictionnaires et noms normalisés (10 min)

Chercher une valeur par clé, après avoir normalisé le texte saisi.

**Où tu travailles :** exemple2.py (jetable)

**Pour comprendre**

- Un dictionnaire associe un nom (clé) à une valeur. get(clé, défaut) donne la valeur de la clé, ou le défaut si elle manque.
- Normaliser un nom signifie lui donner une forme commune : strip retire les espaces aux bords ; lower met les lettres en minuscules.

**Éditeur · Exemple Python à lire ou essayer**

Éditeur : copie cet exemple dans exemple2.py (jetable), enregistre-le, puis lance python3 exemple2.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
prix = {'pomme': 1.2, 'poire': 1.5}
saisie = '   POMME  '
cle = saisie.strip().lower()
print(cle)
print(prix.get(cle, 0))
print(prix.get('banane', 0))
for nom, valeur in prix.items():
    print(nom, valeur)
```

**Actions dans l’ordre**

1. Crée exemple2.py avec l’exemple des fruits et lance-le.
2. Repère la saisie d’origine, la clé nettoyée et la valeur trouvée. Observe aussi le résultat pour une clé absente.
3. Change la casse et les espaces de la saisie ; vérifie que la clé obtenue reste identique.
4. Observe items() dans la boucle : il fournit chaque paire clé/valeur. Supprime le fichier d’essai.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 exemple2.py
```

**Tu sais que c’est bon quand :** Tu obtiens « pomme », puis 1.2, puis 0 (clé absente, sans erreur), puis les deux lignes de la boucle.

*Indice si tu bloques :* strip() retire les espaces au début et à la fin ; lower() passe en minuscules. Les deux renvoient une nouvelle chaîne : le texte d’origine ne change pas. dict.get(clé, valeur_par_défaut) évite l’erreur quand la clé manque.

#### Palier 4 — H2 : aucun en-tête donne trois alertes (10 min)

Écrire le premier test de règles, puis la première version de la fonction qui retourne les alertes.

**Où tu travailles :** headerscope.py ; verification.py

**Pour comprendre**

- Un en-tête HTTP est une information nommée dans une réponse. Ici, tu reçois déjà ces informations sous forme de dictionnaire.
- Une alerte est un texte qui explique une règle en échec ; la fonction retourne une liste de ces textes, sans requête réseau.

**Exemple de résultat attendu**

Ce que tu donnes :

```text
evaluer_entetes({})
```

Ce que tu dois obtenir :

```text
Une liste de 3 alertes : CSP absente, options MIME absentes, options de frame absentes.
```

La formulation reste lisible et prévisible ; ce palier vérifie le nombre.

**Règles à respecter**

- Trois règles indépendantes : Content-Security-Policy, X-Content-Type-Options et X-Frame-Options.
- Un contrôle en échec produit une alerte ; tous les contrôles conformes donnent [].
- Les noms d’en-tête sont comparés sans tenir compte des majuscules/minuscules.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**H2 — Aucun en-tête**
- Entrée : Dictionnaire vide
- Résultat attendu : Trois alertes, une par règle.

**Actions dans l’ordre**

1. Crée headerscope.py et verification.py avec TestRegles(unittest.TestCase) et unittest.main() sous la garde __main__.
2. Écris H2 : evaluer_entetes({}) retourne une liste de trois alertes. Vérifie leur nombre.
3. Lance : l’absence de fonction explique le rouge.
4. Crée evaluer_entetes(entetes) : pour chaque en-tête requis absent, ajoute une alerte lisible.
5. Relance H2 puis commite ; les valeurs et leur normalisation arrivent ensuite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add headerscope.py verification.py
git commit -m "Ajoute les alertes d’absence des trois en-têtes"
```

**Tu sais que c’est bon quand :** python3 verification.py affiche OK pour H2 et git log --oneline montre ton commit.

*Indice si tu bloques :* Une alerte est une chaîne lisible, par exemple « CSP absente ». Crée une liste vide, puis ajoute une alerte pour chaque règle en échec. Commence par une seule règle si tu bloques, puis ajoute les deux autres.

#### Palier 5 — H3 et H4 : noms sans casse, CSP vide (11 min)

Reconnaître les noms d’en-têtes quelle que soit la casse, et refuser une CSP vide.

**Où tu travailles :** headerscope.py ; verification.py

**Pour comprendre**

- La casse distingue majuscules et minuscules. Content-Security-Policy et content-security-policy désignent le même en-tête.
- Une valeur "   " n’est pas utile : strip() la transforme en texte vide.

**Règles à respecter**

- Pour CSP, seule la présence d’une valeur non vide est demandée ; tu n’analyses pas le contenu de sa politique.
- Une CSP absente ou vide produit une alerte CSP.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**H3 — Noms minuscules**
- Entrée : Noms en minuscules et valeurs valides
- Résultat attendu : Zéro alerte.

**H4 — CSP absente ou vide**
- Entrée : Clé manquante, valeur vide ou espaces seulement
- Résultat attendu : Alerte CSP.

**Actions dans l’ordre**

1. Écris H3 : les trois noms en minuscules avec des valeurs conformes donnent zéro alerte.
2. Écris les trois sous-cas de H4 : CSP absente, vide, puis avec seulement des espaces. Garde les deux autres en-têtes conformes pour isoler ce contrôle.
3. Normalise les noms une fois et vérifie une valeur CSP non vide après strip.
4. Relance H2, H3 et H4 puis commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add headerscope.py verification.py
git commit -m "Reconnais les noms sans casse et refuse une CSP vide"
```

**Tu sais que c’est bon quand :** H2, H3 et H4 passent, et le commit apparaît dans git log --oneline.

*Indice si tu bloques :* Piège : une clé en minuscules ne se retrouve pas avec la casse d’origine. Compare des noms normalisés des deux côtés. La règle « après retrait des espaces » s’applique à la valeur de la CSP, pas à son nom.

#### Palier 6 — H5 et H6 : valeurs sans casse ni espaces (11 min)

Comparer les valeurs nosniff, DENY et SAMEORIGIN après normalisation.

**Où tu travailles :** headerscope.py ; verification.py

**Pour comprendre**

- Les valeurs sont comparées après strip() et sans tenir compte de la casse.
- « valeur in liste » permet de vérifier l’appartenance à plusieurs valeurs admises.

**Éditeur · Exemple Python à lire ou essayer**

Éditeur : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
fruits_admis = ['pomme', 'poire']
print('poire' in fruits_admis)
print('kiwi' in fruits_admis)
```

**Règles à respecter**

- X-Content-Type-Options : valeur normalisée nosniff.
- X-Frame-Options : valeur normalisée deny ou sameorigin.
- Chaque valeur refusée ajoute une alerte pour sa propre règle.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**H5 — Options MIME**
- Entrée : nosniff avec espaces et casse variables, puis valeur incorrecte
- Résultat attendu : Première entrée acceptée ; seconde signalée.

**H6 — Options de frame**
- Entrée : DENY, SAMEORIGIN et valeur non admise avec espaces/casse variables
- Résultat attendu : Deux admises ; valeur non admise signalée.

**Actions dans l’ordre**

1. Écris H5 : variantes de nosniff avec casse/espaces admises ; une autre valeur signalée.
2. Écris H6 : variantes de DENY et SAMEORIGIN admises ; une autre valeur signalée.
3. Pour chaque test, garde les deux autres en-têtes conformes.
4. Complète les deux contrôles, relance H2 à H6 puis commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add headerscope.py verification.py
git commit -m "Accepte nosniff, DENY et SAMEORIGIN sans tenir compte de la casse"
```

**Tu sais que c’est bon quand :** H2 à H6 passent. L’exemple des fruits affiche True puis False.

*Indice si tu bloques :* Normalise la valeur avant de la comparer, comme pour la saisie de l’exemple du palier 3. Pour les deux règles, teste une valeur admise avec espaces et majuscules, puis une valeur refusée.

#### Palier 7 — H1 et H7 : profil conforme et règles indépendantes (11 min)

Vérifier qu’un profil complet ne donne aucune alerte, et qu’une seule règle en échec ne fait ressortir qu’une seule alerte.

**Où tu travailles :** headerscope.py ; verification.py

**Pour comprendre**

- Les trois règles se cumulent : un contrôle conforme ne retire pas l’alerte d’un autre.
- Une liste vide [] est attendue quand toutes les règles passent.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**H1 — Profil conforme**
- Entrée : Les trois en-têtes requis avec valeurs admises
- Résultat attendu : Zéro alerte.

**H7 — Règles indépendantes**
- Entrée : Deux valeurs conformes et une incorrecte
- Résultat attendu : Une alerte exactement.

**Actions dans l’ordre**

1. Écris H1 avec les trois en-têtes et des valeurs conformes : attends [].
2. Écris H7 avec deux valeurs conformes et une incorrecte : attends exactement une alerte.
3. Relis les contrôles séparément si le nombre d’alertes est incorrect.
4. Relance H1 à H7 sans changer les attendus déjà verts, puis commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add headerscope.py verification.py
git commit -m "Vérifie le profil conforme et l’indépendance des règles"
```

**Tu sais que c’est bon quand :** python3 verification.py affiche OK pour H1 à H7 et se termine avec 0 ; git log --oneline montre le commit.

*Indice si tu bloques :* Si H7 donne deux alertes au lieu d’une, une règle regarde probablement un autre en-tête que le sien ou compare mal une valeur. Vérifie-les une par une avec un seul en-tête à la fois.

#### Palier 8 — Test en CI puis merge request (12 min)

Faire exécuter les tests par la CI de la merge request, puis fusionner seulement quand le pipeline du dernier commit est vert.

**Où tu travailles :** .gitlab-ci.yml ; MR GitLab

**Pour comprendre**

- git diff montre les lignes modifiées ; git diff --staged montre celles choisies pour le prochain commit. Le diff de la MR compare toute ta branche à main.
- La demande de fusion (MR dans GitLab, PR dans GitHub) permet de relire le travail avant de l’intégrer à main.

**Éditeur · Exemple YAML à lire**

Éditeur : exemple de syntaxe, à adapter ; ce bloc ne se lance pas dans le terminal.

```yaml
# Exemple sans rapport avec HeaderScope : la forme d’un job de CI
saluer:
  script:
    - echo bonjour
```

**Actions dans l’ordre**

1. Lance la suite complète avec la commande indiquée au début de la mission.
2. Avant de livrer, rédige .gitlab-ci.yml toi-même : job bloquant sur les MR avec python3 verification.py. Il ne démarre pas le labo. Teste cette commande en local puis commite la CI.
3. Relis git status et git diff : la livraison doit contenir headerscope.py, verification.py et .gitlab-ci.yml, avec les modifications nécessaires de cette mission.
4. Ajoute les fichiers par leur nom, relis git diff --staged, puis commite ce qui ne l’est pas encore.
5. Pousse feat/regles-entetes et ouvre la demande de fusion vers main.
6. Dans GitLab, ouvre le pipeline du dernier commit : vérifie qu’il a réellement exécuté les tests et qu’il est vert. Un test local réussi ne le remplace pas.
7. Relis le diff et fusionne lorsque le pipeline et les règles de l’école le permettent.
8. Après la fusion, reviens sur main et lance git pull --ff-only avant la mission suivante.

**Terminal · Relire l’état du dépôt**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git status
git diff main --stat
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add .gitlab-ci.yml headerscope.py verification.py
git commit -m "Lance les tests de règles dans la CI de merge request"
```

**Terminal · Publier la branche ou ouvrir la demande de fusion**

```bash
git push -u origin feat/regles-entetes
```

**Terminal · Après la fusion : actualiser la principale**

```bash
git switch main
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git pull --ff-only
```

**Tu sais que c’est bon quand :** Le pipeline du dernier commit est vert dans GitLab, la merge request ne contient que les fichiers attendus, et main local contient la fusion (git log --oneline).

*Indice si tu bloques :* Si le pipeline ne démarre pas, vérifie dans la documentation GitLab de l’école que le job se déclenche sur les merge requests (mot-clé rules). Ne fusionne jamais sur un pipeline rouge ou absent.

**Avant de livrer**

- Les tests s’exécutent localement et sur un runner sans service de laboratoire.
- Les noms sont comparés sans casse ; les valeurs appliquent exactement les normalisations du contrat.
- Les trois alertes de /fragile et zéro alerte de /durci sont les résultats de référence pour la démonstration.
- python3 verification.py affiche OK pour H1 à H7 et se termine avec un code de sortie 0.
- python3 verification.py se termine avec un code de sortie non nul dès qu’une assertion échoue.
- La merge request contient le fichier de CI (.gitlab-ci.yml), headerscope.py et verification.py, sans __pycache__.

### MR2 — feat/client-http (85 min)

Tu sépares la réponse HTTP, son classement et les pannes avant d’écrire le bilan. Avance dans l’ordre des paliers et vérifie chaque résultat avant de poursuivre.

**Avant de commencer**

- Point de départ : MR1 fusionnée ; les règles et H1 à H7 passent sans réseau.
- Ce que tu vas produire : demander et classer_reponse dans headerscope.py ; H8 et H9 dans verification.py.
- Pourquoi : Tu sépares la réponse HTTP, son classement et les pannes avant d’écrire le bilan.
- Commande des tests depuis la racine : `python3 verification.py`. Les cas ci-dessous sont à écrire par toi.

#### Palier 1 — Repartir de main à jour après MR1 (10 min)

Partir de la version fusionnée de la MR1, sans mélanger deux merge requests.

**Où tu travailles :** Dépôt

**Pour comprendre**

- La branche principale (main) contient le travail déjà fusionné. Ta branche feat/... reçoit les changements de cette mission.
- Un dépôt « propre » n’a aucune modification en attente : git status te le confirme.

**Actions dans l’ordre**

1. Ouvre workspaces/headerscope dans VS Code, ou Coder dans Cyber Atelier avec cwd sur « . ».
2. Vérifie que MR1 est fusionnée et que H1 à H7 passent sur main.
3. Lis git status ; enregistre ton travail en cours avant de changer de branche.
4. Reviens sur main avec git switch main, mets-la à jour avec git pull --ff-only, puis crée feat/client-http. Remplace main par master si ton dépôt utilise ce nom.
5. Vérifie le nom de ta branche avec git status. Si elle existe déjà, reprends-la avec git switch sans -c.

**Terminal · Relire l’état du dépôt**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git status
```

**Terminal · Après la fusion : actualiser la principale**

```bash
git switch main
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git pull --ff-only
```

**Terminal · Relire l’état du dépôt**

```bash
git log --oneline -5
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git switch -c feat/client-http
```

**Terminal · Relire l’état du dépôt**

```bash
git status
```

**Tu sais que c’est bon quand :** git log --oneline -5 montre le commit de fusion de la MR1, et git status affiche « On branch feat/client-http ».

*Indice si tu bloques :* Si git status n’est pas propre, ne force rien : demande-toi quels fichiers tu as modifiés et range-les dans un commit ou mets-les de côté. Si git pull --ff-only refuse, ton main local a divergé : relis git log avant d’aller plus loin.

#### Palier 2 — urllib et les deux sortes d’erreurs (10 min)

Comprendre qu’une réponse HTTP d’erreur et une panne de connexion ne sont pas la même chose.

**Où tu travailles :** exemple_reseau.py (jetable)

**Pour comprendre**

- HTTPError signifie que le serveur a répondu avec un code HTTP d’erreur, comme 404 : il existe une réponse et des en-têtes.
- URLError peut signaler une panne de connexion : aucune réponse HTTP utilisable n’a été reçue.

**Éditeur · Exemple Python à lire ou essayer**

Éditeur : copie cet exemple dans exemple_reseau.py (jetable), enregistre-le, puis lance python3 exemple_reseau.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
import urllib.error

erreur_connexion = urllib.error.URLError(ConnectionRefusedError("connexion refusée"))
print("panne :", erreur_connexion.reason)
erreur_http = urllib.error.HTTPError("http://127.0.0.1/exemple", 404, "Introuvable", {}, None)
print(erreur_http.code, erreur_http.reason)
```

**Actions dans l’ordre**

1. Crée exemple_reseau.py avec l’exemple fourni. Il fabrique les erreurs sans contacter de serveur.
2. Lance-le, repère reason pour la panne et code/reason pour l’erreur HTTP.
3. Explique la différence entre ces deux observations, puis supprime le fichier d’essai.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 exemple_reseau.py
```

**Tu sais que c’est bon quand :** Tu vois « panne : » suivi d’un message de connexion, puis « 404 Introuvable ». Le second résultat ne demande aucun réseau.

*Indice si tu bloques :* HTTPError est une sous-classe de URLError : si tu veux traiter les réponses d’erreur à part, place le except HTTPError avant le except URLError. Une connexion refusée donne une panne, jamais un code HTTP.

#### Palier 3 — H8 : une réponse 200 se classe sans réseau (12 min)

Écrire une fonction pure qui reçoit un statut et des en-têtes, et retourne un triplet.

**Où tu travailles :** headerscope.py ; verification.py

**Pour comprendre**

- Un triplet est un tuple de trois valeurs : ici le code HTTP, un état de classement et la liste des alertes.
- classer_reponse reçoit les données directement ; seule demander fera le réseau.

**Éditeur · Exemple Python à lire ou essayer**

Éditeur : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
def bornes(liste):
    return min(liste), max(liste)

petit, grand = bornes([4, 9, 2])
print(petit, grand)
```

**Exemple de résultat attendu**

Ce que tu donnes :

```text
classer_reponse(200, trois en-têtes conformes)
```

Ce que tu dois obtenir :

```text
(200, "HTTP_OK", [])
```

HTTP_OK indique la réponse réussie ; les alertes décrivent les contrôles d’en-têtes.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**H8 — Classement d’une réponse 200**
- Entrée : Appel pur à classer_reponse(200, dictionnaire des trois en-têtes conformes)
- Résultat attendu : Retourne le statut 200, HTTP_OK et zéro alerte.

**Actions dans l’ordre**

1. Écris H8 avec 200 et les trois en-têtes conformes ; vérifie le triplet entier.
2. Lance le test et repère la fonction manquante.
3. Crée classer_reponse(statut, entetes), réutilise evaluer_entetes pour le code 200.
4. Relance H1 à H8 et commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add headerscope.py verification.py
git commit -m "Ajoute classer_reponse pour les réponses 200"
```

**Tu sais que c’est bon quand :** H1 à H8 passent, et git log --oneline montre le commit.

*Indice si tu bloques :* Une fonction peut retourner plusieurs valeurs séparées par des virgules : c’est un triplet, comme l’exemple des bornes le montre. Ne refais pas les règles : appelle evaluer_entetes(entetes).

#### Palier 4 — H9 : les erreurs 404 et 500 gardent leur code (10 min)

Classer les erreurs HTTP sans leur donner d’alertes de politique.

**Où tu travailles :** headerscope.py ; verification.py

**Pour comprendre**

- Une erreur HTTP garde son numéro : 404 et 500 ne deviennent pas une panne sans code.
- Le contrat n’évalue pas la politique d’en-têtes sur ces réponses d’erreur.

**Exemple de résultat attendu**

Ce que tu donnes :

```text
classer_reponse(404, {})
```

Ce que tu dois obtenir :

```text
(404, "HTTP_ERREUR", [])
```

L’absence d’alerte de politique ici n’indique pas une requête réussie.

**Cas de test à écrire**

L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.

**H9 — Classement d’erreurs HTTP**
- Entrée : Appels purs avec statut 404 puis 500 et un dictionnaire d’en-têtes quelconque
- Résultat attendu : Chaque code est conservé avec HTTP_ERREUR et une liste d’alertes vide.

**Actions dans l’ordre**

1. Ajoute H9, séparément pour 404 et 500, avec un dictionnaire d’en-têtes quelconque.
2. Attends le code d’origine, "HTTP_ERREUR" et [].
3. Complète classer_reponse pour les codes autres que 200, sans réseau.
4. Relance H1 à H9 puis commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add headerscope.py verification.py
git commit -m "Classe les erreurs 404 et 500 sans alertes"
```

**Tu sais que c’est bon quand :** python3 verification.py affiche OK pour H1 à H9 et se termine avec 0.

*Indice si tu bloques :* Le contrat dit que les alertes restent vides pour une erreur HTTP : ne calcule rien dans ce cas. Vérifie que le code renvoyé est bien celui que tu as reçu en argument.

#### Palier 5 — Le client : URL limitée et timeout de 2 secondes (10 min)

Demander un chemin fixe du laboratoire avec un délai maximal de 2 secondes.

**Où tu travailles :** headerscope.py

**Pour comprendre**

- L’URL désigne la ressource complète ; le chemin est sa partie finale, comme /durci. La base reste fixe.
- urlopen lit la réponse ; timeout=2 borne l’attente à deux secondes.

**Règles à respecter**

- Chemins admis : /fragile, /durci, /absent, /erreur.
- Base : http://127.0.0.1:8000 ; timeout de deux secondes.
- H8 et H9 restent hors réseau.

**Actions dans l’ordre**

1. Crée demander(chemin) et la liste des quatre chemins admis.
2. Refuse tout autre chemin par ValueError avant tout appel réseau.
3. Construis l’URL avec la base fixe, puis récupère statut et en-têtes de la réponse réussie. Ferme la réponse après lecture.
4. Vérifie à la main le refus de /autre, relance les tests purs et commite. Le client réel sera essayé au palier 7.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -c "from headerscope import demander; demander('/autre')"
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add headerscope.py
git commit -m "Ajoute le client HTTP local avec timeout de 2 secondes"
```

**Tu sais que c’est bon quand :** demander('/autre') lève ValueError avant de contacter quoi que ce soit, et git log --oneline montre le commit.

*Indice si tu bloques :* Le délai se donne avec l’argument nommé timeout de urlopen. Une liste fixe de chemins autorisés se teste avec in avant de construire l’URL. Un délai dépassé peut sortir sous forme de TimeoutError au lieu de URLError : le palier suivant prévoit les deux.

#### Palier 6 — Séparer réponse HTTP d’erreur et panne (10 min)

Rendre une panne de connexion ou un délai dépassé comme un résultat distinct, sans code HTTP.

**Où tu travailles :** headerscope.py

**Pour comprendre**

- HTTPError hérite d’URLError : traite-la d’abord pour conserver la réponse HTTP.
- Panne de connexion et délai dépassé restent distincts des codes 404 et 500.

**Actions dans l’ordre**

1. Dans demander, attrape HTTPError, récupère code et en-têtes puis ferme la ressource.
2. Traite ensuite URLError et TimeoutError : rends une panne sans code HTTP et distingue le délai dépassé d’une autre panne.
3. Garde le classement dans classer_reponse ; la prochaine mission coordonnera les fonctions.
4. Vérifie la compilation, relance H1 à H9 puis commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -m py_compile headerscope.py
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add headerscope.py
git commit -m "Distingue les réponses HTTP d’erreur des pannes de connexion"
```

**Tu sais que c’est bon quand :** py_compile ne signale aucune erreur, H1 à H9 passent, et le commit apparaît dans git log --oneline.

*Indice si tu bloques :* Dans une suite de except, HTTPError doit venir avant URLError, sinon la première clause attrape tout. Un délai et une connexion refusée ne lèvent pas toujours la même exception : vérifie ce que ton code reçoit, sans le deviner.

#### Palier 7 — Démonstration du client (hors tests) (11 min)

Voir le client contre le vrai laboratoire, séparément des tests automatiques.

**Où tu travailles :** Laboratoire local ; headerscope.py

**Pour comprendre**

- 127.0.0.1 désigne la machine du programme : client du Mac et client du conteneur atteignent chacun leur propre labo.
- Cette démonstration dépend d’un serveur réel et reste hors tests automatiques.

**Actions dans l’ordre**

1. Choisis ton environnement : bouton du labo dans Docker, ou python3 labs.py depuis cyberatelier sur le Mac.
2. Depuis le même environnement, demande /fragile, /durci, /absent et /erreur, un par un.
3. Observe 200 pour les deux premiers, 404 pour /absent et 500 pour /erreur.
4. Arrête le labo et réessaie : attends une panne sans code HTTP.
5. Relance le labo pour la suite. Garde ces appels hors de verification.py et dans le périmètre prévu.

**Terminal · Option Mac : démarrer le laboratoire dans un autre terminal**

Terminal séparé sur ton Mac, depuis le dossier cyberatelier. Laisse-le ouvert pendant la démonstration, puis arrête avec Ctrl+C. Dans Docker, utilise plutôt le bouton du laboratoire.

```bash
python3 labs.py
```

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -c "from headerscope import demander; print(demander('/fragile'))"
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 -c "from headerscope import demander; print(demander('/absent'))"
```

**Tu sais que c’est bon quand :** /fragile répond avec un statut 200, /absent avec 404 et /erreur avec 500. Labo arrêté : tu obtiens une panne, pas un code HTTP.

*Indice si tu bloques :* Si la connexion est refusée alors que le laboratoire tourne, vérifie que tu es dans le dossier cyberatelier et que labs.py affiche bien son écoute. Ne change pas le port : les chemins et le client attendent 127.0.0.1:8000.

#### Palier 8 — Livrer la MR2 après un pipeline vert (12 min)

Relire ce que tu livres, pousser la branche, et fusionner seulement après un pipeline vert sur le dernier commit.

**Où tu travailles :** MR GitLab

**Pour comprendre**

- git diff montre les lignes modifiées ; git diff --staged montre celles choisies pour le prochain commit. Le diff de la MR compare toute ta branche à main.
- La demande de fusion (MR dans GitLab, PR dans GitHub) permet de relire le travail avant de l’intégrer à main.

**Actions dans l’ordre**

1. Lance la suite complète avec la commande indiquée au début de la mission.
2. Décris séparément la démonstration du client : le pipeline teste seulement les règles et le classement pur.
3. Relis git status et git diff : la livraison doit contenir headerscope.py et verification.py, avec les modifications nécessaires de cette mission.
4. Ajoute les fichiers par leur nom, relis git diff --staged, puis commite ce qui ne l’est pas encore.
5. Pousse feat/client-http et ouvre la demande de fusion vers main.
6. Dans GitLab, ouvre le pipeline du dernier commit : vérifie qu’il a réellement exécuté les tests et qu’il est vert. Un test local réussi ne le remplace pas.
7. Relis le diff et fusionne lorsque le pipeline et les règles de l’école le permettent.
8. Après la fusion, reviens sur main et lance git pull --ff-only avant la mission suivante.

**Terminal · Relire l’état du dépôt**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git status
git diff main --stat
```

**Terminal · Publier la branche ou ouvrir la demande de fusion**

```bash
git push -u origin feat/client-http
```

**Tu sais que c’est bon quand :** La merge request ne contient que headerscope.py et verification.py (sans __pycache__), et le pipeline du dernier commit est vert dans GitLab.

*Indice si tu bloques :* Un pipeline rouge se lit comme un test : la dernière ligne du journal dit quelle commande a échoué. Si __pycache__ apparaît dans git status, ne l’ajoute pas à la merge request.

**Avant de livrer**

- Le timeout du client vaut 2 secondes et l’URL reste limitée au laboratoire local.
- La fonction pure classe 200, 404 et 500 selon le contrat et H8/H9 couvrent ces retours sans mock avancé.
- Les tests injectés ne sont pas présentés comme preuve de l’I/O réseau ; la CI reste exécutable sans serveur web.
- python3 verification.py affiche OK pour H1 à H9 et se termine avec un code de sortie 0, sans que le laboratoire soit démarré.
- La démonstration du client est documentée à part des tests, et son résultat ne figure pas dans verification.py.

### MR3 — feat/bilan (80 min)

Tu rends lisibles les alertes, les erreurs HTTP et les pannes ; la CI reste indépendante du labo. Avance dans l’ordre des paliers et vérifie chaque résultat avant de poursuivre.

**Avant de commencer**

- Point de départ : MR2 fusionnée ; le client et les règles sont disponibles.
- Ce que tu vas produire : executer_bilan, le texte du bilan, le point d’entrée et README.md ; démonstrations D1 à D3.
- Pourquoi : Tu rends lisibles les alertes, les erreurs HTTP et les pannes ; la CI reste indépendante du labo.
- Commande des tests depuis la racine : `python3 verification.py`. Les cas ci-dessous sont à écrire par toi.

#### Palier 1 — Repartir de main après MR2 (10 min)

Partir de la version fusionnée des MR1 et MR2, dans une branche dédiée au bilan.

**Où tu travailles :** Dépôt

**Pour comprendre**

- La branche principale (main) contient le travail déjà fusionné. Ta branche feat/... reçoit les changements de cette mission.
- Un dépôt « propre » n’a aucune modification en attente : git status te le confirme.

**Actions dans l’ordre**

1. Ouvre workspaces/headerscope dans VS Code, ou Coder dans Cyber Atelier avec cwd sur « . ».
2. Vérifie que MR2 est fusionnée : main contient les deux premières missions.
3. Lis git status ; enregistre ton travail en cours avant de changer de branche.
4. Reviens sur main avec git switch main, mets-la à jour avec git pull --ff-only, puis crée feat/bilan. Remplace main par master si ton dépôt utilise ce nom.
5. Vérifie le nom de ta branche avec git status. Si elle existe déjà, reprends-la avec git switch sans -c.

**Terminal · Relire l’état du dépôt**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git status
```

**Terminal · Après la fusion : actualiser la principale**

```bash
git switch main
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git pull --ff-only
```

**Terminal · Relire l’état du dépôt**

```bash
git log --oneline -6
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git switch -c feat/bilan
```

**Terminal · Relire l’état du dépôt**

```bash
git status
```

**Tu sais que c’est bon quand :** git log --oneline -6 montre les fusions des MR1 et MR2, et git status affiche « On branch feat/bilan ».

*Indice si tu bloques :* Si la branche feat/bilan existe déjà, utilise git switch feat/bilan sans -c, après avoir vérifié avec git log qu’elle contient bien les fusions. Si git pull --ff-only refuse, relis git log avant de continuer.

#### Palier 2 — Choisir un chemin depuis la ligne de commande (10 min)

Lire un argument passé au programme et le refuser s’il n’est pas dans la liste autorisée.

**Où tu travailles :** exemple_choix.py (jetable)

**Pour comprendre**

- sys.argv contient le nom du script puis les arguments du terminal. Le premier argument utilisateur est à la position 1.
- Vérifie la longueur avant de lire cette position pour gérer un lancement sans argument.

**Éditeur · Exemple Python à lire ou essayer**

Éditeur : copie cet exemple dans exemple_choix.py (jetable), enregistre-le, puis lance python3 exemple_choix.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
import sys

FRUITS = ['pomme', 'poire', 'cerise', 'prune']
choix = sys.argv[1] if len(sys.argv) > 1 else 'pomme'
if choix in FRUITS:
    print('fruit choisi :', choix)
else:
    print('inconnu :', choix)
```

**Actions dans l’ordre**

1. Crée exemple_choix.py avec l’exemple des fruits.
2. Lance avec poire : choix admis. Lance avec kiwi : refus.
3. Lance sans argument : valeur par défaut pomme.
4. Repère la lecture de l’argument et la liste autorisée, puis supprime le fichier d’essai.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 exemple_choix.py poire
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 exemple_choix.py kiwi
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 exemple_choix.py
```

**Tu sais que c’est bon quand :** « poire » affiche « fruit choisi : poire », « kiwi » affiche « inconnu : kiwi », et sans argument le programme prend la valeur par défaut.

*Indice si tu bloques :* sys.argv[0] est le nom du script ; le premier vrai argument est sys.argv[1]. Teste d’abord la longueur de la liste pour ne pas planter quand l’argument manque.

#### Palier 3 — Relier le client et les règles (10 min)

Écrire une fonction qui enchaîne les étapes dans le bon ordre : vérifier, demander, classer.

**Où tu travailles :** headerscope.py

**Pour comprendre**

- Orchestrer signifie appeler les étapes dans le bon ordre. Une entrée refusée s’arrête avant toute requête.
- Une panne n’a pas de réponse HTTP à classer.

**Actions dans l’ordre**

1. Crée executer_bilan(chemin) : contrôle le chemin, appelle demander, puis classe une réponse HTTP avec classer_reponse.
2. Pour une panne ou un timeout, conserve le résultat distinct sans classement HTTP.
3. Sous la garde __main__, lis le chemin depuis sys.argv comme dans l’exemple précédent.
4. Garde la cible et les quatre chemins fixes : aucun crawl ni URL arbitraire.
5. Vérifie la compilation, relance H1 à H9 et commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -m py_compile headerscope.py
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 verification.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add headerscope.py
git commit -m "Relie le client, les règles et le classement dans executer_bilan"
```

**Tu sais que c’est bon quand :** py_compile ne signale aucune erreur, H1 à H9 passent, et git log --oneline montre le commit.

*Indice si tu bloques :* Ne refais pas les règles ni le client dans executer_bilan : appelle les fonctions déjà écrites. Une seule fonction assemble les étapes, ce qui permet de tester chaque morceau séparément.

#### Palier 4 — Un bilan lisible et quatre issues distinctes (10 min)

Produire un texte de bilan avec statut, alertes et résumé, et séparer 404, 500, panne et délai.

**Où tu travailles :** headerscope.py

**Pour comprendre**

- La présentation reçoit le résultat et retourne une chaîne ; le lancement principal l’affiche.
- Le texte distingue réponse réussie, erreur HTTP, panne de connexion et timeout.

**Éditeur · Exemple Python à lire ou essayer**

Éditeur : copie cet exemple dans exemple.py (jetable), enregistre-le, puis lance python3 exemple.py. Si plusieurs exemples sont proposés, essaie-les un par un en remplaçant le contenu du fichier. Retire ensuite les fichiers générés et le fichier d’exemple.

```python
produits = [('pomme', 3), ('poire', 0)]
for nom, quantite in produits:
    print(f'{nom} : {quantite} en stock')
```

**Actions dans l’ordre**

1. Écris la présentation sans print : statut, liste d’alertes, résumé « 3 alertes » ou « aucune alerte ».
2. Prévois un libellé différent pour les quatre issues et garde le numéro des erreurs HTTP.
3. Essaie sur les résultats observés ; une panne ne doit pas afficher un faux code HTTP.
4. Vérifie la compilation et commite.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 -m py_compile headerscope.py
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add headerscope.py
git commit -m "Affiche un bilan lisible et distingue les issues HTTP"
```

**Tu sais que c’est bon quand :** Le bilan contient statut, alertes et résumé ; les quatre issues ont des libellés différents ; py_compile ne signale aucune erreur.

*Indice si tu bloques :* Une f-string s’écrit f'{valeur}' et insère la valeur dans le texte. Pour une liste vide d’alertes, écris un texte explicite plutôt que de ne rien afficher.

#### Palier 5 — Vérifier que les tests n’ont pas besoin du laboratoire (10 min)

Prouver que la CI reste verte sans laboratoire, en contrôlant que les tests ne touchent pas le réseau.

**Où tu travailles :** verification.py ; laboratoire

**Pour comprendre**

- Les tests des règles et du classement reçoivent des dictionnaires et des nombres fabriqués.
- Ils doivent passer même quand aucun serveur n’écoute.

**Actions dans l’ordre**

1. Arrête le labo avec son bouton ou Ctrl+C.
2. Lance verification.py : attends 0 avec des tests réellement exécutés.
3. Relis les tests : aucun appel à demander ni urlopen. La recherche proposée doit être vide.
4. Si un appel réel s’est glissé dans la suite, remplace-le par les données directes prévues par H8 et H9.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs. Lance le programme et echo $? ensemble : le nombre affiché est le code du programme ; la console peut afficher code 0 pour echo lui-même.

```bash
python3 verification.py; echo $?
```

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
grep -n 'urlopen\|demander' verification.py
```

**Tu sais que c’est bon quand :** python3 verification.py se termine avec 0, et la commande grep ne trouve aucune ligne.

*Indice si tu bloques :* Si grep trouve une ligne, un test touche au réseau : retire-le des tests, et garde ce contrôle pour la démonstration du palier 7. Le code de sortie doit rester 0 même laboratoire arrêté.

#### Palier 6 — README : périmètre, règles, délai et limites (10 min)

Documenter ce que le programme fait, comment le lancer et ce qu’il ne prouve pas.

**Où tu travailles :** README.md

**Pour comprendre**

- Le README explique où travailler, quelles règles sont vérifiées et comment lancer le programme.
- Une alerte décrit un contrôle d’en-tête précis, sans démontrer qu’un site est exploitable.

**Actions dans l’ordre**

1. Documente 127.0.0.1:8000 et les quatre chemins admis.
2. Explique les trois règles, les normalisations et le timeout de deux secondes.
3. Ajoute lancement, python3 verification.py et la distinction tests hors ligne / labo de démonstration.
4. Écris les limites d’interprétation des en-têtes, puis commite README.md.

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 verification.py
```

**Terminal · Relire l’état du dépôt**

```bash
git status
```

**Terminal · Enregistrer le travail vérifié**

```bash
git add README.md
git commit -m "Documente le périmètre, les règles et les limites de HeaderScope"
```

**Tu sais que c’est bon quand :** README.md contient la commande des tests, le délai de 2 secondes, le périmètre et les limites ; git log --oneline montre le commit.

*Indice si tu bloques :* Un bon README répond à trois questions : que fait le programme, comment le lancer, et qu’est-ce qu’il ne prouve pas. Relis-le comme si tu étais un autre étudiant qui n’a pas vu le cours.

#### Palier 7 — Démonstration D1 à D3 (hors tests) (10 min)

Vérifier le comportement réel du programme sur le laboratoire, sans le confondre avec les tests automatiques.

**Où tu travailles :** Laboratoire local ; headerscope.py

**Pour comprendre**

- D1 à D3 observent manuellement le programme complet et restent séparées de H1 à H9.
- Labo arrêté, l’affichage doit distinguer une panne d’une réponse HTTP d’erreur.

**Actions dans l’ordre**

1. Démarre le labo dans le même environnement que le client.
2. D1 : /fragile donne trois alertes.
3. D2 : /durci donne zéro alerte.
4. D3 : /absent puis /erreur donnent HTTP_ERREUR avec 404 puis 500, sans alerte de politique.
5. Arrête le labo et relance : attends une panne distincte. Consigne les observations hors de verification.py.

**Terminal · Option Mac : démarrer le laboratoire dans un autre terminal**

Terminal séparé sur ton Mac, depuis le dossier cyberatelier. Laisse-le ouvert pendant la démonstration, puis arrête avec Ctrl+C. Dans Docker, utilise plutôt le bouton du laboratoire.

```bash
python3 labs.py
```

**Terminal · Commande à lancer au moment indiqué**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
python3 headerscope.py /fragile
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 headerscope.py /durci
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 headerscope.py /absent
```

**Terminal · Commande à lancer au moment indiqué**

```bash
python3 headerscope.py /erreur
```

**Tu sais que c’est bon quand :** D1 : trois alertes. D2 : zéro alerte. D3 : 404 et 500 identifiés comme erreurs HTTP, sans alerte de politique. Laboratoire arrêté : une panne.

*Indice si tu bloques :* Si tu obtiens une panne au lieu d’une réponse, le laboratoire n’est pas actif : vérifie le bouton de Cyber Atelier ou relance python3 labs.py. Ne change pas de port.

#### Palier 8 — Livrer la MR3 et fermer le bilan (10 min)

Pousser la dernière branche, vérifier le pipeline du dernier commit, puis fusionner seulement si le pipeline est vert.

**Où tu travailles :** MR GitLab

**Pour comprendre**

- git diff montre les lignes modifiées ; git diff --staged montre celles choisies pour le prochain commit. Le diff de la MR compare toute ta branche à main.
- La demande de fusion (MR dans GitLab, PR dans GitHub) permet de relire le travail avant de l’intégrer à main.

**Actions dans l’ordre**

1. Lance la suite complète avec la commande indiquée au début de la mission.
2. Cocher Cyber Atelier indique ton avancement ; cela n’exécute aucun test et n’autorise aucune fusion.
3. Relis git status et git diff : la livraison doit contenir headerscope.py, verification.py et README.md, avec les modifications nécessaires de cette mission.
4. Ajoute les fichiers par leur nom, relis git diff --staged, puis commite ce qui ne l’est pas encore.
5. Pousse feat/bilan et ouvre la demande de fusion vers main.
6. Dans GitLab, ouvre le pipeline du dernier commit : vérifie qu’il a réellement exécuté les tests et qu’il est vert. Un test local réussi ne le remplace pas.
7. Relis le diff et fusionne lorsque le pipeline et les règles de l’école le permettent.
8. Après la fusion, reviens sur main et lance git pull --ff-only avant la mission suivante.

**Terminal · Relire l’état du dépôt**

Terminal du parcours : reste à la racine du dépôt. Exécute ces lignes au moment demandé dans les actions, avec les modifications manuelles entre les blocs.

```bash
git status
git diff main --stat
```

**Terminal · Publier la branche ou ouvrir la demande de fusion**

```bash
git push -u origin feat/bilan
```

**Terminal · Après la fusion : actualiser la principale**

```bash
git switch main
```

**Terminal · Commande à lancer au moment indiqué**

```bash
git pull --ff-only
```

**Tu sais que c’est bon quand :** Le pipeline du dernier commit est vert dans GitLab, la merge request ne contient que les fichiers attendus, et main local contient la fusion (git log --oneline).

*Indice si tu bloques :* Un pipeline vert ne prouve pas que les démonstrations D1 à D3 ont réussi : elles sont séparées. Ne fusionne jamais sur un pipeline rouge ou absent.

**Démonstrations manuelles (hors CI)**

Ces essais utilisent le laboratoire ou les outils réels. Ils sont séparés des tests obligatoires.

**D1 — Résultat fragile**
- Entrée : Réponse locale du chemin /fragile
- Résultat attendu : Trois alertes de politique.

**D2 — Résultat durci**
- Entrée : Réponse locale du chemin /durci
- Résultat attendu : Zéro alerte.

**D3 — Statuts d’erreur**
- Entrée : /absent puis /erreur pendant une démonstration locale
- Résultat attendu : 404 puis 500 identifiés comme erreurs HTTP.

**Avant de livrer**

- La CI vérifie des tests locaux reproductibles et ne prétend pas démarrer le laboratoire scolaire.
- Les quatre chemins restent limités à 127.0.0.1:8000.
- Le README et le bilan distinguent résultats de tests, démonstration et limites des en-têtes.
- python3 verification.py affiche OK pour H1 à H9 et se termine avec 0, laboratoire arrêté.
- Les résultats 404, 500, panne et délai sont affichés avec des libellés distincts.
- La merge request contient headerscope.py, verification.py et README.md, sans __pycache__, et le pipeline du dernier commit est vert.

<!-- END GENERATED EXERCISES -->

## Méthode GitLab

Crée ou utilise un dépôt autorisé par ton école. Vérifie que le runner est actif pour les branches non protégées de MR et que tu as les droits d’ouverture et de fusion. Dans la configuration de la branche principale, applique les règles de l’école et exige les pipelines réussis. Pour chaque étape, branche-toi depuis la principale actualisée, exécute les tests, lis le diff, pousse une MR et fusionne le dernier commit vert. Après chaque fusion, mets à jour la base avant la branche suivante.

La CI doit réellement exécuter les tests. Ne masque pas les erreurs, ne rends pas le job facultatif et ne prends pas un lint valide pour preuve qu’un runner fonctionne. Si l’école n’offre pas de runner ou de règle de fusion, note cette limite au lieu de déclarer le gate validé.

## Repères de temps

Préparation GitLab et lecture : 30 min. MR1 règles et tests : 85 min. MR2 client et erreurs : 85 min. MR3 orchestration, bilan et README : 80 min. Démonstration, relecture et marge : 20 min. Total : 300 min.

## Livrables et limites

Le dossier HeaderScope est vide au départ. Depuis son terminal, clone le dépôt directement dans le dossier courant avec git clone <URL_DU_DEPOT> . avant de créer les fichiers. Le point signifie « ici ». Les commandes du terminal web repartent chacune du dossier courant explicite ; un cd seul ne persiste pas. Pour Git interactif, utilise docker compose exec atelier bash depuis le dossier Cyber Atelier.

Livre un programme, une suite de tests locale utile, une configuration CI, un README clair, trois MR successives et un bilan honnête de ce que la CI et la démonstration valident. Les tests de règles sont autonomes et réalisables sur un runner ordinaire. La démonstration des quatre chemins utilise le laboratoire local de Cyber Atelier quand il est démarré explicitement.

Les en-têtes constituent des signaux de configuration, pas une preuve complète de sécurité. Le client ne visite que les chemins de laboratoire nommés et ne se connecte qu’à 127.0.0.1:8000. La CI de base ne vérifie pas la disponibilité du laboratoire. Une alerte ne prouve pas qu’un site est exploitable ou sûr.
