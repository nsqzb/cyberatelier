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

def generated(data, course):
    guide=data['learningGuide']
    out=[START,'## Comment travailler un exercice','',guide['body'],'']
    out += [f'{i}. {item}' for i,item in enumerate(guide['items'],1)]
    out += ['', '### Le bon endroit pour chaque action','',
      f'Sur ton Mac, ouvre `workspaces/{course["id"]}` dans VS Code. Dans Cyber Atelier, utilise l’éditeur et la console de **Coder**, avec `cwd` sur `.` (la racine du dépôt). Fais la préparation de **Environnement** avant MR1 ; la mission crée ensuite sa branche.', '',
      'Le code Python se place dans l’éditeur. Les commandes `docker compose ...` se lancent sur ton Mac depuis `cyberatelier` ; `/app/...` existe dans le conteneur. Le laboratoire interrogé doit tourner dans le même environnement que ton programme.', '',
      'La console web repart à neuf à chaque exécution : un `cd`, une activation de venv ou `echo $?` ne se transmet pas à la commande suivante. Lance le programme et `echo $?` ensemble quand le palier le demande. Le nombre affiché par echo est celui du programme ; la console peut afficher code 0 pour echo lui-même.', '',
      'Un venv créé sur le Mac ne fonctionne pas dans le conteneur : utilise `python3` dans ce dernier. Remplace `main` par `master` si nécessaire. Si une branche existe déjà, reprends-la avec `git switch NOM` sans `-c`. Après chaque fusion, actualise la branche principale avant la mission suivante.', '',
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
            wanted=[t for t in step.get('tests',[]) if t['id'] in p.get('tests',[])]
            if wanted:
                out += ['**Cas de test à écrire**','','L’entrée est ce que tu donnes au code ; l’attendu est ce que ton test doit vérifier.','']+cases(wanted)
            out += ['**Actions dans l’ordre**','']+[f'{i}. {item}' for i,item in enumerate(p['do'],1)]+['']
            previous_context=None
            for b in p['blocks']:
                out += [f'**{"Terminal" if b["kind"]=="shell" else "Éditeur"} · {b["title"]}**','']
                if b['context']!=previous_context: out += [b['context'],'']
                out += [fence(b['code'],'bash' if b['kind']=='shell' else b['kind']),'']
                previous_context=b['context']
            out += [f'**Tu sais que c’est bon quand :** {p["check"]}','',f'*Indice si tu bloques :* {p["hint"]}','']
        if step.get('demos'):
            out += ['**Démonstrations manuelles (hors CI)**','','Ces essais utilisent le laboratoire ou les outils réels. Ils sont séparés des tests obligatoires.','']+cases(step['demos'])
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
