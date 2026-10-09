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
                self.assertEqual(raised.exception.code, expected)

    def test_stop_closes_listener_and_worker_thread(self):
        thread = self.lab._thread
        port = self.lab.status()["port"]
        self.lab.stop()
        self.assertFalse(thread.is_alive())
        with self.assertRaises((URLError, OSError)):
            urlopen(f"http://127.0.0.1:{port}/", timeout=1)

    def test_only_loopback_bind_is_allowed(self):
        with self.assertRaises(ValueError):
            LabManager(host="0.0.0.0")


if __name__ == "__main__":
    unittest.main()
