import http.client
import json
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

import server


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

    def request(self, method, path, body=None, headers=None, host=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        hs = {"Host": host or f"127.0.0.1:{self.port}"}
        if body is not None:
            hs["Content-Type"] = "application/json"
            body = json.dumps(body).encode()
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
    def process_is_running(pid):
        """A killed orphan may remain briefly as a zombie until init reaps it."""
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
        deadline = time.monotonic() + 1
        while self.process_is_running(pid) and time.monotonic() < deadline: time.sleep(0.02)
        self.assertFalse(self.process_is_running(pid), f"le processus {pid} tourne encore")

        status, timed = self.json_request("POST", "/api/run", {
            "course": "portpilot", "command": "sleep 10 & echo $!; wait", "timeout": 0.15})
        self.assertEqual(status, 200)
        self.assertTrue(timed["timedOut"])
        timeout_pid = int(timed["stdout"].strip())
        deadline = time.monotonic() + 1
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
        deadline = time.monotonic() + 1
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


class ProcessStateTests(unittest.TestCase):
    def test_proc_probe_handles_disappearance_without_hiding_other_errors(self):
        for error in (FileNotFoundError("already gone"), ProcessLookupError("gone during read")):
            with self.subTest(error=type(error).__name__):
                with mock.patch.object(Path, "read_text", side_effect=error):
                    self.assertFalse(ServerApiTests.process_is_running(42))
        for state, expected in (("S", True), ("Z", False)):
            with self.subTest(state=state):
                with mock.patch.object(Path, "read_text", return_value=f"42 (test process) {state} 1"):
                    self.assertEqual(ServerApiTests.process_is_running(42), expected)
        with mock.patch.object(Path, "read_text", side_effect=PermissionError("denied")):
            with self.assertRaises(PermissionError):
                ServerApiTests.process_is_running(42)


if __name__ == "__main__":
    unittest.main()
