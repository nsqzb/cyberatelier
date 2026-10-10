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

## Les trois MR

Les minutes des missions sont incluses dans les 300 minutes du parcours.

### MR1 — feat/empreinte (85 min)

Tu vas écrire une fonction qui calcule l’empreinte SHA-256 d’un fichier, puis la tester sur deux oracles fixes et un cas de fichiers identiques. Méthode : un palier à la fois, un test d’abord (il échoue), puis le plus petit code qui le fait passer, puis un commit.

#### Palier 1 — Prépare la branche feat/empreinte (6 min)

Partir d’un dépôt propre, sur une branche dédiée à cette MR.

- Ouvre le dossier workspaces/fileguard dans le terminal de VS Code (ou, dans le conteneur, docker compose exec atelier bash puis cd /workspaces/fileguard).
- Si le dépôt n’est pas encore cloné, fais d’abord l’étape « Cloner le dépôt » de l’onglet Environnement.
- Crée la branche de MR1 depuis la branche principale, puis vérifie où tu es.

```
git status
```

```
git switch -c feat/empreinte
```

```
git status
```

**Tu sais que c’est bon quand :** git status affiche « On branch feat/empreinte » et « nothing to commit ».

*Indice :* Si Git répond « not a git repository », tu n’es pas dans le dossier du dépôt. Si la branche existe déjà, utilise git switch feat/empreinte, sans -c.

#### Palier 2 — Des octets, pas du texte (10 min)

Comprendre pourquoi on lit un fichier en mode binaire pour obtenir ses octets exacts.

- Un fichier est une suite d’octets. Le mode texte (par défaut) décode le contenu et peut traiter les fins de ligne ; le mode binaire (rb, wb) donne les octets tels quels.
- Fais l’essai hors du dépôt : crée un dossier ~/essais, puis un fichier jetable fruits.bin qui contient les octets d’un mot fictif.
- Relis-le en mode binaire et affiche le contenu et son type. Supprime ensuite le fichier jetable.

```
mkdir -p ~/essais && cd ~/essais
```

```
python3 -c "open('fruits.bin', 'wb').write(b'pomme')"
```

```
python3 -c "d = open('fruits.bin', 'rb').read(); print(d, type(d))"
```

```
rm fruits.bin && cd -
```

**Tu sais que c’est bon quand :** Tu vois b'pomme' et le type <class 'bytes'>.

*Indice :* Le préfixe b devant les guillemets désigne des octets. Une chaîne de texte (str) n’est pas acceptée par hashlib : il faut des octets.

#### Palier 3 — Premier test rouge, puis premier code vert : F1 (14 min)

Écrire le test avant la fonction, voir l’échec, puis faire passer le test avec le minimum de code.

- Notion : un fichier temporaire est créé par tempfile et supprimé à la fin du bloc with. Exemple sans rapport avec l’exercice : un dossier temporaire contenant un fichier de fruits.
- Crée verification.py avec une classe de test unittest. Ajoute le test F1 : un fichier de zéro octet, dans un dossier temporaire créé par le test, comparé à l’oracle du fichier vide écrit en constante dans le test.
- Lance le test : il échoue, parce que fileguard.py n’existe pas encore. C’est la phase rouge, elle est normale.
- Crée fileguard.py avec une fonction calculer_sha256(chemin) (ce nom est proposé ; tu peux le garder). Elle ouvre le fichier en mode binaire, calcule le SHA-256 des octets et renvoie l’empreinte en hexadécimal minuscule. Relance : F1 passe (phase verte).
- Commit de ce palier.

```
python3 -c "import tempfile, pathlib; d = tempfile.TemporaryDirectory(); p = pathlib.Path(d.name) / 'fruits.txt'; p.write_bytes(b'pomme'); print(p.read_bytes())"
```

```
python3 verification.py
```

```
git add fileguard.py verification.py
```

```
git commit -m "Calcule l’empreinte SHA-256 du fichier vide"
```

- **F1** — Empreinte du fichier vide. Entrée : Fichier temporaire de zéro octet Attendu : e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

**Tu sais que c’est bon quand :** F1 passe ; python3 verification.py se termine sans erreur ; git log --oneline montre le nouveau commit.

*Indice :* Phase rouge : une erreur du type ImportError ou NameError est l’échec attendu. Pour la phase verte, la documentation de hashlib et celle d’open donnent les deux outils dont tu as besoin ; l’oracle reste une constante du test.

#### Palier 4 — F2 : les trois octets abc, sans saut de ligne (14 min)

Vérifier que l’empreinte dépend des octets exacts, sans fin de ligne ajoutée.

- Ajoute le test F2 : un fichier temporaire qui contient exactement les octets de « abc », sans saut de ligne final. Compare à l’oracle abc, écrit en constante dans le test.
- Lance les tests. S’il passe tout de suite, c’est possible : écris le test quand même et note-le dans ton message de commit.
- Si F2 échoue, relis comment ton fichier est ouvert et écrit. Ne change jamais la constante de l’oracle pour faire passer le test.
- Une fois F1 et F2 verts, commit.

```
python3 verification.py
```

```
git add fileguard.py verification.py
```

```
git commit -m "Vérifie l’empreinte des trois octets abc"
```

- **F2** — Empreinte des trois octets abc. Entrée : Fichier temporaire contenant exactement b"abc", sans saut de ligne final Attendu : ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad

**Tu sais que c’est bon quand :** F1 et F2 passent, et le code n’a pas été modifié pour contourner une constante.

*Indice :* Pour écrire exactement trois octets, utilise un littéral b suivi de guillemets, sans \n. Vérifie que le test lit les octets sans conversion de texte.

#### Palier 5 — F3 : deux contenus identiques, deux empreintes identiques (14 min)

Écrire un test qui crée lui-même ses fichiers et compare deux résultats.

- Ajoute le test F3 : dans un même dossier temporaire, crée deux fichiers qui ont les mêmes octets, calcule leurs empreintes et compare-les.
- Le test ne lit ni le dossier personnel, ni un journal, ni une fixture : tout ce dont il a besoin est créé dans le dossier temporaire.
- Lance les tests, vérifie que F1, F2 et F3 passent, puis commit.

```
python3 verification.py
```

```
git add fileguard.py verification.py
```

```
git commit -m "Vérifie que deux contenus identiques ont la même empreinte"
```

- **F3** — Contenus identiques. Entrée : Deux fichiers temporaires contenant les mêmes octets Attendu : Empreintes identiques.

**Tu sais que c’est bon quand :** F1, F2 et F3 passent ; git log --oneline montre le nouveau commit.

*Indice :* Écris les mêmes octets dans deux noms différents, puis compare les deux résultats de ta fonction avec assertEqual.

#### Palier 6 — Faire tourner la même suite dans la CI (15 min)

Comprendre ce que la CI exécute, et ce qu’elle ne prouve pas encore.

- Crée .gitlab-ci.yml à la racine du dépôt, avec un seul job dont la ligne script lance uniquement python3 verification.py. Le job ne copie aucune fixture et ne lit aucun chemin du portail.
- Le YAML se lit à l’indentation (deux espaces par niveau). Exemple sans rapport avec l’exercice : un job qui affiche un mot.
- Lance la même commande en local avant de pousser.
- Distingue quatre niveaux : test local réussi ; pipeline GitLab réellement exécuté ; fusion autorisée par les règles de l’école ; case cochée dans Cyber Atelier, qui ne vérifie rien. Un fichier .gitlab-ci.yml présent ne prouve pas qu’un pipeline a tourné.
- Commit ce fichier.

```
job-bonjour:
  script:
    - echo "bonjour"
```

```
python3 verification.py
```

```
git add .gitlab-ci.yml
```

```
git commit -m "Ajoute la CI qui lance la suite locale"
```

**Tu sais que c’est bon quand :** Le fichier est commité. Le pipeline n’est confirmé que lorsque GitLab affiche un job exécuté et vert pour ta branche.

*Indice :* Si GitLab ne lance aucun pipeline, vérifie que le fichier est à la racine du dépôt, que la branche est poussée et que le runner de l’école est actif sur les branches non protégées.

#### Palier 7 — Livre la MR1 sans confondre test local et fusion (12 min)

Relire le diff, pousser la branche, ouvrir la MR et ne fusionner que le dernier commit vert.

- Regarde ce que tu livres : fichiers modifiés et historique. La MR doit contenir fileguard.py, verification.py et .gitlab-ci.yml, sans __pycache__.
- Pousse la branche et ouvre la merge request vers main.
- Relis le diff comme s’il était écrit par quelqu’un d’autre.
- Fusionne seulement si le dernier commit a passé le pipeline GitLab et que les règles de l’école l’autorisent. Vert en local ne suffit pas.
- Après la fusion, reviens sur main et mets-la à jour avant MR2.

```
git status
```

```
git diff main --stat
```

```
git push -u origin feat/empreinte
```

```
git switch main
```

```
git pull --ff-only
```

**Tu sais que c’est bon quand :** La MR ne contient que les trois fichiers attendus, et ta branche main locale contient la fusion (git log --oneline).

*Indice :* Si le push est refusé, vérifie le nom de la branche avec git branch. Ne fusionne pas avant d’avoir relu le diff et vu le pipeline.

**Avant de livrer :**
- La fonction lit les octets et renvoie une empreinte SHA-256 hexadécimale minuscule.
- Les tests comparent aux deux oracles fixes fournis ; la fonction testée ne calcule pas elle-même les valeurs attendues.
- Les tests ne dépendent pas du dossier personnel, d’un journal ou d’une fixture externe.
- La CI exécute uniquement la suite locale (python3 verification.py), sans service distant ni chemin du portail.

### MR2 — feat/manifest (85 min)

Tu vas inventorier les fichiers réguliers du premier niveau d’un dossier, trier les noms, puis écrire un manifest.json déterministe qui exclut lui-même et ne suit aucun lien symbolique. Méthode : un test d’abord, le plus petit code ensuite, un commit par palier de code.

#### Palier 1 — Repars de main à jour et crée feat/manifest (6 min)

Partir de la MR1 fusionnée, pas d’une branche ancienne.

- Reviens sur main et mets-la à jour, puis crée la branche de MR2.
- Vérifie que ton dépôt est propre avant de commencer.

```
git switch main
```

```
git pull --ff-only
```

```
git switch -c feat/manifest
```

```
git status
```

**Tu sais que c’est bon quand :** git status affiche « On branch feat/manifest » et « nothing to commit ».

*Indice :* Si git pull --ff-only refuse, c’est que main a divergé : ne force rien, demande de l’aide avant de continuer.

#### Palier 2 — Copie les fixtures fictives dans ton dépôt (8 min)

Disposer d’un petit dossier d’exemple, relisible, dans le dépôt.

- Sur le Mac, reste dans workspaces/fileguard : ../../ remonte jusqu’au projet Cyber Atelier, où se trouve fixtures/integrity. Dans le conteneur, remplace ../../fixtures par /app/fixtures.
- La commande crée fixtures/, copie les trois fichiers fictifs, puis rend les copies modifiables (chmod u+w). Les originaux restent en lecture seule.
- Vérifie le résultat, puis commit les copies : elles font partie de la MR2.

```
pwd
```

```
mkdir -p fixtures && cp ../../fixtures/integrity/* fixtures/ && chmod u+w fixtures/*
```

```
ls -l fixtures
```

```
git add fixtures
```

```
git commit -m "Ajoute les fixtures fictives FileGuard"
```

**Tu sais que c’est bon quand :** ls fixtures affiche README.txt, message.txt et settings.ini ; git log --oneline montre le commit.

*Indice :* Si cp répond « No such file or directory », pwd te dit où tu es : la commande doit être lancée depuis workspaces/fileguard. Les fixtures ne sont pas présumées présentes sur le runner : les tests, eux, créent leurs propres fichiers.

#### Palier 3 — Un JSON stable : la forme avant le code (10 min)

Savoir écrire exactement le format du contrat, avec un ordre de clés et une fin de ligne stables.

- Notion : json.dumps écrit un dictionnaire dans l’ordre où ses clés ont été ajoutées. Avec indent=2, la sortie est lisible et stable. Exemple sans rapport avec l’exercice : un panier de fruits.
- Contrat : un objet JSON avec la clé schema (valeur 1), puis la clé files : une liste d’objets. Chaque objet a exactement deux clés, name (nom simple) puis sha256 (64 caractères hexadécimaux minuscules). Le fichier se termine par un saut de ligne.
- Tu n’as rien à coder à ce palier : écris à la main, sur un exemple fictif, un JSON qui respecte ce contrat, puis compare-le avec la forme donnée dans le guide.

```
python3 -c "import json; print(json.dumps({'b': 1, 'a': 2}, indent=2))"
```

```
python3 -c "import json; print(json.dumps({'schema': 1, 'files': []}, indent=2))"
```

**Tu sais que c’est bon quand :** Tu sais dire pourquoi sort_keys=True n’est pas adapté ici : il réordonnerait schema et files, alors que le contrat impose schema puis files.

*Indice :* Ne mets pas de chemin absolu dans le JSON. L’empreinte n’est pas encore calculée : ce palier ne sert qu’à fixer la forme.

#### Palier 4 — F4 : dossier vide, premier niveau seulement (14 min)

Lister les fichiers réguliers du premier niveau avec pathlib, sans entrer dans les sous-dossiers.

- Notion : pathlib.Path(dossier).iterdir() donne les entrées directes d’un dossier. Exemple sans rapport : lister les fichiers d’un dossier fruits.
- Ajoute le test F4 : un dossier temporaire vide donne un manifeste valide avec une liste vide. Lance-le, il échoue parce que la fonction n’existe pas encore.
- Écris le plus petit code qui fait passer F4. Ne parcours aucun sous-dossier.
- Commit ce palier.

```
python3 -c "from pathlib import Path; [print(c.name, c.is_file()) for c in Path('.').iterdir()]"
```

```
python3 verification.py
```

```
git add fileguard.py verification.py
```

```
git commit -m "Produit un manifeste vide pour un dossier vide"
```

- **F4** — Dossier vide. Entrée : Dossier temporaire vide Attendu : Manifeste valide avec une liste vide.

**Tu sais que c’est bon quand :** F1 à F4 passent ; git log --oneline montre le commit.

*Indice :* Un sous-dossier apparaît dans iterdir() mais n’est pas un fichier régulier. Vérifie-le avant de l’ajouter à l’inventaire.

#### Palier 5 — F5 : trier les noms et écrire le fichier (15 min)

Obtenir le même fichier quel que soit l’ordre de création des fichiers.

- Ajoute le test F5 : crée plusieurs fichiers dans un ordre non trié, génère le manifeste, puis vérifie que les entrées sont triées par nom.
- Trie les noms avant l’écriture, avec sorted(). Écris le fichier en UTF-8 et ajoute un saut de ligne final, puis vérifie que le contenu correspond au contrat.
- Le nom de fichier du manifeste est manifest.json. Ce palier ne règle pas encore l’exclusion : elle viendra à F6.
- Le guide demande de décider et de documenter si la commande crée ou remplace le manifeste. Note ta décision maintenant ; tu la rédigeras dans le README en MR3.
- Commit ce palier.

```
python3 -c "print(sorted(['zeta.txt', 'alpha.txt']))"
```

```
python3 verification.py
```

```
git add fileguard.py verification.py
```

```
git commit -m "Trie les entrées du manifeste par nom"
```

- **F5** — Ordre déterministe. Entrée : Fichiers créés dans un ordre non trié Attendu : Entrées JSON triées par nom.

**Tu sais que c’est bon quand :** F1 à F5 passent ; le contenu du manifeste est identique d’un lancement à l’autre sur le même dossier.

*Indice :* Trie les noms, pas les empreintes. json.dump n’écrit pas de saut de ligne final : ajoute-le toi-même.

#### Palier 6 — F6 : le manifeste ne se compte pas lui-même (12 min)

Exclure le manifeste de son propre inventaire, même quand il se trouve dans le dossier examiné.

- Ajoute le test F6 : écris le manifeste dans le même dossier que les données, relance l’inventaire, et vérifie que manifest.json n’apparaît pas dans ses propres entrées.
- Écris le plus petit code qui fait passer F6. La comparaison se fait sur le nom simple du fichier, pas sur un chemin complet.
- Commit ce palier.

```
python3 -c "from pathlib import Path; print(Path('dossier/manifest.json').name)"
```

```
python3 verification.py
```

```
git add fileguard.py verification.py
```

```
git commit -m "Exclut le manifeste de son propre inventaire"
```

- **F6** — Exclusion du manifeste. Entrée : Manifeste écrit au même endroit que les données Attendu : Le manifeste ne figure pas dans ses propres entrées.

**Tu sais que c’est bon quand :** F1 à F6 passent ; manifest.json n’apparaît jamais dans les entrées.

*Indice :* Le nom simple d’un fichier est accessible via l’attribut name d’un Path. Compare-le à la constante du nom du manifeste.

#### Palier 7 — F7 : refuser les liens symboliques (12 min)

Refuser clairement un lien symbolique, et tester ce refus quand le système permet d’en créer.

- Notion : os.symlink(cible, lien) crée un lien dans un dossier temporaire. Exemple sans rapport : un raccourci vers un fichier de fruits. Pathlib.is_symlink() dit si une entrée est un lien.
- Ajoute le test F7 : crée un lien vers un fichier temporaire. Si le système refuse de créer le lien, le test se termine proprement avec skipTest et un message clair.
- Écris le code qui refuse le lien avec une erreur explicite dont le message indique qu’un lien symbolique est refusé. Pour le contrat, choisis un type d’exception et documente-le dans le README en MR3.
- Vérifie que le test passe quand le lien existe, et que l’inventaire ne le suit pas. Commit.

```
python3 -c "import os, tempfile, pathlib; d = tempfile.mkdtemp(); os.symlink(pathlib.Path(d) / 'a', pathlib.Path(d) / 'lien'); print(pathlib.Path(d, 'lien').is_symlink())"
```

```
python3 verification.py
```

```
git add fileguard.py verification.py
```

```
git commit -m "Refuse les liens symboliques dans l’inventaire"
```

- **F7** — Lien symbolique. Entrée : Lien symbolique vers un fichier temporaire, si supporté Attendu : Refus clair selon le contrat.

**Tu sais que c’est bon quand :** F1 à F7 passent ; la sortie de l’exemple est True pour le lien.

*Indice :* Vérifie is_symlink() avant is_file() : is_file() suit le lien et répondrait sur la cible. Un test qui ne peut pas créer de lien doit être ignoré avec un message, pas réussir silencieusement.

#### Palier 8 — Livre la MR2 (8 min)

Relire le diff, pousser feat/manifest, ouvrir la MR et ne pas livrer de fichiers générés.

- Regarde le diff : fileguard.py, verification.py, fixtures/. Un manifest.json généré par tes essais ne doit pas être commité.
- Pousse la branche et ouvre la merge request vers main.
- Attends le pipeline vert dans GitLab, puis fusionne seulement si les règles de l’école l’autorisent. Vert en local ne suffit pas.
- Après la fusion, reviens sur main et mets-la à jour avant MR3.

```
git status
```

```
git diff main --stat
```

```
git push -u origin feat/manifest
```

```
git switch main
```

```
git pull --ff-only
```

**Tu sais que c’est bon quand :** git status ne montre aucun manifest.json non suivi à commiter ; la MR contient les fichiers attendus ; main locale contient la fusion.

*Indice :* Si git status montre manifest.json, ajoute-le à .gitignore plutôt que de le commiter, ou supprime-le avant le commit.

**Avant de livrer :**
- Chaque entrée désigne un fichier régulier directement dans le dossier et ne contient aucun chemin absolu.
- Le manifeste est déterministe et exclu de l’inventaire.
- Aucun lien n’est suivi et aucun sous-dossier n’est parcouru.
- Les fixtures fictives (README.txt, settings.ini, message.txt) sont copiées dans le dépôt, avec des droits d’écriture pour tes copies.

### MR3 — feat/comparaison (80 min)

Tu vas comparer le manifeste à l’inventaire courant et classer chaque nom en inchangé, modifié, supprimé ou ajouté, sans analyser le disque entier. Méthode : un test d’abord, le plus petit code ensuite, un commit par palier de code, puis un README et une démonstration.

#### Palier 1 — Repars de main à jour et crée feat/comparaison (5 min)

Partir de la MR2 fusionnée, pour que la comparaison s’appuie sur le bon code.

- Reviens sur main, mets-la à jour, puis crée la branche de MR3.
- Vérifie que ton dépôt est propre.

```
git switch main
```

```
git pull --ff-only
```

```
git switch -c feat/comparaison
```

```
git status
```

**Tu sais que c’est bon quand :** git status affiche « On branch feat/comparaison » et « nothing to commit ».

*Indice :* Si la branche existe déjà, utilise git switch feat/comparaison, sans -c. Vérifie d’abord que MR2 apparaît bien dans git log.

#### Palier 2 — Comparer des ensembles de noms (8 min)

Séparer présence et absence des noms, puis comparer les empreintes nom par nom.

- Notion : un set ne contient que des valeurs distinctes ; la différence ensembliste donne ce qui est dans l’un et pas dans l’autre. Exemple sans rapport : deux paniers de fruits.
- Contrat proposé pour la comparaison : une fonction comparer(manifeste, inventaire) qui renvoie un dictionnaire aux clés inchange, modifie, supprime et ajoute, chacune avec une liste triée de noms. Un nom présent des deux côtés avec une empreinte différente est modifié.
- Le manifeste lui-même est ignoré : aucune entrée qui le concerne ne peut apparaître dans une catégorie.
- Pas de code à ce palier : vérifie sur l’exemple de commande que tu sais ce qu’est une différence et une intersection.

```
python3 -c "a = {'pomme', 'poire'}; b = {'poire', 'kiwi'}; print(a - b, b - a, a & b)"
```

**Tu sais que c’est bon quand :** Tu sais dire, pour un nom, s’il est absent d’un côté, ou présent des deux côtés avec des empreintes différentes.

*Indice :* Garde deux vues séparées : l’ensemble des noms d’un côté, un dictionnaire nom vers empreinte de l’autre. Compare les empreintes seulement pour les noms présents des deux côtés.

#### Palier 3 — F8 : aucun changement (10 min)

Écrire le premier cas de comparaison : tout est inchangé.

- Ajoute le test F8 : un dossier temporaire dont chaque fichier correspond exactement au manifeste. Tous les noms doivent être dans inchange, et les autres catégories vides.
- Lance le test : il échoue tant que comparer n’existe pas. Écris le plus petit code qui fait passer F8.
- Commit ce palier.

```
python3 verification.py
```

```
git add fileguard.py verification.py
```

```
git commit -m "Compare un dossier identique à son manifeste"
```

- **F8** — Aucun changement. Entrée : Le dossier correspond exactement au manifeste Attendu : Tous les fichiers dans inchangé.

**Tu sais que c’est bon quand :** F1 à F8 passent ; git log --oneline montre le commit.

*Indice :* Crée le manifeste avec ta fonction de MR2 dans le dossier temporaire, puis compare : tu n’as pas besoin d’écrire les empreintes à la main.

#### Palier 4 — F9 et F10 : modifié et supprimé (10 min)

Distinguer un fichier dont le contenu a changé d’un fichier qui a disparu.

- Ajoute le test F9 : même nom, contenu différent, donc une empreinte différente. Le nom doit être dans modifie.
- Ajoute le test F10 : un nom présent dans le manifeste mais absent du dossier. Le nom doit être dans supprime.
- Lance les tests, écris le code qui les fait passer, puis commit.

```
python3 verification.py
```

```
git add fileguard.py verification.py
```

```
git commit -m "Classe les fichiers modifiés et supprimés"
```

- **F9** — Fichier modifié. Entrée : Même nom, contenu dont l’empreinte diffère Attendu : Nom dans modifié.
- **F10** — Fichier supprimé. Entrée : Nom du manifeste absent du dossier Attendu : Nom dans supprimé.

**Tu sais que c’est bon quand :** F1 à F10 passent.

*Indice :* Pour F10, le manifeste garde le nom du fichier supprimé : l’inventaire courant, lui, ne le contient plus. Compare les deux ensembles de noms avant de comparer les empreintes.

#### Palier 5 — F11 et F12 : ajouté, puis plusieurs catégories (10 min)

Gérer les nouveaux fichiers, puis vérifier que les quatre catégories restent exactes quand elles coexistent.

- Ajoute le test F11 : un nouveau fichier régulier au premier niveau, absent du manifeste. Son nom doit être dans ajoute.
- Ajoute le test F12 : un dossier qui contient un cas inchangé, un modifié, un supprimé et un ajouté. Chaque nom doit être dans sa catégorie exacte, et nulle part ailleurs.
- Lance les tests, écris le code qui les fait passer, puis commit.

```
python3 verification.py
```

```
git add fileguard.py verification.py
```

```
git commit -m "Classe les fichiers ajoutés et les cas mêlés"
```

- **F11** — Fichier ajouté. Entrée : Nouveau fichier régulier au premier niveau Attendu : Nom dans ajouté.
- **F12** — Plusieurs catégories. Entrée : Dossier avec cas inchangé, modifié, supprimé et ajouté Attendu : Chaque nom dans sa catégorie exacte.

**Tu sais que c’est bon quand :** F1 à F12 passent.

*Indice :* Un nom ne doit jamais apparaître dans deux catégories à la fois. Vérifie-le dans F12 avec un assertEqual sur chaque liste.

#### Palier 6 — F13 et F14 : manifeste vide et manifeste exclu (8 min)

Vérifier les cas limites : un manifeste sans entrée, et un manifeste conservé à côté des données.

- Ajoute le test F13 : un manifeste sans entrée et un dossier qui contient des fichiers. Tous les fichiers doivent être dans ajoute.
- Ajoute le test F14 : le manifeste est conservé à côté des données. Il ne doit jamais être signalé comme ajouté ou modifié.
- Écris le code qui fait passer les deux tests, puis commit.

```
python3 verification.py
```

```
git add fileguard.py verification.py
```

```
git commit -m "Gère le manifeste vide et le manifeste exclu"
```

- **F13** — Manifeste vide. Entrée : Manifeste avec zéro entrée et dossier contenant des données Attendu : Les fichiers sont ajoutés.
- **F14** — Manifeste exclu. Entrée : Manifeste conservé à proximité des données Attendu : Il n’est jamais signalé comme ajouté ou modifié.

**Tu sais que c’est bon quand :** F1 à F14 passent : les quatorze tests sont verts.

*Indice :* Pour F14, l’exclusion doit s’appliquer à l’inventaire courant avant toute comparaison, pas seulement à l’affichage.

#### Palier 7 — Commandes simples et affichage par catégorie (8 min)

Relier la création et la vérification à une ligne de commande, sans parcourir le disque.

- Notion : sys.argv contient les arguments de la ligne de commande. Exemple sans rapport : un petit script qui affiche le premier argument.
- Ajoute deux commandes : creer DOSSIER (écrit manifest.json) et verifier DOSSIER (affiche les quatre catégories, un nom par ligne). Le dossier est toujours explicite ; le programme ne cherche rien ailleurs.
- Vérifie qu’un argument manquant ou un dossier inexistant donne un message clair et un code de sortie non nul.
- Commit ce palier.

```
python3 -c "import sys; print(sys.argv)" creer dossier
```

```
python3 fileguard.py creer fixtures
```

```
python3 fileguard.py verifier fixtures
```

```
git add fileguard.py
```

```
git commit -m "Ajoute les commandes creer et verifier"
```

**Tu sais que c’est bon quand :** Les deux commandes s’exécutent sur le dossier donné et affichent les quatre catégories.

*Indice :* Lis sys.argv[1] pour le nom de la commande, puis sys.argv[2] pour le dossier. Vérifie l’existence du dossier avant de rien écrire.

#### Palier 8 — Rédige le README (9 min)

Expliquer le programme et ses limites à quelqu’un qui ne l’a pas écrit.

- Le README contient : la structure du dossier, le format du manifeste (schema 1, files, name, sha256), les commandes, le comportement des liens symboliques et des sous-dossiers, le sens du résultat et les limites.
- Indique si creer crée ou remplace manifest.json, et quelle exception est levée pour un lien symbolique.
- Écris que le manifeste doit être digne de confiance, puisqu’une personne qui modifie les fichiers peut modifier un manifeste conservé à côté, et que le projet n’est pas un antivirus.
- Commit le README.

```
git add README.md
```

```
git commit -m "Documente FileGuard dans le README"
```

**Tu sais que c’est bon quand :** Un lecteur qui ne connaît pas le projet sait lancer les commandes, lire le résultat et voir les limites.

*Indice :* Relis le contrat du guide et vérifie que chaque point du README correspond à ce que ton code fait réellement.

#### Palier 9 — Démonstration des quatre catégories, puis livraison (12 min)

Montrer les quatre catégories sur un scénario, puis livrer la MR3 et fusionner le dernier commit vert.

- Démonstration (hors tests) : copie les fixtures dans un dossier de démonstration hors du dépôt, crée le manifeste, modifie un fichier, supprime-en un autre, ajoute un nouveau fichier, puis vérifie. Tu dois voir un fichier dans chaque catégorie, et README.txt inchangé.
- Relis le diff de la MR3, pousse la branche, puis ouvre la troisième merge request vers main.
- Attends le pipeline vert dans GitLab et fusionne seulement si les règles de l’école l’autorisent. La démonstration locale n’est pas une preuve de fusion.
- Après la fusion, mets main à jour : la série de trois MR est terminée.

```
cp -r fixtures ~/demo_fileguard
```

```
python3 fileguard.py creer ~/demo_fileguard
```

```
echo "modification" >> ~/demo_fileguard/message.txt
```

```
rm ~/demo_fileguard/settings.ini
```

```
echo "nouveau" > ~/demo_fileguard/nouveau.txt
```

```
python3 fileguard.py verifier ~/demo_fileguard
```

```
git status
```

```
git diff main --stat
```

```
git push -u origin feat/comparaison
```

```
git switch main
```

```
git pull --ff-only
```

**Tu sais que c’est bon quand :** La sortie de verifier range message.txt dans modifie, settings.ini dans supprime, nouveau.txt dans ajoute et README.txt dans inchange ; la MR3 est fusionnée après un pipeline vert.

*Indice :* Si verifier ne trouve pas de manifeste, vérifie que creer a bien écrit manifest.json dans ~/demo_fileguard. Ne fusionne pas avant d’avoir relu le diff et vu le pipeline.

**Avant de livrer :**
- Les quatre catégories ont des tests reproductibles et le manifeste lui-même est ignoré.
- Le programme reste limité au dossier choisi, au premier niveau, sans suivre de symlinks.
- Le README indique que le manifeste doit être digne de confiance et que le projet n’est pas un antivirus.

## Méthode GitLab

Le dossier FileGuard est vide au départ. Clone le dépôt de l’école directement dans le dossier courant avec git clone <URL_DU_DEPOT> . avant de créer les fichiers. Le point signifie « ici ». Le terminal web repart du dossier courant explicite pour chaque commande ; un cd seul ne persiste pas. Pour Git interactif, utilise docker compose exec atelier bash depuis le dossier Cyber Atelier.

Utilise un dépôt autorisé par l’école, un runner actif sur les MR des branches non protégées et les droits convenus pour les règles de fusion. Pour chaque MR, crée la branche depuis la principale actualisée, exécute la même commande de tests localement et en CI, lis le diff, puis ouvre la MR. Fusionne uniquement le dernier commit vert. Après chaque fusion, actualise la principale avant l’étape suivante.

La CI ne dépend pas d’un dossier de données du portail. Les tests créent leurs propres fichiers temporaires. Les fixtures d’exemple peuvent être copiées par l’apprenant dans son dépôt, mais elles ne remplacent pas les tests temporaires et ne sont pas supposées présentes sur le runner d’école.

## Repères de temps

Préparation GitLab et lecture : 30 min. MR1 empreintes et tests : 85 min. MR2 manifeste et tests : 85 min. MR3 comparaison, affichage et README : 80 min. Relecture et marge : 20 min. Total : 300 min.

## Livrables et limites

Livre fileguard.py, verification.py, un README, les fixtures fictives copiées dans le dépôt, une CI qui exécute les tests temporaires et trois MR successives. Montre un scénario où les quatre catégories sont distinguées, et explique clairement que le manifeste de référence doit lui-même être digne de confiance.

FileGuard est un outil pédagogique d’intégrité, pas un antivirus ni une garantie d’authenticité. SHA-256 permet de constater une différence avec un manifeste de confiance ; une personne capable de modifier les fichiers peut aussi modifier un manifeste conservé à côté. Il ne parcourt pas récursivement, ne suit pas les liens et ne cherche pas de secrets.
