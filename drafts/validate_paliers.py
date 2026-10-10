"""Valide drafts/paliers/<step-id>.json contre la mission correspondante de content/courses.json."""
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def main(step_id):
    courses = json.loads((BASE / "content" / "courses.json").read_text(encoding="utf-8"))["courses"]
    step = next((s for c in courses for s in c["steps"] if s["id"] == step_id), None)
    if step is None:
        return [f"mission inconnue : {step_id}"]
    chemin = BASE / "drafts" / "paliers" / f"{step_id}.json"
    try:
        data = json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"fichier illisible : {exc}"]
    erreurs = []
    paliers = data.get("paliers")
    if not isinstance(paliers, list) or len(paliers) < 4:
        return ["paliers : liste d'au moins 4 éléments attendue"]
    ids = [p.get("id") for p in paliers]
    if ids != [f"{step_id}-p{i}" for i in range(1, len(paliers) + 1)]:
        erreurs.append("ids de paliers : attendu <step-id>-p1, p2, … dans l'ordre")
    total = sum(p.get("minutes", 0) for p in paliers if isinstance(p.get("minutes"), int))
    if total != step["minutes"]:
        erreurs.append(f"minutes : somme {total} ≠ {step['minutes']}")
    for p in paliers:
        for cle in ("title", "goal", "do", "check", "hint"):
            if not p.get(cle):
                erreurs.append(f"{p.get('id')} : champ {cle} vide")
        if not isinstance(p.get("do", []), list) or not isinstance(p.get("commands", []), list):
            erreurs.append(f"{p.get('id')} : do et commands doivent être des listes")
    connus = [t["id"] for t in step.get("tests", [])]
    demandes = [t for p in paliers for t in p.get("tests", [])]
    for t in connus:
        if demandes.count(t) != 1:
            erreurs.append(f"test {t} demandé {demandes.count(t)} fois (attendu 1)")
    for t in demandes:
        if t not in connus:
            erreurs.append(f"test inconnu dans un palier : {t}")
    if not data.get("acceptance") or len(data["acceptance"]) < len(step.get("acceptance", [])):
        erreurs.append("acceptance : ne doit pas contenir moins de critères que l'original")
    if not data.get("mission"):
        erreurs.append("mission vide")
    return erreurs


if __name__ == "__main__":
    problemes = main(sys.argv[1])
    print("OK" if not problemes else "\n".join(problemes))
    sys.exit(1 if problemes else 0)
