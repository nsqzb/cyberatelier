# HeaderScope — vérifier trois en-têtes HTTP

**Durée : 5 heures · Niveau débutant · 3 merge requests**

Tu vas écrire un petit client qui demande une ressource au laboratoire local et évalue trois en-têtes de réponse. Le travail porte sur la lecture et la normalisation des en-têtes, les réponses HTTP et les erreurs de connexion. Aucun exploit, parcours de liens ou hôte distant n’est utilisé.

## Contrat du programme

Écris ton programme dans headerscope.py et tes tests dans verification.py. Tu peux choisir les noms de fonctions, mais garde séparées les règles pures, le classement des réponses HTTP, le client et l’orchestration. La bibliothèque standard urllib.request suffit. N’utilise pas de classes ou de fixtures avancées. Une fonction pure classer_reponse(statut, entetes) reçoit un code de statut entier et un mapping d’en-têtes : pour 200 elle retourne le statut, l’état HTTP_OK et les alertes calculées par les règles ; pour 404 ou 500 elle retourne le statut, l’état HTTP_ERREUR et une liste d’alertes vide. Le client appelle cette fonction après avoir obtenu une réponse. Une panne de transport ou un timeout n’a pas de code HTTP et reste un résultat distinct, hors de classer_reponse.

Les contrôles attendus sont :

- Content-Security-Policy existe et sa valeur, après retrait des espaces au début et à la fin, n’est pas vide ;
- X-Content-Type-Options, après retrait des espaces et comparaison sans tenir compte de la casse, vaut nosniff ;
- X-Frame-Options, après retrait des espaces et comparaison sans tenir compte de la casse, vaut DENY ou SAMEORIGIN.

Les noms d’en-tête sont insensibles à la casse. La valeur CSP est seulement vérifiée comme non vide ; les deux autres valeurs sont normalisées avec espaces retirés et casse ignorée. Retourne une alerte lisible par contrôle en échec ; une réponse conforme produit zéro alerte. Garde le nombre et le contenu des alertes prévisibles afin que les tests puissent les vérifier.

La fonction pure classer_reponse(statut, entetes) retourne un triplet (statut, resultat, alertes). Pour 200, resultat vaut HTTP_OK et alertes contient les résultats des trois règles. Pour 404 et 500, resultat vaut HTTP_ERREUR et alertes est vide ; le statut reste dans le triplet. La fonction ne fait aucun accès réseau. Une panne de connexion ou un timeout survient avant le classement et doit être rendu comme un résultat distinct sans code HTTP.

Le laboratoire local répond aux chemins /fragile, /durci, /absent et /erreur sur 127.0.0.1:8000. /fragile renvoie les trois en-têtes volontairement non conformes et doit produire trois alertes. /durci renvoie les trois en-têtes conformes et doit produire zéro alerte. /absent produit une erreur HTTP 404 et /erreur une erreur HTTP 500.

## Les trois MR

Les minutes des missions sont incluses dans les 300 minutes du parcours.

### MR1 — feat/regles-entetes (85 min)

Écris une fonction pure qui reçoit un mapping d’en-têtes et retourne les alertes. Aucun accès réseau n’est nécessaire. Crée des tests utiles dans verification.py et conserve-les dans les MR suivantes. La configuration CI lance ces tests locaux dans chaque MR : elle ne suppose pas que le laboratoire de Cyber Atelier existe sur le runner de l’école.

Écris au moins ces six cas :

1. Trois en-têtes conformes donnent zéro alerte.
2. Dictionnaire vide donne une alerte pour chacun des trois contrôles.
3. Les noms en minuscules sont reconnus.
4. CSP présente avec une valeur vide ou composée d’espaces est signalée.
5. X-Content-Type-Options nosniff avec casse différente et espaces externes est accepté ; une autre valeur est signalée.
6. X-Frame-Options DENY ou SAMEORIGIN est accepté avec casse différente et espaces externes ; une autre valeur est signalée.

Ajoute un cas où une seule règle échoue, pour prouver que les autres règles restent indépendantes. Utilise des assertions réellement exécutées. Le script doit sortir avec un code non nul si une assertion échoue, et afficher un total cohérent.

Ajoute une CI de merge request qui exécute python verification.py (ou python3). Utilise un runner configuré par l’école. Cette MR porte sur la logique pure : aucun accès réseau en CI n’est requis.

### MR2 — feat/client-http (85 min)

Après fusion de MR1, repars de la branche principale à jour. Écris le client HTTP pour demander un chemin fixe du laboratoire sur http://127.0.0.1:8000 avec un timeout de 2 secondes. Il récupère les en-têtes et le statut, puis appelle classer_reponse(statut, entetes). Une réponse 404 ou 500 garde son code, retourne HTTP_ERREUR et une liste d’alertes vide ; elle reste distincte d’une panne de connexion ou d’un timeout.

Teste classer_reponse sans réseau réel et sans mock : injecte directement statut et dictionnaire dans la fonction pure. H8 vérifie le cas 200 avec des en-têtes conformes ; H9 vérifie 404 et 500. Ces tests vérifient le classement et les règles, pas l’entrée/sortie réseau réelle. La démonstration manuelle du client est distincte. Ne présente jamais le service du portail comme un service préinstallé sur le runner d’école.

Tu peux démontrer manuellement le client depuis Cyber Atelier : démarre le laboratoire intégré avec son bouton dans l’interface, essaie /fragile, /durci, /absent et /erreur, puis arrête le laboratoire. N’envoie pas de requête à une cible externe. Ne démarre pas un second service sur le port 8000.

### MR3 — feat/bilan (80 min)

Après fusion de MR2, actualise la branche principale. Écris l’orchestration : configure un des quatre chemins du laboratoire, affiche le statut HTTP, les alertes et un résumé lisible. N’ajoute aucun crawl, URL arbitraire ou scan de cibles. Garde /fragile à trois alertes et /durci à zéro, et affiche séparément les résultats 404, 500, panne et timeout.

Améliore le README pour expliquer le périmètre local, les règles des trois en-têtes, le délai, la commande des tests et le fait que la CI vérifie les règles sans dépendre du laboratoire. La dernière MR garde un pipeline basé sur des tests locaux reproductibles. Une démonstration avec le laboratoire intégré est distincte de cette CI.

## Méthode GitLab

Crée ou utilise un dépôt autorisé par ton école. Vérifie que le runner est actif pour les branches non protégées de MR et que tu as les droits d’ouverture et de fusion. Dans la configuration de la branche principale, applique les règles de l’école et exige les pipelines réussis. Pour chaque étape, branche-toi depuis la principale actualisée, exécute les tests, lis le diff, pousse une MR et fusionne le dernier commit vert. Après chaque fusion, mets à jour la base avant la branche suivante.

La CI doit réellement exécuter les tests. Ne masque pas les erreurs, ne rends pas le job facultatif et ne prends pas un lint valide pour preuve qu’un runner fonctionne. Si l’école n’offre pas de runner ou de règle de fusion, note cette limite au lieu de déclarer le gate validé.

## Repères de temps

Préparation GitLab et lecture : 30 min. MR1 règles et tests : 85 min. MR2 client et erreurs : 85 min. MR3 orchestration, bilan et README : 80 min. Démonstration, relecture et marge : 20 min. Total : 300 min.

## Livrables et limites

Le dossier HeaderScope est vide au départ. Depuis son terminal, clone le dépôt directement dans le dossier courant avec git clone <URL_DU_DEPOT> . avant de créer les fichiers. Le point signifie « ici ». Les commandes du terminal web repartent chacune du dossier courant explicite ; un cd seul ne persiste pas. Pour Git interactif, utilise docker compose exec atelier bash depuis le dossier Cyber Atelier.

Livre un programme, une suite de tests locale utile, une configuration CI, un README clair, trois MR successives et un bilan honnête de ce que la CI et la démonstration valident. Les tests de règles sont autonomes et réalisables sur un runner ordinaire. La démonstration des quatre chemins utilise le laboratoire local de Cyber Atelier quand il est démarré explicitement.

Les en-têtes constituent des signaux de configuration, pas une preuve complète de sécurité. Le client ne visite que les chemins de laboratoire nommés et ne se connecte qu’à 127.0.0.1:8000. La CI de base ne vérifie pas la disponibilité du laboratoire. Une alerte ne prouve pas qu’un site est exploitable ou sûr.
