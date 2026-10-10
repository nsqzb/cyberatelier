"""Synchronise la partie pédagogique des six énoncés depuis courses.json.

Les contrats placés avant les missions et les limites placées après restent
rédigés dans les Markdown. python3 scripts/generate_exercises.py --check
vérifie les fichiers sans les écrire.
"""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
START='<!-- BEGIN GENERATED EXERCISES -->'
END='<!-- END GENERATED EXERCISES -->'
OUTRO={'socle':'## Méthode GitLab et Git','portpilot':'## Cycle de travail et validation',
       'headerscope':'## Méthode GitLab','fileguard':'## Méthode GitLab',
       'toolwrap':'## Méthode Git','reconwrap':'## Méthode GitLab'}

def fence(code, language):
    # L’exemple Markdown peut contenir lui-même un bloc à trois accents.
    marker='`'*max(3,max((len(s) for s in code.split() if s and set(s)=={'`'}),default=0)+1)
    return f'{marker}{language}\n{code}\n{marker}'

def cases(items):
    out=[]
    for case in items:
        out.extend([f'**{case["id"]} — {case["title"]}**',
                    f'- Entrée : {case["input"]}',f'- Résultat attendu : {case["expected"]}',''])
    return out

def blocks(items, placement):
    out=[]
    previous_context=None
    for b in items:
        if b.get('placement','after_actions')!=placement: continue
        out += [f'**{"Terminal" if b["kind"]=="shell" else "Éditeur"} · {b["title"]}**','']
        if b['context']!=previous_context: out += [b['context'],'']
        out += [fence(b['code'],'bash' if b['kind']=='shell' else b['kind']),'']
        previous_context=b['context']
    return out

def generated(data, course):
    guide=data['learningGuide']
    out=[START,'## Comment travailler un exercice','',guide['body'],'']
    out += [f'{i}. {item}' for i,item in enumerate(guide['items'],1)]
    out += ['', '### Le bon endroit pour chaque action','',
      f'Ouvre `workspaces/{course["id"]}` dans VS Code et un terminal du Mac dans ce même dossier. Tu écris et testes le code ici, dans le dépôt Git de l’exercice. Ouvre un second terminal dans `cyberatelier` pour lire les consignes avec `python3 atelier.py voir` et piloter Docker. Le site reste disponible pour la lecture ; l’onglet Coder est facultatif.', '',
      f'Depuis `cyberatelier`, `mkdir -p workspaces/{course["id"]}` puis `cd workspaces/{course["id"]}` permet de rejoindre le dossier du parcours. S’il contient déjà ton exercice, garde ses fichiers, sa branche et son dépôt : ne le reclone pas. La préparation ci-dessous se fait une fois ; la mission crée ensuite sa branche.', '',
      'Le code Python se place dans VS Code et doit être enregistré avant les tests. Les commandes `docker compose ...` et `python3 atelier.py ...` se lancent depuis `cyberatelier`. Leurs appels Docker entrent dans le conteneur ; `/app/fixtures`, `/app/tools` et `/workspaces` sont des chemins internes à celui-ci. Depuis le dépôt d’exercice sur le Mac, les fixtures fournies sont dans `../../fixtures`.', '',
      'Le terminal du Mac conserve son `cd` et son activation de venv. Active `.venv` dans chaque nouveau terminal d’exercice ; `python3` utilise alors ce venv, ou appelle `.venv/bin/python` explicitement. Lis `echo $?` immédiatement après le programme dont tu veux le code, avant toute autre commande. Ajoute `.venv/` à `.gitignore` avant `git add`.', '',
      'PortPilot et HeaderScope exécutés sur le Mac : lance `python3 labs.py` depuis `cyberatelier` dans un autre terminal et garde-le ouvert ; Ctrl+C arrête ce labo Mac. Les outils ToolWrap et les démos ReconWrap tournent dans Docker : `python3 atelier.py labo demarrer`, `labo arreter` et `labo statut` depuis `cyberatelier` pilotent uniquement le labo Docker. Le même numéro 8000 ne relie pas automatiquement les deux environnements.', '',
      'Un venv créé sur le Mac ne fonctionne pas dans Docker : les démos dans le conteneur utilisent son `python3`. Le dossier hôte `workspaces` doit être monté dans Docker pour que les démos ReconWrap lisent ton code ; conserve le `compose.override.yaml` du mode VS Code. Remplace `main` par `master` si nécessaire. Si une branche existe, reprends-la avec `git switch NOM` sans `-c`. Après chaque fusion, actualise la principale dans le dépôt du parcours avant la mission suivante.', '',
      '### Préparation sur le Mac','']
    for item in course['setup']:
        out += [f'**{item["label"]}**','',item.get('context',f'Terminal du Mac, dans workspaces/{course["id"]}.'),'']
        if item.get('command'): out += [fence(item['command'],'bash'),'']
        out += [item.get('note',''),'']
    out += [
      '### Les mots utiles','']
    for term in guide['glossary']:
        out += [f'**{term["title"]}.** {term["body"]}','']
    out += ['## Les trois MR','','Les durées sont des repères compris dans les 300 minutes du parcours.','']
    for index,step in enumerate(course['steps'],1):
        learn=step['learning']
        out += [f'### MR{index} — {step["branch"]} ({step["minutes"]} min)','',step['mission'],'',
          '**Avant de commencer**','',f'- Point de départ : {learn["startingPoint"]}',
          f'- Ce que tu vas produire : {learn["deliverable"]}',f'- Pourquoi : {learn["why"]}',
          f'- Commande des tests depuis la racine : `{learn["testCommand"]}`. Les cas ci-dessous sont à écrire par toi.','']
        for n,p in enumerate(step['paliers'],1):
            out += [f'#### Palier {n} — {p["title"]} ({p["minutes"]} min)','',p['goal'],'',f'**Où tu travailles :** {p["workspace"]}','']
            if p['explanation']:
                out += ['**Pour comprendre**','']+[f'- {item}' for item in p['explanation']]+['']
            out += blocks(p['blocks'],'before_actions')
            if p.get('example'):
                example=p['example']
                out += ['**Exemple de résultat attendu**','','Ce que tu donnes :','',
                        fence(example['input'],'text'),'','Ce que tu dois obtenir :','',
                        fence(example['output'],'text'),'',example['note'],'']
            if p.get('rules'):
                out += ['**Règles à respecter**','']+[f'- {item}' for item in p['rules']]+['']
            wanted=[t for t in step.get('tests',[]) if t['id'] in p.get('tests',[])]
            if wanted:
                out += ['**Cas de test à écrire**','','L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.','']+cases(wanted)
            out += ['**Actions dans l’ordre**','']+[f'{i}. {item}' for i,item in enumerate(p['do'],1)]+['']
            out += blocks(p['blocks'],'after_actions')
            out += [f'**Tu sais que c’est bon quand :** {p["check"]}','']
            if p.get('hints'):
                out += ['**Indices progressifs**','','Depuis le terminal dans `cyberatelier`, `python3 atelier.py indice` révèle un niveau à la fois. Ouvre seulement le niveau nécessaire.','']
                for level,hint in enumerate(p['hints'],1):
                    out += ['<details>',f'<summary>Indice {level}</summary>','',hint,'','</details>','']
            else:
                out += [f'*Indice si tu bloques :* {p["hint"]}','']
        if step.get('demos'):
            out += ['**Démonstrations manuelles (hors CI)**','','Ces essais lisent des fichiers locaux ou utilisent le labo et les outils réels, selon le parcours. Ils sont séparés des tests obligatoires.','']
            if course['id'] in ('toolwrap','reconwrap'):
                out += ['Les cartes ci-dessous conservent le contrat de démonstration initial. Depuis le terminal Mac dans `cyberatelier`, les mentions du « bouton du labo » se réalisent avec `python3 atelier.py labo demarrer` ou `python3 atelier.py labo arreter`. Utilise les commandes Docker du palier de démonstration pour exécuter les outils dans le bon environnement.','']
            out += cases(step['demos'])
        out += ['**Avant de livrer**','']+[f'- {item}' for item in step['acceptance']]+['']
    return '\n'.join(out+[END,''])

def document(data, course, text):
    if START in text:
        before,rest=text.split(START,1)
        _,after=rest.split(END,1)
    else:
        before,rest=text.split('## Les trois MR',1)
        _,suffix=rest.split(OUTRO[course['id']],1)
        after=OUTRO[course['id']]+suffix
    return before.rstrip()+'\n\n'+generated(data,course)+'\n'+after.lstrip()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    data=json.loads((ROOT/'content/courses.json').read_text(encoding='utf-8'))
    outdated=[]
    for c in data['courses']:
        path=ROOT/'content'/f'{c["id"]}.md'
        text=path.read_text(encoding='utf-8')
        result=document(data,c,text)
        if args.check:
            if result!=text: outdated.append(str(path.relative_to(ROOT)))
        else: path.write_text(result,encoding='utf-8')
    if outdated: parser.exit(1,'Énoncés à régénérer : '+', '.join(outdated)+'\n')
    print('Énoncés synchronisés : 6/6.')

if __name__=='__main__': main()
