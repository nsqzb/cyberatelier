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

#### Palier 1 — Prépare ton dépôt et ta branche (10 min)

Avoir un dossier propre, relié à GitHub, sur la branche de la mission.

- Ouvre le dossier workspaces/socle de Cyber Atelier dans VS Code, puis un terminal (Terminal > New Terminal).
- Une branche est une ligne de travail séparée de main : tu codes dessus sans risque, et main ne bouge pas tant que tu n’as pas fusionné.
- Crée la branche de la mission et vérifie où tu es.

```
git switch -c feat/bases
```

```
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

```
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

```
python3 -m unittest -v
```

```
git add outils.py test_outils.py
```

```
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

```
python3 -m unittest -v
```

```
git add outils.py test_outils.py
```

```
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

```
python3 -m unittest -v
```

```
git add outils.py test_outils.py
```

```
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

```
python3 -m unittest -v
```

```
git add outils.py test_outils.py
```

```
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

```
python3 -m unittest -v
```

```
git add outils.py test_outils.py
```

```
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

```
git status
```

```
git diff main --stat
```

```
git push -u origin feat/bases
```

```
gh pr create --base main --title "Bases : validation et analyse de journal" --body "Ajoute outils.py et ses tests S1 à S10."
```

```
git switch main
```

```
git pull --ff-only
```

**Tu sais que c’est bon quand :** La pull request ne contient que outils.py et test_outils.py, et ton main local contient la fusion (git log --oneline).

*Indice :* Si gh pr create se plaint d’une branche non poussée, lance d’abord git push -u origin feat/bases. Fusionne uniquement quand git status est propre et les 10 tests passent.

**Avant de livrer :**
- python3 -m unittest -v affiche OK pour S1 à S10.
- git log --oneline montre un commit par palier de code (au moins cinq).
- La pull request ne contient que outils.py et test_outils.py, sans __pycache__ ni fixtures.

### MR2 — feat/fichiers-erreurs (100 min)

Ajoute journal.py et test_journal.py par paliers : à chaque palier, tu écris un test, tu le vois échouer, tu écris le minimum de code, puis tu fais un commit. Le module lit la copie du journal fictif, compte les lignes malformées sans s’arrêter, gère les erreurs de fichier et le JSON, puis produit un rapport de données. Pourquoi : un journal réel est imparfait ; un outil de sécurité compte ce qu’il ne comprend pas, sans planter au premier problème. Tu apprends aussi à défaire proprement : revert, stash, restore.

#### Palier 1 — Repars d’une base à jour (8 min)

Partir de main à jour, sur une branche neuve, avant d’écrire la moindre ligne.

- Reviens sur main, mets-la à jour, puis crée la branche de la MR2. Pourquoi : chaque MR part d’une base à jour, sinon tu travailles sur un code périmé.
- Relis l’historique : la MR1 doit y être.
- Crée les deux fichiers vides journal.py et test_journal.py : tes premiers tests vont les utiliser.

```
git switch main
```

```
git pull --ff-only
```

```
git switch -c feat/fichiers-erreurs
```

```
git log --oneline
```

```
touch journal.py test_journal.py
```

```
git status
```

**Tu sais que c’est bon quand :** git status affiche « On branch feat/fichiers-erreurs » et deux fichiers non suivis : journal.py et test_journal.py.

*Indice :* Si git pull --ff-only refuse, main a divergé : ne force rien, demande de l’aide. Si la branche existe déjà, utilise git switch feat/fichiers-erreurs (sans -c).

#### Palier 2 — Refuser un chemin vide, sans toucher au disque (10 min)

Écrire un test pour une fonction qui valide une entrée, puis la faire passer.

- Pourquoi : un chemin vide ou blanc est une erreur d’appel ; il faut la signaler avant d’ouvrir quoi que ce soit.
- Dans test_journal.py, écris la classe TestVerifierChemin avec le test S13 : chaîne vide, trois espaces, puis « dossier/auth.log » qui ne doit lever aucune exception.
- Lance les tests : ils échouent, puisque verifier_chemin n’existe pas encore. C’est la phase rouge.
- Écris verifier_chemin(chemin) dans journal.py : elle lève ValueError si le chemin, après retrait des espaces de bord, est vide. Elle ne lit aucun fichier. Relance : c’est la phase verte.
- Fais un commit.

```
def diviser(a, b):
    if b == 0:
        raise ZeroDivisionError("b ne doit pas être zéro")
    return a / b
```

```
python3 -m unittest -v
```

```
git add journal.py test_journal.py
```

```
git commit -m "Ajoute verifier_chemin et refuse les chemins vides"
```

- **S13** — Chemin vide ou blanc. Entrée : Chaîne vide, une chaîne de trois espaces, puis « dossier/auth.log » Attendu : ValueError pour les deux premiers cas ; aucune exception pour le troisième, sans accès au disque.

**Tu sais que c’est bon quand :** S13 passe, et git log --oneline montre ton nouveau commit. Le test passe sans fichier présent : aucun accès au disque.

*Indice :* Retire les espaces avec str.strip() avant de comparer à la chaîne vide. Vérifie la condition en premier : tu n’as pas encore besoin de pathlib.

#### Palier 3 — Lire un fichier UTF-8 et nettoyer ses lignes (14 min)

Lire un fichier avec pathlib, puis écarter les lignes vides et les espaces de bord.

- Pourquoi : pathlib donne un chemin qui marche partout ; l’encodage UTF-8 évite les surprises avec les accents.
- Exemple sans rapport (une liste de courses) : écrire puis relire un fichier dans un dossier temporaire.
- Écris le test S11 : un fichier temporaire de trois lignes, une ligne vide et des espaces en fin de ligne. lire_journal doit renvoyer trois chaînes propres, dans l’ordre.
- Lance les tests : rouge. Écris lire_journal(chemin) : elle appelle verifier_chemin en premier, lit le fichier en UTF-8, puis retourne une liste sans espaces de bord et sans lignes vides.
- Relance : vert, puis commit.

```
import pathlib
import tempfile

with tempfile.TemporaryDirectory() as dossier:
    chemin = pathlib.Path(dossier) / "courses.txt"
    chemin.write_text("pain\nlait\n", encoding="utf-8")
    print(chemin.read_text(encoding="utf-8").splitlines())
```

```
python3 -m unittest -v
```

```
git add journal.py test_journal.py
```

```
git commit -m "Ajoute lire_journal avec nettoyage des lignes"
```

- **S11** — Lecture nettoyée. Entrée : Fichier temporaire de trois lignes, une ligne vide et des espaces en fin de ligne Attendu : Liste de trois chaînes, dans l’ordre, sans espaces de bord et sans ligne vide.

**Tu sais que c’est bon quand :** S11 et S13 passent. Le fichier temporaire disparaît tout seul : git status ne montre aucun fichier de test.

*Indice :* read_text(encoding="utf-8") lit tout le fichier ; splitlines() le découpe en lignes. Pour écarter les lignes vides après retrait des espaces, une boucle for et un test sur la chaîne nettoyée suffisent.

#### Palier 4 — Laisser remonter l’erreur de fichier absent (8 min)

Comprendre qu’une erreur qui n’est pas attrapée remonte jusqu’à l’appelant.

- Pourquoi : un fichier absent est une situation normale. lire_journal ne décide pas quoi en faire : c’est à l’appelant de décider. Donc tu ne l’attrapes pas.
- Exemple : try/except attrape une erreur ; sans except, elle remonte.
- Écris le test S12 : chemin inexistant dans un dossier temporaire, avec assertRaises(FileNotFoundError).
- Lance les tests : le test passe déjà. Ce n’est pas une erreur : c’est la preuve que tu n’as rien caché. Si ton code attrape l’erreur, retire le try.
- Fais un commit du test.

```
try:
    int("abc")
except ValueError:
    print("ce n’est pas un nombre")
```

```
python3 -m unittest -v
```

```
git add test_journal.py
```

```
git commit -m "Teste le fichier absent (FileNotFoundError)"
```

- **S12** — Fichier absent. Entrée : Chemin inexistant dans un dossier temporaire Attendu : lire_journal lève FileNotFoundError (assertRaises).

**Tu sais que c’est bon quand :** S12 passe, et journal.py ne contient aucun except autour de la lecture du fichier.

*Indice :* Relis lire_journal : il ne doit y avoir aucun try autour de l’ouverture du fichier.

#### Palier 5 — Séparer les lignes valides des malformées (14 min)

Parcourir des lignes avec une boucle, compter les refusées, et renvoyer un couple.

- Pourquoi : une ligne abîmée est comptée, elle ne doit pas arrêter le programme.
- Réutilise analyser_ligne de outils.py : from outils import analyser_ligne. Une ligne refusée donne None.
- Écris le test S14 : quatre lignes dont deux invalides, puis une liste vide. Le résultat attendu est un couple (liste, nombre).
- Lance les tests : rouge. Écris charger_evenements(lignes) : une boucle for, une liste pour les valides, un compteur pour les refusées. Retourne le couple.
- Relance : vert, puis commit.

```
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

```
python3 -m unittest -v
```

```
git add journal.py test_journal.py
```

```
git commit -m "Ajoute charger_evenements et compte les lignes malformees"
```

- **S14** — Lignes valides et malformées. Entrée : Quatre lignes dont deux invalides (une mauvaise structure, un événement inconnu), puis une liste vide Attendu : Deux événements dans l’ordre d’arrivée et malformees = 2 ; liste vide : ([], 0).

**Tu sais que c’est bon quand :** S11 à S14 passent. Une liste vide donne ([], 0).

*Indice :* analyser_ligne renvoie None quand la ligne est refusée : c’est à toi de décider si elle compte comme malformée. Vérifie d’abord le cas de la liste vide.

#### Palier 6 — Construire le rapport (14 min)

Assembler un dictionnaire de résultats à partir de fonctions déjà testées.

- Pourquoi : un rapport est d’abord une donnée. Son affichage viendra en MR3, pas ici.
- Exemple : un dictionnaire se lit par sa clé, rapport["quantite"].
- Écris le test S18 (construire_rapport([], 0) donne des zéros et {}), puis S15 (trois LOGIN_OK, deux LOGIN_FAIL dont deux pour alice, une ligne malformée).
- Réutilise compter_evenements et echecs_par_utilisateur de outils.py : ne recopie pas leur logique. lignes_valides vaut le nombre d’événements.
- Fais passer les deux tests, puis commit.

```
rapport = {"nom": "pain", "quantite": 2}
print(rapport["quantite"])
```

```
from outils import compter_evenements, echecs_par_utilisateur
```

```
python3 -m unittest -v
```

```
git add journal.py test_journal.py
```

```
git commit -m "Ajoute construire_rapport"
```

- **S15** — Construction du rapport. Entrée : Trois LOGIN_OK, deux LOGIN_FAIL dont deux pour alice, et un nombre de lignes malformées de 1 Attendu : lignes_valides 5, login_ok 3, login_fail 2, lignes_malformees 1, echecs_par_utilisateur {"alice": 2}.
- **S18** — Journal vide. Entrée : construire_rapport([], 0) Attendu : lignes_valides 0, login_ok 0, login_fail 0, lignes_malformees 0, echecs_par_utilisateur {} ; aucune exception.

**Tu sais que c’est bon quand :** S11 à S15 et S18 passent.

*Indice :* Calcule d’abord les compteurs, puis range-les dans le dictionnaire. Pour alice, echecs_par_utilisateur renvoie déjà un dictionnaire : reprends-le tel quel.

#### Palier 7 — Sauver et relire le JSON (14 min)

Écrire un rapport en JSON, le relire, et transformer un JSON abîmé en message clair.

- Pourquoi : un rapport doit pouvoir être lu par un autre outil ; un fichier abîmé doit donner une erreur claire, pas une trace illisible.
- Exemple : json.dump écrit dans un fichier ouvert, json.load relit. Lance-le dans un dossier jetable, pas dans ton dépôt.
- Écris le test S16 : une clé et une valeur accentuées, sauvegardées puis rechargées. Le résultat doit être égal à l’original.
- Écris le test S17 : un fichier contenant « {pas du json » lève ValueError ; un chemin absent lève FileNotFoundError.
- Écris sauvegarder_rapport et charger_rapport. Dans charger_rapport, attrape json.JSONDecodeError seulement, et lève ValueError avec un message en français qui nomme le fichier. FileNotFoundError reste levée telle quelle.
- Fais un commit.

```
import json

with open("panier.json", "w", encoding="utf-8") as f:
    json.dump({"fruit": "pomme"}, f, ensure_ascii=False, indent=2)

with open("panier.json", encoding="utf-8") as f:
    print(json.load(f))
```

```
try:
    json.loads("[1, 2")
except json.JSONDecodeError as exc:
    print("erreur :", exc)
```

```
python3 -m unittest -v
```

```
git add journal.py test_journal.py
```

```
git commit -m "Ajoute sauvegarder_rapport et charger_rapport en JSON"
```

- **S16** — Aller-retour JSON avec accents. Entrée : Rapport contenant la clé « échecs » et une valeur accentuée, sauvegardé puis rechargé Attendu : Le rapport rechargé est égal à l’original, et le fichier est relu sans erreur par json.load.
- **S17** — Erreurs de chargement JSON. Entrée : Fichier contenant « {pas du json » ; chemin absent Attendu : ValueError pour le fichier corrompu ; FileNotFoundError pour le chemin absent.

**Tu sais que c’est bon quand :** S11 à S18 passent. Le fichier panier.json de l’exemple n’est pas dans git status (supprime-le après l’exemple).

*Indice :* ensure_ascii=False garde les accents lisibles : ouvre le fichier en UTF-8 des deux côtés. JSONDecodeError est une sous-classe de ValueError : vérifie que ton except n’attrape pas aussi FileNotFoundError.

#### Palier 8 — Git de rattrapage : commit fautif, revert, stash, restore (10 min)

Défaire un commit sans réécrire l’historique, mettre une modification de côté, et jeter un brouillon.

- Pourquoi : quand une CI devient rouge, tu n’effaces pas l’historique partagé ; tu ajoutes un commit qui défait le précédent.
- Étape 1 : casse volontairement verifier_chemin (par exemple supprime sa ligne de contrôle), fais le commit, puis constate les échecs.
- Étape 2 : annule ce commit avec git revert, sans éditeur. Les tests repassent.
- Étape 3 : ajoute une ligne de brouillon à la fin de journal.py, mets-la de côté avec git stash, liste la réserve, puis reprends-la avec git stash pop.
- Étape 4 : jette le brouillon avec git restore, puis vérifie que git status est propre.
- Étape 5 : relis git log --oneline. git stash list doit être vide.

```
git add journal.py
```

```
git commit -m "Casse verifier_chemin (exercice)"
```

```
python3 -m unittest -v
```

```
git revert HEAD --no-edit
```

```
python3 -m unittest -v
```

```
echo "# brouillon" >> journal.py
```

```
git stash push -m brouillon
```

```
git stash list
```

```
git stash pop
```

```
git restore journal.py
```

```
git status
```

```
git log --oneline
```

```
git stash list
```

**Tu sais que c’est bon quand :** git log --oneline montre « Casse verifier_chemin (exercice) » puis son revert ; git status est propre ; git stash list est vide.

*Indice :* --no-edit évite l’ouverture d’un éditeur. Si git stash pop signale un conflit, ne force rien : lis git status et demande de l’aide. Le commit fautif reste dans l’historique : c’est voulu, le revert le défait.

#### Palier 9 — Démonstration, pull request (8 min)

Vérifier le rapport sur le journal fictif, puis livrer la MR.

- Démonstration D1 (hors tests, hors CI) : lance la lecture de fixtures/socle/auth.log avec lire_journal, charger_evenements et construire_rapport depuis le terminal. Ce n’est pas un test : le fichier n’est pas versionné.
- Compte les lignes non vides du fichier avec la commande ci-dessous. lignes_valides + lignes_malformees doit égaler ce nombre.
- Relis le diff contre main, pousse la branche, ouvre la pull request (GitLab dit merge request). Fusionne seulement quand python3 -m unittest passe en local : ici aucun pipeline ne tourne.

```
python3 -c "from journal import lire_journal, charger_evenements, construire_rapport; lignes = lire_journal('fixtures/socle/auth.log'); evenements, malformees = charger_evenements(lignes); print(construire_rapport(evenements, malformees))"
```

```
grep -c "[^[:space:]]" fixtures/socle/auth.log
```

```
git status
```

```
git diff main --stat
```

```
git push -u origin feat/fichiers-erreurs
```

```
gh pr create --base main --title "Fichiers, erreurs et JSON" --body "Ajoute journal.py et ses tests S11 à S18."
```

**Tu sais que c’est bon quand :** lignes_valides + lignes_malformees est égal au nombre affiché par grep. La pull request ne contient que journal.py et test_journal.py (et outils.py si tu l’as modifié, avec une raison).

*Indice :* Si la démonstration affiche une erreur, lis la dernière ligne : elle dit quel fichier ou quelle fonction pose problème. Si fixtures/socle/auth.log manque, relance la commande de copie des fixtures de la préparation.

**Démonstrations manuelles (hors tests) :**
- **D1** — Rapport sur la copie du journal fictif. Entrée : Script local (hors tests) qui lit fixtures/socle/auth.log avec lire_journal, charger_evenements et construire_rapport Attendu : Aucune trace d’erreur. lignes_valides + lignes_malformees est égal au nombre de lignes non vides du fichier, que tu comptes avec une commande de ton choix.

**Avant de livrer :**
- python -m unittest passe pour S1 à S18 ; les tests de MR1 (S1 à S10) restent verts.
- Les tests créent leurs fichiers dans un dossier temporaire et ne laissent rien dans le dépôt.
- git log --oneline montre le commit fautif et son revert ; git stash list est vide à la fin.
- Le diff de la MR est relu et ne contient que journal.py, test_journal.py et les modifications éventuelles de outils.py justifiées.
- Chaque palier de code a son commit, avec le message donné dans le palier.

### MR3 — feat/analyseur (70 min)

Assemble un petit programme complet, par paliers : analyseur.py lit un journal passé en argument, affiche le rapport et renvoie un code de retour. Tu sépares les fonctions de données (journal.py, outils.py) de l’affichage (analyseur.py), tu ajoutes le README, puis tu pratiques le conflit de fusion, un rebase local et un tag v0.1.0. Pourquoi : un programme utilisable se lance en ligne de commande, se documente et se versionne proprement ; c’est le modèle de l’outil final.

#### Palier 1 — Repars de main et crée la branche (5 min)

Partir d’une base à jour, avant d’écrire le programme complet.

- Reviens sur main, mets-la à jour, puis crée feat/analyseur.
- Vérifie que outils.py et journal.py sont bien là : la suite du programme s’appuie dessus.

```
git switch main
```

```
git pull --ff-only
```

```
git switch -c feat/analyseur
```

```
git log --oneline
```

```
git status
```

**Tu sais que c’est bon quand :** git status affiche « On branch feat/analyseur » et « nothing to commit, working tree clean ».

*Indice :* Si la branche existe déjà, utilise git switch feat/analyseur (sans -c). Si git pull --ff-only refuse, ne force rien : demande de l’aide.

#### Palier 2 — Formater le rapport : le cas complet (7 min)

Séparer le calcul du texte et son affichage : une fonction qui renvoie une chaîne, sans rien afficher.

- Pourquoi : si formater_rapport renvoie du texte au lieu d’afficher, tu peux tester ce texte sans lancer le programme.
- Exemple sans rapport (un panier de courses) : construire une chaîne ligne par ligne, avec les clés triées.
- Crée analyseur.py (vide) et test_analyseur.py. Écris le test S19 : rapport avec 5 lignes valides, 3 connexions réussies, 2 échecs répartis entre bob (1) et alice (1), et 1 malformée. Les quatre lignes de compteurs ont leurs valeurs, et la ligne alice vient avant la ligne bob.
- Lance les tests : rouge. Écris formater_rapport(rapport) dans analyseur.py : quatre lignes fixes dans l’ordre donné, puis une ligne par utilisateur en échec, triées. Vert, commit.

```
def afficher_panier(articles):
    lignes = []
    for nom in sorted(articles):
        lignes.append(f"{nom} : {articles[nom]}")
    return "\n".join(lignes)

print(afficher_panier({"pomme": 3, "banane": 1}))
```

```
python3 -m unittest -v
```

```
git add analyseur.py test_analyseur.py
```

```
git commit -m "Ajoute formater_rapport avec le cas complet"
```

- **S19** — Formatage complet. Entrée : Rapport avec 5 lignes valides, 3 connexions réussies, 2 échecs répartis entre bob (1) et alice (1), 1 malformée Attendu : Les quatre lignes de compteurs ont leurs valeurs ; la ligne alice apparaît avant la ligne bob.

**Tu sais que c’est bon quand :** S19 passe. Lance python3 analyseur.py : il n’affiche encore rien d’utile, et ce n’est pas grave à ce stade.

*Indice :* Les libellés doivent être exactement ceux du contrat, accents compris : « Lignes valides : », « Connexions réussies : », « Échecs de connexion : », « Lignes malformées : ».

#### Palier 3 — Formater le rapport : sans échec (6 min)

Traiter le cas où personne n’a échoué.

- Écris le test S20 : echecs_par_utilisateur vide. La chaîne doit contenir « Aucun échec » et aucune ligne d’utilisateur.
- Lance les tests : rouge. Adapte formater_rapport : sans échec, la ligne « Aucun échec » remplace les lignes d’utilisateurs. Vert, commit.

```
python3 -m unittest -v
```

```
git add analyseur.py test_analyseur.py
```

```
git commit -m "Affiche Aucun échec quand il n’y a pas d’échec"
```

- **S20** — Formatage sans échec. Entrée : echecs_par_utilisateur vide Attendu : La chaîne contient « Aucun échec » et aucune ligne d’utilisateur.

**Tu sais que c’est bon quand :** S19 et S20 passent.

*Indice :* Un seul if suffit : il décide si on ajoute les lignes d’utilisateurs ou la ligne « Aucun échec ».

#### Palier 4 — Codes de retour : usage et fichier absent (10 min)

Faire renvoyer un code de retour à main, sans jamais quitter le programme soi-même.

- Pourquoi : main renvoie un entier au lieu d’appeler sys.exit ; ainsi un test peut l’appeler et vérifier le code.
- Exemple : print(..., file=sys.stderr) écrit sur la sortie d’erreur, et return donne le code.
- Écris les tests S21 (main([]) : code 2, message sur la sortie d’erreur, rien sur la sortie standard) et S22 (chemin absent dans un dossier temporaire : code 1, aucune exception ne sort de main). Capture la sortie avec io.StringIO et contextlib.redirect_stderr / redirect_stdout.
- Lance les tests : rouge. Écris main(argv) : argv vide donne le code 2 ; un fichier absent donne le code 1 avec un message clair. main attrape FileNotFoundError et ValueError, et nulle part ailleurs. Vert, commit.

```
import sys

def signaler(message):
    print(message, file=sys.stderr)
    return 2

print(signaler("usage : exemple FICHIER"))
```

```
try:
    with open("inexistant.txt", encoding="utf-8") as f:
        print(f.read())
except FileNotFoundError:
    print("fichier introuvable")
```

```
python3 -m unittest -v
```

```
git add analyseur.py test_analyseur.py
```

```
git commit -m "Ajoute main avec les codes de retour 2 et 1"
```

- **S21** — Usage sans argument. Entrée : main([]) Attendu : Code 2 ; message sur la sortie d’erreur ; rien sur la sortie standard.
- **S22** — Fichier absent. Entrée : main avec un chemin inexistant dans un dossier temporaire Attendu : Code 1 ; message clair ; aucune exception ne sort de main.

**Tu sais que c’est bon quand :** S19 à S22 passent. Aucun sys.exit n’apparaît dans analyseur.py à ce stade.

*Indice :* argv est une liste : vérifie d’abord sa longueur. Pour le fichier absent, la fonction de lecture de journal.py fait le travail : main se contente d’attraper l’erreur et de choisir le code.

#### Palier 5 — Codes de retour : succès avec une ligne malformée (10 min)

Faire afficher le rapport et renvoyer 0 quand le fichier est valide.

- Écris le test S23 : fichier temporaire de deux lignes valides et une malformée, passé à main. Code 0, et la sortie contient « Lignes valides : 2 » et « Lignes malformées : 1 ».
- Lance les tests : rouge. Complète main : lis le fichier avec lire_journal, puis charger_evenements, construire_rapport et formater_rapport, affiche le texte et retourne 0.
- Vert, commit.

```
python3 -m unittest -v
```

```
git add analyseur.py test_analyseur.py
```

```
git commit -m "Affiche le rapport et renvoie 0 en cas de succes"
```

- **S23** — Fichier valide avec une ligne malformée. Entrée : Fichier temporaire de deux lignes valides et une malformée, passé à main Attendu : Code 0 ; la sortie contient « Lignes valides : 2 » et « Lignes malformées : 1 ».

**Tu sais que c’est bon quand :** S19 à S23 passent.

*Indice :* Relie les fonctions déjà écrites dans l’ordre de la chaîne de traitement : lire, charger, construire, formater. Pas de copie de leur logique.

#### Palier 6 — Point d’entrée et import sans effet (8 min)

Lancer le programme en ligne de commande, sans qu’importer le module l’exécute.

- Pourquoi : un module peut être importé par un test ou un autre outil sans se lancer tout seul.
- Exemple : le bloc if __name__ == "__main__" ne s’exécute que si on lance le fichier directement.
- Écris le test S24 : importe analyseur dans le test, sortie redirigée. Aucune sortie ne doit apparaître.
- Ajoute en bas de analyseur.py le bloc if __name__ == "__main__" : il transmet sys.argv[1:] à main et utilise le résultat comme code de sortie. Vert, commit.
- Démonstration D2 (hors tests) : lance le programme avec le journal fictif, puis sans argument, et lis le code de retour.

```
import sys

def saluer():
    print("Bonjour")
    return 0

if __name__ == "__main__":
    sys.exit(saluer())
```

```
python3 -m unittest -v
```

```
git add analyseur.py test_analyseur.py
```

```
git commit -m "Ajoute le point d’entrée en ligne de commande"
```

```
python3 analyseur.py fixtures/socle/auth.log
```

```
echo $?
```

```
python3 analyseur.py
```

```
echo $?
```

- **S24** — Import sans effet de bord. Entrée : Import du module analyseur dans le test, sortie redirigée Attendu : Aucune sortie : le bloc __main__ ne s’exécute pas à l’import.

**Tu sais que c’est bon quand :** S19 à S24 passent. Le premier cas affiche le rapport et renvoie 0 ; le second affiche le message d’usage et renvoie 2.

*Indice :* Dans le bloc, appelle main avec sys.argv[1:] et passe son résultat à sys.exit. Si S24 échoue, cherche un print ou un appel de main resté au niveau du module, en dehors du bloc.

#### Palier 7 — README et .gitignore (6 min)

Documenter l’usage, les codes de retour et les limites du programme.

- Pourquoi : un outil sans mode d’emploi n’est pas livrable, et les limites font partie du contrat.
- Rédige README.md avec : l’objectif, le format du journal (AAAA-MM-JJ HH:MM:SS EVENEMENT utilisateur ip), la commande d’usage, les codes de retour 0, 1 et 2, et les limites (données fictives, aucune connexion réseau).
- Vérifie le .gitignore : il doit exclure __pycache__/ et fixtures/. Ajoute ce qui manque.
- Relance les tests, puis fais un commit des deux fichiers.

```
cat .gitignore
```

```
python3 -m unittest -v
```

```
git add README.md .gitignore
```

```
git commit -m "Ajoute le README et complete le .gitignore"
```

**Tu sais que c’est bon quand :** git status est propre, et le README contient les trois codes de retour et la mention des données fictives.

*Indice :* Pour l’usage, écris la commande telle que tu l’as tapée dans la démonstration D2. Pour les limites, relis la section Limites de socle.md.

#### Palier 8 — Provoquer un conflit de fusion et le résoudre (10 min)

Lire les marqueurs de conflit, choisir la ligne voulue, et conclure la fusion à la main.

- Pourquoi : un conflit n’est pas une catastrophe : deux lignes d’historique ont modifié le même endroit, et tu décides. Ce conflit est volontaire et reste local.
- Point de départ : README.md n’existe pas encore sur main, donc les branches d’exercice partent de feat/analyseur, où le README est commité.
- Branche A : change la première ligne de README.md (par exemple « # Analyseur A »), puis commite.
- Branche B : repars de feat/analyseur, change la même ligne différemment (« # Analyseur B »), puis commite.
- Depuis la branche A, lance git merge : un conflit apparaît. Lis git status, repère les marqueurs, garde une seule version de la ligne, supprime les marqueurs, puis commite la fusion.
- Ne pousse rien de ces branches.

```
git switch feat/analyseur
```

```
git switch -c exercice/conflit-a
```

```
git add README.md
```

```
git commit -m "Exercice : variante A du titre"
```

```
git switch feat/analyseur
```

```
git switch -c exercice/conflit-b
```

```
git add README.md
```

```
git commit -m "Exercice : variante B du titre"
```

```
git switch exercice/conflit-a
```

```
git merge exercice/conflit-b
```

```
git status
```

```
grep -n "<<<<<<<\|=======\|>>>>>>>" README.md
```

```
git add README.md
```

```
git commit -m "Resout le conflit du titre (exercice)"
```

```
grep -c "<<<<<<<\|=======\|>>>>>>>" README.md
```

```
git switch feat/analyseur
```

```
git branch -D exercice/conflit-b
```

```
git branch -D exercice/conflit-a
```

```
git branch
```

**Tu sais que c’est bon quand :** La dernière commande grep ne trouve aucun marqueur dans README.md et git branch ne montre plus les branches exercice/. Pourquoi -D : git branch -d refuse de supprimer une branche dont les commits ne sont pas dans feat/analyseur ; tu le sais, et tu supprimes exprès, car c’est un exercice jetable.

*Indice :* Si le conflit te semble pire, git merge --abort annule la fusion et te remet dans l’état d’avant. Une fois le texte corrigé, git diff ne doit plus montrer de lignes <<<<<<< ou >>>>>>>.

#### Palier 9 — Rebase local, tag v0.1.0 et pull request (8 min)

Replacer ta branche au-dessus d’un main qui a avancé, poser un tag annoté, puis ouvrir la MR.

- Pourquoi : un rebase réécrit ta branche par-dessus la base à jour ; tant qu’elle n’est pas poussée, c’est sans risque.
- Fais avancer main en local : ajoute un commentaire d’en-tête à outils.py, puis commite-le sur main. Ne le pousse pas sans l’accord de ton école.
- Replace feat/analyseur au-dessus de main, relis l’historique, pose le tag annoté v0.1.0.
- Relis le diff de la MR contre main. Si git diff origin/main --stat montre outils.py, la correction de main n’est pas sur GitHub : signale-le à ton école avant d’ouvrir la MR.
- Pousse la branche, ouvre la pull request. Pousse le tag seulement si ton école l’autorise.

```
git switch main
```

```
git add outils.py
```

```
git commit -m "Ajoute un commentaire d’en-tete a outils.py"
```

```
git switch feat/analyseur
```

```
git rebase main
```

```
git log --oneline --graph
```

```
git tag -a v0.1.0 -m "Analyseur de journal, version 0.1.0"
```

```
git tag -l
```

```
git diff origin/main --stat
```

```
git push -u origin feat/analyseur
```

```
gh pr create --base main --title "Analyseur de journal" --body "Ajoute analyseur.py, test_analyseur.py et le README (S19 à S24)."
```

**Tu sais que c’est bon quand :** git log --oneline --graph montre feat/analyseur posée au-dessus du commit de main ; git tag -l affiche v0.1.0 ; le README ne contient plus de marqueur de conflit.

*Indice :* Si git rebase main s’arrête sur un conflit, ce n’est pas le conflit voulu : lis git status, ne force rien. Tu peux revenir en arrière avec git rebase --abort. Un tag annoté (-a) contient un message et une date ; un tag léger ne contient rien de plus qu’un nom.

**Démonstrations manuelles (hors tests) :**
- **D2** — Analyseur en ligne de commande. Entrée : python analyseur.py fixtures/socle/auth.log, puis python analyseur.py sans argument ; vérifie le code avec echo $? Attendu : Premier cas : rapport affiché et code 0. Second cas : message d’usage et code 2.

**Avant de livrer :**
- python -m unittest passe pour S1 à S24, et les tests créent leurs fichiers dans un dossier temporaire.
- Le conflit de fusion a été résolu à la main : aucun marqueur <<<<<<< , ======= ou >>>>>>> ne reste dans README.md.
- git log --oneline --graph montre la branche rebasée sur main ; le tag v0.1.0 est présent dans git tag -l.
- La merge request vers la branche principale a été relue ; les branches exercice/ ont été supprimées et ne figurent pas sur GitLab.
- Chaque palier de code a son commit, avec le message donné dans le palier.

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
