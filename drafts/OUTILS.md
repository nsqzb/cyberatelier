# Contrat de l'environnement d'outils (implémenté par l'agent « infra », référencé par les parcours)

Tout est fourni DANS le conteneur Cyber Atelier ; rien n'est exécuté sur un runner GitLab.

## nmap (vrai outil, démonstration uniquement)
- Installé dans l'image (paquet Debian `nmap`). Cible autorisée du lab : `127.0.0.1` ports `8000` (labo HTTP) et `8080` (Cyber Atelier lui-même est hors périmètre : ne le mentionne PAS).
- Commande de référence pour la démo : `nmap -sT -p 8000 -oX - 127.0.0.1` (scan TCP connect, sortie XML sur stdout). Le runner GitLab n'a pas nmap : les tests obligatoires n'appellent JAMAIS nmap, ils lisent des fixtures XML.
- Fixtures XML fictives (fournies en lecture seule dans `/app/fixtures/nmap/`, à copier par l'apprenant) : `open_8000.xml` (1 port open http), `closed_8000.xml` (port closed), `mixed.xml` (3 ports : open, closed, filtered), `broken.xml` (XML invalide).

## adsim — simulateur d'outil Active Directory (stand-in local, FICTIF)
- Programme : `/app/tools/adsim.py`, lancé par `python /app/tools/adsim.py <sujet> [options]`. Domaine fictif `LAB.LOCAL`, données dans `/app/fixtures/adsim/domain.json`. N'interroge aucun réseau, ne se connecte à aucun annuaire réel.
- Sujets : `users`, `groups`, `computers`. Options : `--format json|text` (défaut json), `--delay SECONDS` (attend avant de répondre, pour s'entraîner aux timeouts), `--fail` (sort en erreur pour s'entraîner à gérer un code de retour non nul).
- Sortie JSON : `{"domain": "LAB.LOCAL", "subject": "users", "count": N, "items": [ ... ]}` ; items users : `name`, `enabled` (bool), `groups` (liste). Sortie text : une ligne par item `nom;actif|inactif;groupe1,groupe2`.
- Codes de sortie : 0 succès ; 2 argument invalide (message sur stderr) ; 3 erreur simulée (`--fail`, message sur stderr).
- Fixtures de sortie capturée pour les tests, dans `/app/fixtures/adsim/` : `users.json`, `users.txt`, `groups.json`, `computers.json`, `broken.json` (JSON invalide).

## Journal fictif pour le parcours Socle
- `/app/fixtures/socle/auth.log` : ~40 lignes fictives de connexions (`2026-01-05 08:12:44 LOGIN_OK alice 192.0.2.10` / `LOGIN_FAIL`, adresses de documentation 192.0.2.0/24 uniquement), quelques lignes malformées volontairement.

## Où l'apprenant copie les fixtures
Depuis la console du parcours : `mkdir -p fixtures && cp -r /app/fixtures/<sujet>/. fixtures/<sujet>/ && chmod -R u+w fixtures/<sujet>` (les originaux sont en lecture seule).
