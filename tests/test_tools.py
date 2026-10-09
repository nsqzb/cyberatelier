"""Tests de l'environnement d'outils : adsim et cohérence des fixtures.

Lancer depuis la racine : python3 -m unittest tests.test_tools -v
Aucun réseau. Les fichiers temporaires sont créés dans un TemporaryDirectory
qui est supprimé automatiquement.
"""
from __future__ import annotations

import ipaddress
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
ADSIM = RACINE / "tools" / "adsim.py"
ADSIM_FIX = RACINE / "fixtures" / "adsim"
NMAP_FIX = RACINE / "fixtures" / "nmap"
SOCLE_FIX = RACINE / "fixtures" / "socle"
RESEAU_FIXTURES = ipaddress.ip_network("192.0.2.0/24")
IPV4 = re.compile(r"(?<![\d.])(\d{1,3}(?:\.\d{1,3}){3})(?![\d.])")
LIGNE_AUTH = re.compile(
    r"^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01]) ([01]\d|2[0-3]):[0-5]\d:[0-5]\d "
    r"(LOGIN_OK|LOGIN_FAIL) \S+ \d{1,3}(?:\.\d{1,3}){3}$"
)


def lancer_adsim(*args, timeout=30):
    return subprocess.run(
        [sys.executable, str(ADSIM), *args],
        capture_output=True,
        timeout=timeout,
    )


class AdsimSujetsTests(unittest.TestCase):
    def test_users_json(self):
        res = lancer_adsim("users")
        self.assertEqual(res.returncode, 0, res.stderr)
        data = json.loads(res.stdout.decode("utf-8"))
        self.assertEqual(data["domain"], "LAB.LOCAL")
        self.assertEqual(data["subject"], "users")
        self.assertEqual(data["count"], len(data["items"]))
        self.assertEqual(data["count"], 8)
        for item in data["items"]:
            self.assertEqual(set(item), {"name", "enabled", "groups"})
        self.assertTrue(any(not item["enabled"] for item in data["items"]))

    def test_groups_json(self):
        res = lancer_adsim("groups")
        self.assertEqual(res.returncode, 0, res.stderr)
        data = json.loads(res.stdout.decode("utf-8"))
        self.assertEqual(data["subject"], "groups")
        self.assertEqual(data["count"], 5)
        noms = {item["name"] for item in data["items"]}
        self.assertIn("Domain Admins", noms)
        for item in data["items"]:
            self.assertEqual(set(item), {"name", "description", "members"})

    def test_computers_json(self):
        res = lancer_adsim("computers")
        self.assertEqual(res.returncode, 0, res.stderr)
        data = json.loads(res.stdout.decode("utf-8"))
        self.assertEqual(data["subject"], "computers")
        self.assertEqual(data["count"], 4)
        for item in data["items"]:
            self.assertEqual(set(item), {"name", "os", "enabled"})

    def test_users_text(self):
        res = lancer_adsim("users", "--format", "text")
        self.assertEqual(res.returncode, 0, res.stderr)
        lignes = res.stdout.decode("utf-8").splitlines()
        self.assertEqual(len(lignes), 8)
        for ligne in lignes:
            champs = ligne.split(";")
            self.assertEqual(len(champs), 3, ligne)
            self.assertIn(champs[1], {"actif", "inactif"})

    def test_groups_text(self):
        res = lancer_adsim("groups", "--format", "text")
        self.assertEqual(res.returncode, 0, res.stderr)
        lignes = res.stdout.decode("utf-8").splitlines()
        self.assertEqual(len(lignes), 5)
        for ligne in lignes:
            self.assertEqual(len(ligne.split(";")), 2, ligne)

    def test_computers_text(self):
        res = lancer_adsim("computers", "--format", "text")
        self.assertEqual(res.returncode, 0, res.stderr)
        lignes = res.stdout.decode("utf-8").splitlines()
        self.assertEqual(len(lignes), 4)
        for ligne in lignes:
            champs = ligne.split(";")
            self.assertEqual(len(champs), 3, ligne)
            self.assertIn(champs[2], {"actif", "inactif"})


class AdsimCodesTests(unittest.TestCase):
    def assertErreur(self, res, code):
        self.assertEqual(res.returncode, code, res.stderr)
        self.assertEqual(res.stdout, b"")
        self.assertTrue(res.stderr.strip(), "stderr doit contenir un message")
        self.assertNotIn(b"Traceback", res.stderr)

    def test_sujet_inconnu_code_2(self):
        self.assertErreur(lancer_adsim("utilisateurs"), 2)

    def test_sujet_manquant_code_2(self):
        self.assertErreur(lancer_adsim(), 2)

    def test_format_invalide_code_2(self):
        self.assertErreur(lancer_adsim("users", "--format", "xml"), 2)

    def test_delai_negatif_code_2(self):
        self.assertErreur(lancer_adsim("users", "--delay", "-1"), 2)

    def test_option_inconnue_code_2(self):
        self.assertErreur(lancer_adsim("users", "--inconnue"), 2)

    def test_fail_code_3(self):
        self.assertErreur(lancer_adsim("users", "--fail"), 3)

    def test_message_en_francais(self):
        res = lancer_adsim("utilisateurs")
        self.assertIn("sujet inconnu", res.stderr.decode("utf-8"))


class AdsimDelaiTests(unittest.TestCase):
    def test_delai_court_attend_puis_repond(self):
        debut = time.monotonic()
        res = lancer_adsim("users", "--delay", "0.3")
        duree = time.monotonic() - debut
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertGreaterEqual(duree, 0.3)
        self.assertEqual(json.loads(res.stdout.decode("utf-8"))["count"], 8)


class AdsimFixturesTests(unittest.TestCase):
    def test_fixtures_identiques_a_la_sortie_reelle(self):
        cas = [
            ("users.json", ("users",)),
            ("users.txt", ("users", "--format", "text")),
            ("groups.json", ("groups",)),
            ("computers.json", ("computers",)),
        ]
        for nom, args in cas:
            with self.subTest(fixture=nom):
                res = lancer_adsim(*args)
                self.assertEqual(res.returncode, 0, res.stderr)
                self.assertEqual(res.stdout, (ADSIM_FIX / nom).read_bytes())

    def test_domaine_absent_code_3(self):
        with tempfile.TemporaryDirectory() as tmp:
            copie = Path(tmp) / "tools" / "adsim.py"
            copie.parent.mkdir()
            shutil.copy(ADSIM, copie)
            res = subprocess.run(
                [sys.executable, str(copie), "users"], capture_output=True, timeout=30
            )
            self.assertEqual(res.returncode, 3)
            self.assertIn("introuvable", res.stderr.decode("utf-8"))

    def test_domaine_illisible_code_3(self):
        with tempfile.TemporaryDirectory() as tmp:
            copie = Path(tmp) / "tools" / "adsim.py"
            copie.parent.mkdir()
            shutil.copy(ADSIM, copie)
            cible = Path(tmp) / "fixtures" / "adsim"
            cible.mkdir(parents=True)
            shutil.copy(ADSIM_FIX / "broken.json", cible / "domain.json")
            res = subprocess.run(
                [sys.executable, str(copie), "users"], capture_output=True, timeout=30
            )
            self.assertEqual(res.returncode, 3)
            self.assertIn("illisible", res.stderr.decode("utf-8"))

    def test_adsim_sans_reseau(self):
        source = ADSIM.read_text(encoding="utf-8")
        for module in ("socket", "urllib", "http", "ftplib", "smtplib", "ssl"):
            self.assertIsNone(
                re.search(rf"^\s*(import|from)\s+{module}\b", source, re.MULTILINE),
                f"import réseau interdit : {module}",
            )


class FixturesCoherenceTests(unittest.TestCase):
    def test_xml_nmap_parsables(self):
        for nom in ("open_8000.xml", "closed_8000.xml", "mixed.xml"):
            with self.subTest(fixture=nom):
                racine = ET.parse(NMAP_FIX / nom).getroot()
                self.assertEqual(racine.tag, "nmaprun")
                self.assertIsNotNone(racine.find("host/ports/port/state"))

    def test_broken_xml_non_parsable(self):
        with self.assertRaises(ET.ParseError):
            ET.parse(NMAP_FIX / "broken.xml")

    def test_etats_nmap(self):
        attendus = {
            "open_8000.xml": {"open"},
            "closed_8000.xml": {"closed"},
            "mixed.xml": {"open", "closed", "filtered"},
        }
        for nom, etats in attendus.items():
            with self.subTest(fixture=nom):
                racine = ET.parse(NMAP_FIX / nom).getroot()
                trouves = {p.find("state").get("state") for p in racine.iter("port")}
                self.assertEqual(trouves, etats)

    def test_json_valides(self):
        for nom in ("domain.json", "users.json", "groups.json", "computers.json"):
            with self.subTest(fixture=nom):
                json.loads((ADSIM_FIX / nom).read_text(encoding="utf-8"))

    def test_broken_json_invalide(self):
        with self.assertRaises(json.JSONDecodeError):
            json.loads((ADSIM_FIX / "broken.json").read_text(encoding="utf-8"))

    def test_auth_log(self):
        chemin = SOCLE_FIX / "auth.log"
        self.assertTrue(chemin.is_file())
        lignes = chemin.read_text(encoding="utf-8").splitlines()
        self.assertGreaterEqual(len(lignes), 35)
        malformees = [ligne for ligne in lignes if not LIGNE_AUTH.match(ligne)]
        self.assertIn(len(malformees), (3, 4), malformees)

    def test_adresses_dans_192_0_2_0_24(self):
        # Les XML nmap visent 127.0.0.1, comme la vraie commande de démonstration.
        for xml in NMAP_FIX.glob("*.xml"):
            self.assertNotIn("192.0.2", xml.read_text(encoding="utf-8"))
        fichiers = (
            list(SOCLE_FIX.glob("*.log"))
            + list(ADSIM_FIX.glob("*.json"))
            + list(ADSIM_FIX.glob("*.txt"))
        )
        trouvees = []
        hors_plage = []
        for fichier in fichiers:
            for brut in IPV4.findall(fichier.read_text(encoding="utf-8")):
                trouvees.append(brut)
                if ipaddress.ip_address(brut) not in RESEAU_FIXTURES:
                    hors_plage.append((fichier.name, brut))
        self.assertTrue(trouvees, "aucune adresse trouvée : contrôle sans effet")
        self.assertEqual(hors_plage, [])

    def test_groupes_du_domaine_coherents(self):
        domaine = json.loads((ADSIM_FIX / "domain.json").read_text(encoding="utf-8"))
        noms = {g["name"] for g in domaine["groups"]}
        for user in domaine["users"]:
            self.assertTrue(set(user["groups"]) <= noms, user["name"])


if __name__ == "__main__":
    unittest.main()
