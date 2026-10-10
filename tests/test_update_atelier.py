import copy
from contextlib import contextmanager
import fcntl
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import atelier_version
from scripts.update_atelier import ROOT, CommandRunner, Updater, UpdateError


OLD = "a" * 40
NEW = "b" * 40


class FakeCommands:
    """Git et Docker simulés : aucune mutation de vrais dépôts ou conteneurs."""

    def __init__(self, root):
        self.root = root
        self.branch = "feat/interface"
        self.head = OLD
        self.dirty = False
        self.remote = "origin"
        self.ahead = False
        self.running = True
        self.fail = None
        self.ignored = []
        self.incoming = ["server.py", "mettre-a-jour"]
        self.migrate = False
        self.incomplete_backup = False
        self.image_commit = NEW
        self.events = []
        self.config = {
            "name": "cyberatelier",
            "services": {"atelier": {"volumes": [
                {"type": "bind", "source": str(root / "workspaces"), "target": "/workspaces"},
                {"type": "volume", "source": "data", "target": "/data"},
                {"type": "volume", "source": "home", "target": "/home/atelier"},
            ]}},
            "volumes": {"data": {"name": "cyberatelier_data"}, "home": {"name": "cyberatelier_home"}},
        }

    def run(self, args, *, check=True, stdout=None, capture=True):
        self.events.append((list(args), bool(list((self.root / "backups").glob("*.tar.gz")))))
        command = tuple(args[:3])
        if self.fail == command:
            raise UpdateError("échec simulé")
        value, code = "", 0
        if args[0] == "git":
            if args[1:] == ["rev-parse", "--show-toplevel"]:
                value = str(self.root)
            elif args[1] == "status":
                value = " M server.py\n" if self.dirty else ""
            elif args[1] == "config":
                value = self.remote if args[-1].endswith("remote") else "refs/heads/main"
            elif args[1] == "merge-base":
                code = int(self.ahead)
            elif args[1] == "ls-tree":
                value = "\0".join(self.incoming) + "\0"
            elif args[1] == "ls-files":
                value = "\0".join(self.ignored) + "\0"
            elif args[1] == "rev-parse":
                value = NEW if args[-1] == "refs/remotes/origin/main" else self.head
            elif args[1] == "switch":
                self.branch = args[2]
            elif args[1] == "merge":
                self.head = args[-1]
            elif args[1] != "fetch":
                raise AssertionError(f"Commande Git imprévue : {args}")
        elif args[:2] == ["docker", "compose"]:
            if args[2] == "config":
                config = copy.deepcopy(self.config)
                if self.migrate and self.head == NEW:
                    config["services"]["atelier"]["volumes"][1]["source"] = "new_data"
                value = json.dumps(config)
            elif args[2:4] == ["up", "--help"]:
                value = "--wait --wait-timeout"
            elif args[2] == "ps":
                value = "atelier-container"
            elif "tar" in args:
                stream = io.BytesIO()
                with tarfile.open(fileobj=stream, mode="w") as archive:
                    archive.add(self.root / "workspaces", arcname="workspaces")
                    if not self.incomplete_backup:
                        archive.add(self.root / "data", arcname="data")
                stdout.write(stream.getvalue())
            elif args[2] == "exec":
                value = json.dumps({"commit": self.image_commit, "label": self.image_commit[:7], "source": "image"})
            elif args[2] not in ("build", "up"):
                raise AssertionError(f"Commande Compose imprévue : {args}")
        elif args[:2] == ["docker", "inspect"]:
            value = "true" if self.running else "false"
        elif args[:3] != ["docker", "volume", "inspect"]:
            raise AssertionError(f"Commande imprévue : {args}")
        if check and code:
            raise UpdateError("échec simulé")
        return subprocess.CompletedProcess(args, code, value, "")


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.exercise = self.root / "workspaces" / "socle"
        (self.exercise / ".git").mkdir(parents=True)
        (self.exercise / ".git" / "HEAD").write_text("ref: refs/heads/feat/bases\n")
        (self.exercise / "journal.py").write_text("# mon travail en cours\n")
        (self.root / "data").mkdir()
        (self.root / "data" / "state.json").write_text('{"checked":{"socle-mr1":true}}\n')
        (self.root / "userdata").mkdir()
        (self.root / "userdata" / "terminal.json").write_text('{"version":1,"terminal":{"currentByCourse":{"socle":"socle-mr1-p6"}}}\n')
        (self.root / ".env").write_text("ATELIER_PORT=8081\n")
        (self.root / "drafts").mkdir()
        (self.root / "drafts" / "brouillon.txt").write_text("une note personnelle")
        self.commands = FakeCommands(self.root)
        self.messages = []
        self.updater = Updater(self.root, self.commands, self.messages.append)

    @contextmanager
    def exercise_cwd(self):
        before = Path.cwd()
        os.chdir(self.exercise)
        try:
            yield
        finally:
            os.chdir(before)

    def calls(self, prefix):
        return [args for args, _ in self.commands.events if args[:len(prefix)] == prefix]

    def assert_learner_unchanged(self):
        self.assertEqual((self.exercise / ".git" / "HEAD").read_text(), "ref: refs/heads/feat/bases\n")
        self.assertEqual((self.exercise / "journal.py").read_text(), "# mon travail en cours\n")
        self.assertEqual((self.root / "data" / "state.json").read_text(), '{"checked":{"socle-mr1":true}}\n')
        self.assertEqual((self.root / ".env").read_text(), "ATELIER_PORT=8081\n")
        self.assertEqual((self.root / "drafts" / "brouillon.txt").read_text(), "une note personnelle")

    def test_update_from_exercise_cwd_backs_up_before_checkout_and_preserves_learner(self):
        with self.exercise_cwd():
            self.updater.execute()
        self.assertEqual(self.commands.branch, "main")
        self.assertEqual(self.commands.head, NEW)
        for args, backup_exists in self.commands.events:
            if args[:2] in (["git", "switch"], ["git", "merge"]) or args[:3] == ["docker", "compose", "build"]:
                self.assertTrue(backup_exists, args)
        self.assert_learner_unchanged()
        self.assertEqual(stat.S_IMODE(self.updater.backup_path.stat().st_mode), 0o600)
        with tarfile.open(self.updater.backup_path, "r:gz") as archive:
            for name in ("workspaces/socle/.git/HEAD", "workspaces/socle/journal.py", "data/state.json", "userdata/terminal.json"):
                self.assertEqual(archive.extractfile(name).read(), (self.root / name).read_bytes())
            self.assertFalse(any(entry.name.startswith("home/") for entry in archive))
        self.assertEqual(json.loads((self.root / ".atelier-build.json").read_text()), {"version": 1, "commit": NEW})
        mutations = self.calls(["docker", "compose"])
        build_index = next(i for i, args in enumerate(mutations) if args[2] == "build")
        up_index = next(i for i, args in enumerate(mutations) if args[2] == "up" and "--help" not in args)
        self.assertLess(build_index, up_index)
        self.assertIn("--wait", mutations[up_index])
        self.assertIn("--no-build", mutations[up_index])
        self.assertTrue(any(NEW[:7] in message and "installée" in message for message in self.messages))

    def test_stopped_container_backup_reuses_image_without_build_or_pull(self):
        self.commands.running = False
        self.updater.execute()
        command = self.calls(["docker", "compose", "run"])[0]
        self.assertIn("--no-build", command)
        self.assertEqual(command[command.index("--pull") + 1], "never")
        self.assertNotIn("/home/atelier", command)
        self.assert_learner_unchanged()

    def test_check_fetches_but_does_not_backup_change_branch_or_restart(self):
        self.updater.execute(check=True)
        self.assertTrue(self.calls(["git", "fetch"]))
        self.assertFalse(self.calls(["git", "switch"]))
        self.assertFalse(self.calls(["docker", "compose", "build"]))
        self.assertFalse((self.root / "backups").exists())
        self.assert_learner_unchanged()

    def test_dirty_application_is_refused_before_fetch(self):
        self.commands.dirty = True
        with self.assertRaisesRegex(UpdateError, "modifications suivies"):
            self.updater.execute()
        self.assertFalse(self.calls(["git", "fetch"]))
        self.assertEqual(self.commands.branch, "feat/interface")

    def test_main_must_track_origin_main(self):
        self.commands.remote = "other"
        with self.assertRaisesRegex(UpdateError, "suivre origin/main"):
            self.updater.execute()
        self.assertFalse(self.calls(["git", "fetch"]))

    def test_local_commits_or_divergence_refused_after_fetch_without_checkout(self):
        self.commands.ahead = True
        with self.assertRaisesRegex(UpdateError, "commits locaux"):
            self.updater.execute()
        self.assertFalse(self.calls(["git", "switch"]))
        self.assertEqual(self.commands.head, OLD)

    def test_network_failure_does_not_switch_or_backup(self):
        self.commands.fail = ("git", "fetch", "--no-tags")
        with self.assertRaises(UpdateError):
            self.updater.execute()
        self.assertFalse(self.calls(["git", "switch"]))
        self.assertFalse((self.root / "backups").exists())
        self.assert_learner_unchanged()

    def test_failed_backup_never_switches_or_builds_and_removes_partial_files(self):
        self.commands.fail = ("docker", "compose", "exec")
        with self.assertRaises(UpdateError):
            self.updater.execute()
        self.assertFalse(self.calls(["git", "switch"]))
        self.assertFalse(self.calls(["docker", "compose", "build"]))
        self.assertEqual(list((self.root / "backups").glob("*.tar*")), [])
        self.assertEqual(list((self.root / "backups").glob(".volumes-*")), [])

    def test_incomplete_backup_refuses_update(self):
        self.commands.incomplete_backup = True
        with self.assertRaisesRegex(UpdateError, "incomplète"):
            self.updater.execute()
        self.assertFalse(self.calls(["git", "switch"]))

    def test_build_failure_does_not_restart_running_container(self):
        self.commands.fail = ("docker", "compose", "build")
        with self.assertRaises(UpdateError):
            self.updater.execute()
        self.assertTrue(self.updater.backup_path.is_file())
        self.assertFalse(any("--detach" in args for args in self.calls(["docker", "compose", "up"])))
        self.assert_learner_unchanged()

    def test_mount_migration_is_refused_before_build(self):
        self.commands.migrate = True
        with self.assertRaisesRegex(UpdateError, "montages Docker"):
            self.updater.execute()
        self.assertFalse(self.calls(["docker", "compose", "build"]))
        self.assertTrue(self.updater.backup_path.is_file())
        self.assert_learner_unchanged()

    def test_update_refuses_ignored_environment_file_overwrite(self):
        self.commands.ignored = [".env"]
        self.commands.incoming.append(".env")
        with self.assertRaisesRegex(UpdateError, "écraserait"):
            self.updater.execute()
        self.assertFalse(self.calls(["git", "switch"]))
        self.assert_learner_unchanged()

    def test_failed_health_wait_preserves_backup_and_does_not_restore(self):
        self.commands.fail = ("docker", "compose", "up")
        # --help is a read, so fail only the restart.
        original = self.commands.run
        def run(args, **kwargs):
            if "--detach" in args:
                raise UpdateError("santé indisponible")
            if args[:4] == ["docker", "compose", "up", "--help"]:
                self.commands.fail = None
            return original(args, **kwargs)
        self.commands.run = run
        with self.assertRaisesRegex(UpdateError, "santé"):
            self.updater.execute()
        self.assertTrue(self.updater.backup_path.is_file())
        self.assert_learner_unchanged()
        self.assertFalse(any("-x" in argument for args, _ in self.commands.events for argument in args))

    def test_version_mismatch_is_not_reported_as_success(self):
        self.commands.image_commit = OLD
        with self.assertRaisesRegex(UpdateError, "version installée"):
            self.updater.execute()
        self.assertFalse(any("Cyber Atelier est à jour" in message for message in self.messages))

    def test_wrapper_locates_script_when_called_from_exercise(self):
        fake_bin = self.root / "bin"
        fake_bin.mkdir()
        python = fake_bin / "python3"
        python.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n')
        python.chmod(0o755)
        wrapper = ROOT / "mettre-a-jour"
        result = subprocess.run([str(wrapper), "--check"], cwd=self.exercise,
                                env={**os.environ, "PATH": str(fake_bin) + os.pathsep + os.environ["PATH"]},
                                capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout.splitlines(), [str(ROOT / "scripts" / "update_atelier.py"), "--check"])

    def test_commands_always_run_in_application_root(self):
        result = subprocess.CompletedProcess([], 0, "", "")
        with self.exercise_cwd(), patch("scripts.update_atelier.subprocess.run", return_value=result) as command:
            CommandRunner(self.root).run(["git", "status"])
        self.assertEqual(command.call_args.kwargs["cwd"], self.root)

    def test_concurrent_update_is_refused_without_checkout(self):
        with self.updater.lock():
            with self.assertRaisesRegex(UpdateError, "déjà en cours"):
                Updater(self.root, self.commands, self.messages.append).execute()
        self.assertFalse(self.calls(["git", "switch"]))
        self.assertFalse(self.calls(["docker", "compose", "build"]))

    def test_terminal_backup_never_uses_stat_then_open_during_atomic_replace(self):
        state = self.root / "userdata" / "terminal.json"
        original = state.read_bytes()
        larger = json.dumps({"version": 1, "notes": {"socle": "x" * 2048}}).encode()
        gettarinfo = tarfile.TarFile.gettarinfo
        def race(archive, name=None, arcname=None, fileobj=None):
            entry = gettarinfo(archive, name, arcname, fileobj)
            if name and Path(name).resolve() == state.resolve():
                replacement = state.with_suffix(".new")
                replacement.write_bytes(larger)
                os.replace(replacement, state)
            return entry
        with patch.object(tarfile.TarFile, "gettarinfo", race):
            self.updater.execute()
        with tarfile.open(self.updater.backup_path, "r:gz") as archive:
            data = archive.extractfile("userdata/terminal.json").read()
            self.assertEqual(data, original)
            self.assertEqual(json.loads(data), json.loads(original))
            self.assertEqual(archive.getmember("userdata/terminal.json").mode, 0o600)

    def test_terminal_backup_keeps_single_read_even_if_file_is_replaced_after_read(self):
        state = self.root / "userdata" / "terminal.json"
        original = state.read_bytes()
        larger = json.dumps({"version": 1, "notes": {"socle": "x" * 2048}}).encode()
        read_bytes = Path.read_bytes
        replacements = []
        def race(path):
            data = read_bytes(path)
            if path.resolve() == state.resolve():
                replacement = state.with_suffix(".new")
                replacement.write_bytes(larger)
                os.replace(replacement, state)
                replacements.append(True)
            return data
        with patch.object(Path, "read_bytes", race):
            self.updater.execute()
        self.assertEqual(replacements, [True])
        with tarfile.open(self.updater.backup_path, "r:gz") as archive:
            data = archive.extractfile("userdata/terminal.json").read()
            self.assertEqual(data, original)
            self.assertEqual(json.loads(data), json.loads(original))
        self.assertEqual(state.read_bytes(), larger)

    def test_terminal_writer_lock_refuses_backup_instead_of_reading_during_save(self):
        lock_path = self.root / "userdata" / ".terminal.json.lock"
        with lock_path.open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaisesRegex(UpdateError, "compagnon enregistre"):
                self.updater.execute()
        self.assertFalse(self.calls(["git", "switch"]))
        self.assertFalse(list((self.root / "backups").glob("*.tar.gz")))


class RealGitProtectionTests(unittest.TestCase):
    """Dépôts jetables uniquement ; Docker n'est jamais appelé."""

    def git(self, root, *args):
        return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout.strip()

    def prepare(self, directory):
        root = Path(directory) / "app"
        root.mkdir()
        self.git(root, "init", "-b", "main")
        self.git(root, "config", "user.name", "Test local")
        self.git(root, "config", "user.email", "test@example.invalid")
        (root / ".gitignore").write_text("workspaces/\ndata/\nuserdata/\nbackups/\n")
        (root / "README.md").write_text("application\n")
        self.git(root, "add", ".gitignore", "README.md")
        self.git(root, "commit", "-m", "base")
        original = self.git(root, "rev-parse", "HEAD")
        bare = Path(directory) / "origin.git"
        self.git(root, "clone", "--bare", str(root), str(bare))
        self.git(root, "remote", "add", "origin", str(bare))
        self.git(root, "fetch", "origin")
        self.git(root, "branch", "--set-upstream-to=origin/main", "main")
        incoming = Path(directory) / "incoming"
        self.git(root, "clone", str(bare), str(incoming))
        self.git(incoming, "config", "user.name", "Test local")
        self.git(incoming, "config", "user.email", "test@example.invalid")
        exercise = root / "workspaces" / "socle"
        exercise.mkdir(parents=True)
        self.git(exercise, "init", "-b", "feat/bases")
        (exercise / "code.py").write_text("# travail personnel\n")
        return root, incoming, original

    def updater(self, root):
        class GitOnlyRunner(CommandRunner):
            def run(self, args, **kwargs):
                if args[0] != "git":
                    raise AssertionError(f"Docker ne doit jamais être lancé : {args}")
                return super().run(args, **kwargs)
        return Updater(root, GitOnlyRunner(root), lambda message: None)

    def test_incoming_exact_personal_roots_are_refused_before_checkout(self):
        for reserved in ("workspaces", "data", "userdata", "backups"):
            for symlink in (False, True):
                with self.subTest(reserved=reserved, symlink=symlink), tempfile.TemporaryDirectory() as directory:
                    root, incoming, original = self.prepare(directory)
                    path = incoming / reserved
                    if symlink:
                        path.symlink_to("ailleurs")
                    else:
                        path.write_text("fichier qui remplacerait un dossier")
                    self.git(incoming, "add", "-f", reserved)
                    self.git(incoming, "commit", "-m", "racine à protéger")
                    self.git(incoming, "push", "origin", "main")
                    with self.assertRaisesRegex(UpdateError, "remplace leur racine"):
                        self.updater(root).execute()
                    self.assertEqual(self.git(root, "rev-parse", "HEAD"), original)
                    self.assertEqual((root / "workspaces" / "socle" / "code.py").read_text(), "# travail personnel\n")
                    self.assertEqual(self.git(root / "workspaces" / "socle", "symbolic-ref", "--short", "HEAD"), "feat/bases")

    def test_local_main_personal_root_is_refused_even_if_remote_has_removed_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root, incoming, original = self.prepare(directory)
            self.git(root, "switch", "-c", "feat/application")
            (incoming / "workspaces").symlink_to("ailleurs")
            self.git(incoming, "add", "-f", "workspaces")
            self.git(incoming, "commit", "-m", "ancienne main risquée")
            self.git(incoming, "push", "origin", "main")
            self.git(root, "fetch", "origin")
            self.git(root, "branch", "-f", "main", "origin/main")
            self.git(incoming, "rm", "workspaces")
            self.git(incoming, "commit", "-m", "nouvelle main sans racine risquée")
            self.git(incoming, "push", "origin", "main")
            with self.assertRaisesRegex(UpdateError, "remplace leur racine"):
                self.updater(root).execute()
            self.assertEqual(self.git(root, "symbolic-ref", "--short", "HEAD"), "feat/application")
            self.assertEqual(self.git(root, "rev-parse", "HEAD"), original)
            self.assertEqual((root / "workspaces" / "socle" / "code.py").read_text(), "# travail personnel\n")


class VersionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_git_version_has_priority_over_embedded_image_version(self):
        (self.root / ".git").mkdir()
        (self.root / atelier_version.BUILD_FILE).write_text(json.dumps({"version": 1, "commit": OLD}))
        result = subprocess.CompletedProcess([], 0, NEW + "\n", "")
        with patch("atelier_version.subprocess.run", return_value=result) as command:
            self.assertEqual(atelier_version.version_info(self.root), {"commit": NEW, "label": NEW[:7], "source": "git"})
        self.assertEqual(command.call_args.args[0][2], str(self.root.resolve()))

    def test_container_without_git_uses_build_commit(self):
        (self.root / atelier_version.BUILD_FILE).write_text(json.dumps({"version": 1, "commit": NEW}))
        with patch("atelier_version.subprocess.run") as command:
            self.assertEqual(atelier_version.version_info(self.root), {"commit": NEW, "label": NEW[:7], "source": "image"})
        command.assert_not_called()

    def test_default_root_is_module_location_not_current_directory(self):
        (self.root / atelier_version.BUILD_FILE).write_text(json.dumps({"version": 1, "commit": NEW}))
        with patch("atelier_version.__file__", str(self.root / "atelier_version.py")):
            self.assertEqual(atelier_version.version_info()["commit"], NEW)

    def test_unavailable_git_uses_embedded_commit(self):
        (self.root / ".git").mkdir()
        (self.root / atelier_version.BUILD_FILE).write_text(json.dumps({"version": 1, "commit": NEW}))
        with patch("atelier_version.subprocess.run", side_effect=FileNotFoundError):
            self.assertEqual(atelier_version.version_info(self.root)["source"], "image")

    def test_missing_or_corrupt_build_version_is_development(self):
        for value in (None, "not json", "[]", '{"version":1,"commit":"secret"}', json.dumps({"version": 2, "commit": NEW})):
            with self.subTest(value=value):
                if value is not None:
                    (self.root / atelier_version.BUILD_FILE).write_text(value)
                self.assertEqual(atelier_version.version_info(self.root), {"commit": None, "label": "développement", "source": "development"})


if __name__ == "__main__":
    unittest.main()
