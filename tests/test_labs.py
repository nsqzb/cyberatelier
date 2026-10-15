import socket
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from labs import LabManager


class LabManagerTests(unittest.TestCase):
    def setUp(self):
        self.lab = LabManager(port=0)
        state = self.lab.start()
        self.assertTrue(state["running"], state.get("error"))
        self.assertEqual(state["host"], "127.0.0.1")

    def tearDown(self):
        self.lab.stop()

    def get(self, path):
        return urlopen(f"http://127.0.0.1:{self.lab.status()['port']}{path}", timeout=2)

    def test_lifecycle_is_idempotent_and_restartable(self):
        first = self.lab.status()["port"]
        self.assertEqual(self.lab.start()["port"], first)
        self.assertFalse(self.lab.stop()["running"])
        self.assertFalse(self.lab.stop()["running"])
        self.assertTrue(self.lab.start()["running"])
        self.assertEqual(self.lab.status()["host"], "127.0.0.1")
        with self.get("/fragile") as response:
            self.assertEqual(response.status, 200, "le labo répond après redémarrage")

    def test_fragile_and_hardened_headers(self):
        with self.get("/fragile") as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.read(), "Réponse de démonstration fragile.\n".encode())
            for header in ("Content-Security-Policy", "X-Content-Type-Options", "X-Frame-Options"):
                self.assertIsNone(response.headers.get(header))

        with self.get("/durci") as response:
            self.assertEqual(response.status, 200)
            self.assertTrue(response.headers.get("Content-Security-Policy", "").strip())
            self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
            self.assertEqual(response.headers.get("X-Frame-Options"), "DENY")

    def test_root_and_status_routes(self):
        with self.get("/") as response:
            self.assertEqual(response.status, 200)
            self.assertIn(b"/fragile", response.read())
        for path, expected in (("/absent", 404), ("/erreur", 500), ("/ailleurs", 404)):
            with self.subTest(path=path):
                with self.assertRaises(HTTPError) as raised:
                    self.get(path)
                raised.exception.close()
                self.assertEqual(raised.exception.code, expected)

    def test_stop_closes_listener_and_worker_thread(self):
        thread = self.lab._thread
        port = self.lab.status()["port"]
        self.lab.stop()
        self.assertFalse(thread.is_alive())
        with self.assertRaises(URLError):
            urlopen(f"http://127.0.0.1:{port}/", timeout=1)

    def test_hardened_headers_exact_values_and_no_python_version(self):
        with self.get("/durci") as response:
            self.assertEqual(response.headers["Content-Security-Policy"], "default-src 'self'")
            self.assertEqual(response.read(), "Réponse de démonstration durcie.\n".encode())
            self.assertNotIn("Python", response.headers.get("Server", ""))

    def test_paths_are_matched_exactly(self):
        for path in ("/durci?x=1", "/fragile/", "/DURCI"):
            with self.subTest(path=path):
                with self.assertRaises(HTTPError) as raised:
                    self.get(path)
                raised.exception.close()
                self.assertEqual(raised.exception.code, 404)

    def test_only_loopback_bind_is_allowed(self):
        for host in ("0.0.0.0", "", "::", "::1", "127.0.0.2", "192.0.2.1"):
            with self.subTest(host=host), self.assertRaises(ValueError):
                LabManager(host=host)
        self.assertEqual(LabManager(host="localhost").host, "127.0.0.1")

    def test_invalid_ports_are_rejected(self):
        for port in (-1, 65536, 70000, "8000", 8000.0, None, True):
            with self.subTest(port=port), self.assertRaises(ValueError):
                LabManager(port=port)


class LabPortConflictTests(unittest.TestCase):
    def test_busy_port_is_reported_without_exception(self):
        for bind_host in ("127.0.0.1", "0.0.0.0"):
            with self.subTest(bind_host=bind_host):
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as other:
                    other.bind((bind_host, 0))
                    other.listen()
                    port = other.getsockname()[1]
                    lab = LabManager(port=port)
                    state = lab.start()
                    self.assertFalse(state["running"])
                    self.assertIn("error", state)
                    self.assertFalse(lab.stop()["running"])

    def test_stop_before_start_is_harmless(self):
        lab = LabManager(port=0)
        self.assertEqual(lab.stop(), {"running": False, "host": "127.0.0.1", "port": 0})


if __name__ == "__main__":
    unittest.main()
