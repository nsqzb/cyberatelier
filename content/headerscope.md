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

Le laboratoire local répond aux chemins /fragile, /durci, /absent et /erreur sur 127.0.0.1:8000. /fragile répond 200 sans aucun des trois en-têtes contrôlés et doit produire trois alertes. /durci renvoie les trois en-têtes conformes et doit produire zéro alerte. /absent produit une erreur HTTP 404 et /erreur une erreur HTTP 500.

## Les trois MR

Les minutes des missions sont incluses dans les 300 minutes du parcours.

### MR1 — feat/regles-entetes (85 min)

Écris les règles de contrôle des trois en-têtes par paliers courts : à chaque palier, tu écris un test, tu le vois échouer, tu écris le minimum de code pour le faire passer, puis tu fais un commit. Cette MR ne touche pas au réseau : les tests H1 à H7 appellent directement tes fonctions avec des dictionnaires.

#### Palier 1 — Prépare ton dépôt et ta branche (10 min)

Partir d’une branche de travail propre, dédiée à cette MR.

- Ouvre le dossier workspaces/headerscope dans VS Code, puis un terminal (Terminal > New Terminal).
- Le clone du dépôt et la branche feat/regles-entetes ont été préparés pendant le parcours. Tu vérifies seulement où tu es, sans rien écraser.
- Une branche est une ligne de travail séparée de main : main ne bouge pas tant que tu n’as pas fusionné.

```
git status
```

```
git switch feat/regles-entetes
```

```
git status
```

**Tu sais que c’est bon quand :** git status affiche « On branch feat/regles-entetes » et « nothing to commit, working tree clean ».

*Indice :* Si Git répond « not a git repository », tu n’es pas dans workspaces/headerscope. Si la branche n’existe pas, reviens sur main à jour (git switch main puis git pull --ff-only) puis crée-la avec git switch -c feat/regles-entetes.

#### Palier 2 — Un premier unittest et le code de sortie (10 min)

Savoir lire un test qui passe ou échoue, et comprendre pourquoi la CI se fie au code de sortie.

- Pourquoi : la CI décide si la merge request passe d’après le code de sortie de python3 verification.py. Un test qui échoue doit donc faire sortir le programme avec un code non nul.
- Crée un fichier exemple.py jetable (il ne sera pas livré) avec le code ci-dessous. saluer est un exemple sans rapport avec HeaderScope.
- Lance-le avec la bonne valeur, puis change la valeur attendue en « Bonjour Ada !! » pour voir un échec. Remets la bonne valeur, puis supprime le fichier : rm exemple.py.

```
import unittest

def saluer(prenom):
    return 'Bonjour ' + prenom + ' !'

class TestSaluer(unittest.TestCase):
    def test_saluer_une_personne(self):
        self.assertEqual(saluer('Ada'), 'Bonjour Ada !')

if __name__ == '__main__':
    unittest.main()
```

```
python3 exemple.py
```

```
python3 exemple.py; echo $?
```

**Tu sais que c’est bon quand :** Avec la bonne valeur, tu vois « OK » et echo affiche 0. Avec la mauvaise, tu vois « FAILED » et echo affiche 1.

*Indice :* unittest.main() lance les tests du fichier. Le code de sortie 0 signifie succès ; toute autre valeur signifie qu’un test a échoué. Lis les messages d’échec de bas en haut : la dernière ligne dit ce qui ne va pas.

#### Palier 3 — Dictionnaires et noms normalisés (10 min)

Chercher une valeur par clé, après avoir normalisé le texte saisi.

- Pourquoi : les noms d’en-têtes HTTP ne dépendent pas de la casse. Il faut donc comparer des textes normalisés, pas les textes bruts.
- Crée un fichier exemple2.py jetable avec le code ci-dessous. Les fruits sont un exemple sans rapport avec HeaderScope.
- Lance-le, puis ajoute une saisie avec d’autres espaces et une autre casse. Supprime exemple2.py ensuite.

```
prix = {'pomme': 1.2, 'poire': 1.5}
saisie = '   POMME  '
cle = saisie.strip().lower()
print(cle)
print(prix.get(cle, 0))
print(prix.get('banane', 0))
for nom, valeur in prix.items():
    print(nom, valeur)
```

```
python3 exemple2.py
```

**Tu sais que c’est bon quand :** Tu obtiens « pomme », puis 1.2, puis 0 (clé absente, sans erreur), puis les deux lignes de la boucle.

*Indice :* strip() retire les espaces au début et à la fin ; lower() passe en minuscules. Les deux renvoient une nouvelle chaîne : le texte d’origine ne change pas. dict.get(clé, valeur_par_défaut) évite l’erreur quand la clé manque.

#### Palier 4 — H2 : aucun en-tête donne trois alertes (10 min)

Écrire le premier test de règles, puis la première version de la fonction qui retourne les alertes.

- Crée headerscope.py (vide au départ) et verification.py avec une classe TestRegles, sur le modèle de l’exemple du palier 2.
- Écris H2 : un dictionnaire d’en-têtes vide donne trois alertes, une par règle. Le test ne vérifie que le nombre d’alertes.
- Lance les tests : ils échouent parce que la fonction n’existe pas encore (phase rouge, c’est normal).
- Écris dans headerscope.py la fonction evaluer_entetes(entetes), qui retourne une liste d’alertes. Ce palier ne traite que les absences : une règle absente ajoute une alerte lisible. Lance : H2 passe (phase verte).
- Commit.

```
from headerscope import evaluer_entetes

class TestRegles(unittest.TestCase):
    def test_h2_aucun_entete(self):
        alertes = evaluer_entetes({})
        self.assertEqual(len(alertes), 3)
```

```
python3 verification.py
```

```
git add headerscope.py verification.py
```

```
git commit -m "Ajoute les alertes d’absence des trois en-têtes"
```

- **H2** — Aucun en-tête. Entrée : Dictionnaire vide Attendu : Trois alertes, une par règle.

**Tu sais que c’est bon quand :** python3 verification.py affiche OK pour H2 et git log --oneline montre ton commit.

*Indice :* Une alerte est une chaîne lisible, par exemple « CSP absente ». Crée une liste vide, puis ajoute une alerte pour chaque règle en échec. Commence par une seule règle si tu bloques, puis ajoute les deux autres.

#### Palier 5 — H3 et H4 : noms sans casse, CSP vide (11 min)

Reconnaître les noms d’en-têtes quelle que soit la casse, et refuser une CSP vide.

- Pourquoi : un serveur peut envoyer content-security-policy ou Content-Security-Policy. La règle doit trouver l’en-tête dans les deux cas.
- Écris H3 : des noms en minuscules avec des valeurs valides donnent zéro alerte. Lance : rouge si la recherche est sensible à la casse.
- Écris H4 : clé absente, valeur vide ou valeur faite seulement d’espaces donnent une alerte CSP. Lance : rouge.
- Corrige evaluer_entetes : normalise les noms une seule fois, puis, pour la CSP, retire les espaces au début et à la fin de la valeur avant de vérifier qu’elle n’est pas vide. Lance : H2, H3 et H4 passent.
- Commit.

```
python3 verification.py
```

```
git add headerscope.py verification.py
```

```
git commit -m "Reconnais les noms sans casse et refuse une CSP vide"
```

- **H3** — Noms minuscules. Entrée : Noms en minuscules et valeurs valides Attendu : Zéro alerte.
- **H4** — CSP absente ou vide. Entrée : Clé manquante, valeur vide ou espaces seulement Attendu : Alerte CSP.

**Tu sais que c’est bon quand :** H2, H3 et H4 passent, et le commit apparaît dans git log --oneline.

*Indice :* Piège : une clé en minuscules ne se retrouve pas avec la casse d’origine. Compare des noms normalisés des deux côtés. La règle « après retrait des espaces » s’applique à la valeur de la CSP, pas à son nom.

#### Palier 6 — H5 et H6 : valeurs sans casse ni espaces (11 min)

Comparer les valeurs nosniff, DENY et SAMEORIGIN après normalisation.

- Écris H5 : nosniff avec espaces et casse variables est accepté ; une autre valeur est signalée. Lance : rouge.
- Écris H6 : DENY et SAMEORIGIN avec espaces et casse variables sont admis ; une valeur non admise est signalée. Lance : rouge.
- Corrige les deux règles : normalise la valeur (retrait des espaces puis passage en minuscules) avant la comparaison. Pour les valeurs admises, une liste de textes en minuscules suffit.
- Pourquoi : la liste des valeurs admises se lit mieux qu’une suite de conditions quand il y en a plusieurs.
- Commit.

```
fruits_admis = ['pomme', 'poire']
print('poire' in fruits_admis)
print('kiwi' in fruits_admis)
```

```
python3 verification.py
```

```
git add headerscope.py verification.py
```

```
git commit -m "Accepte nosniff, DENY et SAMEORIGIN sans tenir compte de la casse"
```

- **H5** — Options MIME. Entrée : nosniff avec espaces et casse variables, puis valeur incorrecte Attendu : Première entrée acceptée ; seconde signalée.
- **H6** — Options de frame. Entrée : DENY, SAMEORIGIN et valeur non admise avec espaces/casse variables Attendu : Deux admises ; valeur non admise signalée.

**Tu sais que c’est bon quand :** H2 à H6 passent. L’exemple des fruits affiche True puis False.

*Indice :* Normalise la valeur avant de la comparer, comme pour la saisie de l’exemple du palier 3. Pour les deux règles, teste une valeur admise avec espaces et majuscules, puis une valeur refusée.

#### Palier 7 — H1 et H7 : profil conforme et règles indépendantes (11 min)

Vérifier qu’un profil complet ne donne aucune alerte, et qu’une seule règle en échec ne fait ressortir qu’une seule alerte.

- Écris H1 : les trois en-têtes requis avec des valeurs admises donnent zéro alerte.
- Écris H7 : deux valeurs conformes et une incorrecte donnent exactement une alerte. Ce test prouve qu’une règle n’en annule pas une autre.
- Lance les tests. Si H1 ou H7 échoue, relis chaque règle séparément : une règle ne doit regarder que son propre en-tête.
- Corrige le minimum, puis lance tous les tests : H1 à H7 doivent passer sans que tu modifies les tests déjà verts.
- Commit.

```
python3 verification.py
```

```
git add headerscope.py verification.py
```

```
git commit -m "Vérifie le profil conforme et l’indépendance des règles"
```

- **H1** — Profil conforme. Entrée : Les trois en-têtes requis avec valeurs admises Attendu : Zéro alerte.
- **H7** — Règles indépendantes. Entrée : Deux valeurs conformes et une incorrecte Attendu : Une alerte exactement.

**Tu sais que c’est bon quand :** python3 verification.py affiche OK pour H1 à H7 et se termine avec 0 ; git log --oneline montre le commit.

*Indice :* Si H7 donne deux alertes au lieu d’une, une règle regarde probablement un autre en-tête que le sien ou compare mal une valeur. Vérifie-les une par une avec un seul en-tête à la fois.

#### Palier 8 — Test en CI puis merge request (12 min)

Faire exécuter les tests par la CI de la merge request, puis fusionner seulement quand le pipeline du dernier commit est vert.

- Pourquoi : quatre choses ne se confondent pas. Ton test local réussi n’est pas un pipeline GitLab exécuté ; un pipeline vert n’est pas encore une fusion autorisée ; et une case cochée dans Cyber Atelier ne prouve rien.
- Crée .gitlab-ci.yml à la racine : un job qui lance python3 verification.py et qui tourne sur les merge requests. Ne rends pas le job facultatif et ne masque pas ses erreurs.
- Le job n’a pas besoin du laboratoire : le runner de l’école n’en a pas. Si le job échoue, lis la dernière ligne du journal : elle dit quelle commande a échoué.
- Relis le diff, pousse la branche, ouvre la merge request dans GitLab de l’école (branche feat/regles-entetes vers main), puis attends le pipeline du dernier commit.
- Fusionne seulement si le pipeline est vert. Après fusion, reviens sur main à jour.

```
# Exemple sans rapport avec HeaderScope : la forme d’un job de CI
saluer:
  script:
    - echo bonjour
```

```
git status
```

```
git diff main --stat
```

```
git add .gitlab-ci.yml headerscope.py verification.py
```

```
git commit -m "Lance les tests de règles dans la CI de merge request"
```

```
git push -u origin feat/regles-entetes
```

```
git switch main
```

```
git pull --ff-only
```

**Tu sais que c’est bon quand :** Le pipeline du dernier commit est vert dans GitLab, la merge request ne contient que les fichiers attendus, et main local contient la fusion (git log --oneline).

*Indice :* Si le pipeline ne démarre pas, vérifie dans la documentation GitLab de l’école que le job se déclenche sur les merge requests (mot-clé rules). Ne fusionne jamais sur un pipeline rouge ou absent.

**Avant de livrer :**
- Les tests s’exécutent localement et sur un runner sans service de laboratoire.
- Les noms sont comparés sans casse ; les valeurs appliquent exactement les normalisations du contrat.
- Les trois alertes de /fragile et zéro alerte de /durci sont les résultats de référence pour la démonstration.
- python3 verification.py affiche OK pour H1 à H7 et se termine avec un code de sortie 0.
- python3 verification.py se termine avec un code de sortie non nul dès qu’une assertion échoue.
- La merge request contient le fichier de CI (.gitlab-ci.yml), headerscope.py et verification.py, sans __pycache__.

### MR2 — feat/client-http (85 min)

Ajoute le client HTTP limité aux chemins du laboratoire, avec un timeout de 2 secondes, puis classe les réponses avec une fonction pure. Tu testes le classement en lui passant directement le statut et les en-têtes, sans réseau et sans mock. La démonstration du client est une étape à part, avec le laboratoire démarré.

#### Palier 1 — Repartir de main à jour après MR1 (10 min)

Partir de la version fusionnée de la MR1, sans mélanger deux merge requests.

- Pourquoi : chaque merge request part de la base à jour. Sinon tu relis du code qui n’est pas encore dans main.
- Vérifie que ton dépôt est propre, reviens sur main et récupère la fusion de la MR1.
- Crée la branche de la MR2 à partir de ce main à jour.

```
git status
```

```
git switch main
```

```
git pull --ff-only
```

```
git log --oneline -5
```

```
git switch -c feat/client-http
```

```
git status
```

**Tu sais que c’est bon quand :** git log --oneline -5 montre le commit de fusion de la MR1, et git status affiche « On branch feat/client-http ».

*Indice :* Si git status n’est pas propre, ne force rien : demande-toi quels fichiers tu as modifiés et range-les dans un commit ou mets-les de côté. Si git pull --ff-only refuse, ton main local a divergé : relis git log avant d’aller plus loin.

#### Palier 2 — urllib et les deux sortes d’erreurs (10 min)

Comprendre qu’une réponse HTTP d’erreur et une panne de connexion ne sont pas la même chose.

- Pourquoi : un 404 a un code et des en-têtes ; une connexion refusée n’a ni l’un ni l’autre. Ton client doit traiter les deux cas séparément.
- Crée un fichier exemple_reseau.py jetable avec le code ci-dessous. L’exemple vise le port 9 de ton Mac, où rien n’écoute : c’est une panne de connexion, pas une réponse. Ce n’est pas le laboratoire.
- Lance-le. Puis supprime le fichier : rm exemple_reseau.py.

```
import urllib.request
import urllib.error

try:
    urllib.request.urlopen('http://127.0.0.1:9/', timeout=2)
except urllib.error.URLError as erreur:
    print('panne :', erreur.reason)

erreur_http = urllib.error.HTTPError('http://127.0.0.1/exemple', 404, 'Introuvable', {}, None)
print(erreur_http.code, erreur_http.reason)
```

```
python3 exemple_reseau.py
```

**Tu sais que c’est bon quand :** Tu vois « panne : » suivi d’un message de connexion, puis « 404 Introuvable ». Le second résultat ne demande aucun réseau.

*Indice :* HTTPError est une sous-classe de URLError : si tu veux traiter les réponses d’erreur à part, place le except HTTPError avant le except URLError. Une connexion refusée donne une panne, jamais un code HTTP.

#### Palier 3 — H8 : une réponse 200 se classe sans réseau (12 min)

Écrire une fonction pure qui reçoit un statut et des en-têtes, et retourne un triplet.

- Pourquoi : classer une réponse n’a pas besoin de réseau. Tu passes directement les valeurs : pas de mock, pas de serveur.
- Écris H8 : classer_reponse(200, trois en-têtes conformes) doit retourner le statut 200, l’état HTTP_OK et zéro alerte. Lance : rouge, la fonction n’existe pas encore.
- Écris classer_reponse dans headerscope.py en réutilisant evaluer_entetes de la MR1. Pour un statut 200, retourne le statut, HTTP_OK et les alertes. Lance : H8 passe, H1 à H7 restent verts.
- Commit.

```
def bornes(liste):
    return min(liste), max(liste)

petit, grand = bornes([4, 9, 2])
print(petit, grand)
```

```
python3 verification.py
```

```
git add headerscope.py verification.py
```

```
git commit -m "Ajoute classer_reponse pour les réponses 200"
```

- **H8** — Classement d’une réponse 200. Entrée : Appel pur à classer_reponse(200, dictionnaire des trois en-têtes conformes) Attendu : Retourne le statut 200, HTTP_OK et zéro alerte.

**Tu sais que c’est bon quand :** H1 à H8 passent, et git log --oneline montre le commit.

*Indice :* Une fonction peut retourner plusieurs valeurs séparées par des virgules : c’est un triplet, comme l’exemple des bornes le montre. Ne refais pas les règles : appelle evaluer_entetes(entetes).

#### Palier 4 — H9 : les erreurs 404 et 500 gardent leur code (10 min)

Classer les erreurs HTTP sans leur donner d’alertes de politique.

- Écris H9 : des appels purs avec 404, puis 500, et un dictionnaire d’en-têtes quelconque. Chaque code doit ressortir avec HTTP_ERREUR et une liste d’alertes vide.
- Lance : rouge, les codes 404 et 500 ne sont pas encore traités.
- Ajoute dans classer_reponse le cas des autres codes : statut conservé, HTTP_ERREUR, alertes vides. Lance : tous les tests passent.
- Commit.

```
python3 verification.py
```

```
git add headerscope.py verification.py
```

```
git commit -m "Classe les erreurs 404 et 500 sans alertes"
```

- **H9** — Classement d’erreurs HTTP. Entrée : Appels purs avec statut 404 puis 500 et un dictionnaire d’en-têtes quelconque Attendu : Chaque code est conservé avec HTTP_ERREUR et une liste d’alertes vide.

**Tu sais que c’est bon quand :** python3 verification.py affiche OK pour H1 à H9 et se termine avec 0.

*Indice :* Le contrat dit que les alertes restent vides pour une erreur HTTP : ne calcule rien dans ce cas. Vérifie que le code renvoyé est bien celui que tu as reçu en argument.

#### Palier 5 — Le client : URL limitée et timeout de 2 secondes (10 min)

Demander un chemin fixe du laboratoire avec un délai maximal de 2 secondes.

- Pourquoi : le client est la seule partie qui parle au réseau. Tout le reste reste pur et testable sans réseau.
- Écris une fonction demander(chemin) qui construit l’URL à partir de http://127.0.0.1:8000 et du chemin. Elle n’accepte que /fragile, /durci, /absent et /erreur ; un autre chemin lève ValueError avant tout appel réseau.
- Appelle urlopen avec timeout=2 pour le cas d’une réponse réussie, puis retourne le statut et les en-têtes reçus.
- Ce palier n’a pas de test automatique : H8 et H9 ne touchent pas le réseau. La vérification réelle est la démonstration du palier 7.

```
python3 -c "from headerscope import demander; demander('/autre')"
```

```
git add headerscope.py
```

```
git commit -m "Ajoute le client HTTP local avec timeout de 2 secondes"
```

**Tu sais que c’est bon quand :** demander('/autre') lève ValueError avant de contacter quoi que ce soit, et git log --oneline montre le commit.

*Indice :* Le délai se donne avec l’argument nommé timeout de urlopen. Une liste fixe de chemins autorisés se teste avec in avant de construire l’URL. Un délai dépassé peut sortir sous forme de TimeoutError au lieu de URLError : le palier suivant prévoit les deux.

#### Palier 6 — Séparer réponse HTTP d’erreur et panne (10 min)

Rendre une panne de connexion ou un délai dépassé comme un résultat distinct, sans code HTTP.

- Pourquoi : l’utilisateur doit voir la différence entre « le serveur a répondu 404 » et « le serveur n’a pas répondu ».
- Dans demander, attrape HTTPError : il porte le code et les en-têtes. Transmets-les à classer_reponse.
- Attrape ensuite URLError et TimeoutError : retourne un résultat de panne distinct, sans code HTTP, et sans appeler classer_reponse.
- Vérifie que le fichier compile et que les tests restent verts.

```
python3 -m py_compile headerscope.py
```

```
python3 verification.py
```

```
git add headerscope.py
```

```
git commit -m "Distingue les réponses HTTP d’erreur des pannes de connexion"
```

**Tu sais que c’est bon quand :** py_compile ne signale aucune erreur, H1 à H9 passent, et le commit apparaît dans git log --oneline.

*Indice :* Dans une suite de except, HTTPError doit venir avant URLError, sinon la première clause attrape tout. Un délai et une connexion refusée ne lèvent pas toujours la même exception : vérifie ce que ton code reçoit, sans le deviner.

#### Palier 7 — Démonstration du client (hors tests) (11 min)

Voir le client contre le vrai laboratoire, séparément des tests automatiques.

- Pourquoi : cette démonstration exige le laboratoire. Elle n’entre ni dans verification.py ni dans la CI : le runner de l’école n’a pas le laboratoire.
- Option A, dans Cyber Atelier (Docker) : vérifie que le laboratoire intégré est actif. Il démarre avec l’application ; son bouton permet de le relancer.
- Option B, sur ton Mac : depuis le dossier cyberatelier, lance python3 labs.py dans un terminal. Il répond sur 127.0.0.1:8000. Arrête-le avec Ctrl+C.
- Choisis une seule source à la fois. Le client du Mac interroge le laboratoire du Mac ; la console Docker interroge celui du conteneur.
- Demande /fragile, /durci, /absent et /erreur, un par un. Arrête ensuite le laboratoire et relance le client : tu dois voir une panne, distincte d’un code HTTP.
- N’envoie aucune requête vers une autre cible.

```
python3 labs.py
```

```
python3 -c "from headerscope import demander; print(demander('/fragile'))"
```

```
python3 -c "from headerscope import demander; print(demander('/absent'))"
```

**Tu sais que c’est bon quand :** /fragile répond avec un statut 200, /absent avec 404 et /erreur avec 500. Labo arrêté : tu obtiens une panne, pas un code HTTP.

*Indice :* Si la connexion est refusée alors que le laboratoire tourne, vérifie que tu es dans le dossier cyberatelier et que labs.py affiche bien son écoute. Ne change pas le port : les chemins et le client attendent 127.0.0.1:8000.

#### Palier 8 — Livrer la MR2 après un pipeline vert (12 min)

Relire ce que tu livres, pousser la branche, et fusionner seulement après un pipeline vert sur le dernier commit.

- Relis le diff comme si c’était le code de quelqu’un d’autre : ce qui est ajouté, ce qui est retiré, et l’absence de fichiers parasites.
- Pousse la branche, puis ouvre la merge request dans GitLab de l’école (feat/client-http vers main).
- Attends le pipeline du dernier commit. Un test local vert ne remplace pas ce pipeline, et ce pipeline ne prouve pas que le laboratoire fonctionne.
- Fusionne seulement si le pipeline est vert.

```
git status
```

```
git diff main --stat
```

```
git push -u origin feat/client-http
```

**Tu sais que c’est bon quand :** La merge request ne contient que headerscope.py et verification.py (sans __pycache__), et le pipeline du dernier commit est vert dans GitLab.

*Indice :* Un pipeline rouge se lit comme un test : la dernière ligne du journal dit quelle commande a échoué. Si __pycache__ apparaît dans git status, ne l’ajoute pas à la merge request.

**Avant de livrer :**
- Le timeout du client vaut 2 secondes et l’URL reste limitée au laboratoire local.
- La fonction pure classe 200, 404 et 500 selon le contrat et H8/H9 couvrent ces retours sans mock avancé.
- Les tests injectés ne sont pas présentés comme preuve de l’I/O réseau ; la CI reste exécutable sans serveur web.
- python3 verification.py affiche OK pour H1 à H9 et se termine avec un code de sortie 0, sans que le laboratoire soit démarré.
- La démonstration du client est documentée à part des tests, et son résultat ne figure pas dans verification.py.

### MR3 — feat/bilan (80 min)

Relie le client et les règles dans un petit programme qui affiche un bilan lisible, puis documente le périmètre et les limites. Tu valides les règles par les tests locaux, qui n’ont pas besoin du laboratoire. La démonstration avec le laboratoire vient à part, à la fin.

#### Palier 1 — Repartir de main après MR2 (10 min)

Partir de la version fusionnée des MR1 et MR2, dans une branche dédiée au bilan.

- Pourquoi : le bilan s’appuie sur le client et sur les règles fusionnés. Repars donc de main à jour, pas d’une ancienne branche.
- Vérifie que ton dépôt est propre, reviens sur main, récupère les fusions, puis crée la branche feat/bilan.

```
git status
```

```
git switch main
```

```
git pull --ff-only
```

```
git log --oneline -6
```

```
git switch -c feat/bilan
```

```
git status
```

**Tu sais que c’est bon quand :** git log --oneline -6 montre les fusions des MR1 et MR2, et git status affiche « On branch feat/bilan ».

*Indice :* Si la branche feat/bilan existe déjà, utilise git switch feat/bilan sans -c, après avoir vérifié avec git log qu’elle contient bien les fusions. Si git pull --ff-only refuse, relis git log avant de continuer.

#### Palier 2 — Choisir un chemin depuis la ligne de commande (10 min)

Lire un argument passé au programme et le refuser s’il n’est pas dans la liste autorisée.

- Pourquoi : le programme ne traite qu’un seul chemin, choisi parmi les quatre chemins du laboratoire. Un argument hors liste doit être refusé avant tout appel réseau.
- Crée un fichier exemple_choix.py jetable avec le code ci-dessous. Les fruits sont un exemple sans rapport avec HeaderScope.
- Lance-le avec un fruit de la liste, puis avec un fruit absent, et sans argument. Supprime exemple_choix.py ensuite.

```
import sys

FRUITS = ['pomme', 'poire', 'cerise', 'prune']
choix = sys.argv[1] if len(sys.argv) > 1 else 'pomme'
if choix in FRUITS:
    print('fruit choisi :', choix)
else:
    print('inconnu :', choix)
```

```
python3 exemple_choix.py poire
```

```
python3 exemple_choix.py kiwi
```

```
python3 exemple_choix.py
```

**Tu sais que c’est bon quand :** « poire » affiche « fruit choisi : poire », « kiwi » affiche « inconnu : kiwi », et sans argument le programme prend la valeur par défaut.

*Indice :* sys.argv[0] est le nom du script ; le premier vrai argument est sys.argv[1]. Teste d’abord la longueur de la liste pour ne pas planter quand l’argument manque.

#### Palier 3 — Relier le client et les règles (10 min)

Écrire une fonction qui enchaîne les étapes dans le bon ordre : vérifier, demander, classer.

- Écris executer_bilan(chemin) : elle vérifie que le chemin est l’un des quatre chemins fixes, appelle demander(chemin), puis classe la réponse avec classer_reponse.
- Garde l’ordre : vérifier le chemin, puis demander, puis classer. Un chemin refusé s’arrête avant tout appel réseau.
- Ajoute un bloc if __name__ == '__main__': qui lit le chemin dans sys.argv, comme dans l’exemple du palier 2.
- Ne sors aucun crawl, aucune URL arbitraire et aucun scan : le programme reste sur les quatre chemins.
- Commit.

```
python3 -m py_compile headerscope.py
```

```
python3 verification.py
```

```
git add headerscope.py
```

```
git commit -m "Relie le client, les règles et le classement dans executer_bilan"
```

**Tu sais que c’est bon quand :** py_compile ne signale aucune erreur, H1 à H9 passent, et git log --oneline montre le commit.

*Indice :* Ne refais pas les règles ni le client dans executer_bilan : appelle les fonctions déjà écrites. Une seule fonction assemble les étapes, ce qui permet de tester chaque morceau séparément.

#### Palier 4 — Un bilan lisible et quatre issues distinctes (10 min)

Produire un texte de bilan avec statut, alertes et résumé, et séparer 404, 500, panne et délai.

- Écris une fonction qui reçoit le résultat et retourne un texte : le statut, la liste des alertes et un résumé comme « 3 alertes » ou « aucune alerte ». Elle retourne le texte sans l’afficher, pour rester pure.
- Pour une panne et pour un délai dépassé, retourne un libellé distinct de tout code HTTP.
- Pourquoi : un texte qui retourne au lieu d’afficher se teste et se réutilise sans modifier l’écran.
- Commit.

```
produits = [('pomme', 3), ('poire', 0)]
for nom, quantite in produits:
    print(f'{nom} : {quantite} en stock')
```

```
python3 -m py_compile headerscope.py
```

```
git add headerscope.py
```

```
git commit -m "Affiche un bilan lisible et distingue les issues HTTP"
```

**Tu sais que c’est bon quand :** Le bilan contient statut, alertes et résumé ; les quatre issues ont des libellés différents ; py_compile ne signale aucune erreur.

*Indice :* Une f-string s’écrit f'{valeur}' et insère la valeur dans le texte. Pour une liste vide d’alertes, écris un texte explicite plutôt que de ne rien afficher.

#### Palier 5 — Vérifier que les tests n’ont pas besoin du laboratoire (10 min)

Prouver que la CI reste verte sans laboratoire, en contrôlant que les tests ne touchent pas le réseau.

- Pourquoi : sur le runner de l’école, le laboratoire n’existe pas. Si un test dépend de lui, la CI devient rouge pour une mauvaise raison.
- Arrête le laboratoire (Ctrl+C dans le terminal de labs.py, ou son bouton dans Cyber Atelier), puis lance les tests.
- Vérifie que verification.py n’appelle ni urlopen ni demander : c’est H8 et H9 qui passent des valeurs directement.

```
python3 verification.py; echo $?
```

```
grep -n 'urlopen\|demander' verification.py
```

**Tu sais que c’est bon quand :** python3 verification.py se termine avec 0, et la commande grep ne trouve aucune ligne.

*Indice :* Si grep trouve une ligne, un test touche au réseau : retire-le des tests, et garde ce contrôle pour la démonstration du palier 7. Le code de sortie doit rester 0 même laboratoire arrêté.

#### Palier 6 — README : périmètre, règles, délai et limites (10 min)

Documenter ce que le programme fait, comment le lancer et ce qu’il ne prouve pas.

- Pourquoi : un README qui promet trop trompe le lecteur. Écris ce que la CI prouve, et ce qu’elle ne prouve pas.
- Rédige README.md avec : le périmètre (127.0.0.1:8000 et les quatre chemins seulement) ; les règles des trois en-têtes et leur normalisation ; le délai de 2 secondes ; la commande des tests (python3 verification.py) ; le fait que la CI ne suppose pas le laboratoire.
- Ajoute une section « limites » : un en-tête n’est pas une preuve de sécurité, une alerte ne dit pas qu’un site est exploitable, et le laboratoire est un outil de démonstration.
- Commit.

```
python3 verification.py
```

```
git status
```

```
git add README.md
```

```
git commit -m "Documente le périmètre, les règles et les limites de HeaderScope"
```

**Tu sais que c’est bon quand :** README.md contient la commande des tests, le délai de 2 secondes, le périmètre et les limites ; git log --oneline montre le commit.

*Indice :* Un bon README répond à trois questions : que fait le programme, comment le lancer, et qu’est-ce qu’il ne prouve pas. Relis-le comme si tu étais un autre étudiant qui n’a pas vu le cours.

#### Palier 7 — Démonstration D1 à D3 (hors tests) (10 min)

Vérifier le comportement réel du programme sur le laboratoire, sans le confondre avec les tests automatiques.

- Ces démonstrations (HeaderScope D1 à D3) exigent le laboratoire. Elles ne sont pas des tests de verification.py et ne doivent pas y entrer.
- Option A, dans Cyber Atelier : vérifie que le laboratoire intégré est actif ; son bouton permet de l’arrêter ou de le relancer.
- Option B, sur ton Mac : depuis le dossier cyberatelier, lance python3 labs.py, puis Ctrl+C pour l’arrêter.
- D1 : /fragile doit donner trois alertes. D2 : /durci doit donner zéro alerte. D3 : /absent puis /erreur doivent être identifiés comme 404 puis 500, des erreurs HTTP.
- Arrête ensuite le laboratoire et relance une fois le programme : tu dois voir une panne, distincte des 404 et 500.

```
python3 labs.py
```

```
python3 headerscope.py /fragile
```

```
python3 headerscope.py /durci
```

```
python3 headerscope.py /absent
```

```
python3 headerscope.py /erreur
```

**Tu sais que c’est bon quand :** D1 : trois alertes. D2 : zéro alerte. D3 : 404 et 500 identifiés comme erreurs HTTP, sans alerte de politique. Laboratoire arrêté : une panne.

*Indice :* Si tu obtiens une panne au lieu d’une réponse, le laboratoire n’est pas actif : vérifie le bouton de Cyber Atelier ou relance python3 labs.py. Ne change pas de port.

#### Palier 8 — Livrer la MR3 et fermer le bilan (10 min)

Pousser la dernière branche, vérifier le pipeline du dernier commit, puis fusionner seulement si le pipeline est vert.

- Relis le diff de la branche : headerscope.py, verification.py et README.md, sans fichier parasite.
- Pousse la branche, puis ouvre la merge request dans GitLab de l’école (feat/bilan vers main).
- Attends le pipeline du dernier commit. Pour cette MR : test local vert, pipeline GitLab exécuté, autorisation de fusion et case cochée dans Cyber Atelier sont quatre choses différentes. Seul le pipeline et la règle de fusion de l’école comptent pour la fusion.
- Fusionne seulement si le pipeline est vert. Après fusion, reviens sur main à jour.

```
git status
```

```
git diff main --stat
```

```
git push -u origin feat/bilan
```

```
git switch main
```

```
git pull --ff-only
```

**Tu sais que c’est bon quand :** Le pipeline du dernier commit est vert dans GitLab, la merge request ne contient que les fichiers attendus, et main local contient la fusion (git log --oneline).

*Indice :* Un pipeline vert ne prouve pas que les démonstrations D1 à D3 ont réussi : elles sont séparées. Ne fusionne jamais sur un pipeline rouge ou absent.

**Démonstrations manuelles (hors tests) :**
- **D1** — Résultat fragile. Entrée : Réponse locale du chemin /fragile Attendu : Trois alertes de politique.
- **D2** — Résultat durci. Entrée : Réponse locale du chemin /durci Attendu : Zéro alerte.
- **D3** — Statuts d’erreur. Entrée : /absent puis /erreur pendant une démonstration locale Attendu : 404 puis 500 identifiés comme erreurs HTTP.

**Avant de livrer :**
- La CI vérifie des tests locaux reproductibles et ne prétend pas démarrer le laboratoire scolaire.
- Les quatre chemins restent limités à 127.0.0.1:8000.
- Le README et le bilan distinguent résultats de tests, démonstration et limites des en-têtes.
- python3 verification.py affiche OK pour H1 à H9 et se termine avec 0, laboratoire arrêté.
- Les résultats 404, 500, panne et délai sont affichés avec des libellés distincts.
- La merge request contient headerscope.py, verification.py et README.md, sans __pycache__, et le pipeline du dernier commit est vert.

## Méthode GitLab

Crée ou utilise un dépôt autorisé par ton école. Vérifie que le runner est actif pour les branches non protégées de MR et que tu as les droits d’ouverture et de fusion. Dans la configuration de la branche principale, applique les règles de l’école et exige les pipelines réussis. Pour chaque étape, branche-toi depuis la principale actualisée, exécute les tests, lis le diff, pousse une MR et fusionne le dernier commit vert. Après chaque fusion, mets à jour la base avant la branche suivante.

La CI doit réellement exécuter les tests. Ne masque pas les erreurs, ne rends pas le job facultatif et ne prends pas un lint valide pour preuve qu’un runner fonctionne. Si l’école n’offre pas de runner ou de règle de fusion, note cette limite au lieu de déclarer le gate validé.

## Repères de temps

Préparation GitLab et lecture : 30 min. MR1 règles et tests : 85 min. MR2 client et erreurs : 85 min. MR3 orchestration, bilan et README : 80 min. Démonstration, relecture et marge : 20 min. Total : 300 min.

## Livrables et limites

Le dossier HeaderScope est vide au départ. Depuis son terminal, clone le dépôt directement dans le dossier courant avec git clone <URL_DU_DEPOT> . avant de créer les fichiers. Le point signifie « ici ». Les commandes du terminal web repartent chacune du dossier courant explicite ; un cd seul ne persiste pas. Pour Git interactif, utilise docker compose exec atelier bash depuis le dossier Cyber Atelier.

Livre un programme, une suite de tests locale utile, une configuration CI, un README clair, trois MR successives et un bilan honnête de ce que la CI et la démonstration valident. Les tests de règles sont autonomes et réalisables sur un runner ordinaire. La démonstration des quatre chemins utilise le laboratoire local de Cyber Atelier quand il est démarré explicitement.

Les en-têtes constituent des signaux de configuration, pas une preuve complète de sécurité. Le client ne visite que les chemins de laboratoire nommés et ne se connecte qu’à 127.0.0.1:8000. La CI de base ne vérifie pas la disponibilité du laboratoire. Une alerte ne prouve pas qu’un site est exploitable ou sûr.
