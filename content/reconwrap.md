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

## Les trois MR

Les minutes des missions sont incluses dans les 300 minutes du parcours.

### MR1 — feat/architecture (100 min)

Pose la structure du package reconwrap/ et le contrat commun, en paliers courts. A chaque palier, tu écris un test, tu le vois échouer, tu écris le minimum de code, tu le vois passer, puis tu fais un commit. Chaque module expose une fonction qui prend une cible validée et des options, et retourne un dict normalisé (module, statut OK, ERREUR ou IGNORE, donnees, alertes, duree_s). Le registre associe un nom à une fonction ; le dispatch convertit une exception en résultat ERREUR. Cette MR ne lance aucun outil : les tests utilisent de faux modules. Pourquoi : ce contrat est la colonne vertébrale du framework. Sans lui, ajouter un module oblige à modifier tout le reste.

#### Palier 1 — Crée le package et protège le venv (10 min)

Avoir un package reconwrap/ importable, et un .gitignore qui protège le venv avant ton premier commit.

- Vérifie que tu es sur la branche de la MR : la préparation l’a créée. Si tu n’y es pas, reviens-y avant de continuer.
- Un package est un dossier qui contient un fichier __init__.py : Python le voit alors comme un module importable. Le fichier __main__.py permet de le lancer avec python -m reconwrap.
- Crée le .gitignore AVANT ton premier git add. Il doit contenir trois motifs, un par ligne : .venv/, __pycache__/ et rapports/.
- En MR1, __main__.py peut seulement afficher un message : la CLI arrive en MR2, mais la commande ne doit jamais planter.
- Pourquoi le venv : il isole les outils de ton projet. Il ne se commite jamais.

```
git branch --show-current
```

```
ls -d .venv   # si le dossier n’existe pas : python3 -m venv .venv
```

```
Exemple travaillé, sans rapport avec ReconWrap, dans un dossier jetable :
mkdir exemple_pkg
touch exemple_pkg/__init__.py
echo 'print("Bonjour depuis le paquet")' > exemple_pkg/__main__.py
python3 -m exemple_pkg
rm -r exemple_pkg
```

```
git status
```

```
git add .gitignore reconwrap/__init__.py reconwrap/__main__.py
```

```
git commit -m "Crée la structure du package reconwrap"
```

**Tu sais que c’est bon quand :** git status n’affiche plus .venv/, et .venv/bin/python -m reconwrap s’exécute sans traceback.

*Indice :* Si .venv/ apparaît encore dans git status, ton .gitignore n’est pas enregistré ou un motif est mal écrit (le point au début de .venv compte). Le message de l’exemple jetable doit venir de ton __main__.py.

#### Palier 2 — La fabrique du résultat (R1) (10 min)

Construire un dict à cinq clés exactes depuis une fonction, avec annotations de type et docstring.

- Crée tests/__init__.py (vide) : il permet à python -m unittest de trouver tes tests depuis la racine.
- Écris R1 dans tests/test_core.py : la fabrique reçoit module « faux », statut « OK », donnees vide, alertes vide, duree_s 0.0. Vérifie les cinq clés exactes, que alertes est une liste et que duree_s est positif ou nul.
- Lance les tests : ils échouent (rouge). Écris dans reconwrap/core.py la fonction minimale qui construit le dict. Pas de contrôle de statut ici : il arrive au palier suivant.
- Pourquoi les annotations : elles disent quel type on attend (str, list, float). Python ne les vérifie pas à l’exécution, mais elles se lisent comme une documentation.
- Pourquoi la docstring : c’est la première chaîne de la fonction. help(fonction) l’affiche.

```
Exemple travaillé, sans rapport avec ReconWrap :
def doubler(n: int) -> int:
    """Retourne le double de n."""
    return n * 2
```

```
Dans un fichier jetable contenant cet exemple, ajoute la ligne help(doubler) à la fin, puis relance-le avec python3 : la docstring s’affiche.
```

```
.venv/bin/python -m unittest -v
```

- **R1** — Résultat normalisé. Entrée : Fabrique appelée avec module « faux », statut « OK », donnees vide, alertes vide et duree_s 0.0. Attendu : Dict aux cinq clés exactes module, statut, donnees, alertes, duree_s ; alertes est une liste et duree_s un nombre positif ou nul.

**Tu sais que c’est bon quand :** R1 passe : le dict a exactement les clés module, statut, donnees, alertes, duree_s.

*Indice :* Commence par écrire le dict littéral, puis relis le contrat. Un test par règle : ici, seule la forme du dict est testée.

#### Palier 3 — Le statut refusé (R2) (10 min)

Refuser tout statut hors de OK, ERREUR et IGNORE, avec une erreur qui explique ce qui ne va pas.

- Écris R2 dans tests/test_core.py : un statut « FAUX », puis « ok » en minuscules. Les deux doivent lever ValueError, avec un message en français qui cite le statut refusé.
- Lance les tests (rouge), puis ajoute le contrôle dans la fabrique. Aucun dict ne doit être retourné dans ces deux cas.
- Pourquoi lever une erreur tôt : un statut faux, s’il circule, fausse le rapport final sans que personne ne le remarque.
- Fais un commit du contrat (fabrique et tests R1 et R2).

```
Exemple travaillé, sans rapport avec ReconWrap :
MENU = ("margherita", "reine")
def commander(plat):
    if plat not in MENU:
        raise ValueError(f"plat inconnu : {plat}")
    return f"Commande : {plat}"
```

```
.venv/bin/python -m unittest -v
```

```
git add reconwrap/core.py tests/__init__.py tests/test_core.py
```

```
git commit -m "Ajoute le contrat de résultat normalisé"
```

- **R2** — Statut refusé. Entrée : Statut « FAUX », puis statut « ok » en minuscules. Attendu : ValueError avec un message en français qui cite le statut refusé. Aucun dict n’est retourné : les minuscules sont refusées aussi.

**Tu sais que c’est bon quand :** R1 et R2 passent. « ok » en minuscules est refusé.

*Indice :* Un tuple de statuts et l’opérateur in comparent exactement : les minuscules sont donc refusées. Le message doit contenir le statut reçu.

#### Palier 4 — La cible loopback seulement (R5) (10 min)

Refuser toute cible qui n’est pas 127.0.0.1 avant qu’un module soit appelé.

- Écris R5 dans tests/test_core.py. Utilise un faux module qui note chacun de ses appels dans une liste : le test vérifie que la liste reste vide pour les cibles refusées.
- Les cas : 127.0.0.1 accepté ; 192.0.2.10, example.com, une chaîne vide, 10.0.0.0/24 et « 127.0.0.1; ls » doivent lever ValueError.
- Écris la validation dans reconwrap/core.py. Un contrôle de type d’abord, puis une comparaison exacte : une règle lisible vaut mieux qu’une règle astucieuse.
- Pourquoi une règle si stricte : la cible est la seule porte entre le framework et le réseau. Ce qui n’est pas explicitement permis est refusé.

```
Exemple travaillé, sans rapport avec ReconWrap :
try:
    n = int("abc")
except ValueError as erreur:
    print("pas un nombre :", erreur)
```

```
Documentation utile à lire, sans l’utiliser forcément : ipaddress (https://docs.python.org/3/library/ipaddress.html)
```

```
.venv/bin/python -m unittest -v
```

```
git add reconwrap/core.py tests/test_core.py
```

```
git commit -m "Valide la cible : seule 127.0.0.1 est acceptée"
```

- **R5** — Cible loopback seulement. Entrée : 127.0.0.1, puis 192.0.2.10, example.com, une chaîne vide, 10.0.0.0/24 et « 127.0.0.1; ls ». Attendu : 127.0.0.1 est accepté. Toutes les autres valeurs lèvent ValueError et aucun module n’est appelé.

**Tu sais que c’est bon quand :** R5 passe : 127.0.0.1 est accepté, les six autres valeurs lèvent ValueError, et le faux module n’est jamais appelé.

*Indice :* Vérifie d’abord le type, puis compare la chaîne exacte. Une chaîne qui contient autre chose (espace, point-virgule) doit être refusée, pas réparée.

#### Palier 5 — Le registre des modules (R3) (10 min)

Associer un nom de module à sa fonction, et signaler clairement un nom inconnu.

- Écris R3 dans tests/test_core.py : un registre avec trois faux modules nommés network, web et ad, puis une demande du module « scanner ». Le test attend ValueError qui liste les modules connus, et vérifie qu’aucun faux module n’a été appelé.
- Lance les tests (rouge), puis écris le registre dans reconwrap/core.py. C’est un dictionnaire ordinaire : nom vers fonction.
- Pourquoi un registre : ajouter un module devient une ligne dans un seul endroit, sans toucher au reste.

```
Exemple travaillé, sans rapport avec ReconWrap :
def dire_bonjour():
    return "bonjour"

ACTIONS = {"bonjour": dire_bonjour}
print(ACTIONS["bonjour"]())
print(sorted(ACTIONS))
```

```
.venv/bin/python -m unittest -v
```

```
git add reconwrap/core.py tests/test_core.py
```

```
git commit -m "Ajoute le registre des modules"
```

- **R3** — Nom de module inconnu. Entrée : Registre contenant trois faux modules nommés network, web et ad ; demande du module « scanner ». Attendu : ValueError qui liste les modules connus. Aucun des trois faux modules n’est appelé.

**Tu sais que c’est bon quand :** R3 passe : le nom inconnu donne une erreur qui liste les noms connus, sans appel de module.

*Indice :* Une fonction peut être rangée dans un dictionnaire comme n’importe quelle valeur. Pour la liste des noms connus, sorted() donne un ordre stable.

#### Palier 6 — Le dispatch et l’isolation des pannes (R4) (10 min)

Appeler un module par son nom, et transformer une exception en résultat ERREUR sans rien propager.

- Écris R4 dans tests/test_core.py : un faux module lève RuntimeError avec le message « boom ». Le dispatch ne doit rien propager ; il retourne statut ERREUR, alertes vide, et donnees contient le message.
- Dans le dispatch : cherche la fonction dans le registre (R3), valide la cible (R5), appelle le module dans un bloc protégé, puis construis le résultat avec la fabrique.
- Attrape Exception, pas BaseException : Ctrl+C doit toujours interrompre le programme.
- Pourquoi isoler : un module qui plante ne doit pas faire tomber le rapport ni les autres modules (c’est la suite de MR2).
- Commit : le dispatch et son isolation.

```
Exemple travaillé, sans rapport avec ReconWrap :
def lire_note(texte):
    try:
        return int(texte)
    except ValueError as erreur:
        return f"erreur : {erreur}"

print(lire_note("12"))
print(lire_note("douze"))
```

```
.venv/bin/python -m unittest -v
```

```
git add reconwrap/core.py tests/test_core.py
```

```
git commit -m "Isole les erreurs des modules dans le dispatch"
```

- **R4** — Exception isolée. Entrée : Faux module qui lève RuntimeError avec le message « boom ». Attendu : Le dispatch ne propage pas l’exception ; il retourne statut ERREUR, alertes vide, et donnees contient le message d’erreur.

**Tu sais que c’est bon quand :** R1 à R5 passent. Un module qui lève une exception donne un résultat ERREUR, sans traceback.

*Indice :* Le texte de l’exception est dans la variable de l’except (as erreur). Il doit finir dans donnees, pas être affiché.

#### Palier 7 — Un logger par module (10 min)

Ajouter du logging au dispatch sans que les tests dépendent du texte affiché.

- Le logging écrit des messages avec un niveau : DEBUG pour le détail, INFO pour le déroulé, ERREUR pour les pannes. Un logger se crée par nom ; le nom du module apparaît dans le format.
- Branche un logger par module (par exemple avec le nom du module comme nom de logger) et enregistre : appel du module (INFO), panne (ERREUR), détail (DEBUG).
- Les tests R1 à R5 vérifient les résultats, pas les lignes affichées. N’écris pas de test sur le texte du journal.
- Pourquoi : le journal aide à comprendre une exécution ; c’est le résultat qui est la donnée fiable.
- Commit séparé pour le logging.

```
Exemple travaillé, sans rapport avec ReconWrap :
import logging
logging.basicConfig(level=logging.INFO, format="%(name)s %(levelname)s %(message)s")
journal = logging.getLogger("cuisine")
journal.info("four préchauffé")
journal.debug("température lue : 180")
```

```
.venv/bin/python -m unittest -v
```

```
git add reconwrap/core.py
```

```
git commit -m "Ajoute le logging du dispatch"
```

**Tu sais que c’est bon quand :** Un module en panne produit une ligne ERREUR visible, et R1 à R5 passent toujours.

*Indice :* Avec level=INFO, la ligne DEBUG n’apparaît pas : c’est normal. Regarde ce que le format affiche avant de choisir le nom du logger.

#### Palier 8 — Ajouter un module ne touche pas le dispatch (10 min)

Vérifier l’acceptance clé : un nouveau module ne demande que de l’ajouter au registre.

- Ajoute un quatrième faux module dans tests/test_core.py (par exemple « cloud ») et enregistre-le seulement dans le registre.
- Lance le dispatch sur ce nouveau nom : il doit fonctionner sans rien changer dans la fonction de dispatch.
- Relis git diff reconwrap/core.py : la fonction de dispatch ne doit pas avoir bougé depuis le palier précédent.
- Pourquoi : si ajouter un module oblige à retoucher le dispatch, chaque module nouveau devient un risque de casse.

```
git diff reconwrap/core.py
```

```
.venv/bin/python -m unittest -v
```

**Tu sais que c’est bon quand :** Le faux module « cloud » répond via le dispatch, et le diff du dispatch est vide depuis le palier précédent.

*Indice :* Si tu as dû modifier le dispatch pour le faire fonctionner, la structure n’est pas bonne : reviens au registre seul.

#### Palier 9 — Vérifier et committer proprement (10 min)

Contrôler chaque commit avant de le faire : état, diff en zone de préparation, tests, commandes.

- Avant chaque commit : git status, git diff, puis python -m unittest. Tu n’ajoutes que les fichiers que tu nommes.
- Pourquoi la zone de préparation : git add choisit ce qui entre dans le commit. git diff --staged montre exactement ce qui sera committé.
- Relis l’historique : chaque commit doit décrire une seule chose (structure, contrat, cible, registre, dispatch, logging).
- Lance le module une dernière fois : .venv/bin/python -m reconwrap.

```
Exemple travaillé dans un dépôt jetable, hors de ReconWrap :
mkdir ~/essai-git && cd ~/essai-git && git init -b main
echo bonjour > a.txt
git add a.txt
git diff --staged
git commit -m "Premier essai"
cd - 
```

```
git status
```

```
git diff --staged
```

```
git log --oneline
```

```
.venv/bin/python -m reconwrap
```

**Tu sais que c’est bon quand :** git log --oneline montre les commits atomiques de la MR, git status est propre, et python -m reconwrap ne lève pas d’erreur.

*Indice :* Si un commit contient plusieurs sujets, tu peux le scinder : git reset --soft HEAD~1 annule le dernier commit en gardant les modifications. Demande-toi d’abord si c’est nécessaire.

#### Palier 10 — Pousser la MR1 et la faire relire (10 min)

Pousser la branche, ouvrir la merge request sur le dépôt de l’école, et distinguer ce qui est vérifié de ce qui est autorisé.

- Relis le diff complet de la MR : git diff main --stat, puis git diff main. Tu relis comme si c’était le code de quelqu’un d’autre.
- Pousse la branche, puis ouvre la merge request dans l’interface GitLab de l’école. Il n’y a pas encore de pipeline en MR1 : le fichier .gitlab-ci.yml arrive en MR3.
- Quatre résultats à ne pas confondre : tes tests locaux, le pipeline réellement exécuté, l’autorisation de fusion donnée par l’école, et la case cochée dans Cyber Atelier (déclarative, elle ne vérifie rien).
- Fusionne seulement si l’école l’autorise. Après fusion, remets main à jour avant de créer la branche suivante.

```
git status
```

```
git log --oneline main..HEAD
```

```
git push -u origin feat/architecture
```

```
git switch main
```

```
git pull --ff-only
```

**Tu sais que c’est bon quand :** La merge request est ouverte avec seulement les fichiers de MR1 ; ton main local est à jour après fusion (git log --oneline).

*Indice :* Si git push se plaint, vérifie d’abord que tu es bien sur feat/architecture (git branch --show-current). Ne fusionne pas sans relecture.

**Avant de livrer :**
- python -m reconwrap s’exécute sans traceback, même si aucun module n’est encore branché.
- Les tests R1 à R5 passent localement avec python -m unittest, sans réseau et sans outil externe.
- Ajouter un faux module ne demande aucune modification du dispatch : seul le registre change.
- Le .venv n’est pas suivi par Git, les commits sont atomiques et le diff de la MR a été relu.

### MR2 — feat/orchestration-rapport (100 min)

Branche les trois modules réels sur le contrat de MR1, en paliers courts : chaque palier a un seul objectif, un test quand il y en a un, et un commit. Le module réseau reprend ton PortPilot et lit le XML de nmap ; le module web reprend ton HeaderScope sur les quatre chemins du labo ; le module AD appelle adsim. Un module en échec ne fait échouer ni les autres ni le rapport. La CLI argparse choisit les modules, la cible, le chemin web et le format ; les rapports JSON et Markdown s’écrivent dans un dossier dédié, avec une date passée en paramètre. Pourquoi : c’est la première fois que ton code parle à de vrais outils. Tu isoles les effets de bord (processus, réseau, disque) pour que le reste reste testable.

#### Palier 1 — Copier les fixtures dans le dépôt (8 min)

Rendre les fixtures nmap et adsim suivies par Git, pour que la CI les lise à la place des vrais outils.

- Fais cette copie sur le Mac, depuis workspaces/reconwrap : ../../ remonte jusqu’au projet Cyber Atelier, où se trouvent les dossiers fixtures/nmap et fixtures/adsim. Les originaux sont en lecture seule, le chmod rend tes copies modifiables.
- Fais cette copie sur le Mac, depuis workspaces/reconwrap : ../../ remonte jusqu’au projet Cyber Atelier, où se trouvent les dossiers fixtures/nmap et fixtures/adsim. Les originaux sont en lecture seule, le chmod rend tes copies modifiables.
- Pourquoi chmod : une copie de fichier en lecture seule ne peut pas être modifiée ; chmod u+w rend tes copies modifiables, sans toucher aux originaux.
- Vérifie que Git suit les copies, et qu’aucun .venv ni rapport n’est ajouté.

```
Exemple travaillé, sans rapport avec ReconWrap :
mkdir -p recettes_copie && cp -r recettes/. recettes_copie/
# le point après recettes/ copie le contenu du dossier, pas le dossier lui-même
```

```
mkdir -p fixtures && cp -r ../../fixtures/nmap/. fixtures/nmap/ && cp -r ../../fixtures/adsim/. fixtures/adsim/ && chmod -R u+w fixtures
```

```
git status
```

```
git add fixtures
```

```
git commit -m "Ajoute les fixtures nmap et adsim"
```

**Tu sais que c’est bon quand :** git status a listé les fichiers de fixtures/nmap et fixtures/adsim, et ces fichiers sont dans le commit.

*Indice :* Si cp refuse d’écrire, tu essaies d’écrire dans les originaux : vérifie que ta destination est bien fixtures/ dans ton dépôt.

#### Palier 2 — Lire un XML avec ElementTree (8 min)

Lire un fichier XML et retrouver ses balises et attributs avec la bibliothèque standard.

- Un XML est une arborescence de balises. ElementTree le transforme en objets : chaque élément a un nom (tag), des attributs (attrib) et des méthodes de recherche.
- Pourquoi : nmap te donne un XML. Le découper à la main avec du texte casse au premier changement de mise en forme.
- Ouvre fixtures/nmap/open_8000.xml dans VS Code, repère la balise qui porte l’état d’un port. Tu n’écris pas encore le module : c’est une lecture.
- Une lecture qui échoue lève ParseError : c’est ce que le module devra transformer en ERREUR au palier suivant.

```
Exemple travaillé, sans rapport avec ReconWrap :
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

```
.venv/bin/python -c "import xml.etree.ElementTree as ET; print(ET.parse('fixtures/nmap/open_8000.xml').getroot().tag)"
```

**Tu sais que c’est bon quand :** Tu affiches le tag de la racine de open_8000.xml, et tu as repéré la balise qui porte l’état du port 8000.

*Indice :* Utilise les noms de balises tels qu’ils apparaissent dans le fichier. Les attributs se lisent avec get(), pas avec le texte entre balises.

#### Palier 3 — Le module réseau et le XML nmap (R12) (10 min)

Transformer un XML nmap en résultat du contrat : open, closed, filtered, ou ERREUR si le XML est cassé.

- Reprends la logique de PortPilot : la validation de la cible et du port reste la même. Relis ton code avant de le brancher ; ne le copie pas à l’aveugle.
- Écris R12 dans tests/test_network.py : open_8000.xml, closed_8000.xml, mixed.xml et broken.xml. Les tests lisent ces fichiers ; ils n’appellent jamais nmap.
- Écris la fonction du module : elle reçoit un chemin de XML (option « fichier fourni », utilisée par la CI) et retourne le contrat de MR1. Un XML cassé donne ERREUR, sans exception qui sort.
- Pourquoi un fichier fourni : le test devient déterministe. La voie nmap réelle se branchera au même endroit, mais la CI ne la lance jamais.
- Commit du module réseau.

```
.venv/bin/python -m unittest -v
```

```
git add reconwrap/network.py tests/test_network.py
```

```
git commit -m "Ajoute le module réseau et la lecture XML nmap"
```

- **R12** — Lecture XML nmap. Entrée : Fixtures nmap : open_8000.xml, closed_8000.xml, mixed.xml et broken.xml. Attendu : Le port 8000 est open dans open_8000.xml et closed dans closed_8000.xml. mixed.xml donne open, closed et filtered. broken.xml donne ERREUR sans exception.

**Tu sais que c’est bon quand :** R12 passe : open, closed, filtered pour les bons fichiers, ERREUR sans traceback pour broken.xml.

*Indice :* Pour mixed.xml, un port peut avoir un état différent des autres : cherche le port 8000 précisément, pas le premier port du fichier. Pour broken.xml, attrape l’erreur de lecture et retourne ERREUR.

#### Palier 4 — Le module web et le classement hors réseau (R14) (10 min)

Classer une réponse HTTP (code et en-têtes) sans ouvrir de connexion, et distinguer code HTTP, panne et timeout.

- Reprends le classement de HeaderScope : trois en-têtes à vérifier et leur conformité. Relis ton code avant de le brancher.
- Sépare deux choses : la lecture de la réponse (réseau, plus tard) et le classement (pur). Le classement reçoit un code et un dictionnaire d’en-têtes, et retourne le contrat : il se teste hors ligne.
- Accepte seulement les quatre chemins du labo : /fragile, /durci, /absent, /erreur.
- Dans donnees, distingue un code HTTP (404, 500), une panne de connexion et un timeout. Ces deux derniers cas ne sont pas testés ici : tu les verras en démonstration D6.
- Écris R14 dans tests/test_web.py, puis le classement. Les en-têtes HTTP ne sont pas sensibles à la casse.

```
Exemple travaillé, sans rapport avec ReconWrap :
stock = {"Pommes": 3, "Poires": 0}
stock_min = {nom.lower(): n for nom, n in stock.items()}
print(stock_min["pommes"])
```

```
.venv/bin/python -m unittest -v
```

```
git add reconwrap/web.py tests/test_web.py
```

```
git commit -m "Ajoute le classement web hors réseau"
```

- **R14** — Classement web sans réseau. Entrée : Statut 404 avec en-têtes quelconques, puis statut 200 avec les trois en-têtes conformes. Attendu : 404 : statut ERREUR, code 404 conservé, alertes vide. 200 conforme : zéro alerte. Aucune connexion n’est ouverte.

**Tu sais que c’est bon quand :** R14 passe : 404 donne ERREUR avec le code conservé, 200 conforme donne zéro alerte, et aucune connexion n’est ouverte.

*Indice :* Une fonction pure est plus simple à tester : elle ne fait que transformer ses arguments. Garde la connexion dans une autre fonction, plus tard.

#### Palier 5 — Le module AD et la sortie capturée (R13) (10 min)

Lire une sortie JSON d’adsim capturée et la transformer en résultat du contrat, sans appeler adsim.

- adsim est un simulateur fictif du domaine LAB.LOCAL. Dans le test, tu lis users.json et broken.json comme des sorties capturées : tu n’appelles pas adsim.
- Pourquoi json.load : il lit un fichier JSON et le transforme en dictionnaires et listes. Un JSON cassé lève json.JSONDecodeError : c’est ce qui doit donner ERREUR.
- Écris R13 dans tests/test_ad.py : pour users.json, le nombre de comptes égale count, et les comptes actifs et inactifs sont distingués. Pour broken.json, ERREUR avec un message.
- Écris la partie lecture du module AD. Le lancement d’adsim viendra au palier suivant.

```
Exemple travaillé, sans rapport avec ReconWrap :
import json
texte = '{"fruits": [{"nom": "pomme", "stock": 3}, {"nom": "poire", "stock": 0}]}'
donnees = json.loads(texte)
print([f["nom"] for f in donnees["fruits"] if f["stock"] > 0])
try:
    json.loads("{pas du json")
except json.JSONDecodeError as erreur:
    print("JSON invalide :", erreur)
```

```
.venv/bin/python -m unittest -v
```

```
git add reconwrap/ad.py tests/test_ad.py
```

```
git commit -m "Ajoute la lecture des sorties adsim capturées"
```

- **R13** — Lecture AD depuis fixtures. Entrée : Fixtures adsim : users.json, puis broken.json. Le module lit la sortie capturée, il n’appelle pas adsim. Attendu : users.json : le nombre de comptes égale count et actifs et inactifs sont distingués. broken.json donne ERREUR avec un message.

**Tu sais que c’est bon quand :** R13 passe : le nombre de comptes égale count, actifs et inactifs sont séparés, et broken.json donne ERREUR.

*Indice :* Relis la structure de users.json avant d’écrire le code : le nom des champs compte. Compte les comptes à partir de la liste, puis compare à count.

#### Palier 6 — Lancer adsim sans shell (8 min)

Appeler adsim depuis Python de façon sûre : liste d’arguments, délai maximal, et ERREUR en cas de panne.

- Le module AD lance adsim avec subprocess.run, en passant les arguments dans une liste. Jamais shell=True : une valeur reçue ne doit jamais devenir une commande de shell.
- Pourquoi une liste : chaque élément est passé tel quel. Avec shell=True, un caractère spécial comme le point-virgule serait interprété.
- timeout= limite la durée. Un dépassement lève subprocess.TimeoutExpired : transforme-le en ERREUR.
- Un code de retour non nul, ou une sortie qui n’est pas du JSON valide, donne ERREUR. Un succès passe à la même lecture que R13.
- Ce palier n’a pas de test automatique : la CI ne lance pas adsim. Tu vérifies à la démonstration D5, dans le conteneur.

```
Exemple travaillé, sans rapport avec ReconWrap :
import subprocess
resultat = subprocess.run(["echo", "a; b"], capture_output=True, text=True, timeout=5)
print(resultat.returncode, resultat.stdout.strip())
```

```
grep -n "shell=True" reconwrap/*.py   # aucune ligne ne doit s’afficher
```

```
.venv/bin/python -m unittest -v
```

```
git add reconwrap/ad.py
```

```
git commit -m "Lance adsim avec subprocess et délai maximal"
```

**Tu sais que c’est bon quand :** grep ne trouve aucun shell=True, et les tests R1 à R14 passent toujours.

*Indice :* Le chemin d’adsim se construit à partir du dossier du projet (pathlib), pas à partir de l’endroit où tu tapes la commande. Lis la documentation de subprocess.run pour timeout.

#### Palier 7 — L’orchestration : un échec ne bloque pas les autres (R6) (8 min)

Exécuter plusieurs modules dans l’ordre demandé, en isolant chaque échec.

- Écris R6 dans tests/test_orchestration.py : trois faux modules dans l’ordre A (OK), B (lève une exception), C (OK).
- L’orchestrateur reçoit une liste de noms, appelle chaque module par le dispatch de MR1, et collecte les résultats dans cet ordre.
- Pourquoi : un module qui plante est une information à rapporter, pas une raison d’arrêter le programme.
- Commit de l’orchestrateur.

```
Exemple travaillé, sans rapport avec ReconWrap :
nombres = [1, 2, 3]
carres = [n * n for n in nombres]
print(carres)
```

```
.venv/bin/python -m unittest -v
```

```
git add reconwrap/core.py tests/test_orchestration.py
```

```
git commit -m "Exécute plusieurs modules en isolant les échecs"
```

- **R6** — Échec isolé. Entrée : Trois faux modules dans cet ordre : A retourne OK, B lève une exception, C retourne OK. Attendu : Trois résultats dans l’ordre demandé : A OK, B ERREUR, C OK. C est bien exécuté après l’échec de B.

**Tu sais que c’est bon quand :** R6 passe : résultats dans l’ordre A OK, B ERREUR, C OK ; C est bien exécuté après l’échec de B.

*Indice :* L’ordre des résultats suit l’ordre de la liste reçue, pas celui du dictionnaire ni celui de l’exécution.

#### Palier 8 — La CLI argparse et les modules inconnus (R7) (8 min)

Lire les options de la ligne de commande et refuser un module inconnu avec le code de sortie 2.

- Écris R7 dans tests/test_cli.py : appelle la fonction principale de la CLI avec une liste d’arguments, dans un dossier temporaire. Vérifie le code de retour, le message sur stderr, et l’absence de rapport.
- Pourquoi une fonction main qui reçoit une liste : le test n’a pas besoin de lancer un sous-processus, il reste rapide et déterministe.
- Crée cli.py : --modules (choix dans le registre), --cible (127.0.0.1 par défaut), --chemin, --format (json ou md), --sortie. Ajoute __main__.py qui appelle la CLI.
- argparse écrit lui-même les erreurs d’usage sur stderr et sort avec le code 2.

```
Exemple travaillé, sans rapport avec ReconWrap :
import argparse
parser = argparse.ArgumentParser(prog="repas")
parser.add_argument("--plat", choices=["soupe", "salade"], default="soupe")
print(parser.parse_args(["--plat", "salade"]).plat)
parser.parse_args(["--plat", "pizza"])   # erreur : code 2 et SystemExit
```

```
.venv/bin/python -m unittest -v
```

```
.venv/bin/python -m reconwrap --modules scanner; echo $?
```

```
git add reconwrap/cli.py reconwrap/__main__.py tests/test_cli.py
```

```
git commit -m "Ajoute la CLI argparse et le refus des modules inconnus"
```

- **R7** — Module inconnu en CLI. Entrée : --modules network,scanner, dans un dossier temporaire. Attendu : Code de sortie 2, message d’erreur sur stderr, aucun rapport écrit.

**Tu sais que c’est bon quand :** R7 passe, et la commande avec un module inconnu affiche 2 après le message d’erreur.

*Indice :* Pour tester une sortie avec code 2, attends une exception SystemExit dans le test (assertRaises) et vérifie son code.

#### Palier 9 — La cible refusée en CLI (R8) et git stash (10 min)

Refuser une cible autre que 127.0.0.1 dans la CLI avant tout appel, et pratiquer git stash et git restore.

- Écris R8 dans tests/test_cli.py : --cible 192.0.2.10 dans un dossier temporaire. Le test vérifie le code 2, qu’aucun module n’est appelé, et qu’aucun fichier n’est écrit.
- Ne réécris pas la règle de cible : réutilise la validation de MR1 depuis la CLI.
- Pratique une fois git stash : modifie une ligne sans importance de cli.py, lance git stash, vérifie que git status est propre, puis git stash pop.
- git restore annule une modification non commitée, et elle est définitive. Pratique-le seulement sur un fichier de test jetable, comme ~/essai-git de MR1.

```
Exemple jetable :
cd ~/essai-git && echo "ligne en trop" >> a.txt
git restore a.txt
cat a.txt
cd -
```

```
.venv/bin/python -m unittest -v
```

```
git stash push -m "essai"
```

```
git stash pop
```

```
git add reconwrap/cli.py tests/test_cli.py
```

```
git commit -m "Refuse une cible autre que 127.0.0.1 dans la CLI"
```

- **R8** — Cible refusée en CLI. Entrée : --cible 192.0.2.10, dans un dossier temporaire. Attendu : Code de sortie 2, aucun module appelé, aucun fichier écrit.

**Tu sais que c’est bon quand :** R8 passe ; tu as vu git stash mettre tes modifications de côté et les rendre (git stash list est vide).

*Indice :* Une cible refusée doit échouer avant le lancement de tout module : le contrôle se fait en tête de la CLI.

#### Palier 10 — Rapports JSON et Markdown (R9, R10, R11) (12 min)

Écrire un rapport JSON et Markdown déterministe, dans un dossier dédié, avec des noms de fichiers sûrs.

- R9 : la date est un paramètre de la fonction d’écriture. Le test injecte 2026-01-05T08:00:00. Deux écritures identiques doivent donner deux fichiers JSON identiques octet pour octet.
- Pourquoi : un rapport qui change à chaque lancement sans raison est illisible dans un diff et impossible à comparer.
- R10 : un nom « ../../evil » ou « rapport final/v1 » est refusé ou nettoyé. Aucun fichier n’est créé hors du dossier demandé, et le nom ne contient aucun séparateur. Choisis refuser ou nettoyer, et écris ton choix dans la docstring.
- R11 : Markdown avec un titre, une ligne par module avec son statut, et les alertes sous leur module, dans l’ordre des résultats.
- Documente le code de sortie choisi : tu le reprendras dans le README de MR3.

```
Exemple travaillé, sans rapport avec ReconWrap :
import json
print(json.dumps({"b": 1, "a": 2}, sort_keys=True, ensure_ascii=False))
from pathlib import Path
print(Path("dossier/courses.txt").name)
```

```
Exemple travaillé dans un dossier temporaire, sans rapport avec ReconWrap :
import tempfile
from pathlib import Path
with tempfile.TemporaryDirectory() as dossier:
    chemin = Path(dossier) / "liste.txt"
    chemin.write_text("lait\npain\n", encoding="utf-8")
    print(chemin.read_text(encoding="utf-8").split())
```

```
.venv/bin/python -m unittest -v
```

```
cmp rapport_a/rapport.json rapport_b/rapport.json   # sans sortie : fichiers identiques
```

```
git add reconwrap/rapport.py tests/test_rapport.py
```

```
git commit -m "Ajoute les rapports JSON et Markdown"
```

- **R9** — Rapport JSON déterministe. Entrée : Mêmes résultats écrits deux fois, avec la date injectée 2026-01-05T08:00:00, dans deux dossiers temporaires. Attendu : Les deux fichiers JSON sont identiques octet pour octet. Ils contiennent la date injectée et, pour chaque module, les clés module, statut et alertes.
- **R10** — Nom de fichier sûr. Entrée : Nom de rapport « ../../evil » puis « rapport final/v1 », dans un dossier temporaire. Attendu : Le nom est refusé ou nettoyé. Aucun fichier n’est créé en dehors du dossier demandé, et aucun nom ne contient de séparateur de chemin.
- **R11** — Rapport Markdown. Entrée : Un résultat OK sans alerte, puis un résultat ERREUR avec deux alertes. Attendu : Un titre, une ligne par module avec son statut, les alertes listées sous leur module, dans l’ordre des résultats.

**Tu sais que c’est bon quand :** R9, R10 et R11 passent ; deux écritures donnent des JSON identiques ; aucun fichier ne sort du dossier demandé.

*Indice :* Passe la date en argument de la fonction et écris le JSON avec sort_keys=True. Pour R11, lis les résultats dans l’ordre reçu et construis les lignes au fur et à mesure.

#### Palier 11 — Démonstrations contre le labo (hors CI) (8 min)

Prouver, à un moment donné et labo démarré, que D1 à D6 se comportent comme attendu. Ce ne sont pas des tests.

- Démarre le labo avec son bouton dans Cyber Atelier. Les démonstrations ne figurent pas dans la CI : elles disent seulement que le labo réagissait ainsi au moment de l’essai.
- Lance les démonstrations dans le conteneur (docker compose exec atelier bash, puis cd /workspaces/reconwrap) avec python3 : le venv créé sur le Mac n’y fonctionne pas, et le module n’a pas besoin de dépendance.
- D5 utilise adsim, qui n’existe que dans le conteneur. D6 se lance après avoir arrêté le labo avec son bouton, puis te demande de le relancer pour la suite.
- Note les résultats dans les notes du parcours, pas dans le dépôt.

```
python3 -m reconwrap --modules network --cible 127.0.0.1 --format json --sortie rapports/   # D1
```

```
python3 -m reconwrap --modules web --chemin /fragile --format md --sortie rapports/   # D2
```

```
python3 -m reconwrap --modules web --chemin /durci --format md --sortie rapports/   # D3
```

```
python3 -m reconwrap --modules web --chemin /absent --format md --sortie rapports/   # D4 (puis --chemin /erreur)
```

```
python3 -m reconwrap --modules ad --format json --sortie rapports/   # D5, dans le conteneur
```

```
python3 -m reconwrap --modules network,web,ad --format json --sortie rapports/   # D6, labo arrêté
```

**Tu sais que c’est bon quand :** D1 : port 8000 open. D2 : trois alertes. D3 : zéro alerte. D4 : ERREUR avec 404, puis 500. D5 : comptes LAB.LOCAL. D6 : panne web distincte d’un code HTTP, et le rapport est écrit.

*Indice :* Si une démonstration donne un résultat inattendu, vérifie d’abord que le labo est démarré (son bouton) avant de changer le code.

**Démonstrations manuelles (hors tests) :**
- **D1** — Réseau contre le labo. Entrée : Labo démarré avec son bouton. python -m reconwrap --modules network --cible 127.0.0.1 --format json --sortie rapports/ Attendu : Le port 8000 est signalé open dans le rapport JSON.
- **D2** — Web : chemin fragile. Entrée : Labo démarré. --modules web --chemin /fragile --format md Attendu : Trois alertes, une par en-tête absent ou non conforme.
- **D3** — Web : chemin durci. Entrée : Labo démarré. --modules web --chemin /durci --format md Attendu : Zéro alerte.
- **D4** — Erreurs HTTP 404 et 500. Entrée : Labo démarré. --modules web avec --chemin /absent, puis --chemin /erreur. Attendu : Statut ERREUR avec le code 404, puis avec le code 500 ; alertes vide dans les deux cas.
- **D5** — Active Directory avec adsim. Entrée : python -m reconwrap --modules ad --format json --sortie rapports/ (dans le conteneur). Attendu : Les comptes du domaine LAB.LOCAL apparaissent avec leur état actif ou inactif. Aucun annuaire réel n’est contacté.
- **D6** — Labo arrêté. Entrée : Arrête le labo avec son bouton, puis lance --modules network,web,ad. Attendu : Le module web signale une panne de connexion, distincte d’un code HTTP. Les autres modules produisent quand même leur résultat et le rapport est écrit.

**Avant de livrer :**
- Les neuf tests R6 à R14 passent localement avec python -m unittest, sans nmap, sans labo et sans réseau.
- Un module en échec ne bloque ni les autres modules ni l’écriture du rapport. Le code de sortie choisi est documenté et identique à chaque lancement.
- Toute cible autre que 127.0.0.1 est refusée avant l’appel d’un module. Le code n’utilise jamais shell=True.
- Les démonstrations D1 à D6 sont consignées à part, avec le labo démarré explicitement. Elles ne figurent pas dans la CI.

### MR3 — feat/doc-qualite (70 min)

Rends le projet utilisable par quelqu’un d’autre, en paliers courts. Relis ton diff, documente l’API publique, écris un README qu’une personne peut suivre seule, puis ajoute le pipeline GitLab qui lance python -m unittest. Tu termines par le CHANGELOG, un conflit et une annulation faits dans des branches jetables, une page sur le projet final, puis la fusion et le tag v0.1.0. Le pipeline reste sur des tests locaux : il n’appelle ni nmap, ni labo, ni réseau. Pourquoi : un outil que personne ne sait lancer ou relire n’est pas un livrable. La documentation et la release sont des compétences de projet, pas un décor.

#### Palier 1 — Relire le diff et documenter l’API (10 min)

Relire ton diff comme si c’était celui d’un autre, puis ajouter docstrings et annotations à l’API publique.

- Commence par la branche de MR3 : après la fusion de MR2, mets main à jour et crée feat/doc-qualite.
- Relis le diff complet par rapport à main avec une checklist écrite par toi : noms, erreurs, effets de bord, chemins, tests. Garde la checklist hors du dépôt.
- Pour chaque fonction publique : une docstring (une phrase, puis paramètres et retour) et des annotations de type. Vérifie que la docstring décrit ce que la fonction fait réellement.
- Pourquoi : une annotation fausse trompe plus qu’une absence d’annotation.

```
git switch main && git pull --ff-only && git switch -c feat/doc-qualite
```

```
git diff main --stat
```

```
git diff main
```

```
Exemple travaillé, sans rapport avec ReconWrap :
def compter_mots(texte: str) -> int:
    """Retourne le nombre de mots d’un texte."""
    return len(texte.split())
```

```
.venv/bin/python -m unittest -v
```

```
git add reconwrap/
```

```
git commit -m "Ajoute docstrings et annotations de type"
```

**Tu sais que c’est bon quand :** Chaque fonction publique a une docstring exacte et des annotations ; les tests passent toujours.

*Indice :* Relis en te mettant à la place de quelqu’un qui n’a pas écrit le code : si un nom ou un message ne dit pas ce qu’il fait, corrige le nom ou la docstring.

#### Palier 2 — Écrire le README (10 min)

Écrire un README qu’une personne sans aide peut suivre pour installer, lancer et étendre l’outil.

- Plan du README : installation (venv avec python3 -m venv .venv, puis .venv/bin/python), lancement, options de la CLI (--modules, --cible, --chemin, --format, --sortie), architecture (un module par domaine), comment ajouter un module, périmètre loopback, limites éthiques et légales.
- Pour l’ajout d’un module, décris les trois gestes : écrire la fonction selon le contrat, la brancher dans le registre, écrire ses tests. Ne retouche pas le dispatch.
- Pourquoi : un outil que personne ne sait lancer n’est pas un livrable.
- Teste ton README : suis-le à la lettre dans un dossier propre (un clone dans un dossier temporaire) et note chaque endroit où tu bloques.

```
Exemple travaillé, sans rapport avec ReconWrap :
# Recettes
## Installation
```bash
python3 -m venv .venv
```
```

```
git add README.md
```

```
git commit -m "Rédige le README"
```

**Tu sais que c’est bon quand :** Tu as suivi le README dans un dossier propre et tu lances les tests et l’aide sans rien devoir deviner.

*Indice :* Pour chaque étape du README, écris la commande exacte puis le résultat attendu. Une phrase qui ne correspond à rien dans le code doit être corrigée.

#### Palier 3 — Contrat des trois modules et aide CLI (R15, R17) (8 min)

Vérifier que les trois modules respectent le contrat hors ligne, et que l’aide de la CLI est complète.

- Écris R15 dans tests/test_contrat.py : relis les résultats de network (fixture XML), de ad (fixture JSON) et de web (classement injecté) avec la fabrique de MR1. Vérifie les cinq clés, un statut OK, ERREUR ou IGNORE, et une liste d’alertes.
- Pourquoi : si un module change de forme, ce test casse ici, et pas dans ton rapport final.
- Écris R17 : python -m reconwrap --help doit sortir avec le code 0 et afficher --modules, --cible, --chemin, --format et --sortie.
- Pour tester plusieurs cas du même type sans écrire dix fois la même ligne, unittest a subTest.

```
Exemple travaillé, sans rapport avec ReconWrap :
import unittest
class TestCarres(unittest.TestCase):
    def test_carres(self):
        for n, attendu in [(2, 4), (3, 9)]:
            with self.subTest(n=n):
                self.assertEqual(n * n, attendu)
```

```
.venv/bin/python -m unittest -v
```

```
.venv/bin/python -m reconwrap --help; echo $?
```

```
git add tests/test_contrat.py tests/test_cli.py
```

```
git commit -m "Ajoute les tests de contrat et d’aide CLI"
```

- **R15** — Contrat des trois modules hors ligne. Entrée : Résultats de network (fixture XML), ad (fixture JSON) et web (classement injecté), relus avec la fabrique de résultat de MR1. Attendu : Les trois résultats ont les cinq clés, un statut OK, ERREUR ou IGNORE, et une liste d’alertes.
- **R17** — Aide de la CLI. Entrée : python -m reconwrap --help Attendu : Code de sortie 0. L’aide affiche les options --modules, --cible, --chemin, --format et --sortie.

**Tu sais que c’est bon quand :** R15 et R17 passent, et l’aide affiche les cinq options.

*Indice :* Pour un module hors ligne, passe-lui le fichier de fixture au lieu de le lancer : le test reste rapide et sans réseau.

#### Palier 4 — Le pipeline GitLab et la suite complète (R16) (10 min)

Écrire le pipeline qui lance les tests sur chaque merge request, et prouver que la suite passe sans labo ni nmap.

- GitLab CI lit un fichier .gitlab-ci.yml à la racine du dépôt. Un job est une étape avec une image (Python) et une liste de commandes. Lis la documentation des règles pour limiter le job aux merge requests.
- Pourquoi l’indentation compte en YAML : les niveaux se lisent par les espaces. Exemple sans rapport :
- Écris le fichier toi-même : une image Python, une étape qui lance python -m unittest depuis la racine, déclenchée sur les merge requests. Cyber Atelier ne fournit pas ce fichier.
- R16 : labo arrêté, nmap non utilisé. Depuis la racine, la commande doit sortir avec le code 0, les tests R1 à R15 doivent être découverts, et aucun test ne se connecte à 127.0.0.1:8000 ni n’appelle nmap ou adsim.
- Pousse la branche et ouvre la merge request. Attends le pipeline. Si l’école n’a pas de runner, note-le au lieu de déclarer la CI validée.

```
Exemple YAML sans rapport avec ReconWrap :
courses:
  - lait
  - pain
```

```
.venv/bin/python -m unittest; echo $?
```

```
git add .gitlab-ci.yml
```

```
git commit -m "Ajoute le pipeline GitLab qui lance unittest"
```

```
git push -u origin feat/doc-qualite
```

- **R16** — Suite complète sans labo. Entrée : python -m unittest lancé depuis la racine, labo arrêté et nmap absent du système. Attendu : Code de sortie 0. Les tests R1 à R15 sont découverts, et aucun test ne se connecte à 127.0.0.1:8000 ni n’appelle nmap ou adsim.

**Tu sais que c’est bon quand :** La commande du pipeline est celle que tu as testée en local, depuis la racine, et elle sort avec 0. Le statut du pipeline dans GitLab est noté tel qu’il est.

*Indice :* Le piège fréquent : une commande qui marche depuis un sous-dossier, mais pas depuis la racine. Tu lances tes tests depuis la racine, comme le pipeline.

#### Palier 5 — Le CHANGELOG de la version 0.1.0 (8 min)

Écrire l’historique de la version 0.1.0 : ce qui est ajouté et ce qui reste limité.

- Crée CHANGELOG.md avec une section 0.1.0 : ajouts, puis limites connues.
- Une entrée par changement visible pour l’utilisateur, en phrases courtes. Les limites connues comptent autant que les ajouts.
- Pourquoi : quelqu’un qui découvre l’outil doit savoir ce qu’il sait faire et ce qu’il ne fait pas.

```
Exemple travaillé, sans rapport avec ReconWrap :
## 0.1.0
### Ajouté
- Recette de crêpes.
### Limites connues
- Pas de version sans gluten.
```

```
git add CHANGELOG.md
```

```
git commit -m "Ajoute le CHANGELOG pour la version 0.1.0"
```

**Tu sais que c’est bon quand :** CHANGELOG.md contient une section 0.1.0 avec des ajouts et des limites connues.

*Indice :* Une limite connue est une information utile : par exemple, le module AD ne tourne que sur le domaine fictif.

#### Palier 6 — La page sur le projet final (8 min)

Rédiger un bilan honnête : ce qui est fait, ce qui reste à apprendre, et les autorisations nécessaires.

- Crée docs/PROJET_FINAL.md avec trois parties : ce que tu ferais (un module AD réel contre un domaine dont tu as l’autorisation écrite, une interface graphique optionnelle), ce que tu ne ferais pas, et un bilan avec la liste de ce qui reste à apprendre.
- Précise l’autorisation écrite nécessaire pour tout test sur un vrai domaine : un accord écrit, daté, du propriétaire du domaine.
- Pour chaque idée, demande-toi : est-ce que je l’ai faite, ou est-ce que je la ferais ? Un bilan qui dit « je ne sais pas encore » est une réponse valide.

```
git add docs/PROJET_FINAL.md
```

```
git commit -m "Rédige la page sur le projet final"
```

**Tu sais que c’est bon quand :** docs/PROJET_FINAL.md distingue fait, à faire, et autorisation nécessaire.

*Indice :* Un projet qui touche à un vrai réseau ou un vrai annuaire demande une autorisation écrite avant le premier test, même pour un essai rapide.

#### Palier 7 — Un conflit et un revert dans des branches jetables (8 min)

Résoudre un conflit en lisant les marqueurs, et annuler un commit avec git revert, sans toucher à la branche principale.

- Un conflit n’est pas une erreur : Git demande une décision quand deux branches changent la même ligne. Exemple sans rapport dans un dépôt jetable :
- Dans les branches jetables de ce palier (depuis main à jour), modifie la même ligne de README.md sur deux branches, puis fusionne l’une dans l’autre : Git signale le conflit.
- Lis les marqueurs <<<<<<<, ======= et >>>>>>> dans README.md, garde la version voulue, supprime les marqueurs, puis git add et git commit.
- git revert crée un commit inverse : l’historique reste intact. git reset réécrit l’historique : ne l’utilise pas sur une branche partagée. Fais le revert sur une branche jetable, jamais sur main.
- Supprime les branches jetables une fois terminé.

```
Exemple jetable, hors de ReconWrap :
mkdir ~/essai-conflit && cd ~/essai-conflit && git init -b main
echo pain > recette.txt && git add recette.txt && git commit -m "Recette de base"
git switch -c sucre && echo sucre > recette.txt && git commit -am "Ajoute le sucre"
git switch main && git switch -c sel && echo sel > recette.txt && git commit -am "Ajoute le sel"
git merge sucre   # conflit attendu
cd -
```

```
git switch main && git pull --ff-only
```

```
git switch -c jetable-conflit-a && (modifie une ligne de README.md, puis git commit -am "Essai A")
```

```
git switch main && git switch -c jetable-conflit-b && (modifie la même ligne, puis git commit -am "Essai B")
```

```
git merge jetable-conflit-a   # conflit sur README.md : résous-le, puis git add README.md && git commit
```

```
git switch main && git switch -c jetable-revert && (ajoute une ligne, git commit -am "Commit de test")
```

```
git revert HEAD --no-edit
```

```
git switch main && git branch -D jetable-conflit-a jetable-conflit-b jetable-revert
```

**Tu sais que c’est bon quand :** grep -n "<<<<<<<" README.md ne trouve rien ; le commit de test n’est pas dans main ; git branch n’affiche plus les branches jetables.

*Indice :* Ne garde jamais les marqueurs. Pour annuler, utilise git revert sur une branche jetable, pas git reset. git branch -D ne sert qu’aux branches jetables.

#### Palier 8 — Ouvrir la MR3, la fusionner et poser le tag v0.1.0 (8 min)

Faire relire la MR3, la fusionner si l’école l’autorise, puis poser le tag annoté v0.1.0 sur la principale.

- Relis le diff de la MR3 avec ta checklist du premier palier. Ouvre la merge request dans GitLab.
- Attends le pipeline. La fusion n’a lieu que si le pipeline est vert et que l’école l’autorise. Sinon, note l’état réel.
- Après fusion, mets main à jour, puis pose le tag annoté v0.1.0. Un tag annoté a un message et un auteur. Pousse-le séparément de la branche.
- Pourquoi un tag : il fige la version. Une version déplacée après coup trompe tous ceux qui s’y fient.

```
git status
```

```
git push -u origin feat/doc-qualite
```

```
git switch main && git pull --ff-only
```

```
git tag -a v0.1.0 -m "ReconWrap 0.1.0"
```

```
git push origin v0.1.0
```

```
git show --stat v0.1.0
```

**Tu sais que c’est bon quand :** git tag --list affiche v0.1.0, et git show v0.1.0 pointe sur le même commit que main après fusion.

*Indice :* Si la fusion n’a pas eu lieu, ne pose pas le tag. Un tag annoté a son propre message : écris-le court.

**Avant de livrer :**
- Une personne qui n’a pas écrit le code peut installer et lancer l’outil en suivant le README, sans aide extérieure.
- Le pipeline de la MR lance python -m unittest et passe. Si l’instance de l’école n’a pas de runner, note-le au lieu de déclarer la CI validée.
- Le tag v0.1.0 pointe sur le commit fusionné de la principale. Le conflit et le revert ont été faits dans des branches jetables, supprimées ensuite.
- docs/PROJET_FINAL.md distingue ce qui est fait, ce qui reste à apprendre, et précise l’autorisation nécessaire pour tout test sur un vrai domaine.

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
