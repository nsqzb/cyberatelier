# Suivre les exercices depuis le terminal du Mac

## Lire un palier et reprendre ton travail

Depuis le dossier de l’application :

```bash
cd /Users/anas/Documents/cyberatelier
python3 atelier.py
```

Le lecteur affiche le palier courant et ses repères : dossier de travail,
branche Git réelle, branche demandée par la mission, fichiers à écrire,
résultats attendus et actions. Tu peux avancer, revenir ou demander un indice.
Quitter puis relancer reprend le dernier palier consulté.

Tu peux aussi utiliser directement les commandes suivantes :

```bash
python3 atelier.py voir
python3 atelier.py suivant
python3 atelier.py precedent
python3 atelier.py parcours socle
python3 atelier.py indice
python3 atelier.py fait
python3 atelier.py a-refaire
python3 atelier.py statut
python3 atelier.py contexte
python3 atelier.py preparer
```

`indice` révèle progressivement un rappel, une piste puis un exemple.
`fait` coche seulement le palier que tu déclares terminé : cela ne lance pas
de tests et ne confirme aucune fusion. `suivant` permet de consulter la suite
sans cocher le palier. Les commandes affichées dans les consignes ne sont pas
exécutées par le lecteur : tu les lances toi-même.

`preparer` affiche les étapes d’installation du parcours. Reprends une branche
existante avec `git switch NOM`, au lieu de la créer à nouveau. Un dépôt déjà
initialisé ne doit pas être cloné une seconde fois.

## Garder les deux dépôts distincts

| Dossier | Son rôle | Commandes concernées |
| --- | --- | --- |
| `cyberatelier` | Application et énoncés | Lecteur, Docker, mises à jour de l’application |
| `cyberatelier/workspaces/socle` | Ton exercice Socle | Code, tests, commits et branche comme `feat/bases` |

Garde le lecteur dans un terminal et travaille sur ton code dans un autre :

```bash
cd /Users/anas/Documents/cyberatelier/workspaces/socle
git status
git branch --show-current
```

Tu peux invoquer le lecteur sans quitter le dossier de l’exercice :

```bash
python3 ../../atelier.py voir
python3 ../../atelier.py indice
```

Le lecteur lit ta branche pour l’afficher. Il ne change pas de branche,
ne fait pas de commit et ne modifie aucun fichier d’exercice.

## Choisir le bon laboratoire

Pour un programme que tu lances sur le Mac, démarre le laboratoire sur le Mac
dans un terminal séparé, depuis `cyberatelier` :

```bash
python3 labs.py
```

Il écoute sur `127.0.0.1:8000` du Mac. Arrête-le avec `Ctrl+C` quand une
démonstration demande d’observer une connexion refusée.

Pour nmap, adsim et les démonstrations exécutées dans Docker, depuis
`cyberatelier` sur le Mac :

```bash
docker compose up -d
python3 atelier.py labo statut
python3 atelier.py labo arreter
python3 atelier.py labo demarrer
```

Ces trois dernières commandes contrôlent le laboratoire à l’intérieur de
Docker. `127.0.0.1` dans Docker désigne le conteneur. Un environnement `.venv`
créé sur le Mac s’utilise sur le Mac ; dans Docker, utilise le Python fourni
par le conteneur. Les tests automatiques demandés restent indépendants des
laboratoires et des outils réels.

## Retrouver ta progression

Le lecteur conserve sa position, tes cases déclaratives et tes notes dans
`userdata/terminal.json`. Git ignore ce fichier. Au premier lancement, il
essaie de récupérer ta progression existante auprès de l’atelier local si
Docker est disponible, sans ouvrir le navigateur ni modifier les données
du serveur. Sans Docker, il fonctionne avec son fichier local.

Après cette première importation, les progressions du terminal et du site
évoluent séparément. Continue à utiliser le terminal pour garder un suivi
cohérent. Un fichier de progression invalide provoque un message d’erreur ;
il n’est pas remplacé automatiquement par une progression vide.

## Mettre à jour l’application

Après la fusion d’une MR dans `main`, depuis `cyberatelier` :

```bash
./mettre-a-jour
```

Depuis le dossier d’un exercice, le même outil est accessible par son chemin :

```bash
../../mettre-a-jour
```

Il sauvegarde tes données, actualise le dépôt de l’application puis reconstruit
Docker. La branche et les commits de ton exercice restent en place. Les
sauvegardes sont conservées dans `backups/`. Tu peux vérifier la version avec :

```bash
python3 ../../atelier.py version
```

`./mettre-a-jour --check` consulte les changements disponibles sans installer
la mise à jour.
