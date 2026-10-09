# PortPilot — scanner TCP de laboratoire

**Durée : 5 heures · Niveau débutant · 3 merge requests**

Tu vas écrire un petit programme Python qui essaie une connexion TCP vers quelques ports de 127.0.0.1, conserve un état par port et affiche un bilan. Il n’envoie aucune donnée applicative et ne récupère aucune bannière. Un port ouvert signifie uniquement que la connexion TCP a réussi : cela ne prouve ni une vulnérabilité ni la nature du service.

Le parcours complet et les définitions détaillées des fonctions et des huit tests sont dans le [PDF PortPilot](/downloads/PortPilot.pdf). Ce fichier reprend aussi les étapes GitLab et les critères de livraison.

## Préparation

Utilise le dépôt autorisé par ton école, son URL et sa branche principale (main ou master). Il te faut Python 3, Git, un runner GitLab actif utilisable par les branches de MR et les droits nécessaires aux règles de fusion. Sans runner ou accès aux règles, tu peux développer et exécuter les tests localement, mais la CI bloquante reste non validée.

Le dossier de cours dans Cyber Atelier est vide. Clone le dépôt de l’école directement dans ce dossier avant de créer tes fichiers, avec git clone <URL_DU_DEPOT> . (le point signifie « ici »). Ainsi, le dépôt ne se retrouve pas dans un sous-dossier. Le terminal web lance chaque commande dans le dossier courant explicite et ne garde pas un cd d’une commande à la suivante. Pour une session Git interactive, ouvre un terminal de ta machine et lance docker compose exec atelier bash depuis le dossier de Cyber Atelier. Initialise le dépôt avec README.md et .gitignore ; ce dernier exclut les caches Python et portpilot.zip. Protège la branche principale selon les règles de l’école : pas de push direct, force push désactivé, fusion après pipeline réussi et option pipeline ignoré comme réussi désactivée. Vérifie que le runner accepte les jobs de branches non protégées et les tags demandés.

## Contrats Python

Écris cinq fonctions dans portpilot.py et les tests dans verification.py.

- valider_ports(ports) accepte une liste non vide de 1 à 10 ports distincts, entiers de 1 à 65535 inclus. Elle retourne les mêmes valeurs dans le même ordre. Elle lève ValueError pour une liste vide, plus de dix éléments, un doublon, une valeur hors bornes, un texte, un nombre décimal ou un booléen. Ne convertis pas le texte en entier. Une entrée qui n’est pas une liste est hors contrat.
- tester_port(port) utilise uniquement l’hôte constant 127.0.0.1 et le délai fixe de 0,5 seconde. Elle retourne exactement OUVERT si la connexion réussit, REFUSE pour ConnectionRefusedError, TIMEOUT pour un dépassement du délai et ERREUR pour un autre OSError. Toute socket créée est fermée même en cas d’échec.
- scanner_ports(ports) valide toute la liste avant toute connexion, fait une tentative par port dans l’ordre reçu et retourne une liste de paires [port, état] dans ce même ordre.
- resumer(resultats) retourne cinq compteurs entiers : total, ouverts, refuses, timeouts, erreurs. Les catégories totalisent total. Une liste vide donne cinq zéros.
- main coordonne la liste configurée, le scan, l’affichage d’un résultat par port et le bilan. Pour une liste invalide, affiche un message clair. L’import de portpilot par verification.py ne doit pas lancer main.

Reste dans le périmètre : pas de saisie interactive, d’arguments, de classes, de threads, de paquets pip, de plage de ports, de scan externe, d’exploitation, de lecture de fichiers ou de rapport écrit sur disque.

## Les trois MR

Les minutes des missions sont comprises dans les 300 minutes du parcours.

### MR1 — feat/validation (80 min)

Implémente valider_ports, les tests T1 à T5 et la première CI. T1 vérifie l’acceptation de [1, 8000, 65535] avec ordre et valeurs préservés. T2 refuse la liste vide. T3 refuse onze ports valides distincts. Pour T4, teste séparément chacun des six cas dans une liste d’un élément : [-1], [0], [65536], [« 8000 »], [80,5] et [True]. T5 refuse un doublon.

Pour chacun des tests négatifs T2 à T5, l’absence de ValueError est un échec ; toute autre exception est aussi un échec. Pour T4, chaque sous-cas doit être contrôlé séparément. verification.py importe le module, appelle réellement les tests et affiche un total cohérent. Une assertion ratée doit donner un code de sortie non nul.

Dans .gitlab-ci.yml, définis la politique de pipeline pour merge_request_event, sans règle finale permissive qui lancerait tous les push, et un job verifier qui exécute la même commande que localement (python verification.py, ou python3 selon l’environnement). N’emploie ni allow_failure, ni job manuel. La validation CI Lint contrôle la syntaxe, pas le fonctionnement du runner.

Pour démontrer le gate, ouvre une MR non-Draft sans conflit, vérifie le commit du pipeline, puis introduis sur la branche une petite régression réelle du code sans toucher aux tests. Observe que le pipeline rouge bloque la fusion. Corrige le code, pousse la correction, vérifie le dernier pipeline vert et fusionne. Conserve le lien du pipeline rouge et le motif du blocage.

### MR2 — feat/connexion (70 min)

Après la fusion de MR1, reviens sur la branche principale et récupère-la avant de créer cette branche. Implémente tester_port et ajoute T6 en conservant T1 à T5.

T6 ouvre dans le test une socket TCP IPv4 liée à 127.0.0.1 et au port 0. Le système attribue un port disponible ; lis-le avec getsockname(), appelle listen() et garde l’écoute ouverte pendant l’appel à tester_port. Vérifie exactement OUVERT, puis ferme l’écoute même si une assertion échoue. accept(), thread, attente fixe et port pré-réservé ne sont pas nécessaires. Le port 0 est réservé à l’allocation du test et demeure interdit à la liste scannée.

La CI continue d’exécuter toute la suite locale. Elle ne dépend ni d’un service déjà présent ni d’un laboratoire web. Le test utilise uniquement la boucle locale du runner.

### MR3 — feat/scan-bilan (80 min)

Après la fusion de MR2, actualise la branche principale. Implémente scanner_ports, resumer et main, puis ajoute T7 et T8 sans retirer les tests existants.

T7 crée deux sockets d’écoute éphémères distinctes, les garde ouvertes toutes les deux, puis vérifie que le scan retourne exactement les deux ports ouverts dans l’ordre fourni. Ferme les deux sockets systématiquement. T8 construit cinq résultats contractuels — deux OUVERT, un REFUSE, un TIMEOUT, un ERREUR — et vérifie les cinq compteurs exacts, puis les cinq zéros pour une liste vide. T8 vérifie le comptage, pas la production de vraies erreurs réseau. Les catégories réseau négatives doivent être implémentées et relues sans prétendre qu’elles sont couvertes par les huit tests.

Finalise README.md avant le pipeline de livraison. Il décrit l’objectif et ses limites, les prérequis, la configuration de la liste, le lancement, les quatre états, les tests et le téléchargement de l’artefact. Choisis un port disponible pour la démonstration locale et inscris-le dans ta liste avant le dernier commit. Pour une démonstration locale, tu peux lancer un serveur sur ce port puis exécuter PortPilot dans un autre terminal ; après arrêt du serveur, REFUSE est attendu. Le PDF propose 8000 comme exemple. Dans Cyber Atelier, le bouton du laboratoire intégré permet de démarrer et arrêter un service local : utilise-le au lieu de lancer un deuxième serveur sur le port 8000.

Étends la CI à deux stages successifs : test, puis livraison. Le job de livraison ne s’exécute qu’après le succès des tests et fabrique portpilot.zip contenant exactement portpilot.py, verification.py et README.md, conservé comme artefact téléchargeable pendant sept jours. Vérifie le contenu de l’artefact du dernier pipeline vert de MR3 avant expiration.

## Cycle de travail et validation

Pour chaque MR, développe et teste localement, lis git status et git diff, ajoute explicitement les fichiers nécessaires, crée des commits descriptifs et pousse sur la branche de la MR. Ouvre la MR vers la branche principale, vérifie le pipeline du dernier commit et relis le diff. Après chaque fusion, actualise la branche principale avant de créer la suivante. Une seule MR finale ne remplace pas les trois étapes.

Commande locale depuis la racine : python verification.py. Adapte python en python3 si nécessaire. Une assertion échouée doit rester visible et rendre le processus non nul. Ne lance pas Python en mode optimisé. Les huit tests couvrent validation valide, liste vide, trop d’éléments, six cas invalides testés séparément dans des listes à un élément, doublons, connexion ouverte, scan de deux ports dans l’ordre et bilan mixte/vide.

## Livrables et limites

Le dépôt final contient portpilot.py, verification.py, README.md, .gitignore et .gitlab-ci.yml, trois MR fusionnées au dernier pipeline vert, le lien du pipeline rouge de MR1 avec son motif, et l’artefact portpilot.zip du pipeline vert de MR3. Le ZIP contient uniquement les trois fichiers annoncés.

L’outil tente seulement une connexion TCP sur 127.0.0.1, de façon séquentielle, avec une tentative et un délai de 0,5 seconde par port. Il ne prouve ni vulnérabilité, ni disponibilité générale, ni identité d’un service. Le projet ne couvre pas toutes les branches d’erreur réseau par tests automatisés. L’exercice concerne exclusivement un laboratoire local autorisé.
