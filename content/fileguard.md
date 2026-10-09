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

Écris une fonction qui calcule l’empreinte SHA-256 d’un fichier en lisant ses octets. Dans des fichiers temporaires, vérifie ces deux oracles fixes indépendamment de ta fonction :

- Fichier vide, zéro octet : e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.
- Exactement trois octets ASCII abc, sans saut de ligne final : ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad.

Écris les trois octets comme bytes afin d’éviter toute conversion ou fin de ligne implicite. Les valeurs attendues sont des constantes d’oracle, pas le résultat de la fonction testée.

Ajoute un test que deux fichiers identiques ont la même empreinte. Les tests doivent fonctionner dans un répertoire temporaire créé par le test et ne dépendre ni du dossier utilisateur ni de journaux. La CI exécute uniquement cette suite locale, sans service distant.

### MR2 — feat/manifest (85 min)

Après fusion de MR1, repars de la branche principale à jour. Construis l’inventaire des fichiers réguliers au premier niveau, trie les noms et écris manifest.json avec le format contractuel. Exclue le manifeste. Refuse les liens symboliques et n’entre pas dans les sous-dossiers.

Écris des tests avec répertoires temporaires : manifeste vide pour un dossier vide, noms triés de manière déterministe, contenu attendu, manifeste lui-même exclu, lien symbolique refusé si le système sait en créer. Copie également les fixtures fournies dans le dépôt de l’exercice pour disposer d’un petit exemple relisible : README.txt, settings.ini et message.txt contiennent uniquement des données fictives, sans secrets.

Le manifeste peut être régénéré ; indique dans le programme et le README si la commande crée ou remplace le fichier. Ne promets pas de détecter un changement survenu puis restauré avant la vérification.

### MR3 — feat/comparaison (80 min)

Après fusion de MR2, actualise la principale. Implémente la comparaison avec les quatre catégories. Ajoute des tests isolés qui couvrent : tout inchangé, un fichier modifié, un fichier supprimé, un fichier ajouté, plusieurs catégories dans le même résultat, manifeste vide et manifeste exclu du scan. Utilise des fichiers temporaires et des empreintes connues ou produites par ta fonction ; aucun journal préexistant ne doit être nécessaire.

Orchestre la création puis la vérification depuis des commandes simples et affiche les noms des fichiers par catégorie. Termine le README : structure du dossier, format du manifeste, commandes, comportement des liens et sous-dossiers, sens du résultat et limites. Les opérations restent dans le dossier de données explicitement choisi ; n’analyse pas automatiquement tout le disque.

## Méthode GitLab

Le dossier FileGuard est vide au départ. Clone le dépôt de l’école directement dans le dossier courant avec git clone <URL_DU_DEPOT> . avant de créer les fichiers. Le point signifie « ici ». Le terminal web repart du dossier courant explicite pour chaque commande ; un cd seul ne persiste pas. Pour Git interactif, utilise docker compose exec atelier bash depuis le dossier Cyber Atelier.

Utilise un dépôt autorisé par l’école, un runner actif sur les MR des branches non protégées et les droits convenus pour les règles de fusion. Pour chaque MR, crée la branche depuis la principale actualisée, exécute la même commande de tests localement et en CI, lis le diff, puis ouvre la MR. Fusionne uniquement le dernier commit vert. Après chaque fusion, actualise la principale avant l’étape suivante.

La CI ne dépend pas d’un dossier de données du portail. Les tests créent leurs propres fichiers temporaires. Les fixtures d’exemple peuvent être copiées par l’apprenant dans son dépôt, mais elles ne remplacent pas les tests temporaires et ne sont pas supposées présentes sur le runner d’école.

## Repères de temps

Préparation GitLab et lecture : 30 min. MR1 empreintes et tests : 85 min. MR2 manifeste et tests : 85 min. MR3 comparaison, affichage et README : 80 min. Relecture et marge : 20 min. Total : 300 min.

## Livrables et limites

Livre fileguard.py, verification.py, un README, les fixtures fictives copiées dans le dépôt, une CI qui exécute les tests temporaires et trois MR successives. Montre un scénario où les quatre catégories sont distinguées, et explique clairement que le manifeste de référence doit lui-même être digne de confiance.

FileGuard est un outil pédagogique d’intégrité, pas un antivirus ni une garantie d’authenticité. SHA-256 permet de constater une différence avec un manifeste de confiance ; une personne capable de modifier les fichiers peut aussi modifier un manifeste conservé à côté. Il ne parcourt pas récursivement, ne suit pas les liens et ne cherche pas de secrets.
