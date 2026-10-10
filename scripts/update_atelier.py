#!/usr/bin/env python3
"""Met à jour l'application après sauvegarde, sans modifier les exercices."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime
import fcntl
import gzip
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import uuid


ROOT = Path(__file__).resolve().parents[1]
BUILD_FILE = ".atelier-build.json"
COMPOSE = ["docker", "compose"]


class UpdateError(Exception):
    """Un prérequis ou une opération a échoué sans restauration automatique."""


class CommandRunner:
    def __init__(self, root: Path):
        self.root = root

    def run(self, args, *, check=True, stdout=None, capture=True):
        try:
            result = subprocess.run(
                args, cwd=self.root, check=False,
                text=stdout is None,
                stdout=stdout if stdout is not None else (subprocess.PIPE if capture else None),
                stderr=subprocess.PIPE if capture else None,
            )
        except OSError as error:
            raise UpdateError(f"Impossible de lancer {args[0]}. Vérifie son installation.") from error
        if check and result.returncode:
            # Les erreurs Git peuvent contenir une URL avec des identifiants.
            operation = " ".join(args[:3])
            raise UpdateError(f"La commande « {operation} » a échoué (code {result.returncode}).")
        return result


class Updater:
    def __init__(self, root: Path = ROOT, runner=None, output=print):
        self.root = Path(root).resolve()
        self.runner = runner or CommandRunner(self.root)
        self.output = output
        self.backup_path = None

    def git(self, *args, check=True):
        return self.runner.run(["git", *args], check=check)

    def compose(self, *args, **kwargs):
        return self.runner.run(COMPOSE + list(args), **kwargs)

    def clean_application(self):
        if self.git("status", "--porcelain=v1", "--untracked-files=no").stdout.strip():
            raise UpdateError(
                "L'application contient des modifications suivies par Git. "
                "Enregistre-les dans un commit avant la mise à jour. "
                "Cela ne concerne pas ton code dans workspaces/."
            )

    def check_git(self):
        top = Path(self.git("rev-parse", "--show-toplevel").stdout.strip()).resolve()
        if top != self.root:
            raise UpdateError("Cet outil doit être dans le dépôt Cyber Atelier, pas dans un dépôt d'exercice.")
        self.clean_application()
        remote = self.git("config", "--get", "branch.main.remote", check=False)
        merge = self.git("config", "--get", "branch.main.merge", check=False)
        if remote.returncode or merge.returncode or remote.stdout.strip() != "origin" or merge.stdout.strip() != "refs/heads/main":
            raise UpdateError("La branche main de l'application doit suivre origin/main. Aucune branche n'a été changée.")
        self.git("rev-parse", "--verify", "refs/heads/main")
        self.output("Recherche des mises à jour de l'application sur GitHub…")
        self.git("fetch", "--no-tags", "origin", "refs/heads/main:refs/remotes/origin/main")
        ancestry = self.git("merge-base", "--is-ancestor", "refs/heads/main", "refs/remotes/origin/main", check=False)
        if ancestry.returncode:
            raise UpdateError(
                "main contient des commits locaux absents de GitHub, ou son historique a divergé. "
                "Mise à jour refusée : aucun reset ni rebase automatique."
            )
        # switch main passe d'abord par l'arbre local, avant la fusion du commit distant.
        incoming = set()
        for reference in ("refs/heads/main", "refs/remotes/origin/main"):
            incoming.update(self.git("ls-tree", "-r", "--name-only", "-z", reference).stdout.split("\0"))
        protected = ("workspaces", "data", "userdata", "backups")
        if any(path == reserved or path.startswith(reserved + "/") for path in incoming for reserved in protected):
            raise UpdateError("Une version de main suit des dossiers de données personnels, ou remplace leur racine. Mise à jour refusée.")
        ignored = self.git("ls-files", "--others", "--ignored", "--exclude-standard", "-z", "--", ".env", "compose.override.yaml", "drafts/").stdout.split("\0")
        if any(path and path in incoming for path in ignored):
            raise UpdateError("La version distante écraserait un fichier local ignoré (.env ou brouillon). Mise à jour refusée.")
        current = self.git("rev-parse", "refs/heads/main").stdout.strip()
        target = self.git("rev-parse", "refs/remotes/origin/main").stdout.strip()
        self.output(f"Application : main {current[:7]} → origin/main {target[:7]}.")
        return target

    def configuration(self):
        try:
            config = json.loads(self.compose("config", "--format", "json").stdout)
            service = config["services"]["atelier"]
            mounts = service["volumes"]
            selected = {item["target"]: item for item in mounts if item["target"] in ("/workspaces", "/data")}
            if len(selected) != 2:
                raise KeyError("montages manquants")
            return config
        except (ValueError, TypeError, KeyError) as error:
            raise UpdateError("La configuration Docker doit conserver les montages /workspaces et /data.") from error

    @staticmethod
    def storage_signature(config):
        return json.dumps({
            "name": config.get("name"),
            "mounts": config["services"]["atelier"]["volumes"],
            "volumes": config.get("volumes", {}),
        }, sort_keys=True)

    def check_docker(self, config):
        help_text = self.compose("up", "--help").stdout
        if "--wait" not in help_text or "--wait-timeout" not in help_text:
            raise UpdateError("Docker Compose doit prendre en charge --wait et --wait-timeout. Mets Docker Desktop à jour.")
        for mount in config["services"]["atelier"]["volumes"]:
            if mount.get("target") not in ("/workspaces", "/data"):
                continue
            if mount.get("type") == "bind":
                if not Path(mount["source"]).is_dir():
                    raise UpdateError(f"Le dossier monté sur {mount['target']} n'existe pas. Aucune donnée n'a été créée.")
            elif mount.get("type") == "volume":
                source = mount["source"]
                name = config.get("volumes", {}).get(source, {}).get("name", source)
                self.runner.run(["docker", "volume", "inspect", name])
            else:
                raise UpdateError(f"Le montage {mount['target']} ne permet pas une sauvegarde persistante.")
        containers = self.compose("ps", "--all", "--quiet", "atelier").stdout.split()
        if len(containers) > 1:
            raise UpdateError("Plusieurs conteneurs atelier existent : vérifie Docker Compose avant la mise à jour.")
        if not containers:
            return False
        running = self.runner.run(["docker", "inspect", "--format", "{{.State.Running}}", containers[0]])
        return running.stdout.strip() == "true"

    def local_state(self):
        state = self.root / "userdata" / "terminal.json"
        if state.is_symlink() or (state.exists() and not state.is_file()):
            raise UpdateError("userdata/terminal.json doit être un fichier normal pour être sauvegardé.")
        return state if state.exists() else None

    def add_terminal_snapshot(self, archive, state):
        # Le CLI remplace atomiquement terminal.json : stat + open pourrait mélanger
        # l'ancienne taille et le nouveau contenu. Lire un instantané sous son verrou.
        lock_path = state.parent / f".{state.name}.lock"
        descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        with os.fdopen(descriptor, "a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_SH | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise UpdateError("Le compagnon enregistre ta progression. Relance la mise à jour dans un instant.") from error
            data = state.read_bytes()
        entry = tarfile.TarInfo("userdata/terminal.json")
        entry.size = len(data)
        entry.mode = 0o600
        archive.addfile(entry, io.BytesIO(data))

    @contextmanager
    def lock(self):
        directory = self.root / "backups"
        if directory.is_symlink():
            raise UpdateError("backups/ doit être un dossier local normal.")
        directory.mkdir(mode=0o700, exist_ok=True)
        descriptor = os.open(directory / ".update.lock", os.O_CREAT | os.O_RDWR, 0o600)
        with os.fdopen(descriptor, "w") as handle:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise UpdateError("Une mise à jour est déjà en cours dans ce dépôt.") from error
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)

    def backup(self, running):
        state = self.local_state()
        directory = self.root / "backups"
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        destination = directory / f"cyberatelier-{timestamp}-{uuid.uuid4().hex[:8]}.tar.gz"
        tar_fd, tar_name = tempfile.mkstemp(prefix=".volumes-", suffix=".tar", dir=directory)
        gzip_name = None
        try:
            self.output("Sauvegarde de ton code, des dépôts d'exercice et de ta progression…")
            with os.fdopen(tar_fd, "wb") as archive:
                if running:
                    self.compose("exec", "-T", "atelier", "tar", "-cf", "-", "-C", "/", "workspaces", "data", stdout=archive)
                else:
                    # L'image déjà installée et les montages Compose existants sont réutilisés.
                    self.compose("run", "--rm", "--no-deps", "--no-build", "--pull", "never", "-T", "--entrypoint", "tar", "atelier", "-cf", "-", "-C", "/", "workspaces", "data", stdout=archive)
            with tarfile.open(tar_name, "r") as archive:
                directories = {entry.name.rstrip("/") for entry in archive if entry.isdir()}
                if not {"workspaces", "data"}.issubset(directories):
                    raise UpdateError("La sauvegarde Docker est incomplète : workspaces ou data manque. Mise à jour arrêtée.")
            with tarfile.open(tar_name, "a") as archive:
                if state:
                    self.add_terminal_snapshot(archive, state)
            gzip_fd, gzip_name = tempfile.mkstemp(prefix=".backup-", suffix=".tar.gz", dir=directory)
            with os.fdopen(gzip_fd, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb") as zipped, open(tar_name, "rb") as source:
                shutil.copyfileobj(source, zipped)
            os.replace(gzip_name, destination)
            self.backup_path = destination
            self.output(f"Sauvegarde terminée : {destination}")
            return destination
        except (OSError, tarfile.TarError) as error:
            raise UpdateError("La sauvegarde n'a pas pu être terminée. La mise à jour est arrêtée.") from error
        finally:
            Path(tar_name).unlink(missing_ok=True)
            if gzip_name:
                Path(gzip_name).unlink(missing_ok=True)

    def write_build_version(self, commit):
        if len(commit) not in (40, 64) or any(character not in "0123456789abcdef" for character in commit):
            raise UpdateError("Git n'a pas renvoyé une version valide. Construction arrêtée.")
        descriptor, name = tempfile.mkstemp(prefix=".atelier-build-", dir=self.root)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump({"version": 1, "commit": commit}, handle)
                handle.write("\n")
            os.replace(name, self.root / BUILD_FILE)
        finally:
            Path(name).unlink(missing_ok=True)

    def installed_version(self, commit):
        code = "import json; from atelier_version import version_info; print(json.dumps(version_info()))"
        result = self.compose("exec", "-T", "atelier", "python", "-c", code)
        try:
            version = json.loads(result.stdout)
            if version.get("commit") != commit:
                raise ValueError("version différente")
        except (ValueError, AttributeError) as error:
            raise UpdateError("Docker répond, mais la version installée ne correspond pas à la version construite.") from error
        self.output(f"Cyber Atelier est à jour. Version installée : {commit[:7]}.")
        self.output("Ton code, tes branches d'exercice et ta progression sont conservés. Tu peux reprendre ton palier.")

    def execute(self, check=False):
        target = self.check_git()
        config = self.configuration()
        running = self.check_docker(config)
        self.local_state()
        if check:
            self.output(f"Vérification terminée : version proposée {target[:7]}. Aucune branche changée, aucun conteneur redémarré.")
            return
        with self.lock():
            self.clean_application()
            self.backup(running)
            self.clean_application()
            self.output("Mise à jour du dépôt de l'application sur main…")
            self.git("switch", "main")
            # Réutilise exactement le commit vérifié avant la sauvegarde, sans second téléchargement.
            self.git("merge", "--ff-only", target)
            if self.storage_signature(self.configuration()) != self.storage_signature(config):
                raise UpdateError("La mise à jour change les montages Docker. Construction refusée ; tes volumes et l'ancien conteneur sont conservés.")
            commit = self.git("rev-parse", "HEAD").stdout.strip()
            self.write_build_version(commit)
            self.output("Construction de la nouvelle image. L'ancien conteneur reste disponible pendant cette étape…")
            self.compose("build", "atelier", capture=False)
            self.output("Redémarrage de Cyber Atelier et attente de son état de santé…")
            self.compose("up", "--detach", "--no-build", "--wait", "--wait-timeout", "120", "atelier", capture=False)
            self.installed_version(commit)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Met à jour Cyber Atelier après sauvegarde de tes exercices et de ta progression.")
    parser.add_argument("--check", action="store_true", help="vérifie GitHub et Docker, sans changer de branche, sauvegarder ni redémarrer")
    args = parser.parse_args(argv)
    updater = Updater()
    try:
        updater.execute(check=args.check)
    except (UpdateError, OSError) as error:
        print(f"Mise à jour arrêtée : {error}", file=sys.stderr)
        if updater.backup_path:
            print(f"Sauvegarde disponible : {updater.backup_path}. Aucune restauration automatique n'a été faite.", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Mise à jour interrompue. Aucune restauration automatique n'a été faite.", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
