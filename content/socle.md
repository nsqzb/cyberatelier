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

Écris 4 petites fonctions, chacune avec ses tests : à chaque palier, tu écris un test, tu le vois échouer, tu écris le code qui le fait passer, puis tu fais un commit.

Tu avances en 8 paliers. À chaque palier de code : un test, il échoue, tu écris le code qui le fait passer, tu fais un commit. Les fichiers sont `outils.py` et `test_outils.py`.

#### Palier 1 — Prépare ton dépôt et ta branche (10 min)

Avoir un dossier propre, relié à GitHub, sur la branche de la mission.

- Ouvre le dossier workspaces/socle de Cyber Atelier dans VS Code, puis un terminal (Terminal > New Terminal).
- Une branche est une ligne de travail séparée de main : tu codes dessus sans risque, et main ne bouge pas tant que tu n’as pas fusionné.
- Crée la branche de la mission et vérifie où tu es.

```bash
git switch -c feat/bases
```

```bash
git status
```

**Tu sais que c’est bon quand :** git status affiche « On branch feat/bases » et « nothing to commit, working tree clean ».

*Indice :* Si Git répond « not a git repository », tu n’es pas dans le bon dossier. Si la branche existe déjà, utilise git switch feat/bases (sans -c).

#### Palier 2 — Écris ton tout premier test (10 min)

Comprendre à quoi sert un test avant d’en écrire pour de vrai.

- Crée un fichier exemple.py (jetable, il ne sera pas livré) et recopie le code ci-dessous. Ici, doubler est un exemple sans rapport avec ton exercice.
- Lance-le. Puis remplace 8 par 9, relance et lis le message : c’est ainsi que Python te dit qu’un test échoue. Remets 8.
- Retiens la forme : une classe qui hérite de unittest.TestCase, des méthodes dont le nom commence par test_, et assertEqual(obtenu, attendu).
- Quand c’est compris, supprime le fichier : rm exemple.py.

```
import unittest

def doubler(n):
    return n * 2

class TestDoubler(unittest.TestCase):
    def test_doubler_un_nombre(self):
        self.assertEqual(doubler(4), 8)

if __name__ == "__main__":
    unittest.main()
```

```bash
python3 exemple.py -v
```

**Tu sais que c’est bon quand :** Tu as vu « OK » avec 8, puis « FAIL » avec 9, et tu sais lire la ligne « AssertionError: 8 != 9 ».

*Indice :* Si python3 n’est pas trouvé, tape python3 --version dans le terminal de VS Code. Les messages d’échec se lisent de bas en haut : la dernière ligne dit ce qui ne va pas.

#### Palier 3 — Un test d’abord, puis la fonction : les noms valides (15 min)

Écrire un test AVANT le code (il échoue), puis le minimum de code pour le faire passer.

- Crée test_outils.py : importe unittest et from outils import valider_nom_utilisateur, puis une classe TestValiderNomUtilisateur avec un test pour S1.
- Lance les tests : ils échouent parce que outils.py n’existe pas encore. C’est la phase « rouge », elle est normale.
- Crée outils.py avec valider_nom_utilisateur(nom), qui retourne True ou False. Fais passer S1 : c’est la phase « verte ».
- Contrat complet de la fonction, que tu vas compléter aux deux paliers suivants : le nom fait de 3 à 16 caractères, commence par une lettre ASCII, puis ne contient que des lettres ASCII, des chiffres, _ ou -. Les espaces de début et de fin sont retirés avant le contrôle. Un nom qui n’est pas une chaîne lève TypeError.

```bash
python3 -m unittest -v
```

```bash
git add outils.py test_outils.py
```

```bash
git commit -m "Ajoute valider_nom_utilisateur pour les noms valides"
```

- **S1** — Nom valide simple. Entrée : « alice », « Alice_01 », « a-b-c » Attendu : True pour les trois.

**Tu sais que c’est bon quand :** python3 -m unittest -v affiche 1 test OK, et git log --oneline montre ton nouveau commit.

*Indice :* La fonction n’a pas besoin d’être maligne maintenant : S1 ne vérifie que des noms valides. Écris le test suivant avant de compliquer la fonction.

#### Palier 4 — Les limites : longueur et caractères (15 min)

Faire échouer un test, puis compléter la fonction règle par règle.

- Ajoute les tests S2 et S3, lance-les : certains échouent.
- Complète valider_nom_utilisateur : longueur de 3 à 16, première lettre ASCII, caractères suivants autorisés.
- Relance les tests après chaque règle ajoutée : tu avances par petits pas, jamais à l’aveugle.

```bash
python3 -m unittest -v
```

```bash
git add outils.py test_outils.py
```

```bash
git commit -m "Contrôle la longueur et les caractères des noms"
```

- **S2** — Bornes de longueur. Entrée : « abc » (3 caractères), une chaîne valide de 16 caractères, « ab » (2), une chaîne valide de 17 caractères Attendu : True pour 3 et 16 caractères, False pour 2 et 17.
- **S3** — Premier caractère et caractères interdits. Entrée : « 1alice », « _alice », « ali ce », « ali.ce », « alicé », chaîne vide Attendu : False pour les six cas.

**Tu sais que c’est bon quand :** S1, S2 et S3 passent.

*Indice :* Piège : str.isalpha() et str.isalnum() acceptent aussi les lettres accentuées comme « é ». Pour rester en ASCII, compare chaque caractère à la chaîne string.ascii_letters (module string), ou teste avec str.isascii().

#### Palier 5 — Espaces et mauvais types (12 min)

Gérer deux cas limites, dont une erreur levée volontairement.

- Ajoute les tests S4 et S5.
- S4 : les espaces autour du nom sont retirés avant le contrôle.
- S5 : un nom qui n’est pas une chaîne lève TypeError. Pour tester une exception avec unittest, la forme est celle de l’exemple ci-dessous (ici avec int, sans rapport avec ton exercice).
- Écris le code pour que tout passe, puis fais un commit.

```
with self.assertRaises(ValueError):
    int("abc")
```

```bash
python3 -m unittest -v
```

```bash
git add outils.py test_outils.py
```

```bash
git commit -m "Gère les espaces et les types invalides"
```

- **S4** — Espaces de bord. Entrée : « bob » entouré d’espaces, puis « b » entouré d’espaces Attendu : True pour « bob » après retrait des espaces ; False pour « b », qui fait 1 caractère.
- **S5** — Type non chaîne. Entrée : None, puis 42 Attendu : Les deux appels lèvent TypeError (assertRaises).

**Tu sais que c’est bon quand :** S1 à S5 passent.

*Indice :* isinstance(nom, str) vérifie le type. Fais ce contrôle en premier, avant d’appeler une méthode de chaîne comme strip().

#### Palier 6 — Lire une ligne de journal (15 min)

Transformer une ligne de texte en données avec split, un dictionnaire et None.

- Le journal fictif contient des lignes comme « 2026-01-05 08:12:44 LOGIN_OK alice 192.0.2.10 » : date, heure, événement, utilisateur, adresse IP.
- Contrat de analyser_ligne(ligne) : elle retourne un dictionnaire avec les clés date, heure, evenement, utilisateur et ip. Elle retourne None si la ligne est vide (après retrait des espaces de bord), si elle n’a pas exactement 5 champs, si l’événement n’est ni LOGIN_OK ni LOGIN_FAIL, ou si l’adresse n’a pas exactement 4 nombres entiers de 0 à 255 séparés par des points.
- Procède test par test : S6 d’abord, puis S7, puis S8. Un test, un correctif.

```bash
python3 -m unittest -v
```

```bash
git add outils.py test_outils.py
```

```bash
git commit -m "Ajoute analyser_ligne"
```

- **S6** — Ligne de journal nominale. Entrée : « 2026-01-05 08:12:44 LOGIN_OK alice 192.0.2.10 » Attendu : Dictionnaire exact : date « 2026-01-05 », heure « 08:12:44 », evenement « LOGIN_OK », utilisateur « alice », ip « 192.0.2.10 ».
- **S7** — Lignes refusées par la structure ou l’événement. Entrée : Chaîne vide ; ligne à 4 champs ; ligne à 6 champs ; événement « LOGIN_BOOM » Attendu : None pour les quatre cas.
- **S8** — Adresse invalide. Entrée : ip « 192.0.2.300 », ip « 192.0.2 », ip « abc.def.ghi.jkl » Attendu : None pour les trois lignes.

**Tu sais que c’est bon quand :** S1 à S8 passent.

*Indice :* split() sans argument découpe sur les espaces et ignore ceux des bords. Pour l’adresse, découpe sur les points puis vérifie chaque morceau : est-ce des chiffres, puis est-ce entre 0 et 255 ?

#### Palier 7 — Compter les événements (13 min)

Parcourir une liste avec une boucle et construire des dictionnaires.

- compter_evenements(evenements) reçoit une liste de dictionnaires renvoyés par analyser_ligne. Elle retourne toujours les deux clés LOGIN_OK et LOGIN_FAIL, même à zéro, et ne modifie pas la liste reçue.
- echecs_par_utilisateur(evenements) ne garde que les utilisateurs ayant au moins un LOGIN_FAIL, avec leur nombre d’échecs. Une liste vide donne un dictionnaire vide.
- Écris S9 puis la première fonction, puis S10 et la seconde.

```bash
python3 -m unittest -v
```

```bash
git add outils.py test_outils.py
```

```bash
git commit -m "Ajoute le comptage des événements et des échecs"
```

- **S9** — Comptage des événements. Entrée : Liste vide, puis deux LOGIN_OK et un LOGIN_FAIL. Vérifier aussi que la liste d’entrée est identique avant et après l’appel. Attendu : Liste vide : LOGIN_OK 0 et LOGIN_FAIL 0. Deuxième cas : LOGIN_OK 2 et LOGIN_FAIL 1. Liste inchangée.
- **S10** — Échecs par utilisateur. Entrée : Liste vide ; alice avec deux LOGIN_FAIL ; bob avec un seul LOGIN_OK ; carol avec un LOGIN_FAIL Attendu : Liste vide : {}. Cas mixte : {"alice": 2, "carol": 1}, sans bob.

**Tu sais que c’est bon quand :** Les 10 tests S1 à S10 passent.

*Indice :* Pars d’un dictionnaire qui contient déjà les deux clés à 0, puis parcours la liste avec une boucle for. dict.get(clé, 0) renvoie 0 quand la clé n’existe pas encore.

#### Palier 8 — Livre ta pull request (10 min)

Relire ton travail, le pousser sur GitHub et le fusionner proprement.

- Regarde ce que tu vas livrer : fichiers modifiés et historique.
- Pousse la branche, puis ouvre la pull request (GitHub dit pull request ; GitLab dit merge request, c’est la même idée).
- Relis le diff dans GitHub comme si c’était le code de quelqu’un d’autre. Ici aucun contrôle automatique ne tourne : c’est toi qui vérifies que les 10 tests passent en local avant de fusionner. Un pipeline viendra avec les parcours GitLab.
- Clique sur « Merge pull request » dans GitHub, puis reviens sur main à jour pour préparer la mission suivante.

```bash
git status
```

```bash
git diff main --stat
```

```bash
git push -u origin feat/bases
```

```bash
gh pr create --base main --title "Bases : validation et analyse de journal" --body "Ajoute outils.py et ses tests S1 à S10."
```

```bash
git switch main
```

```bash
git pull --ff-only
```

**Tu sais que c’est bon quand :** La pull request ne contient que outils.py et test_outils.py, et ton main local contient la fusion (git log --oneline).

*Indice :* Si gh pr create se plaint d’une branche non poussée, lance d’abord git push -u origin feat/bases. Fusionne uniquement quand git status est propre et les 10 tests passent.

**Avant de livrer :**
- python3 -m unittest -v affiche OK pour S1 à S10.
- git log --oneline montre un commit par palier de code (au moins cinq).
- La pull request ne contient que outils.py et test_outils.py, sans __pycache__ ni fixtures.

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
