# Conversion d'une mission en paliers (agents de rédaction)

Lis d'abord : CLAUDE.md, drafts/BRIEF.md, et SURTOUT le modèle de référence : dans content/courses.json, la mission `socle-mr1` (clé `paliers`). Imite son niveau de guidage, son ton et sa granularité.

## Mission
Pour chaque mission (`steps[]`) de ton parcours, convertis `tasks` (+ `hint`) en une liste `paliers` plus guidée. L'apprenant est un vrai débutant en Python et Git, il code dans VS Code sur son Mac (terminal de VS Code, `python3`), son dépôt est le dossier `workspaces/<parcours>`, il pousse sur GitHub (dépôt privé) ; les parcours GitLab de l'école gardent leurs exigences GitLab (CI, MR, pipeline) quand le contenu actuel les demande.

## Règle d'or : NE RIEN RACCOURCIR, RENDRE PLUS SIMPLE
- Garde TOUTES les exigences actuelles : chaque élément de `tasks`, `tests`, `acceptance` et `demos` doit se retrouver (reformulé en plus simple si besoin). N'enlève aucun cas de test, aucune contrainte de périmètre, aucune règle de sécurité.
- Rends plus simple en DÉCOUPANT : plus de paliers, plus petits (10 à 20 minutes chacun, un seul objectif), pas moins de contenu. Une mission a typiquement 6 à 10 paliers.
- Explique le POURQUOI de chaque notion nouvelle (une phrase). Pour toute notion nouvelle (boucle, exception, dictionnaire, tempfile, subprocess, argparse, mock, package, venv, logging, etc.), ajoute un EXEMPLE TRAVAILLÉ court dans `commands` sur un sujet SANS RAPPORT avec l'exercice (ex. `doubler`, une liste de fruits, un fichier de courses). Cet exemple n'est jamais la solution de l'exercice.
- Rythme « rouge puis vert » : écrire le test, le voir échouer, écrire le minimum de code, le voir passer, commit. Un commit par palier de code, message exact donné dans `commands`.
- Donne les commandes Git EXACTES aux étapes de livraison (status, diff, add de fichiers nommés, commit avec message, push -u origin <branche>, ouverture de PR/MR, retour sur main + pull --ff-only).
- Précise, à chaque palier où ça compte, la différence entre « test local réussi » et « pipeline / fusion autorisée ».
- INTERDIT : fournir la solution (code de la fonction demandée, fichier .gitlab-ci.yml complet, regex ou algorithme final). Les indices guident sans donner la réponse.
- Cible réseau : uniquement 127.0.0.1 / labo local. Les tests obligatoires n'utilisent ni labo, ni nmap, ni réseau (mocks, fixtures, fichiers temporaires). Les démos (`demos`) restent séparées et ne sont PAS des paliers de tests ; mentionne-les dans un palier final « démonstration » via la consigne, sans les inclure dans `tests`.

## Format de sortie : UN fichier par mission, dans drafts/paliers/<step-id>.json
```
{
  "mission": "phrase d'intro de la mission (réécris-la pour qu'elle annonce la méthode par paliers)",
  "acceptance": ["tous les critères actuels, complétés si besoin, jamais supprimés"],
  "paliers": [
    {
      "id": "<step-id>-p1",            // p1, p2, p3… dans l'ordre
      "title": "titre court",
      "minutes": 12,                    // entier ; la SOMME doit être égale à `minutes` de la mission
      "goal": "une phrase : ce que ce palier t'apporte",
      "do": ["actions courtes, une par élément, en tutoyant"],
      "commands": ["une commande ou un petit bloc de code par élément (exemple travaillé, commande Git, commande de test)"],
      "tests": ["T1"],                  // ids des tests de la mission demandés dans CE palier (optionnel)
      "check": "comment l'apprenant sait que c'est bon (observable)",
      "hint": "un indice qui guide sans donner la solution"
    }
  ]
}
```
Contraintes vérifiées automatiquement : chaque id de test de la mission apparaît dans exactement un palier ; la somme des minutes des paliers = minutes de la mission ; ids `<step-id>-p<n>` uniques ; champs `title`, `goal`, `do`, `check`, `hint` non vides ; JSON valide.
Valide chaque fichier avec : `python3 drafts/validate_paliers.py <step-id>` (corrige jusqu'à « OK »).

## Interdits de périmètre
N'écris QUE dans drafts/paliers/. Ne modifie pas content/courses.json ni aucun autre fichier. Aucune commande git en écriture, aucun docker. Français, tutoiement, factuel. À la fin, réponds avec : les fichiers écrits, le nombre de paliers par mission, et tout élément que tu as dû reformuler ou dont tu doutes.
