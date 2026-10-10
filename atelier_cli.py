"""Lecture des exercices et progression locale, sans exécuter leur code."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import textwrap
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parent
MAX_JSON = 1_048_576


class AtelierError(Exception):
    """Erreur que l'apprenant peut lire sans traceback."""


def read_json(path: Path):
    try:
        with path.open("rb") as stream:
            data = stream.read(MAX_JSON + 1)
        if len(data) > MAX_JSON:
            raise AtelierError(f"Fichier trop volumineux : {path}.")
        return json.loads(data.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AtelierError(f"Impossible de lire {path} : {exc}. Le fichier est conservé.") from exc


class Curriculum:
    def __init__(self, path: Path):
        self.courses = {}
        self.missions = {}
        self.paliers = {}
        self.order = {}
        data = read_json(path)
        try:
            if data["version"] != 1 or not isinstance(data["courses"], list) or not data["courses"]:
                raise ValueError("version 1 et parcours attendus")
            for course in data["courses"]:
                cid = course["id"]
                if not isinstance(cid, str) or not cid or cid in self.courses:
                    raise ValueError("identifiant de parcours invalide ou dupliqué")
                if not isinstance(course["title"], str) or not isinstance(course["steps"], list):
                    raise ValueError("titre ou missions du parcours invalides")
                self.courses[cid] = course
                self.order[cid] = []
                for mission in course["steps"]:
                    mid = mission["id"]
                    if not isinstance(mid, str) or mid in self.missions:
                        raise ValueError("identifiant de mission invalide ou dupliqué")
                    if not isinstance(mission["title"], str) or not isinstance(mission["paliers"], list):
                        raise ValueError("titre ou paliers de mission invalides")
                    self.missions[mid] = mission
                    for palier in mission["paliers"]:
                        pid = palier["id"]
                        if not isinstance(pid, str) or pid in self.paliers:
                            raise ValueError("identifiant de palier invalide ou dupliqué")
                        # Ces valeurs sont affichées ou parcourues ensuite.
                        for key in ("title", "goal", "check"):
                            if not isinstance(palier[key], str):
                                raise ValueError(f"{pid} : {key} doit être du texte")
                        for key in ("do", "explanation", "rules", "hints", "commands", "tests"):
                            if key in palier and (not isinstance(palier[key], list) or
                                                  any(not isinstance(item, str) for item in palier[key])):
                                raise ValueError(f"{pid} : {key} doit être une liste de textes")
                        if "example" in palier and (not isinstance(palier["example"], dict) or
                            any(not isinstance(palier["example"].get(key), str) for key in ("input", "output", "note"))):
                            raise ValueError(f"{pid} : exemple invalide")
                        if "blocks" in palier and (not isinstance(palier["blocks"], list) or any(
                            not isinstance(block, dict) or any(not isinstance(block.get(key), str)
                            for key in ("code", "kind", "title", "context")) for block in palier["blocks"])):
                            raise ValueError(f"{pid} : blocs invalides")
                        self.paliers[pid] = (cid, mission, palier)
                        self.order[cid].append(pid)
                if not self.order[cid]:
                    raise ValueError(f"aucun palier dans {cid}")
        except (KeyError, TypeError, ValueError) as exc:
            raise AtelierError(f"Énoncés invalides dans {path} : {exc}.") from exc

    def first_pending(self, cid: str, checked: list[str]):
        return next((pid for pid in self.order[cid] if pid not in checked), self.order[cid][-1])


def normalize_progression(value, curriculum: Curriculum):
    if not isinstance(value, dict) or value.get("version") != 1:
        raise AtelierError("Progression invalide : version 1 attendue. Le fichier est conservé.")
    selected = value.get("selectedCourse", "socle")
    if not isinstance(selected, str) or selected not in curriculum.courses:
        raise AtelierError("Parcours sélectionné inconnu dans la progression. Le fichier est conservé.")
    normalized = {"version": 1, "selectedCourse": selected}
    for key, maximum in (("paliers", 500), ("completed", 100)):
        entries = value.get(key, [])
        if (not isinstance(entries, list) or len(entries) > maximum or
                any(not isinstance(entry, str) or len(entry) > 100 for entry in entries)):
            raise AtelierError(f"Progression invalide : {key}. Le fichier est conservé.")
        # Garder aussi les identifiants inconnus : une mise à jour ne doit pas les effacer.
        normalized[key] = list(dict.fromkeys(entries))
    for key, maximum in (("notes", 20_000), ("mrLinks", 2048)):
        entries = value.get(key, {})
        if not isinstance(entries, dict) or any(
                not isinstance(k, str) or not isinstance(v, str) or len(v) > maximum
                for k, v in entries.items()):
            raise AtelierError(f"Progression invalide : {key}. Le fichier est conservé.")
        normalized[key] = entries.copy()
    for cid in curriculum.courses:
        normalized["notes"].setdefault(cid, "")
    return normalized


def local_port(root: Path, environ=None):
    """Même priorité que Compose : environnement, puis .env, puis 8080."""
    environ = os.environ if environ is None else environ
    port = environ.get("ATELIER_PORT")
    if port is None:
        env_path = root / ".env"
        try:
            lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
        except (OSError, UnicodeError) as exc:
            raise AtelierError(f"Impossible de lire {env_path} : {exc}.") from exc
        for line in lines:
            line = line.strip()
            if line.startswith("export "):
                line = line[7:].lstrip()
            if "=" not in line or line.startswith("#"):
                continue
            key, raw = line.split("=", 1)
            if key.strip() == "ATELIER_PORT":
                try:
                    parts = shlex.split(raw, comments=True)
                except ValueError as exc:
                    raise AtelierError("ATELIER_PORT mal formé dans .env.") from exc
                port = parts[0] if len(parts) == 1 else ""
    port = "8080" if port is None or port == "" else port
    if not isinstance(port, str) or not port.isascii() or not port.isdecimal() or not 1 <= int(port) <= 65535:
        raise AtelierError("ATELIER_PORT doit être un numéro entre 1 et 65535.")
    return int(port)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def fetch_local_progression(root: Path):
    url = f"http://127.0.0.1:{local_port(root)}/api/state"
    # Pas de proxy système ni redirection : uniquement l'API de ce poste.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(url, timeout=1) as response:
            raw = response.read(MAX_JSON + 1)
        if len(raw) > MAX_JSON:
            raise AtelierError("La progression locale reçue est trop volumineuse.")
        return json.loads(raw.decode("utf-8")), url
    except (urllib.error.URLError, TimeoutError, OSError):
        return None, "indisponible"
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise AtelierError("L'API locale renvoie une progression illisible ; aucune sauvegarde remplacée.") from exc


class StateStore:
    def __init__(self, path: Path, curriculum: Curriculum, root: Path, import_remote=True):
        self.path = path
        self.curriculum = curriculum
        self.notice = ""
        if path.exists():
            raw = read_json(path)
            self.data = normalize_progression(raw, curriculum)
            terminal = raw.get("terminal", {})
            if not isinstance(terminal, dict):
                raise AtelierError("État terminal invalide. Le fichier est conservé.")
            cursors = terminal.get("currentByCourse", {})
            levels = terminal.get("hintLevels", {})
            if (not isinstance(cursors, dict) or not isinstance(levels, dict) or
                    any(cid not in curriculum.courses or pid not in curriculum.order[cid]
                        for cid, pid in cursors.items()) or
                    any(pid not in curriculum.paliers or type(level) is not int or not 0 <= level <= 3
                        for pid, level in levels.items())):
                raise AtelierError("Position ou indices invalides dans la progression. Le fichier est conservé.")
            self.data["terminal"] = {**terminal, "currentByCourse": cursors.copy(), "hintLevels": levels.copy()}
        else:
            raw, source = fetch_local_progression(root) if import_remote else (None, "désactivé")
            if raw is None:
                raw = {"version": 1, "selectedCourse": next(iter(curriculum.courses))}
                self.notice = ("API locale indisponible : aucune ancienne progression importée. "
                               if import_remote else "Import de la progression Docker désactivé. ")
                self.notice += "Progression terminal locale créée sur le Mac."
            else:
                self.notice = "Progression existante importée une fois (cases, notes et liens MR)."
            self.data = normalize_progression(raw, curriculum)
            self.data["terminal"] = {"currentByCourse": {}, "hintLevels": {}, "importedFrom": source}
            self.save()

    def save(self):
        temporary = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.path.parent,
                                             prefix=f".{self.path.name}.", delete=False) as stream:
                temporary = Path(stream.name)
                json.dump(self.data, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        except OSError as exc:
            raise AtelierError(f"Impossible d'enregistrer {self.path} : {exc}.") from exc
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()

    @property
    def cid(self):
        return self.data["selectedCourse"]

    @property
    def pid(self):
        return self.data["terminal"]["currentByCourse"].get(
            self.cid, self.curriculum.first_pending(self.cid, self.data["paliers"]))

    def select(self, pid):
        if pid not in self.curriculum.paliers:
            raise AtelierError(f"Palier inconnu : {pid}.")
        cid = self.curriculum.paliers[pid][0]
        self.data["selectedCourse"] = cid
        self.data["terminal"]["currentByCourse"][cid] = pid
        self.save()

    def course(self, cid):
        if cid not in self.curriculum.courses:
            raise AtelierError(f"Parcours inconnu : {cid}. Choisis : {', '.join(self.curriculum.courses)}.")
        self.data["selectedCourse"] = cid
        self.select(self.pid)

    def move(self, delta):
        order = self.curriculum.order[self.cid]
        index = order.index(self.pid)
        target = index + delta
        if not 0 <= target < len(order):
            return False
        self.select(order[target])
        return True

    def mark(self, checked):
        current = self.pid
        entries = self.data["paliers"]
        if checked and current not in entries:
            entries.append(current)
        if not checked:
            self.data["paliers"] = [pid for pid in entries if pid != current]
        self.select(current)


def git_info(path: Path):
    if not path.is_dir():
        return "dossier à préparer"
    try:
        # rev-parse peut remonter au dépôt de l'application : vérifier la racine avant la branche.
        top = subprocess.run(["git", "-C", str(path), "rev-parse", "--show-toplevel"],
                             check=False, capture_output=True, text=True, timeout=2)
        if top.returncode or Path(top.stdout.strip()).resolve() != path.resolve():
            return "aucun dépôt Git propre à ce parcours"
        branch = subprocess.run(["git", "-C", str(path), "symbolic-ref", "--quiet", "--short", "HEAD"],
                                check=False, capture_output=True, text=True, timeout=2)
        if branch.returncode == 0:
            return branch.stdout.strip()
        return "HEAD détachée (aucune branche active)"
    except (OSError, subprocess.TimeoutExpired):
        return "Git indisponible"


def version(root: Path):
    try:
        from atelier_version import version_info
    except ImportError:
        pass
    else:
        info = version_info(root)
        return f"Version locale de Cyber Atelier : {info['label']} ({info['source']})"
    try:
        result = subprocess.run(["git", "-C", str(root), "rev-parse", "--short=12", "HEAD"],
                                capture_output=True, text=True, check=False, timeout=2)
        head = result.stdout.strip() if result.returncode == 0 else "indisponible"
    except (OSError, subprocess.TimeoutExpired):
        head = "indisponible"
    return f"Version locale de Cyber Atelier : {head}"


def docker_lab(root: Path, action: str):
    """L'action sur le labo est demandée explicitement, hors progression."""
    url = f"http://127.0.0.1:{local_port(root)}/api/lab"
    data = None if action == "statut" else json.dumps({"running": action == "demarrer"}).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(request, timeout=3) as response:
            raw = response.read(MAX_JSON + 1)
        if len(raw) > MAX_JSON:
            raise AtelierError("Réponse du laboratoire trop volumineuse.")
        result = json.loads(raw.decode("utf-8"))
        if not isinstance(result, dict) or type(result.get("running")) is not bool:
            raise AtelierError("Réponse du laboratoire invalide.")
        if action == "demarrer" and not result["running"]:
            raise AtelierError(f"Le laboratoire n'a pas démarré : {result.get('error') or 'vérifie le port du laboratoire' }.")
        return result
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise AtelierError("Laboratoire indisponible : vérifie que Docker et Cyber Atelier sont lancés.") from exc
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise AtelierError("Réponse du laboratoire illisible.") from exc


class Companion:
    def __init__(self, curriculum, state, root, workspace_root, out=None):
        self.curriculum = curriculum
        self.state = state
        self.root = root.resolve()
        self.workspace_root = workspace_root.resolve()
        self.out = out or sys.stdout

    def line(self, value=""):
        print(value, file=self.out)

    def paragraph(self, value):
        for line in str(value).splitlines():
            self.line(textwrap.fill(line, width=88, break_long_words=False, break_on_hyphens=False))

    def items(self, values, numbered=False):
        for index, value in enumerate(values, 1):
            prefix = f"{index}. " if numbered else "- "
            self.line(textwrap.fill(value, width=88, initial_indent=prefix,
                                    subsequent_indent=" " * len(prefix), break_long_words=False,
                                    break_on_hyphens=False))

    @property
    def current(self):
        return self.curriculum.paliers[self.state.pid]

    def context(self):
        cid, mission, palier = self.current
        workspace = self.workspace_root / cid
        self.line(f"Terminal : Mac · Dossier de l'exercice : {workspace}")
        self.line(f"Branche réelle de l'exercice : {git_info(workspace)}")
        self.line(f"Branche de la mission : {mission.get('branch', 'voir la mission')}")
        self.line(f"Application Cyber Atelier : {self.root} · branche {git_info(self.root)}")
        self.line(f"Pour travailler sur l'exercice : cd {shlex.quote(str(workspace))}")
        self.line("Les commandes ci-dessous sont à lancer toi-même dans le terminal du Mac.")
        self.line("Les appels docker compose se lancent depuis le dossier Cyber Atelier.")

    def blocks(self, palier, placement):
        for block in palier.get("blocks", []):
            if block.get("placement", "after_actions") != placement:
                continue
            kind = block.get("kind", "shell")
            self.line()
            self.line(f"{block.get('title', 'Extrait')} [{kind}]")
            self.paragraph(block.get("context", ""))
            if kind == "shell":
                code = block.get("code", "")
                cwd = self.root if "docker compose" in code else self.workspace_root / self.state.cid
                self.line(f"Dossier sur ton Mac : {cwd}")
            self.line(block.get("code", ""))

    def show(self):
        cid, mission, palier = self.current
        order = self.curriculum.order[cid]
        self.line(f"{self.curriculum.courses[cid]['title']} · {mission['title']}")
        self.line(f"Palier {order.index(self.state.pid) + 1}/{len(order)} · {palier['title']} · {palier.get('minutes', '?')} min")
        self.line(f"Identifiant : {self.state.pid} · {'fait' if self.state.pid in self.state.data['paliers'] else 'à faire'} (déclaratif)")
        self.context()
        self.line()
        self.paragraph(f"Objectif : {palier['goal']}")
        if palier.get("workspace"):
            self.paragraph(f"Fichiers concernés : {palier['workspace']}")
        self.items(palier.get("explanation", []))
        self.blocks(palier, "before_actions")
        if palier.get("example"):
            example = palier["example"]
            self.line()
            self.line("Exemple")
            self.line(f"Entrée : {example.get('input', '')}")
            self.line(f"Résultat attendu : {example.get('output', '')}")
            self.paragraph(example.get("note", ""))
        if palier.get("rules"):
            self.line()
            self.line("Règles à respecter")
            self.items(palier["rules"])
        self.line()
        self.line("Ce que tu fais")
        self.items(palier.get("do", []), numbered=True)
        self.blocks(palier, "after_actions")
        if not palier.get("blocks"):
            for command in palier.get("commands", []):
                self.line(command)
        if palier.get("tests"):
            self.line()
            self.line("Cas de test à écrire et vérifier")
            tests = {test["id"]: test for test in mission.get("tests", [])}
            for tid in palier["tests"]:
                test = tests.get(tid)
                if test:
                    self.paragraph(f"{tid} — {test['title']}")
                    self.paragraph(f"Entrée : {test['input']}")
                    self.paragraph(f"Attendu : {test['expected']}")
            self.line(f"Commande des tests : {mission.get('learning', {}).get('testCommand', 'voir la mission')}")
        # Afficher aussi les cas des démonstrations au palier qui les demande.
        last = mission["paliers"][-1]["id"] == self.state.pid
        text = " ".join([palier["title"], palier["goal"], *palier.get("do", [])])
        for demo in mission.get("demos", []):
            if last or "démonstr" in text.casefold() or re.search(rf"\b{re.escape(demo['id'])}\b", text):
                self.line()
                self.paragraph(f"Démonstration hors CI {demo['id']} — {demo['title']}")
                self.paragraph(f"Entrée : {demo['input']}")
                self.paragraph(f"Attendu : {demo['expected']}")
        if last:
            self.line()
            self.line("Avant de livrer la mission")
            self.items(mission.get("acceptance", []))
        self.line()
        self.paragraph(f"Pour valider toi-même ce palier : {palier['check']}")
        self.line("Une case ne vérifie ni tes tests, ni la CI, ni la fusion de ta MR.")
        level = self.state.data["terminal"]["hintLevels"].get(self.state.pid, 0)
        if level:
            self.hint(level, save=False)
        self.line()
        self.line("Commandes : suivant · precedent · fait · a-refaire · indice · parcours · statut · aide · quitter")

    def hint(self, level=None, save=True):
        palier = self.current[2]
        hints = palier.get("hints") or [palier.get("hint") or "Relis le contrat, puis vérifie un seul cas à la fois."]
        previous = self.state.data["terminal"]["hintLevels"].get(self.state.pid, 0)
        target = min(previous + 1, len(hints)) if level is None else min(level, len(hints))
        if save:
            self.state.data["terminal"]["hintLevels"][self.state.pid] = target
            self.state.select(self.state.pid)
        for index, hint in enumerate(hints[:target], 1):
            self.paragraph(f"Indice {index}/{len(hints)} : {hint}")
        if target == len(hints):
            self.line("Tous les indices de ce palier sont affichés.")

    def status(self):
        self.context()
        self.line(f"Progression locale : {self.state.path}")
        for cid, course in self.curriculum.courses.items():
            pids = self.curriculum.order[cid]
            done = sum(pid in self.state.data["paliers"] for pid in pids)
            missions = sum(step["id"] in self.state.data["completed"] for step in course["steps"])
            self.line(f"{cid} : {done}/{len(pids)} paliers cochés · {missions}/{len(course['steps'])} missions déclarées terminées")
        self.line("Le suivi terminal est enregistré sur le Mac ; l'état du site n'est pas écrasé.")

    def setup(self):
        course = self.curriculum.courses[self.state.cid]
        self.context()
        self.paragraph(course.get("description", ""))
        for setup in course.get("setup", []):
            self.line()
            self.line(setup["label"])
            self.paragraph(setup.get("note", ""))
            self.line(setup["command"])

    def execute(self, args):
        action = args.action
        if action in (None, "voir"):
            target = getattr(args, "palier", None)
            if target:
                if target.isdecimal():
                    index = int(target) - 1
                    order = self.curriculum.order[self.state.cid]
                    if not 0 <= index < len(order):
                        raise AtelierError(f"Choisis un numéro de palier de 1 à {len(order)}.")
                    target = order[index]
                self.state.select(target)
            else:
                self.state.select(self.state.pid)
            self.show()
        elif action in ("suivant", "precedent"):
            if not self.state.move(1 if action == "suivant" else -1):
                self.line("Tu es au dernier palier du parcours." if action == "suivant" else "Tu es au premier palier du parcours.")
            self.show()
        elif action == "parcours":
            if args.id:
                self.state.course(args.id)
                self.show()
            else:
                for cid, course in self.curriculum.courses.items():
                    self.line(f"{cid} — {course['title']}")
                self.line("Choisir : parcours <identifiant>, par exemple parcours socle")
        elif action in ("fait", "a-refaire"):
            self.state.mark(action == "fait")
            self.line(f"{self.state.pid} : {'fait' if action == 'fait' else 'à refaire'} (déclaratif).")
        elif action == "indice":
            self.hint(args.niveau)
        elif action == "statut":
            self.status()
        elif action == "contexte":
            self.context()
        elif action == "preparer":
            self.setup()
        elif action == "labo":
            result = docker_lab(self.root, args.operation)
            self.line(f"Laboratoire dans Docker : {'démarré' if result['running'] else 'arrêté'}.")
            self.line(f"Adresse pour les outils dans Docker : http://127.0.0.1:{result.get('port', 8000)}.")
            self.line("Pour les exercices Python du Mac, utilise python3 labs.py dans un second terminal.")
        elif action == "note":
            if args.texte is not None:
                if len(args.texte) > 20_000:
                    raise AtelierError("Une note ne peut pas dépasser 20 000 caractères.")
                self.state.data["notes"][self.state.cid] = args.texte
                self.state.save()
            self.line(self.state.data["notes"].get(self.state.cid, "") or "Aucune note pour ce parcours.")
        elif action == "mr":
            mid = self.current[1]["id"]
            if args.url is not None:
                if len(args.url) > 2048 or (args.url and not args.url.startswith(("https://", "http://"))):
                    raise AtelierError("Indique une URL HTTP(S) de MR, ou un texte vide pour retirer le lien.")
                self.state.data["mrLinks"][mid] = args.url
                self.state.save()
            self.line(f"{mid} : {self.state.data['mrLinks'].get(mid) or 'aucun lien MR enregistré'}")


def parser():
    result = argparse.ArgumentParser(description="Cyber Atelier dans le terminal du Mac : un palier à la fois.")
    result.add_argument("--state-file", type=Path, default=ROOT / "userdata" / "terminal.json",
                        help="fichier de progression local (défaut : userdata/terminal.json)")
    result.add_argument("--workspace-root", type=Path, default=ROOT / "workspaces",
                        help="dossier contenant les dépôts des parcours")
    result.add_argument("--no-import", action="store_true", help="ne pas importer l'API locale au premier lancement")
    sub = result.add_subparsers(dest="action")
    show = sub.add_parser("voir", help="afficher ou rejoindre un palier")
    show.add_argument("palier", nargs="?", help="identifiant stable ou numéro dans le parcours")
    course = sub.add_parser("parcours", help="lister ou choisir un parcours")
    course.add_argument("id", nargs="?")
    for name, help_text in (("suivant", "palier suivant sans le cocher"), ("precedent", "palier précédent"),
                            ("fait", "déclarer le palier courant fait"), ("a-refaire", "retirer sa case"),
                            ("statut", "afficher la progression"), ("contexte", "dossier et branche réels"),
                            ("preparer", "consignes de préparation"), ("version", "version locale de l'application")):
        sub.add_parser(name, help=help_text)
    hint = sub.add_parser("indice", help="révéler l'indice suivant")
    hint.add_argument("--niveau", type=int, choices=(1, 2, 3))
    note = sub.add_parser("note", help="lire ou remplacer la note du parcours")
    note.add_argument("texte", nargs="?")
    mr = sub.add_parser("mr", help="lire ou enregistrer le lien MR de la mission")
    mr.add_argument("url", nargs="?")
    lab = sub.add_parser("labo", help="piloter explicitement le laboratoire Docker, sans navigateur")
    lab.add_argument("operation", choices=("demarrer", "arreter", "statut"))
    return result


def interactive(companion: Companion, argument_parser):
    companion.execute(argparse.Namespace(action="voir", palier=None))
    while True:
        try:
            raw = input("\natelier> ").strip()
        except (EOFError, KeyboardInterrupt):
            companion.line("\nTa position est enregistrée. À bientôt.")
            return 0
        if raw in ("quitter", "q", "exit"):
            companion.line("Ta position est enregistrée. À bientôt.")
            return 0
        if not raw:
            continue
        if raw in ("aide", "help", "?"):
            argument_parser.print_help(file=companion.out)
            companion.line('Exemples : voir 6 · parcours socle · indice · note "mon idée" · mr "https://…"')
            continue
        try:
            args = argument_parser.parse_args(shlex.split(raw))
            if args.action == "version":
                companion.line(version(companion.root))
            else:
                companion.execute(args)
        except SystemExit:
            continue
        except (AtelierError, ValueError) as exc:
            companion.line(f"Erreur : {exc}")


def main(argv=None):
    argument_parser = parser()
    args = argument_parser.parse_args(argv)
    if args.action == "version":
        print(version(ROOT))
        return 0
    try:
        curriculum = Curriculum(ROOT / "content" / "courses.json")
        state = StateStore(args.state_file.resolve(), curriculum, ROOT, not args.no_import)
        companion = Companion(curriculum, state, ROOT, args.workspace_root)
        if state.notice:
            companion.line(state.notice)
        if args.action is None and sys.stdin.isatty():
            return interactive(companion, argument_parser)
        companion.execute(args)
        return 0
    except (AtelierError, OSError) as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 1
