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

Pose la structure du package et le contrat commun. Cette MR ne lance aucun outil : les tests utilisent de faux modules. Pourquoi : ce contrat est la colonne vertébrale du framework. Sans lui, ajouter un module oblige à modifier tout le reste.

Ce que tu dois faire, dans l’ordre :

1. Crée le package `reconwrap/` avec `__init__.py` et `__main__.py`, puis un `.gitignore` qui couvre `.venv/`, `__pycache__/` et `rapports/`. Vérifie avec `git status` que `.venv` n’apparaît pas.
2. Écris la fabrique du résultat normalisé. Elle refuse tout statut hors de `OK`, `ERREUR` et `IGNORE`.
3. Valide la cible : seule `127.0.0.1` passe.
4. Crée le registre (nom vers fonction) et le dispatch. Un nom inconnu est signalé clairement ; une exception de module devient un résultat `ERREUR`.
5. Ajoute un logger par module (niveaux DEBUG, INFO, ERREUR, format avec le nom du module). Les tests vérifient les résultats, pas le texte affiché.
6. Avant chaque commit : `git status`, `git diff`, `python -m unittest`. Fais des commits atomiques (structure, contrat, registre, logging séparés), puis relis le diff complet de la MR.

**Tests locaux à écrire :**

- **R1 — Résultat normalisé.** Entrée : fabrique appelée avec module « faux », statut « OK », donnees vide, alertes vide, duree_s 0.0. Attendu : dict aux cinq clés exactes ; `alertes` est une liste et `duree_s` un nombre positif ou nul.
- **R2 — Statut refusé.** Entrée : statut « FAUX », puis « ok » en minuscules. Attendu : `ValueError` avec un message en français qui cite le statut ; aucun dict retourné. Les minuscules sont refusées aussi.
- **R3 — Module inconnu.** Entrée : registre de trois faux modules (network, web, ad), demande du module « scanner ». Attendu : `ValueError` qui liste les modules connus ; aucun faux module appelé.
- **R4 — Exception isolée.** Entrée : faux module qui lève `RuntimeError` avec le message « boom ». Attendu : pas de propagation ; statut `ERREUR`, alertes vide, `donnees` contient le message d’erreur.
- **R5 — Cible loopback seulement.** Entrée : `127.0.0.1`, puis `192.0.2.10`, `example.com`, une chaîne vide, `10.0.0.0/24` et `127.0.0.1; ls`. Attendu : `127.0.0.1` accepté ; toutes les autres valeurs lèvent `ValueError`, sans appel de module.

**Acceptance :**

- `python -m reconwrap` s’exécute sans traceback, même sans module branché.
- R1 à R5 passent avec `python -m unittest`, sans réseau et sans outil externe.
- Ajouter un faux module ne demande aucune modification du dispatch : seul le registre change.
- Le `.venv` n’est pas suivi par Git, les commits sont atomiques, le diff a été relu.

### MR2 — feat/orchestration-rapport (100 min)

Branche les trois modules réels sur le contrat de MR1 et ajoute l’orchestration. Un module en échec ne fait échouer ni les autres ni le rapport. Pourquoi : c’est la première fois que ton code parle à de vrais outils. Tu apprends à isoler les effets de bord (processus, réseau, disque) pour que le reste reste testable.

Ce que tu dois faire, dans l’ordre :

1. Copie les fixtures dans le dépôt, puis vérifie qu’elles sont suivies :
   `mkdir -p fixtures && cp -r /app/fixtures/nmap/. fixtures/nmap/ && cp -r /app/fixtures/adsim/. fixtures/adsim/ && chmod -R u+w fixtures`
   Les originaux sont en lecture seule.
2. **Module réseau.** Reprends la logique de PortPilot (validation, états `open`, `closed`, `filtered`) et lis le XML avec `xml.etree.ElementTree`. Ajoute une option qui lit un XML fourni, utilisée par la CI. Un XML cassé donne `ERREUR`, sans trace d’exception.
3. **Module web.** Reprends le classement de HeaderScope et accepte l’un des quatre chemins du labo. Dans `donnees`, distingue un code HTTP (404, 500), une panne de connexion et un timeout.
4. **Module AD.** Lance `adsim` avec `subprocess` en liste d’arguments, jamais avec `shell=True`, avec un délai maximal. Un code de retour non nul ou un JSON invalide donne `ERREUR`. Ajoute une option qui lit une sortie capturée, utilisée par la CI.
5. **CLI argparse.** `--modules` (choix parmi le registre), `--cible` (127.0.0.1 par défaut), `--chemin` (pour le module web), `--format` (`json` ou `md`), `--sortie` (dossier de rapport). Une valeur invalide donne le code de sortie 2. Pratique `git stash` et `git restore` au moins une fois pendant cette MR.
6. **Rapport.** Écris le JSON et le Markdown dans le dossier de sortie, avec des noms de fichiers sûrs (sans séparateur de chemin ni `..`) et une date passée en paramètre. Documente le code de sortie choisi.

**Tests locaux à écrire :**

- **R6 — Échec isolé.** Entrée : trois faux modules dans l’ordre A (OK), B (lève une exception), C (OK). Attendu : trois résultats dans cet ordre, A OK, B ERREUR, C OK ; C est exécuté après l’échec de B.
- **R7 — Module inconnu en CLI.** Entrée : `--modules network,scanner`, dossier temporaire. Attendu : code 2, message sur stderr, aucun rapport écrit.
- **R8 — Cible refusée en CLI.** Entrée : `--cible 192.0.2.10`. Attendu : code 2, aucun module appelé, aucun fichier écrit.
- **R9 — Rapport JSON déterministe.** Entrée : mêmes résultats écrits deux fois, date injectée `2026-01-05T08:00:00`, deux dossiers temporaires. Attendu : deux fichiers JSON identiques octet pour octet ; la date injectée et, par module, les clés `module`, `statut` et `alertes` sont présentes.
- **R10 — Nom de fichier sûr.** Entrée : nom « ../../evil », puis « rapport final/v1 », dossier temporaire. Attendu : nom refusé ou nettoyé ; aucun fichier créé hors du dossier demandé ; aucun séparateur de chemin dans le nom.
- **R11 — Rapport Markdown.** Entrée : un résultat OK sans alerte, un résultat ERREUR avec deux alertes. Attendu : un titre, une ligne par module avec son statut, les alertes sous leur module, dans l’ordre des résultats.
- **R12 — Lecture XML nmap.** Entrée : `open_8000.xml`, `closed_8000.xml`, `mixed.xml`, `broken.xml`. Attendu : port 8000 `open` dans le premier, `closed` dans le deuxième ; `mixed.xml` donne `open`, `closed` et `filtered` ; `broken.xml` donne `ERREUR` sans exception.
- **R13 — Lecture AD depuis fixtures.** Entrée : `users.json`, puis `broken.json`, lus comme sorties capturées (le module n’appelle pas adsim). Attendu : pour `users.json`, le nombre de comptes égale `count` et actifs et inactifs sont distingués ; `broken.json` donne `ERREUR` avec un message.
- **R14 — Classement web sans réseau.** Entrée : statut 404 avec des en-têtes quelconques, puis statut 200 avec les trois en-têtes conformes. Attendu : 404 donne `ERREUR`, code 404 conservé, alertes vide ; 200 conforme donne zéro alerte. Aucune connexion n’est ouverte.

**Démonstrations (hors CI, labo démarré avec son bouton) :**

- **D1 — Réseau contre le labo.** `python -m reconwrap --modules network --cible 127.0.0.1 --format json --sortie rapports/`. Attendu : le port 8000 est signalé `open`.
- **D2 — Web : chemin fragile.** `--modules web --chemin /fragile --format md`. Attendu : trois alertes, une par en-tête absent ou non conforme.
- **D3 — Web : chemin durci.** `--modules web --chemin /durci --format md`. Attendu : zéro alerte.
- **D4 — Erreurs HTTP 404 et 500.** `--modules web` avec `--chemin /absent`, puis `--chemin /erreur`. Attendu : statut `ERREUR` avec le code 404, puis avec le code 500 ; alertes vide dans les deux cas.
- **D5 — Active Directory avec adsim.** `python -m reconwrap --modules ad --format json --sortie rapports/`, dans le conteneur. Attendu : les comptes du domaine `LAB.LOCAL` apparaissent avec leur état actif ou inactif ; aucun annuaire réel n’est contacté.
- **D6 — Labo arrêté.** Arrête le labo avec son bouton, puis lance `--modules network,web,ad`. Attendu : le module web signale une panne de connexion, distincte d’un code HTTP ; les autres modules produisent quand même leur résultat et le rapport est écrit.

**Acceptance :**

- R6 à R14 passent avec `python -m unittest`, sans nmap, sans labo et sans réseau.
- Un module en échec ne bloque ni les autres ni l’écriture du rapport ; le code de sortie est documenté et identique à chaque lancement.
- Toute cible autre que `127.0.0.1` est refusée avant l’appel d’un module. Le code n’utilise jamais `shell=True`.
- D1 à D6 sont consignées à part, avec le labo démarré explicitement. Elles ne figurent pas dans la CI.

### MR3 — feat/doc-qualite (70 min)

Rends le projet utilisable par quelqu’un d’autre. Pourquoi : un outil que personne ne sait lancer ou relire n’est pas un livrable. La documentation et la release sont des compétences de projet.

Ce que tu dois faire, dans l’ordre :

1. Relis le diff complet de la branche par rapport à la principale avec une checklist écrite par toi (noms, erreurs, effets de bord, chemins, tests). Ajoute docstrings et annotations de type à l’API publique, puis vérifie qu’elles correspondent au comportement réel.
2. Écris le README : installation dans un venv, lancement, options de la CLI, architecture (un module par domaine), comment ajouter un module, périmètre loopback, limites éthiques et légales.
3. Écris `.gitlab-ci.yml` : une image Python, une étape qui lance `python -m unittest` depuis la racine, déclenchée sur les merge requests. Vérifie la commande en local avant de pousser.
4. Crée `CHANGELOG.md` (version 0.1.0, ajouts, limites connues). Une fois la MR fusionnée, pose le tag annoté `v0.1.0` sur la branche principale (`git tag -a`) et pousse-le séparément.
5. Dans une branche jetable, provoque un conflit volontaire sur `README.md` entre deux branches, résous-le en lisant les marqueurs, puis annule un commit de test avec `git revert` sur une autre branche jetable, jamais sur la principale. Supprime ensuite les branches jetables.
6. Rédige `docs/PROJET_FINAL.md` : ce que tu ferais pour le projet final (module AD réel contre un domaine dont tu as l’autorisation écrite, interface graphique optionnelle, ce que tu ne ferais pas). Termine par un bilan honnête et la liste de ce qui reste à apprendre.

**Tests locaux à écrire :**

- **R15 — Contrat des trois modules hors ligne.** Entrée : résultats de `network` (fixture XML), `ad` (fixture JSON) et `web` (classement injecté), relus avec la fabrique de MR1. Attendu : cinq clés, statut `OK`, `ERREUR` ou `IGNORE`, liste d’alertes.
- **R16 — Suite complète sans labo.** Entrée : `python -m unittest` depuis la racine, labo arrêté, nmap absent. Attendu : code 0 ; R1 à R15 sont découverts ; aucun test ne se connecte à `127.0.0.1:8000` ni n’appelle nmap ou adsim.
- **R17 — Aide de la CLI.** Entrée : `python -m reconwrap --help`. Attendu : code 0 ; l’aide affiche `--modules`, `--cible`, `--chemin`, `--format` et `--sortie`.

**Acceptance :**

- Une personne qui n’a pas écrit le code peut installer et lancer l’outil en suivant le README, sans aide extérieure.
- Le pipeline de la MR lance `python -m unittest` et passe. Si l’instance de l’école n’a pas de runner, tu le notes au lieu de déclarer la CI validée.
- Le tag `v0.1.0` pointe sur le commit fusionné de la principale. Le conflit et le revert ont été faits dans des branches jetables, supprimées ensuite.
- `docs/PROJET_FINAL.md` distingue ce qui est fait, ce qui reste à apprendre, et précise l’autorisation nécessaire pour tout test sur un vrai domaine.

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
