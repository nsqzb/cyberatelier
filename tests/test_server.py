import http.client
import json
import os
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

import server

# Sous Linux, /proc distingue un processus vivant d'un zombie. Ailleurs (macOS),
# os.kill(pid, 0) suffit : les orphelins tués sont récupérés aussitôt par launchd.
HAS_PROC = Path("/proc/self/stat").exists()
# Marge large : un runner CI chargé peut mettre plus d'une seconde à récolter un processus.
KILL_DEADLINE = 5


class FakeLab:
    def __init__(self):
        self.running = False
        self.host = "127.0.0.1"
        self.port = 8000

    def start(self): self.running = True
    def stop(self): self.running = False
    def status(self): return {"running": self.running, "host": self.host, "port": self.port}


class ServerApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.workspaces = root / "workspaces"
        self.data = root / "data"
        self.httpd = server.create_server("127.0.0.1", 0, self.workspaces, self.data, FakeLab())
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.httpd.server_address[1]

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=2)
        self.temp.cleanup()

    def request(self, method, path, body=None, headers=None, host=None, body_bytes=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        hs = {"Host": host or f"127.0.0.1:{self.port}"}
        if body is not None:
            hs["Content-Type"] = "application/json"
            body = json.dumps(body).encode()
        if body_bytes is not None:
            body = body_bytes
        hs.update(headers or {})
        conn.request(method, path, body=body, headers=hs)
        response = conn.getresponse()
        data = response.read()
        status = response.status
        content_type = response.getheader("Content-Type", "")
        conn.close()
        return status, content_type, data

    def json_request(self, method, path, body=None, **kwargs):
        status, _, raw = self.request(method, path, body, **kwargs)
        return status, json.loads(raw)

    @staticmethod
    def process_is_running(pid, use_proc=None):
        """A killed orphan may remain briefly as a zombie until init reaps it."""
        if not (HAS_PROC if use_proc is None else use_proc):
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                return False
            except PermissionError:
                return True
            return True
        try:
            stat = Path(f"/proc/{pid}/stat").read_text()
            state = stat[stat.rfind(")") + 2:].split()[0]
            return state != "Z"
        except (FileNotFoundError, ProcessLookupError):
            # /proc can disappear after open(), while read() is still pending.
            return False

    def test_files_round_trip_and_state_persisted_atomically(self):
        self.assertEqual(self.json_request("GET", "/api/files?course=portpilot")[1], {"files": []})
        status, result = self.json_request("POST", "/api/file", {
            "course": "portpilot", "path": "src/check.py", "content": "print('ok')\n"})
        self.assertEqual(status, 200)
        self.assertEqual(result, {"ok": True, "path": "src/check.py"})
        self.assertEqual(self.json_request("GET", "/api/file?course=portpilot&path=src%2Fcheck.py")[1]["content"], "print('ok')\n")
        state = {"version": 1, "selectedCourse": "fileguard", "completed": ["fileguard-mr1"],
                 "notes": {"fileguard": "à reprendre"}, "mrLinks": {"fileguard-mr1": "https://gitlab.example/mr/1"}}
        normalized = {**state, "notes": {**{c: "" for c in server.COURSES}, "fileguard": "à reprendre"}, "paliers": []}
        self.assertEqual(self.json_request("POST", "/api/state", state), (200, normalized))
        self.assertEqual(self.json_request("GET", "/api/state"), (200, normalized))
        self.assertFalse(any(p.name.startswith(".atelier-") for p in self.data.iterdir()))

    def test_paliers_are_saved_deduplicated_and_validated(self):
        base = {"version": 1, "selectedCourse": "socle", "completed": [], "notes": {}, "mrLinks": {}}
        status, saved = self.json_request("POST", "/api/state", {**base, "paliers": ["socle-mr1-p1", "socle-mr1-p1", "socle-mr1-p2"]})
        self.assertEqual(status, 200)
        self.assertEqual(saved["paliers"], ["socle-mr1-p1", "socle-mr1-p2"])
        self.assertEqual(self.json_request("GET", "/api/state")[1]["paliers"], ["socle-mr1-p1", "socle-mr1-p2"])
        status, _ = self.json_request("POST", "/api/state", {**base, "paliers": "pas-une-liste"})
        self.assertEqual(status, 400)
        status, old = self.json_request("POST", "/api/state", base)
        self.assertEqual((status, old["paliers"]), (200, []), "une ancienne progression sans paliers reste valide")

    def test_health_reports_the_installed_version(self):
        installed = {"commit": "a" * 40, "label": "aaaaaaa", "source": "image"}
        with mock.patch("server.version_info", return_value=installed):
            status, result = self.json_request("GET", "/api/health")
        self.assertEqual(status, 200)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["version"], installed)

    def test_path_and_symlink_traversal_are_rejected(self):
        for bad in ("../secret", "/etc/passwd", "a%2F..%2Fsecret", "a\\b"):
            status, result = self.json_request("POST", "/api/file", {
                "course": "portpilot", "path": bad, "content": "x"})
            self.assertEqual(status, 400, bad)
            self.assertIn("error", result)
        root = self.workspaces / "portpilot"
        (root / "outside-link").symlink_to(self.data, target_is_directory=True)
        status, result = self.json_request("POST", "/api/file", {
            "course": "portpilot", "path": "outside-link/state.json", "content": "x"})
        self.assertEqual(status, 400)
        self.assertIn("error", result)

    def test_create_only_conflict_and_invalid_origin(self):
        self.request("POST", "/api/file", {"course": "headerscope", "path": "a.py", "content": "one"})
        status, body = self.json_request("POST", "/api/file", {
            "course": "headerscope", "path": "a.py", "content": "two", "createOnly": True})
        self.assertEqual(status, 409)
        self.assertIn("existe", body["error"])
        status, body = self.json_request("POST", "/api/state", {"version": 1}, headers={"Origin": "https://evil.example"})
        self.assertEqual(status, 403)
        self.assertIn("error", body)
        status, body = self.json_request("GET", "/api/state", host="evil.example")
        self.assertEqual(status, 403)

    def test_run_returns_nonzero_and_timeout_without_transport_error(self):
        status, result = self.json_request("POST", "/api/run", {
            "course": "portpilot", "command": "printf failed; exit 7", "cwd": "."})
        self.assertEqual(status, 200)
        self.assertEqual(result["exitCode"], 7)
        self.assertEqual(result["stdout"], "failed")
        self.assertFalse(result["timedOut"])
        status, result = self.json_request("POST", "/api/run", {
            "course": "portpilot", "command": "sleep 5", "timeout": 0.15})
        self.assertEqual(status, 200)
        self.assertTrue(result["timedOut"])
        self.assertLess(result["duration"], 2)

    def test_run_kills_background_children_and_bounds_output(self):
        # A detached-looking background child must still be contained in the command's process group.
        status, result = self.json_request("POST", "/api/run", {
            "course": "portpilot", "command": "sleep 10 & echo $!"})
        self.assertEqual(status, 200)
        pid = int(result["stdout"].strip())
        deadline = time.monotonic() + KILL_DEADLINE
        while self.process_is_running(pid) and time.monotonic() < deadline: time.sleep(0.02)
        self.assertFalse(self.process_is_running(pid), f"le processus {pid} tourne encore")

        status, timed = self.json_request("POST", "/api/run", {
            "course": "portpilot", "command": "sleep 10 & echo $!; wait", "timeout": 0.15})
        self.assertEqual(status, 200)
        self.assertTrue(timed["timedOut"])
        timeout_pid = int(timed["stdout"].strip())
        deadline = time.monotonic() + KILL_DEADLINE
        while self.process_is_running(timeout_pid) and time.monotonic() < deadline: time.sleep(0.02)
        self.assertFalse(self.process_is_running(timeout_pid), f"le processus {timeout_pid} tourne encore après timeout")

        status, result = self.json_request("POST", "/api/run", {
            "course": "portpilot", "command": "yes x | head -c 100000"})
        self.assertEqual(status, 200)
        self.assertTrue(result["truncated"])
        self.assertEqual(len(result["stdout"].encode()), server.MAX_RUN_OUTPUT)

    def test_run_timeout_survives_early_stdout_eof_and_kills_redirected_child(self):
        status, result = self.json_request("POST", "/api/run", {
            "course": "portpilot", "command": "exec sleep 60 >/dev/null 2>&1", "timeout": 0.2})
        self.assertEqual(status, 200)
        self.assertTrue(result["timedOut"])
        self.assertLess(result["duration"], 2)

        status, result = self.json_request("POST", "/api/run", {
            "course": "portpilot", "command": "sleep 60 >/dev/null 2>&1 & echo $!; exit", "timeout": 2})
        self.assertEqual(status, 200)
        pid = int(result["stdout"].strip())
        deadline = time.monotonic() + KILL_DEADLINE
        while self.process_is_running(pid) and time.monotonic() < deadline: time.sleep(0.02)
        self.assertFalse(self.process_is_running(pid), f"le processus redirigé {pid} tourne encore")

    def test_workspace_zip_bounds_uncompressed_data(self):
        root = self.workspaces / "fileguard"
        payload = b"0" * server.MAX_FILE
        for index in range(server.MAX_ZIP // server.MAX_FILE + 1):
            (root / f"sample-{index}.txt").write_bytes(payload)
        status, body = self.json_request("GET", "/api/workspace.zip?course=fileguard")
        self.assertEqual(status, 413)
        self.assertIn("volumineux", body["error"])

    def test_json_body_required_and_health_lab_endpoint(self):
        status, _, raw = self.request("POST", "/api/file", headers={"Content-Type": "text/plain"})
        self.assertEqual(status, 400)
        self.assertIn("error", json.loads(raw))
        self.assertEqual(self.json_request("GET", "/api/lab")[1]["running"], True)
        status, health = self.json_request("GET", "/api/health")
        self.assertEqual(status, 200)
        self.assertEqual(health["status"], "ok")

    def test_detached_descendant_holding_stdout_does_not_block_or_keep_the_lock(self):
        # Un petit-fils qui quitte le groupe (setsid) en gardant stdout ne doit ni bloquer la requête
        # jusqu'à sa fin, ni laisser le verrou pris pour les commandes suivantes.
        # Le shell attend que le descendant ait quitté le groupe (PID écrit après setsid) avant de se terminer :
        # sinon le serveur le tuerait encore légitimement avec le groupe, et le cas testé n'existerait pas.
        detach = ("python3 -c 'import os, time; os.setsid(); open(\"escaped.tmp\", \"w\").write(str(os.getpid())); "
                  "os.replace(\"escaped.tmp\", \"escaped.pid\"); time.sleep(20)' & "
                  "while [ ! -s escaped.pid ]; do sleep 0.05; done; echo detache")
        status, result = self.json_request("POST", "/api/run", {"course": "portpilot", "command": detach, "timeout": 20})
        self.assertEqual(status, 200)
        escaped = int((self.workspaces / "portpilot" / "escaped.pid").read_text())
        self.addCleanup(lambda: os.kill(escaped, 9) if self.process_is_running(escaped) else None)
        self.assertIn("detache", result["stdout"])
        self.assertFalse(result["timedOut"])
        self.assertTrue(self.process_is_running(escaped), "le descendant a bien échappé au groupe")
        # La réponse arrive environ PIPE_GRACE après la fin du shell, pas à la fin du descendant (20 s).
        self.assertLess(result["duration"], 15)
        status, result = self.json_request("POST", "/api/run", {"course": "portpilot", "command": "echo suivant"})
        self.assertEqual((status, result["stdout"]), (200, "suivant\n"))

    def test_malformed_fields_are_client_errors(self):
        for course in (["portpilot"], {"a": 1}, 3, None):
            with self.subTest(course=course):
                status, body = self.json_request("POST", "/api/file", {"course": course, "path": "a.py", "content": "x"})
                self.assertEqual(status, 400)
                status, body = self.json_request("POST", "/api/run", {"course": course, "command": "true"})
                self.assertEqual(status, 400)
        for path in ("..%5cevil.txt", "a%5Cb", "a%00b"):
            with self.subTest(path=path):
                status, _ = self.json_request("POST", "/api/file", {"course": "portpilot", "path": path, "content": "x"})
                self.assertEqual(status, 400)
        self.assertEqual(list((self.workspaces / "portpilot").iterdir()), [])

    def test_os_errors_do_not_leak_host_paths(self):
        (self.workspaces / "portpilot" / "dossier").mkdir()
        status, body = self.json_request("GET", "/api/file?course=portpilot&path=dossier")
        self.assertEqual(status, 400)
        self.assertNotIn(str(self.workspaces), body["error"])
        self.assertNotIn("/", body["error"])

    def test_state_rejects_boolean_version_and_unsafe_links(self):
        base = {"selectedCourse": "socle", "completed": [], "notes": {}, "mrLinks": {}}
        self.assertEqual(self.json_request("POST", "/api/state", {**base, "version": True})[0], 400)
        for link in ("javascript:alert(1)", "data:text/html,x", "file:///etc/passwd"):
            with self.subTest(link=link):
                status, _ = self.json_request("POST", "/api/state", {**base, "version": 1, "mrLinks": {"socle-mr1": link}})
                self.assertEqual(status, 400)
        status, saved = self.json_request("POST", "/api/state", {**base, "version": 1, "mrLinks": {"socle-mr1": "https://github.com/x/y/pull/1"}})
        self.assertEqual((status, saved["mrLinks"]), (200, {"socle-mr1": "https://github.com/x/y/pull/1"}))

    def test_corrupted_state_is_set_aside_and_defaults_are_served(self):
        self.data.mkdir(exist_ok=True)
        (self.data / "state.json").write_text("{pas du json", encoding="utf-8")
        status, state = self.json_request("GET", "/api/state")
        self.assertEqual((status, state), (200, server.DEFAULT_STATE))
        kept = list(self.data.glob("state.invalide-*.json"))
        self.assertEqual(len(kept), 1, "le fichier illisible est conservé à côté")
        self.assertEqual(kept[0].read_text(encoding="utf-8"), "{pas du json")

    def test_file_close_to_the_limit_is_accepted_despite_json_escaping(self):
        content = "\n" * (server.MAX_FILE - 10)
        status, result = self.json_request("POST", "/api/file", {"course": "portpilot", "path": "grand.txt", "content": content})
        self.assertEqual(status, 200, result)
        status, _ = self.json_request("POST", "/api/file", {"course": "portpilot", "path": "trop.txt", "content": "x" * (server.MAX_FILE + 1)})
        self.assertEqual(status, 413)

    def test_non_standard_json_and_hostile_inputs_are_rejected(self):
        for raw in (b'{"course":"portpilot","command":"sleep 1","timeout":NaN}',
                    b'{"course":"portpilot","command":"sleep 1","timeout":Infinity}',
                    b"[" * 200_000):
            with self.subTest(raw=raw[:40]):
                status, _, body = self.request("POST", "/api/run", headers={"Content-Type": "application/json"},
                                               body_bytes=raw)
                self.assertEqual(status, 400, body)
        status, _ = self.json_request("POST", "/api/state", {"version": 1, "selectedCourse": []})
        self.assertEqual(status, 400)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "mkfifo indisponible")
    def test_fifo_is_refused_without_blocking(self):
        os.mkfifo(self.workspaces / "portpilot" / "tube")
        started = time.monotonic()
        status, body = self.json_request("GET", "/api/file?course=portpilot&path=tube")
        self.assertEqual(status, 400)
        self.assertLess(time.monotonic() - started, 2)

    def test_security_headers_on_api_and_static_responses(self):
        for path in ("/", "/api/health"):
            with self.subTest(path=path):
                conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
                self.addCleanup(conn.close)
                conn.request("GET", path, headers={"Host": f"127.0.0.1:{self.port}"})
                response = conn.getresponse()
                response.read()
                self.assertEqual(response.getheader("X-Frame-Options"), "DENY")
                self.assertEqual(response.getheader("X-Content-Type-Options"), "nosniff")
                self.assertIn("frame-ancestors 'none'", response.getheader("Content-Security-Policy", ""))
                self.assertNotIn("Python", response.getheader("Server", ""))

    def test_error_response_closes_the_connection(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        self.addCleanup(conn.close)
        conn.request("POST", "/api/state", body=b'{"version": 1}' + b" " * 200,
                     headers={"Host": f"127.0.0.1:{self.port}", "Origin": "https://evil.example", "Content-Type": "application/json"})
        response = conn.getresponse()
        response.read()
        self.assertEqual(response.status, 403)
        self.assertEqual(response.getheader("Connection", "").lower(), "close")


class RealLabApiTests(unittest.TestCase):
    def test_lab_endpoint_starts_and_stops_the_real_lab(self):
        from labs import LabManager
        from urllib.request import urlopen
        with tempfile.TemporaryDirectory() as temp:
            httpd = server.create_server("127.0.0.1", 0, Path(temp) / "w", Path(temp) / "d", LabManager(port=0))
            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()
            try:
                port = httpd.server_address[1]

                def call(method, body=None):
                    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
                    conn.request(method, "/api/lab", body=json.dumps(body).encode() if body is not None else None,
                                 headers={"Host": f"127.0.0.1:{port}", "Content-Type": "application/json"})
                    response = conn.getresponse()
                    result = (response.status, json.loads(response.read()))
                    conn.close()
                    return result

                status, lab = call("GET")
                self.assertEqual((status, lab["running"]), (200, True))
                with urlopen(f"http://127.0.0.1:{lab['port']}/durci", timeout=2) as response:
                    self.assertEqual(response.headers["X-Frame-Options"], "DENY")
                self.assertEqual(call("POST", {"running": False})[1]["running"], False)
                self.assertEqual(call("POST", {"running": True})[1]["running"], True)
                self.assertEqual(call("POST", {"running": "oui"})[0], 400)
            finally:
                httpd.shutdown()
                httpd.server_close()
                thread.join(timeout=2)
        self.assertFalse(httpd.lab.status()["running"], "server_close arrête le labo")


class ProcessStateTests(unittest.TestCase):
    def test_proc_probe_handles_disappearance_without_hiding_other_errors(self):
        for error in (FileNotFoundError("already gone"), ProcessLookupError("gone during read")):
            with self.subTest(error=type(error).__name__):
                with mock.patch.object(Path, "read_text", side_effect=error):
                    self.assertFalse(ServerApiTests.process_is_running(42, use_proc=True))
        for state, expected in (("S", True), ("Z", False)):
            with self.subTest(state=state):
                with mock.patch.object(Path, "read_text", return_value=f"42 (test process) {state} 1"):
                    self.assertEqual(ServerApiTests.process_is_running(42, use_proc=True), expected)
        with mock.patch.object(Path, "read_text", side_effect=PermissionError("denied")):
            with self.assertRaises(PermissionError):
                ServerApiTests.process_is_running(42, use_proc=True)

    def test_signal_probe_is_used_without_proc(self):
        self.assertTrue(ServerApiTests.process_is_running(os.getpid(), use_proc=False))
        for error, expected in ((ProcessLookupError(), False), (PermissionError(), True)):
            with self.subTest(error=type(error).__name__):
                with mock.patch("os.kill", side_effect=error):
                    self.assertEqual(ServerApiTests.process_is_running(42, use_proc=False), expected)


if __name__ == "__main__":
    unittest.main()
