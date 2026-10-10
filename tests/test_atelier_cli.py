"""Contrats du compagnon Mac, sans Docker ni dépôts de l'apprenant."""

import argparse
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import atelier_cli as cli


class CompanionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.curriculum = cli.Curriculum(cli.ROOT / "content" / "courses.json")

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.state_file = self.root / "userdata" / "terminal.json"
        self.out = io.StringIO()

    def state(self, import_remote=False):
        return cli.StateStore(self.state_file, self.curriculum, self.root, import_remote)

    def companion(self, state=None):
        return cli.Companion(self.curriculum, state or self.state(), self.root, self.root / "workspaces", self.out)

    def test_imports_five_cases_notes_and_mr_once_then_resumes_six(self):
        checked = [f"socle-mr1-p{n}" for n in range(1, 6)]
        remote = {"version": 1, "selectedCourse": "socle", "paliers": checked,
                  "completed": [], "notes": {"socle": "mon repère"},
                  "mrLinks": {"socle-mr1": "https://gitlab.example/mr/1"}}
        with patch.object(cli, "fetch_local_progression", return_value=(remote, "http://127.0.0.1:8080/api/state")) as fetch:
            state = self.state(True)
            self.assertEqual(state.pid, "socle-mr1-p6")
            self.assertEqual(state.data["paliers"], checked)
            self.assertEqual(state.data["notes"]["socle"], "mon repère")
            self.assertEqual(state.data["mrLinks"], remote["mrLinks"])
            state.select("socle-mr1-p8")
            state = self.state(True)
            self.assertEqual(state.pid, "socle-mr1-p8")
            fetch.assert_called_once_with(self.root)
        self.assertEqual(remote["paliers"], checked, "l'import ne modifie pas l'objet reçu")

    def test_accepts_older_v1_progression_without_paliers(self):
        self.state_file.parent.mkdir()
        self.state_file.write_text(json.dumps({"version": 1, "selectedCourse": "socle",
                                               "completed": ["socle-mr1"], "notes": {}, "mrLinks": {}}))
        state = self.state()
        self.assertEqual(state.data["paliers"], [])
        self.assertEqual(state.data["completed"], ["socle-mr1"])
        self.assertEqual(state.pid, "socle-mr1-p1")

    def test_navigation_remembers_each_course_without_marking_any_case(self):
        state = self.state()
        state.select("socle-mr1-p6")
        self.assertTrue(state.move(1))
        state.course("toolwrap")
        state.select("toolwrap-mr2-p3")
        state.course("socle")
        self.assertEqual(self.state().pid, "socle-mr1-p7")
        self.assertEqual(state.data["paliers"], [])
        self.assertEqual(state.data["completed"], [])
        self.assertTrue(state.move(-1))
        self.assertEqual(self.state().pid, "socle-mr1-p6")

    def test_navigation_stops_at_course_boundaries(self):
        state = self.state()
        self.assertFalse(state.move(-1))
        state.select(self.curriculum.order["socle"][-1])
        self.assertFalse(state.move(1))
        self.assertEqual(state.cid, "socle")

    def test_marking_is_idempotent_reversible_and_does_not_complete_mission(self):
        state = self.state()
        state.mark(True)
        state.mark(True)
        self.assertEqual(self.state().data["paliers"], ["socle-mr1-p1"])
        self.assertEqual(state.data["completed"], [])
        state.mark(False)
        self.assertEqual(self.state().data["paliers"], [])

    def test_corrupt_or_invalid_state_is_never_overwritten(self):
        self.state_file.parent.mkdir()
        samples = [b"not json", b'{"version": 99}',
                   b'{"version":1,"selectedCourse":[]}',
                   b'{"version":1,"terminal":{"currentByCourse":{"socle":"unknown"}}}',
                   b'{"version":1,"terminal":{"hintLevels":{"socle-mr1-p1":true}}}']
        for original in samples:
            with self.subTest(original=original):
                self.state_file.write_bytes(original)
                with self.assertRaises(cli.AtelierError):
                    self.state()
                self.assertEqual(self.state_file.read_bytes(), original)

    def test_atomic_write_failure_preserves_previous_file(self):
        state = self.state()
        original = self.state_file.read_bytes()
        with patch.object(cli.os, "replace", side_effect=OSError("lecture seule")):
            with self.assertRaises(cli.AtelierError):
                state.select("socle-mr1-p6")
        self.assertEqual(self.state_file.read_bytes(), original)
        self.assertEqual(list(self.state_file.parent.glob(".terminal.json.write-*")), [])

    def test_stale_session_refuses_to_erase_cases_and_notes_from_other_terminal(self):
        first = self.state()
        second = self.state()
        first.data["notes"]["socle"] = "note récente"
        first.mark(True)
        original = self.state_file.read_bytes()
        with self.assertRaisesRegex(cli.AtelierError, "autre terminal"):
            second.select("socle-mr1-p6")
        self.assertEqual(self.state_file.read_bytes(), original)
        second.reload()
        second.select("socle-mr1-p6")
        current = self.state()
        self.assertEqual(current.data["notes"]["socle"], "note récente")
        self.assertEqual(current.data["paliers"], ["socle-mr1-p1"])
        self.assertEqual(current.pid, "socle-mr1-p6")

    def test_explicit_application_block_does_not_need_docker_to_show_correct_folder(self):
        companion = self.companion()
        block = {"kind": "shell", "code": "python3 labs.py", "cwd": "application",
                 "context": "Terminal du Mac", "title": "Lancer le labo"}
        companion.blocks({"blocks": [block]}, "after_actions")
        self.assertIn(f"Dossier sur ton Mac : {self.root.resolve()}", self.out.getvalue())
        self.assertNotIn(f"Dossier sur ton Mac : {self.root.resolve() / 'workspaces' / 'socle'}", self.out.getvalue())

    def test_unknown_historical_progression_ids_are_preserved(self):
        data = {"version": 1, "selectedCourse": "socle", "paliers": ["ancien-palier"],
                "completed": ["ancienne-mission"], "notes": {}, "mrLinks": {"ancienne-mission": "https://example.test/mr"}}
        self.state_file.parent.mkdir()
        self.state_file.write_text(json.dumps(data))
        state = self.state()
        state.mark(True)
        self.assertIn("ancien-palier", self.state().data["paliers"])
        self.assertIn("ancienne-mission", self.state().data["completed"])

    def test_offline_creation_works_without_docker_and_records_no_import(self):
        with patch.object(cli, "fetch_local_progression", return_value=(None, "indisponible")):
            state = self.state(True)
        self.assertEqual(state.data["terminal"]["importedFrom"], "indisponible")
        self.assertEqual(state.data["paliers"], [])
        self.assertIn("locale", state.notice)

    def test_invalid_api_progression_does_not_create_file(self):
        with patch.object(cli, "fetch_local_progression", return_value=({"version": 42}, "local")):
            with self.assertRaises(cli.AtelierError):
                self.state(True)
        self.assertFalse(self.state_file.exists())

    def test_hints_reveal_one_at_a_time_and_remember_level(self):
        companion = self.companion()
        palier = companion.current[2]
        with patch.dict(palier, {"hints": ["notion", "méthode", "exemple à part"]}):
            companion.hint()
            self.assertIn("Indice 1/3 : notion", self.out.getvalue())
            self.assertNotIn("méthode", self.out.getvalue())
            companion.hint()
            self.assertEqual(self.state().data["terminal"]["hintLevels"][companion.state.pid], 2)
            companion.hint(3)
            companion.hint()
            self.assertEqual(self.state().data["terminal"]["hintLevels"][companion.state.pid], 3)

    def test_nested_git_branch_is_separate_and_parent_is_never_mistaken_for_course(self):
        def git(*args, cwd):
            subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)
        git("init", "-b", "main", cwd=self.root)
        course = self.root / "workspaces" / "socle"
        course.mkdir(parents=True)
        self.assertEqual(cli.git_info(course), "aucun dépôt Git propre à ce parcours")
        git("init", "-b", "feat/bases", cwd=course)
        self.assertEqual(cli.git_info(course), "feat/bases")
        self.assertEqual(cli.git_info(self.root), "main")

    def test_show_contains_only_one_palier_and_never_runs_commands(self):
        state = self.state()
        state.select("socle-mr1-p6")
        companion = self.companion(state)
        workspace = self.root / "workspaces" / "socle"
        workspace.mkdir(parents=True)
        exercise = workspace / "outils.py"
        exercise.write_text("# mon travail\n")
        with patch.object(cli, "git_info", return_value="feat/bases"), patch.object(cli.subprocess, "run") as run:
            companion.show()
            run.assert_not_called()
        text = self.out.getvalue()
        self.assertIn("socle-mr1-p6", text)
        self.assertNotIn("Identifiant : socle-mr1-p7", text)
        self.assertIn("S6 —", text)
        self.assertIn("S7 —", text)
        self.assertIn("S8 —", text)
        self.assertIn("None", text)
        self.assertIn(str(workspace), text)
        self.assertIn("Branche réelle de l'exercice : feat/bases", text)
        self.assertIn("Une case ne vérifie ni tes tests", text)
        self.assertEqual(exercise.read_text(), "# mon travail\n")
        self.assertEqual(list(workspace.iterdir()), [exercise])

    def test_cli_can_run_from_any_cwd_and_resume_by_stable_id(self):
        command = [sys.executable, str(cli.ROOT / "atelier.py"), "--state-file", str(self.state_file), "--no-import"]
        first = subprocess.run([*command, "voir", "socle-mr1-p6"], cwd=self.root,
                               text=True, capture_output=True, check=True)
        second = subprocess.run([*command, "voir"], cwd=self.root, text=True, capture_output=True, check=True)
        self.assertIn("Identifiant : socle-mr1-p6", first.stdout)
        self.assertIn("Identifiant : socle-mr1-p6", second.stdout)

    def test_invalid_curriculum_has_readable_error(self):
        bad = self.root / "courses.json"
        bad.write_text('{"version":1,"courses":[{"id":"socle","title":"Socle","steps":[null]}]}')
        with self.assertRaisesRegex(cli.AtelierError, "Énoncés invalides"):
            cli.Curriculum(bad)


class LocalApiTests(unittest.TestCase):
    def test_port_reads_quoted_dotenv_and_environment_has_priority(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(cli.local_port(root, {}), 8080)
            (root / ".env").write_text('# configuration\nexport ATELIER_PORT = "8765" # local\n')
            self.assertEqual(cli.local_port(root, {}), 8765)
            self.assertEqual(cli.local_port(root, {"ATELIER_PORT": "8081"}), 8081)
            self.assertEqual(cli.local_port(root, {"ATELIER_PORT": ""}), 8080)
            (root / ".env").write_text('ATELIER_PORT=""\n')
            self.assertEqual(cli.local_port(root, {}), 8080)
            for value in ("65536", "0", "8080; touch x", "${PORT}"):
                with self.subTest(value=value), self.assertRaises(cli.AtelierError):
                    cli.local_port(root, {"ATELIER_PORT": value})

    def test_initial_import_is_get_only_and_proxy_and_redirects_are_disabled(self):
        response = io.BytesIO(b'{"version":1,"selectedCourse":"socle"}')
        with patch.object(cli, "local_port", return_value=8765), patch.object(cli.urllib.request, "build_opener") as build:
            build.return_value.open.return_value = response
            data, source = cli.fetch_local_progression(Path("/unused"))
        self.assertEqual(data["version"], 1)
        self.assertEqual(source, "http://127.0.0.1:8765/api/state")
        build.return_value.open.assert_called_once_with(source, timeout=1)
        self.assertIsInstance(build.call_args.args[0], cli.urllib.request.ProxyHandler)
        self.assertEqual(build.call_args.args[0].proxies, {})
        redirect = build.call_args.args[1]
        self.assertIsInstance(redirect, cli.NoRedirect)
        self.assertIsNone(redirect.redirect_request(None, None, 302, "", {}, "https://external.test/"))

    def test_lab_explicit_actions_use_only_local_lab_route(self):
        for action, method, body in (("statut", "GET", None), ("demarrer", "POST", {"running": True}),
                                     ("arreter", "POST", {"running": False})):
            with self.subTest(action=action), patch.object(cli, "local_port", return_value=8081), \
                    patch.object(cli.urllib.request, "build_opener") as build:
                build.return_value.open.return_value = io.BytesIO(json.dumps({"running": action != "arreter", "port": 8000}).encode())
                result = cli.docker_lab(Path("/unused"), action)
                request = build.return_value.open.call_args.args[0]
                self.assertEqual(request.full_url, "http://127.0.0.1:8081/api/lab")
                self.assertEqual(request.get_method(), method)
                self.assertEqual(json.loads(request.data) if request.data else None, body)
                self.assertIsInstance(result["running"], bool)

    def test_lab_failure_is_readable_and_import_offline_is_optional(self):
        error = cli.urllib.error.URLError("connection refused")
        with patch.object(cli.urllib.request, "build_opener") as build:
            build.return_value.open.side_effect = error
            with self.assertRaisesRegex(cli.AtelierError, "Docker"):
                cli.docker_lab(cli.ROOT, "demarrer")
            self.assertEqual(cli.fetch_local_progression(cli.ROOT), (None, "indisponible"))


if __name__ == "__main__":
    unittest.main()
