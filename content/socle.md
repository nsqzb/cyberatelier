# Socle Python & Git — bases, tests et premier travail en équipe

**Durée : 5 heures · Niveau débutant · 3 merge requests**

Ce parcours est le point d’entrée de Cyber Atelier. Tu connais déjà les variables, les listes et les fonctions. Ici, tu vas écrire de petites fonctions pures, les tester avec unittest, lire un journal de connexions fictif, puis livrer le tout avec Git comme le ferait une équipe. Les données sont entièrement fictives : aucune cible réseau, aucun outil offensif. Le but est d’arriver à PortPilot, HeaderScope et FileGuard avec les réflexes en place.

Les exercices ne donnent aucune solution. Tu trouveras des contrats précis (entrées, sorties, erreurs, cas limites), des tests décrits en prose et des indices progressifs. Pratique chaque commande Git sur ton propre dépôt : le guide ne remplace pas le cours.

## Contrat du programme

Le programme final tient en trois fichiers Python et un README :

- `outils.py` : fonctions pures de validation et de comptage (MR1) ;
- `journal.py` : lecture de fichier, erreurs, JSON et rapport de données (MR2) ;
- `analyseur.py` : affichage du rapport et point d’entrée en ligne de commande (MR3).

Chaque fichier a son fichier de tests : `test_outils.py`, `test_journal.py`, `test_analyseur.py`. Tous utilisent unittest, lancé avec `python -m unittest` depuis le dossier du projet. Aucun `pip install`, aucun pytest.

Le journal fictif est `fixtures/socle/auth.log`. Tu le copies dans la console avec la commande de préparation ; les originaux sont en lecture seule, la copie est modifiable. Il n’est jamais versionné : ton `.gitignore` l’exclut.

Le format d’une ligne de journal est :

`AAAA-MM-JJ HH:MM:SS EVENEMENT utilisateur ip`

Par exemple : `2026-01-05 08:12:44 LOGIN_OK alice 192.0.2.10`. Les événements acceptés sont `LOGIN_OK` et `LOGIN_FAIL`. Une ligne qui ne respecte pas ce format est « malformée » : elle est comptée, pas une raison de planter.

## Les trois MR

Les minutes de chaque mission sont incluses dans les 300 minutes du parcours (voir la section Repères de temps).

### MR1 — feat/bases (100 min)

Crée le fichier `outils.py` et `test_outils.py`. Les fonctions de ce fichier ne lisent aucun fichier et n’affichent rien : elles reçoivent des valeurs et renvoient un résultat.

Contrats à implémenter :

1. `valider_nom_utilisateur(nom)` retourne `True` ou `False`. Si `nom` n’est pas une chaîne, elle lève `TypeError`. Les espaces de début et de fin sont retirés avant contrôle. Le nom doit faire entre 3 et 16 caractères, commencer par une lettre ASCII, et ne contenir ensuite que des lettres ASCII, des chiffres, `_` ou `-`. La casse est conservée et n’influence pas le résultat.
2. `analyser_ligne(ligne)` retourne un dictionnaire aux clés `date`, `heure`, `evenement`, `utilisateur` et `ip`, ou `None`. Elle retourne `None` si la ligne est vide après retrait des espaces de bord, si elle n’a pas exactement cinq champs, si l’événement n’est ni `LOGIN_OK` ni `LOGIN_FAIL`, ou si l’adresse n’a pas exactement quatre nombres entiers de 0 à 255 séparés par des points.
3. `compter_evenements(evenements)` prend une liste de dictionnaires renvoyés par `analyser_ligne`. Elle retourne toujours les clés `LOGIN_OK` et `LOGIN_FAIL`, même à zéro, et ne modifie pas la liste reçue.
4. `echecs_par_utilisateur(evenements)` ne retient que les utilisateurs ayant au moins un `LOGIN_FAIL`, avec leur nombre d’échecs. Une liste vide donne un dictionnaire vide.

Le premier unittest utilise une classe qui hérite de `unittest.TestCase`, des méthodes nommées `test_...` et les assertions `assertEqual`, `assertIsNone`, `assertTrue`, `assertFalse` et `assertRaises`. Un test relancé à chaque modification prouve qu’une correction n’en casse pas une autre : c’est le réflexe que demandera le futur framework.

Tests à écrire (ids S1 à S10) :

- **S1** : noms valides simples (`alice`, `Alice_01`, `a-b-c`) donnent `True`.
- **S2** : bornes de longueur : 3 et 16 caractères valides, 2 et 17 refusés.
- **S3** : premier caractère et caractères interdits (`1alice`, `_alice`, `ali ce`, `ali.ce`, `alicé`, chaîne vide) donnent `False`.
- **S4** : espaces de bord : un nom `bob` entouré d’espaces est valide ; `b` entouré d’espaces ne l’est pas, car il ne fait qu’un caractère.
- **S5** : `None` et `42` lèvent `TypeError`.
- **S6** : la ligne nominale `2026-01-05 08:12:44 LOGIN_OK alice 192.0.2.10` donne le dictionnaire exact attendu.
- **S7** : chaîne vide, ligne à 4 champs, ligne à 6 champs, événement `LOGIN_BOOM` donnent `None`.
- **S8** : adresses `192.0.2.300`, `192.0.2` et `abc.def.ghi.jkl` donnent `None`.
- **S9** : comptage d’une liste vide (zéros pour les deux clés), puis de deux `LOGIN_OK` et un `LOGIN_FAIL` ; la liste d’entrée est identique avant et après l’appel.
- **S10** : échecs par utilisateur : liste vide donne `{}` ; dans le cas mixte alice (deux échecs), bob (succès seul) et carol (un échec), le résultat est `{"alice": 2, "carol": 1}`.

Pour la partie Git, tu livres cette MR de bout en bout :

- crée un `.gitignore` avec au moins `__pycache__/` et `fixtures/` ;
- vérifie avec `git status` et `git diff` ce qui sera commité ;
- ajoute les fichiers voulus avec `git add`, fais un commit au message clair à l’impératif, relis avec `git log --oneline` ;
- pousse la branche avec `git push -u origin feat/bases` et ouvre la merge request vers la branche principale ;
- relis le diff de la MR avant de la déclarer prête.

Ce que tu dois observer : `python -m unittest -v` affiche OK pour S1 à S10, `git status` est propre après commit, le diff de la MR ne contient que `.gitignore`, `outils.py` et `test_outils.py`.

### MR2 — feat/fichiers-erreurs (100 min)

Repars de la branche principale à jour (`git switch main`, `git pull`), puis crée `feat/fichiers-erreurs`. Ajoute `journal.py` et `test_journal.py`.

Contrats à implémenter :

1. `verifier_chemin(chemin)` lève `ValueError` si le chemin est vide ou ne contient que des espaces, sans accéder au disque.
2. `lire_journal(chemin)` appelle `verifier_chemin`, lit le fichier en UTF-8 avec `pathlib`, retourne une liste de chaînes sans espaces de bord et sans lignes vides. Elle laisse remonter `FileNotFoundError` si le fichier est absent.
3. `charger_evenements(lignes)` retourne un couple `(evenements, malformees)`. `evenements` contient les dictionnaires valides obtenus avec `analyser_ligne` de `outils.py`, dans l’ordre d’arrivée ; `malformees` compte les lignes refusées. Une liste vide donne `([], 0)`.
4. `construire_rapport(evenements, nb_malformees)` retourne un dictionnaire aux clés `lignes_valides`, `login_ok`, `login_fail`, `lignes_malformees` et `echecs_par_utilisateur`. Réutilise `compter_evenements` et `echecs_par_utilisateur`.
5. `sauvegarder_rapport(rapport, chemin)` écrit le JSON avec `json.dump` (UTF-8, `ensure_ascii=False`, `indent=2`). `charger_rapport(chemin)` le relit avec `json.load`. Si le JSON est invalide, elle attrape `json.JSONDecodeError` et lève `ValueError` avec un message en français qui nomme le fichier. `FileNotFoundError` reste levé telle quelle.

Tests à écrire avec `tempfile.TemporaryDirectory` pour fabriquer chaque fichier (ids S11 à S18) :

- **S11** : fichier de trois lignes, une ligne vide et des espaces en fin de ligne : liste de trois chaînes, dans l’ordre, nettoyées.
- **S12** : chemin inexistant dans un dossier temporaire : `FileNotFoundError`.
- **S13** : chaîne vide, chaîne de trois espaces : `ValueError` ; `dossier/auth.log` : aucune exception.
- **S14** : quatre lignes dont deux invalides (une mauvaise structure, un événement inconnu) : deux événements dans l’ordre et `malformees` à 2 ; liste vide : `([], 0)`.
- **S15** : trois `LOGIN_OK`, deux `LOGIN_FAIL` dont deux pour alice, une ligne malformée : `lignes_valides` 5, `login_ok` 3, `login_fail` 2, `lignes_malformees` 1, `echecs_par_utilisateur` `{"alice": 2}`.
- **S16** : rapport avec une clé et une valeur accentuées, sauvegardé puis rechargé : le résultat est égal à l’original, et le fichier est relu sans erreur par `json.load`.
- **S17** : fichier contenant `{pas du json` : `ValueError` ; chemin absent : `FileNotFoundError`.
- **S18** : `construire_rapport([], 0)` donne des zéros et `{}`, sans exception.

Démonstration locale (D1, hors tests) : un script qui lit la copie `fixtures/socle/auth.log` avec les trois fonctions de lecture. Vérifie que `lignes_valides + lignes_malformees` est égal au nombre de lignes non vides du fichier, que tu comptes avec une commande de ton choix.

Pratique Git, sur ta branche, dans cet ordre :

1. fais un commit volontairement fautif (une fonction cassée) et constate l’échec des tests ;
2. annule-le avec `git revert`, sans réécrire l’historique ;
3. mets une modification en cours de côté avec `git stash`, puis récupère-la avec `git stash pop` ;
4. annule une modification de fichier non commitée avec `git restore` ;
5. relis `git log --oneline`, pousse, ouvre la MR.

Ce que tu dois observer : les tests S1 à S18 passent, `git log --oneline` montre le commit fautif et son revert, `git stash list` est vide à la fin.

### MR3 — feat/analyseur (70 min)

Crée `analyseur.py`, `test_analyseur.py` et `README.md` dans `feat/analyseur`, toujours depuis la branche principale à jour.

Contrats à implémenter :

1. `formater_rapport(rapport)` retourne une chaîne, sans rien afficher. Quatre lignes fixes et dans cet ordre : `Lignes valides : `, `Connexions réussies : `, `Échecs de connexion : `, `Lignes malformées : `. Suit une ligne par utilisateur en échec, triés par ordre alphabétique. Sans échec, la ligne `Aucun échec` remplace ces lignes.
2. `main(argv)` retourne un code de retour entier et ne ferme jamais le programme. `argv` vide : message d’usage sur la sortie d’erreur, code 2. Fichier absent ou invalide : message clair sur la sortie d’erreur, code 1. Succès : affiche le rapport et retourne 0. `main` est le seul endroit qui attrape `FileNotFoundError` et `ValueError`.
3. Le fichier se termine par le bloc standard `if __name__ == "__main__"`, qui transmet les arguments à `main` et utilise son résultat comme code de sortie. Importer le module n’affiche rien.

Tests à écrire avec unittest (ids S19 à S24) :

- **S19** : rapport complet : les compteurs ont leurs valeurs, et alice apparaît avant bob.
- **S20** : sans échec : la chaîne contient `Aucun échec` et aucune ligne d’utilisateur.
- **S21** : `main([])` : code 2, message sur la sortie d’erreur, rien sur la sortie standard.
- **S22** : chemin absent dans un dossier temporaire : code 1, aucune exception ne sort de `main`.
- **S23** : fichier temporaire de deux lignes valides et une malformée : code 0, et la sortie contient `Lignes valides : 2` et `Lignes malformées : 1`.
- **S24** : importer le module dans un test, sortie redirigée : aucune sortie.

Utilise `io.StringIO` et `contextlib.redirect_stdout` pour capturer la sortie.

Le `README.md` doit contenir : l’objectif du programme, le format du journal, la commande d’usage, les codes de retour (0, 1, 2) et les limites (données fictives, aucune connexion réseau).

Démonstration locale (D2, hors tests) : lance `python analyseur.py fixtures/socle/auth.log` (rapport et code 0), puis `python analyseur.py` sans argument (message d’usage et code 2). Vérifie le code avec `echo $?`.

Pratique Git, guidée pas à pas. Le conflit est volontaire et reste local :

1. depuis la branche principale à jour, crée `exercice/conflit-a`, modifie la première ligne de `README.md` et commite ;
2. reviens sur la branche principale, crée `exercice/conflit-b`, modifie la même ligne différemment et commite ;
3. depuis `exercice/conflit-a`, lance `git merge exercice/conflit-b` : un conflit apparaît ;
4. lis `git status`, repère les marqueurs `<<<<<<<`, `=======` et `>>>>>>>`, garde la ligne voulue, supprime les marqueurs, puis `git add` et `git commit` ; si tu veux recommencer, `git merge --abort` annule la fusion en cours ;
5. supprime les deux branches d’exercice avec `git branch -d`.

Ensuite, sur `feat/analyseur` :

- après une petite modification de la branche principale (par exemple une correction dans `README.md`), lance `git rebase main` et relis `git log --oneline --graph` ;
- pose le tag annoté `v0.1.0` avec `git tag -a v0.1.0 -m "Analyseur de journal, version 0.1.0"` ;
- pousse la branche, ouvre la MR vers la branche principale, relis son diff ; ne pousse le tag que si ton école l’autorise.

Ce que tu dois observer : les tests S1 à S24 passent, aucun marqueur de conflit ne reste dans `README.md`, `git tag -l` affiche `v0.1.0`, les branches `exercice/` n’apparaissent pas sur GitLab.

## Méthode GitLab et Git

Chaque MR suit le même cycle, que tu dois pratiquer sur ton dépôt :

1. mettre la branche principale à jour (`git switch main`, `git pull`) ;
2. créer la branche de la MR (`git switch -c feat/...`) ;
3. écrire le code et les tests, puis lancer `python -m unittest` ;
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

Dans la console du parcours, dans l’ordre : vérifie Python et Git, configure ton identité Git avec tes propres valeurs (commande à faire une seule fois), clone le dépôt (commande interactive, dans `docker compose exec atelier bash`, puis `cd /workspaces/socle`), vérifie avec `git status`, copie les fixtures, crée la branche `feat/bases`.

## Livrables

- Dépôt contenant `outils.py`, `journal.py`, `analyseur.py`, leurs tests unittest, `README.md` et `.gitignore`.
- Trois MR successives, chacune créée depuis la branche principale à jour et relue avant fusion.
- Tests S1 à S24 exécutés localement avec `python -m unittest` ; démonstrations D1 et D2 faites à la main, hors CI.
- Tag `v0.1.0` posé, avec conflit et rebase réalisés sur des branches locales.

## Limites

- Données entièrement fictives (`fixtures/socle`, adresses 192.0.2.0/24) ; aucun réseau, aucune cible, aucun outil offensif.
- Les tests obligatoires n’ouvrent pas `fixtures/` et n’ont besoin d’aucun service : ils tournent sur un runner sans labo. La lecture de `auth.log` reste une démonstration locale.
- Le parcours n’introduit ni pytest, ni packaging, ni CI complète : ce sont des étapes ultérieures.
- Le conflit et le rebase sont provoqués sur des branches locales jetables, jamais sur la branche principale.

## Bilan honnête

À la fin de ce parcours, tu dois être capable d’écrire une petite fonction pure avec ses cas limites, de la tester avec unittest, de lire un fichier en gérant les erreurs, de manipuler JSON, et de livrer une MR propre avec Git : branche, commit, push, relecture, conflit résolu, tag.

Ce que ce parcours ne fait pas encore : écrire un package installable, utiliser `subprocess` ou `argparse` dans un vrai programme de sécurité, mettre en place une CI complète sur ton propre runner. Tu les rencontreras dans PortPilot, HeaderScope et FileGuard, puis dans le framework. Ne compte pas sur ce parcours pour être autonome sur ces sujets : il te donne les fondations, la pratique reste à faire.
