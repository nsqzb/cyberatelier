# Mode d'emploi des outils fournis

Ce document décrit les outils et fixtures livrés dans l'image Cyber Atelier : nmap (outil réel, démonstration uniquement), adsim (simulateur **fictif** d'Active Directory) et les fixtures. Source : `tools/adsim.py`, `fixtures/nmap/`, `fixtures/adsim/`, `fixtures/socle/`, `fixtures/integrity/`, et les parcours dans `content/courses.json`. Vérifié à la date du 2026-10-10.

Dans le conteneur, tout se trouve sous `/app` et est en lecture seule. Les commandes ci-dessous se lancent dans `docker compose exec atelier bash`, ou dans la console du parcours.

## 1. nmap

nmap est un outil réel, installé dans l'image par le `Dockerfile` (paquet Debian `nmap`). Il ne sert qu'à une **démonstration** sur le labo local.

**Commande de démo** (le labo doit être démarré : il l'est au lancement de l'application, le bouton de la page du parcours permet de l'arrêter ou de le relancer) :

```bash
nmap -sT -p 8000 -oX - 127.0.0.1
```

- `-sT` : scan TCP connect, qui ne demande pas de privilèges particuliers.
- `-p 8000` : un seul port, celui du labo HTTP.
- `-oX -` : sortie au format XML, envoyée sur la sortie standard. C'est ce XML que ToolWrap et ReconWrap apprennent à lire avec `xml.etree.ElementTree`.
- Cible : `127.0.0.1` uniquement.

Une sortie réussie contient `<state state="open" ...>` pour le port 8000. Labo arrêté, l'état attendu est `closed`, comme dans `closed_8000.xml` (attendu d'après les fixtures, non observé ici).

**Fixtures XML fictives** (copies modifiables à faire dans ton dépôt, voir section 4) :

| Fichier | Contenu | Usage |
|---|---|---|
| `open_8000.xml` | un port 8000 `open` (service `http-alt`) | lecture d'un état ouvert |
| `closed_8000.xml` | un port 8000 `closed` | lecture d'un état fermé |
| `mixed.xml` | trois ports : `open`, `closed`, `filtered` | ordre et états mélangés |
| `broken.xml` | XML invalide | erreur de parsing attendue |

**Limites**
- Une seule cible (`127.0.0.1`) et un seul port (`8000`) dans le lab. Pas de scan de plage, pas de cible externe, pas d'option qui élargit le périmètre.
- Le runner GitLab de l'école n'a pas nmap, et `127.0.0.1` y désigne le runner. Les tests obligatoires n'appellent donc jamais nmap : ils lisent les fixtures XML.
- Un état `open` ne prouve ni la nature du service, ni une vulnérabilité.
- Vérification de l'installation : `nmap --version` dans le conteneur. Non vérifié dans ce document.

## 2. adsim (simulateur fictif d'Active Directory)

`adsim` est un simulateur **fictif** d'un outil d'annuaire Active Directory, pour s'entraîner à piloter un outil externe et à lire sa sortie. Domaine : `LAB.LOCAL`. Il n'ouvre **aucune connexion réseau** (un test vérifie qu'aucun module réseau n'est importé) et n'interroge aucun annuaire réel. Les données sont celles de `fixtures/adsim/domain.json`.

**Emplacement et lancement**

```bash
python /app/tools/adsim.py <sujet> [options]
```

Le script lit toujours `domain.json` à côté de lui, dans `/app/fixtures/adsim/`. La copie que tu fais dans ton dépôt (`fixtures/adsim/`) n'est pas lue par adsim : elle sert à tes tests.

**Sujets** (argument obligatoire, positionnel)
- `users` : 8 comptes.
- `groups` : 5 groupes (`Domain Users`, `Domain Admins`, `IT Support`, `Comptabilite`, `Direction`).
- `computers` : 4 machines.

**Options**

| Option | Défaut | Effet |
|---|---|---|
| `--format json` ou `--format text` | `json` | Format de sortie (section suivante). Toute autre valeur donne le code 2. |
| `--delay SECONDES` | `0` | Attend avant de répondre. Valeur comprise entre 0 et 60, décimale acceptée. Hors plage : code 2. Sert à s'entraîner aux délais d'attente. |
| `--fail` | désactivé | Simule une erreur de service : message sur la sortie d'erreur, code 3. S'applique après `--delay` et avant la lecture du domaine. |
| `-h` | | Affiche l'aide. |

**Codes de sortie**

| Code | Quand | Sortie |
|---|---|---|
| `0` | succès | résultat sur la sortie standard |
| `2` | sujet manquant ou inconnu, format inconnu, `--delay` hors plage, option inconnue | message en français sur la sortie d'erreur, rien sur la sortie standard |
| `3` | `--fail`, ou fichier `domain.json` absent, illisible ou mal formé | message en français sur la sortie d'erreur |

Aucune trace Python (`Traceback`) n'est affichée dans ces cas.

**Format JSON** (par défaut)

```json
{
  "domain": "LAB.LOCAL",
  "subject": "computers",
  "count": 4,
  "items": [
    {"name": "WS-COMPTA-01", "os": "Windows 10 Pro", "enabled": true}
  ]
}
```

Les champs de `items` dépendent du sujet :
- `users` : `name`, `enabled` (booléen), `groups` (liste de noms).
- `groups` : `name`, `description`, `members` (liste de noms).
- `computers` : `name`, `os`, `enabled` (booléen).

`count` est le nombre d'éléments de `items`.

**Format texte** (`--format text`) : une ligne par élément, champs séparés par `;`, listes séparées par `,`, sans en-tête.

| Sujet | Forme d'une ligne | Exemple réel |
|---|---|---|
| `users` | `nom;actif\|inactif;groupe1,groupe2` | `alice;actif;Domain Users,IT Support` |
| `groups` | `nom;membre1,membre2` | `Domain Admins;claire` |
| `computers` | `nom;os;actif\|inactif` | `WS-DIR-02;Windows 11 Pro;actif` |

**Exemples réels** (sorties relevées le 2026-10-10)

```bash
python /app/tools/adsim.py users --format text
# alice;actif;Domain Users,IT Support
# bob;actif;Domain Users,Comptabilite
# ...
# svc-sauvegarde;inactif;Domain Users
```

```bash
python /app/tools/adsim.py utilisateurs ; echo $?
# adsim : sujet inconnu : utilisateurs. Choisissez users, groups ou computers.
# 2
```

**Limites**
- Données fixes : rien ne change d'une exécution à l'autre, et rien ne se modifie.
- Pas de LDAP, Kerberos, mot de passe, authentification ni droits réels. Les attributs sont ceux du fichier de données.
- Le module Active Directory de ReconWrap et les démonstrations D5 s'appuient sur ce simulateur. Le vrai Active Directory se pratiquera dans le projet final, sur un domaine personnel.
- Le texte d'aide de `-h` mélange les titres d'argparse (en anglais) et les descriptions (en français).

## 3. Fixtures

Les fixtures sont des données **fictives**. Les originaux sont dans l'image, en lecture seule, sous `/app/fixtures/`. Les tests de Cyber Atelier lisent les originaux ; les tests de l'apprenant lisent les copies de son dépôt.

| Dossier (image) | Fichiers | Parcours et usage | Adresses |
|---|---|---|---|
| `fixtures/integrity/` | `README.txt`, `message.txt`, `settings.ini` | FileGuard : manifeste et comparaison (sans manifeste de référence) | aucune |
| `fixtures/socle/` | `auth.log` (40 lignes, 3 ou 4 malformées) | Socle : lecture du journal, démonstrations D1 et D2 | `192.0.2.0/24` (documentation) |
| `fixtures/nmap/` | `open_8000.xml`, `closed_8000.xml`, `mixed.xml`, `broken.xml` | ToolWrap (MR3 : lecture XML) et ReconWrap (lecture XML) | `127.0.0.1` |
| `fixtures/adsim/` | `domain.json`, `users.json`, `users.txt`, `groups.json`, `computers.json`, `broken.json` | ToolWrap (lecture JSON, erreurs) et ReconWrap (module AD) | domaine `LAB.LOCAL` |

`domain.json` est la donnée lue par adsim. `users.json`, `users.txt`, `groups.json` et `computers.json` sont les sorties réelles d'adsim, comparées octet par octet aux sorties des commandes par les tests. `broken.json` est un JSON invalide.

**Copier les fixtures dans ton dépôt**

Les commandes sont dans les consignes de chaque parcours ; le bouton « Préparer dans la console » de l'onglet Environnement remplit la commande sans l'exécuter. Une commande de console repart à neuf : utilise les chemins absolus.

```bash
# FileGuard (MR2)
mkdir -p fixtures && cp /app/fixtures/integrity/* fixtures/ && chmod u+w fixtures/*

# Socle
mkdir -p fixtures && cp -r /app/fixtures/socle/. fixtures/socle/ && chmod -R u+w fixtures/socle

# ToolWrap : nmap et adsim
mkdir -p fixtures && cp -r /app/fixtures/nmap/. fixtures/nmap/ && chmod -R u+w fixtures/nmap
mkdir -p fixtures && cp -r /app/fixtures/adsim/. fixtures/adsim/ && chmod -R u+w fixtures/adsim
```

ReconWrap (MR2) fait la même copie de `nmap` et `adsim`, depuis une tâche du parcours, puis vérifie avec `git status` que les copies sont suivies par Git.

Le fichier `auth.log` n'est pas à versionner : le `.gitignore` de la MR1 du socle l'exclut. Les copies (`fixtures/...`) restent modifiables, ce qui permet de simuler un fichier modifié ou une sortie cassée. Les originaux ne le sont pas.

**Vérifier les fixtures** : `python -m unittest tests.test_tools -v` (dans l'image, depuis `/app`) contrôle la cohérence des fixtures. Ces tests sont ceux de Cyber Atelier, pas les tiens.
