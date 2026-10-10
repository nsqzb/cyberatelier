"""Petit serveur HTTP local utilisé par les exercices HeaderScope.

Ce module fournit uniquement des réponses de démonstration. Il n'exécute pas
de code apprenant et ne contacte aucune autre machine.
"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import RLock, Thread


class _LabHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, _format, *_args):
        # Les accès du laboratoire ne polluent pas la sortie du serveur UI.
        return

    def _respond(self, status, body, headers=()):
        payload = body.encode("utf-8")
        self.send_response(status)
        for name, value in headers:
            self.send_header(name, value)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(payload)
        self.close_connection = True

    def do_GET(self):
        routes = {
            "/": (200, "Laboratoire HTTP Cyber Atelier\nRoutes : /fragile, /durci, /absent, /erreur\n", ()),
            "/fragile": (200, "Réponse de démonstration fragile.\n", ()),
            "/durci": (
                200,
                "Réponse de démonstration durcie.\n",
                (("Content-Security-Policy", "default-src 'self'"),
                 ("X-Content-Type-Options", "nosniff"),
                 ("X-Frame-Options", "DENY")),
            ),
            "/absent": (404, "Ressource absente.\n", ()),
            "/erreur": (500, "Erreur de démonstration.\n", ()),
        }
        result = routes.get(self.path)
        if result is None:
            self._respond(404, "Ressource absente.\n")
            return
        status, body, headers = result
        self._respond(status, body, headers)


class LabManager:
    """Démarre et arrête le serveur local du laboratoire de façon sûre."""

    def __init__(self, host="127.0.0.1", port=8000):
        if host not in ("127.0.0.1", "localhost", "::1"):
            raise ValueError("Le laboratoire doit être lié à une adresse loopback.")
        self.host = "127.0.0.1" if host == "localhost" else host
        self.port = port
        self.error = None
        self._server = None
        self._thread = None
        self._lock = RLock()

    def start(self):
        with self._lock:
            if self._server is not None:
                return self.status()
            try:
                server = _LabHTTPServer((self.host, self.port), _Handler)
                thread = Thread(target=server.serve_forever, name="cyberatelier-lab", daemon=True)
                thread.start()
                self._server, self._thread = server, thread
                self.port = server.server_address[1]
                self.error = None
            except OSError as exc:
                self.error = str(exc)
            return self.status()

    def stop(self):
        with self._lock:
            server, thread = self._server, self._thread
            if server is None:
                return self.status()
            self._server = self._thread = None
            server.shutdown()
            server.server_close()
            if thread is not None:
                thread.join()
            return self.status()

    def status(self):
        with self._lock:
            result = {"running": self._server is not None, "host": self.host, "port": self.port}
            if self.error:
                result["error"] = self.error
            return result


if __name__ == "__main__":
    # Lancement direct sur ta machine : python3 labs.py (arrêt avec Ctrl+C).
    # Utile quand tu codes dans VS Code : le labo répond alors sur 127.0.0.1:8000 de ton Mac.
    import time

    lab = LabManager()
    etat = lab.start()
    if not etat["running"]:
        raise SystemExit(f"Impossible de démarrer le laboratoire : {etat.get('error')}")
    print(f"Laboratoire actif sur http://{etat['host']}:{etat['port']}/ (Ctrl+C pour arrêter)")
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        lab.stop()
