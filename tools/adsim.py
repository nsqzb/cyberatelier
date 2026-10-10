#!/usr/bin/env python3
"""Simulateur FICTIF d'un outil Active Directory pour Cyber Atelier.

Usage :
    python tools/adsim.py {users,groups,computers} [--format json|text]
                          [--delay SECONDES] [--fail]

Lit uniquement fixtures/adsim/domain.json (domaine fictif LAB.LOCAL).
N'ouvre aucune connexion réseau et n'interroge aucun annuaire réel.

Codes de sortie :
    0  succès
    2  argument invalide (message sur stderr)
    3  erreur simulée (--fail) ou fichier du domaine absent ou invalide
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

DOMAIN_FILE = Path(__file__).resolve().parent.parent / "fixtures" / "adsim" / "domain.json"
SUJETS = ("users", "groups", "computers")
FORMATS = ("json", "text")
DELAI_MAX = 60.0
CLES_DOMAINE = ("domain", "groups", "users", "computers")

EXIT_OK = 0
EXIT_ARGUMENTS = 2
EXIT_SIMULEE = 3


class DomainError(Exception):
    """Le fichier du domaine simulé est absent ou ne respecte pas le format attendu."""


class ParseurFrancais(argparse.ArgumentParser):
    """Remplace les messages d'argparse (anglais) par un message français."""

    def error(self, message: str) -> None:
        ecrire(sys.stderr, "adsim : arguments invalides. Aide : adsim.py -h\n")
        sys.exit(EXIT_ARGUMENTS)


def ecrire(flux, texte: str) -> None:
    """Écrit du texte en UTF-8, quelle que soit la locale du système."""
    flux.buffer.write(texte.encode("utf-8"))
    flux.buffer.flush()


def erreur_arguments(message: str) -> int:
    ecrire(sys.stderr, f"adsim : {message}\n")
    return EXIT_ARGUMENTS


def construire_parseur() -> argparse.ArgumentParser:
    parseur = ParseurFrancais(
        prog="adsim.py",
        description="Simulateur d'annuaire Active Directory FICTIF (domaine LAB.LOCAL). Aucun réseau.",
    )
    parseur.add_argument("sujet", nargs="?", help="users, groups ou computers")
    parseur.add_argument("--format", default="json", help="json (défaut) ou text")
    parseur.add_argument(
        "--delay", type=float, default=0.0, metavar="SECONDES",
        help="attend avant de répondre (entre 0 et 60)",
    )
    parseur.add_argument("--fail", action="store_true", help="simule une erreur (code de sortie 3)")
    return parseur


def valider_domaine(donnees) -> None:
    """Vérifie la forme du domaine ; lève DomainError avec un message français."""
    if not isinstance(donnees, dict):
        raise DomainError("format du domaine invalide : un objet JSON est attendu")
    for cle in CLES_DOMAINE:
        if cle not in donnees:
            raise DomainError(f"format du domaine invalide : clé absente « {cle} »")
    groupes, utilisateurs, ordinateurs = donnees["groups"], donnees["users"], donnees["computers"]
    if not all(isinstance(x, list) for x in (groupes, utilisateurs, ordinateurs)):
        raise DomainError("format du domaine invalide : groups, users et computers sont des listes")
    if not isinstance(donnees["domain"], str):
        raise DomainError("format du domaine invalide : « domain » doit être une chaîne")

    noms_groupes = set()
    for groupe in groupes:
        if not isinstance(groupe, dict) or not isinstance(groupe.get("name"), str):
            raise DomainError("format du domaine invalide : groupe mal formé")
        noms_groupes.add(groupe["name"])

    for user in utilisateurs:
        if not (isinstance(user, dict) and isinstance(user.get("name"), str)
                and isinstance(user.get("enabled"), bool) and isinstance(user.get("groups"), list)):
            raise DomainError("format du domaine invalide : utilisateur mal formé")
        for nom in user["groups"]:
            if not (isinstance(nom, str) and nom in noms_groupes):
                raise DomainError(f"format du domaine invalide : groupe inconnu pour {user['name']}")

    for machine in ordinateurs:
        if not (isinstance(machine, dict) and isinstance(machine.get("name"), str)
                and isinstance(machine.get("os"), str) and isinstance(machine.get("enabled"), bool)):
            raise DomainError("format du domaine invalide : ordinateur mal formé")


def charger_domaine(fichier: Path = DOMAIN_FILE):
    try:
        with fichier.open(encoding="utf-8") as source:
            donnees = json.load(source)
    except FileNotFoundError as exc:
        raise DomainError(f"fichier du domaine introuvable : {fichier}") from exc
    except (OSError, ValueError) as exc:
        raise DomainError(f"fichier du domaine illisible : {exc}") from exc
    valider_domaine(donnees)
    return donnees


def construire(sujet: str, domaine: dict) -> list[dict]:
    if sujet == "users":
        return [
            {"name": u["name"], "enabled": u["enabled"], "groups": list(u["groups"])}
            for u in domaine["users"]
        ]
    if sujet == "groups":
        return [
            {
                "name": g["name"],
                "description": g.get("description", ""),
                "members": [u["name"] for u in domaine["users"] if g["name"] in u["groups"]],
            }
            for g in domaine["groups"]
        ]
    return [
        {"name": o["name"], "os": o["os"], "enabled": o["enabled"]}
        for o in domaine["computers"]
    ]


def formater_text(sujet: str, items: list[dict]) -> str:
    lignes = []
    for item in items:
        if sujet == "users":
            etat = "actif" if item["enabled"] else "inactif"
            lignes.append(f"{item['name']};{etat};{','.join(item['groups'])}")
        elif sujet == "groups":
            lignes.append(f"{item['name']};{','.join(item['members'])}")
        else:
            etat = "actif" if item["enabled"] else "inactif"
            lignes.append(f"{item['name']};{item['os']};{etat}")
    return "".join(f"{ligne}\n" for ligne in lignes)


def main(argv: list[str] | None = None) -> int:
    args = construire_parseur().parse_args(argv)

    if args.sujet is None:
        return erreur_arguments("sujet manquant. Choisissez users, groups ou computers.")
    if args.sujet not in SUJETS:
        return erreur_arguments(f"sujet inconnu : {args.sujet}. Choisissez users, groups ou computers.")
    if args.format not in FORMATS:
        return erreur_arguments(f"format inconnu : {args.format}. Choisissez json ou text.")
    if not (0 <= args.delay <= DELAI_MAX):  # rejette aussi NaN
        return erreur_arguments(f"--delay doit être un nombre entre 0 et {DELAI_MAX:g} secondes.")

    time.sleep(args.delay)

    if args.fail:
        ecrire(sys.stderr, "adsim : erreur simulée (--fail). Le service d'annuaire ne répond pas.\n")
        return EXIT_SIMULEE

    try:
        domaine = charger_domaine()
    except DomainError as exc:
        ecrire(sys.stderr, f"adsim : {exc}\n")
        return EXIT_SIMULEE

    items = construire(args.sujet, domaine)
    if args.format == "json":
        charge = {
            "domain": domaine["domain"],
            "subject": args.sujet,
            "count": len(items),
            "items": items,
        }
        sortie = json.dumps(charge, ensure_ascii=False, indent=2) + "\n"
    else:
        sortie = formater_text(args.sujet, items)
    ecrire(sys.stdout, sortie)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
