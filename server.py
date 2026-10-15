"""Serveur local de Cyber Atelier (bibliothèque standard uniquement)."""
from __future__ import annotations

import io
import json
import math
import os
import re
import selectors
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from atelier_version import version_info

BASE_DIR = Path(__file__).resolve().parent
COURSES = {"socle", "portpilot", "headerscope", "fileguard", "toolwrap", "reconwrap"}
EXCLUDED = {".git", ".venv", "__pycache__"}
MAX_FILE = 1_048_576
MAX_STATE = 1_048_576
MAX_RUN_OUTPUT = 65_536
MAX_ZIP = 20 * 1024 * 1024
MAX_FILES = 2000
# Le JSON échappe certains caractères sur 6 octets : le corps d'un fichier de 1 Mio peut dépasser MAX_STATE.
MAX_FILE_BODY = 6 * MAX_FILE + 4096
PIPE_GRACE = 1.0
DEFAULT_STATE = {"version": 1, "selectedCourse": "socle", "completed": [],
                 "notes": {c: "" for c in sorted(COURSES)}, "mrLinks": {}, "paliers": []}


def _state_normalize(value):
    if not isinstance(value, dict) or type(value.get("version")) is not int or value["version"] != 1:
        raise ValueError("Progression invalide : version 1 attendue.")
    course = value.get("selectedCourse", "socle")
    if not isinstance(course, str) or course not in COURSES:
        raise ValueError("Parcours sélectionné invalide.")
    completed = value.get("completed", [])
    if not isinstance(completed, list) or len(completed) > 100 or any(not isinstance(x, str) or len(x) > 100 for x in completed):
        raise ValueError("Liste des missions terminées invalide.")
    paliers = value.get("paliers", [])
    if not isinstance(paliers, list) or len(paliers) > 500 or any(not isinstance(x, str) or len(x) > 100 for x in paliers):
        raise ValueError("Liste des paliers terminés invalide.")
    notes = value.get("notes", {})
    links = value.get("mrLinks", {})
    if not isinstance(notes, dict) or not isinstance(links, dict):
        raise ValueError("Notes ou liens invalides.")
    clean_notes = {}
    for key, val in notes.items():
        if key not in COURSES or not isinstance(val, str) or len(val) > 20_000:
            raise ValueError("Une note est invalide ou trop longue.")
        clean_notes[key] = val
    clean_links = {}
    for key, val in links.items():
        if not isinstance(key, str) or len(key) > 100 or not isinstance(val, str) or len(val) > 2048:
            raise ValueError("Un lien de merge request est invalide ou trop long.")
        if val and urllib.parse.urlsplit(val).scheme.lower() not in {"http", "https"}:
            raise ValueError("Un lien de merge request doit commencer par http:// ou https://.")
        clean_links[key] = val
    return {"version": 1, "selectedCourse": course, "completed": list(dict.fromkeys(completed)),
            "notes": {**{c: "" for c in sorted(COURSES)}, **clean_notes}, "mrLinks": clean_links, "paliers": list(dict.fromkeys(paliers))}


class AtelierServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address, handler, workspaces_dir, data_dir, lab_manager=None):
        super().__init__(address, handler)
        self.workspaces_dir = Path(workspaces_dir).resolve()
        self.data_dir = Path(data_dir).resolve()
        self.workspaces_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        for course in COURSES:
            (self.workspaces_dir / course).mkdir(exist_ok=True)
        self.state_path = self.data_dir / "state.json"
        self.run_lock = threading.Lock()
        if lab_manager is None:
            from labs import LabManager
            lab_manager = LabManager(host="127.0.0.1", port=int(os.environ.get("LAB_PORT", "8000")))
        self.lab = lab_manager
        try:
            self.lab.start()
        except Exception:
            pass

    def server_close(self):
        try:
            self.lab.stop()
        finally:
            super().server_close()


def _api_error(handler, status, message):
    # Le corps de la requête n'a peut-être pas été lu : la connexion ne peut pas être réutilisée.
    handler.close_connection = True
    handler._json(status, {"error": str(message)})


def _reject_constant(name):
    raise ValueError(f"Valeur JSON non standard refusée : {name}.")


class RequestHandler(BaseHTTPRequestHandler):
    server: AtelierServer
    protocol_version = "HTTP/1.1"
    server_version = "CyberAtelier"
    sys_version = ""
    # Un client qui annonce un corps sans l'envoyer ne bloque pas un thread indéfiniment.
    timeout = 30

    def end_headers(self):
        # L'interface ne doit jamais être affichée dans le cadre d'un autre site (clickjacking).
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", "frame-ancestors 'none'")
        self.send_header("Referrer-Policy", "no-referrer")
        super().end_headers()

    def log_message(self, fmt, *args):
        # Keep command output and potentially sensitive local paths out of logs.
        return

    def _json(self, status, value):
        body = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if self.close_connection:
            self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)

    def _check_local(self):
        host = self.headers.get("Host", "")
        try:
            parsed = urllib.parse.urlsplit("//" + host)
            hostname = (parsed.hostname or "").lower()
            port = parsed.port
        except ValueError:
            hostname = ""
            port = None
        if hostname not in {"localhost", "127.0.0.1", "::1"}:
            raise PermissionError("Hôte non autorisé.")
        origin = self.headers.get("Origin")
        if origin:
            try:
                parsed_origin = urllib.parse.urlsplit(origin)
                origin_host = (parsed_origin.hostname or "").lower()
                origin_port = parsed_origin.port
            except ValueError:
                origin_host = ""
                origin_port = None
                parsed_origin = None
            if (not parsed_origin or parsed_origin.scheme not in {"http", "https"} or
                    origin_host != hostname or origin_port != port or parsed_origin.username or parsed_origin.password):
                raise PermissionError("Origine différente refusée.")

    def _query(self, parsed, key):
        values = urllib.parse.parse_qs(parsed.query, keep_blank_values=True, strict_parsing=True)
        if len(values.get(key, [])) != 1 or len(values) != 1:
            raise ValueError("Paramètres de requête invalides.")
        return values[key][0]

    def _course_root(self, course):
        if not isinstance(course, str) or course not in COURSES:
            raise ValueError("Parcours inconnu.")
        root = self.server.workspaces_dir / course
        if root.is_symlink():
            raise ValueError("Lien symbolique interdit dans le workspace.")
        return root

    @staticmethod
    def _relative_path(raw):
        if not isinstance(raw, str) or not raw or "\x00" in raw or "\\" in raw:
            raise ValueError("Chemin de fichier invalide.")
        decoded = urllib.parse.unquote(raw, errors="strict")
        if "\x00" in decoded or "\\" in decoded:
            raise ValueError("Chemin de fichier invalide.")
        path = Path(decoded)
        if path.is_absolute() or decoded.startswith("/") or any(p in {"", ".", ".."} for p in decoded.split("/")):
            raise ValueError("Chemin absolu ou traversal refusé.")
        if any(part in EXCLUDED for part in path.parts):
            raise ValueError("Ce chemin est exclu.")
        return path

    def _safe_target(self, root, rel, create_parents=False):
        root = root.resolve(strict=True)
        target = root
        for idx, part in enumerate(rel.parts):
            target = target / part
            if target.is_symlink():
                raise ValueError("Les liens symboliques sont interdits.")
            if idx < len(rel.parts) - 1 and target.exists() and not target.is_dir():
                raise ValueError("Un élément du chemin n'est pas un dossier.")
            if idx < len(rel.parts) - 1 and create_parents and not target.exists():
                target.mkdir()
        try:
            target.resolve(strict=False).relative_to(root)
        except ValueError:
            raise ValueError("Chemin hors du workspace refusé.")
        return target

    def _read_json(self, limit=MAX_STATE):
        if self.headers.get_content_type() != "application/json":
            raise ValueError("Le corps doit être au format JSON.")
        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            raise ValueError("Taille du corps invalide.")
        if length < 0 or length > limit:
            raise OverflowError("Corps JSON trop volumineux.")
        raw = self.rfile.read(length)
        try:
            # NaN et Infinity ne sont pas du JSON standard : un délai NaN échapperait à la limite de 30 s.
            return json.loads(raw.decode("utf-8"), parse_constant=_reject_constant)
        except (UnicodeDecodeError, json.JSONDecodeError, RecursionError):
            raise ValueError("JSON invalide.")

    def _dispatch(self):
        try:
            self._check_local()
            parsed = urllib.parse.urlsplit(self.path)
            if parsed.path.startswith("/api/"):
                self._api(parsed)
            elif self.command == "GET":
                self._static(parsed.path)
            else:
                _api_error(self, 404, "Ressource introuvable.")
        except PermissionError as e:
            _api_error(self, 403, str(e))
        except OverflowError as e:
            _api_error(self, 413, str(e))
        except FileNotFoundError:
            _api_error(self, 404, "Fichier introuvable.")
        except FileExistsError as e:
            _api_error(self, 409, str(e) or "Le fichier existe déjà.")
        except ValueError as e:
            _api_error(self, 400, str(e) or "Requête invalide.")
        except OSError:
            # Les messages système contiennent des chemins absolus de l'hôte.
            _api_error(self, 400, "Opération impossible sur ce chemin.")
        except Exception:
            _api_error(self, 500, "Erreur interne du serveur.")

    do_GET = _dispatch
    do_POST = _dispatch

    def _load_state(self):
        path = self.server.state_path
        if not path.exists():
            return DEFAULT_STATE
        try:
            return _state_normalize(json.loads(path.read_text(encoding="utf-8")))
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
            # Un fichier illisible bloquerait l'interface : il est conservé à côté, jamais écrasé.
            backup = path.with_name(f"state.invalide-{time.strftime('%Y%m%d-%H%M%S')}.json")
            os.replace(path, backup)
            return DEFAULT_STATE

    def _api(self, parsed):
        p = parsed.path
        if p == "/api/health" and self.command == "GET":
            try:
                git = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=2).stdout.strip()
            except Exception:
                git = "git indisponible"
            self._json(200, {"status": "ok", "python": sys.version.split()[0], "git": git,
                             "lab": self.server.lab.status(), "mode": "local",
                             "version": version_info(BASE_DIR)})
        elif p == "/api/state":
            if self.command == "GET":
                self._json(200, self._load_state())
            elif self.command == "POST":
                state = _state_normalize(self._read_json())
                self._atomic_write(self.server.state_path, json.dumps(state, ensure_ascii=False, indent=2).encode(), 0o600)
                self._json(200, state)
            else: _api_error(self, 405, "Méthode non autorisée.")
        elif p == "/api/files" and self.command == "GET":
            root = self._course_root(self._query(parsed, "course"))
            files = []
            for base, dirs, names in os.walk(root, followlinks=False):
                dirs[:] = sorted(d for d in dirs if d not in EXCLUDED and not (Path(base) / d).is_symlink())
                for name in sorted(names):
                    target = Path(base) / name
                    if target.is_symlink() or not target.is_file(): continue
                    rel = target.relative_to(root).as_posix()
                    files.append({"path": rel, "size": target.stat().st_size})
                    if len(files) >= MAX_FILES: break
                if len(files) >= MAX_FILES: break
            self._json(200, {"files": files})
        elif p == "/api/file":
            if self.command == "GET":
                q = urllib.parse.parse_qs(parsed.query, keep_blank_values=True, strict_parsing=True)
                if set(q) != {"course", "path"} or any(len(v) != 1 for v in q.values()): raise ValueError("Paramètres invalides.")
                root = self._course_root(q["course"][0]); rel = self._relative_path(q["path"][0]); target = self._safe_target(root, rel)
                # Un FIFO ou un périphérique bloquerait open() : seuls les fichiers ordinaires sont lus.
                if not target.is_file(): raise ValueError("Ce chemin n'est pas un fichier.")
                if target.stat().st_size > MAX_FILE: raise OverflowError("Fichier trop volumineux.")
                with target.open("rb") as stream:
                    data = stream.read(MAX_FILE + 1)
                if len(data) > MAX_FILE: raise OverflowError("Fichier trop volumineux.")
                try: content = data.decode("utf-8")
                except UnicodeDecodeError: raise ValueError("Le fichier n'est pas un texte UTF-8.")
                self._json(200, {"path": rel.as_posix(), "content": content})
            elif self.command == "POST":
                body = self._read_json(MAX_FILE_BODY)
                if not isinstance(body, dict) or set(body) - {"course", "path", "content", "createOnly"} or not all(k in body for k in ("course", "path", "content")):
                    raise ValueError("Champs attendus : course, path, content, createOnly optionnel.")
                if not isinstance(body["content"], str): raise ValueError("Le contenu doit être du texte.")
                data = body["content"].encode("utf-8")
                if len(data) > MAX_FILE: raise OverflowError("Fichier trop volumineux (limite 1 Mo).")
                if "createOnly" in body and not isinstance(body["createOnly"], bool): raise ValueError("createOnly doit être booléen.")
                root = self._course_root(body["course"]); rel = self._relative_path(body["path"])
                target = self._safe_target(root, rel, create_parents=True)
                if body.get("createOnly") and target.exists(): raise FileExistsError("Le fichier existe déjà.")
                self._atomic_write(target, data, create_only=body.get("createOnly", False))
                self._json(200, {"ok": True, "path": rel.as_posix()})
            else: _api_error(self, 405, "Méthode non autorisée.")
        elif p == "/api/run" and self.command == "POST":
            self._run(self._read_json())
        elif p == "/api/lab":
            if self.command == "GET": self._json(200, self.server.lab.status())
            elif self.command == "POST":
                body = self._read_json()
                if not isinstance(body, dict) or set(body) != {"running"} or not isinstance(body["running"], bool): raise ValueError("running doit être booléen.")
                if body["running"]: self.server.lab.start()
                else: self.server.lab.stop()
                self._json(200, self.server.lab.status())
            else: _api_error(self, 405, "Méthode non autorisée.")
        elif p == "/api/workspace.zip" and self.command == "GET":
            course = self._query(parsed, "course")
            archive = self._workspace_zip(self._course_root(course))
            self.send_response(200); self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Disposition", f'attachment; filename="{course}.zip"')
            self.send_header("Content-Length", str(len(archive))); self.end_headers(); self.wfile.write(archive)
        else:
            _api_error(self, 404, "API introuvable.")

    @staticmethod
    def _atomic_write(target, data, mode=0o600, create_only=False):
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".atelier-", dir=str(target.parent))
        try:
            os.fchmod(fd, mode)
            with os.fdopen(fd, "wb") as stream:
                stream.write(data); stream.flush(); os.fsync(stream.fileno())
            if create_only:
                # A hard link makes createOnly atomic even when two requests race.
                os.link(tmp, target)
            else:
                os.replace(tmp, target)
        finally:
            try: os.unlink(tmp)
            except FileNotFoundError: pass

    def _run(self, body):
        if not isinstance(body, dict) or set(body) - {"course", "command", "cwd", "timeout"} or not all(k in body for k in ("course", "command")):
            raise ValueError("Champs attendus : course, command, cwd optionnel.")
        if not isinstance(body["command"], str) or not body["command"].strip() or len(body["command"]) > 4096:
            raise ValueError("Commande invalide ou trop longue.")
        timeout = body.get("timeout", 30)
        if (not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or not math.isfinite(timeout)
                or timeout <= 0 or timeout > 30):
            raise ValueError("Le délai doit être compris entre 0 et 30 secondes.")
        root = self._course_root(body["course"])
        cwd_value = body.get("cwd", ".")
        cwd_rel = Path(".") if cwd_value == "." else self._relative_path(cwd_value)
        cwd = self._safe_target(root, cwd_rel)
        if not cwd.is_dir(): raise ValueError("Le dossier de travail n'existe pas.")
        if not self.server.run_lock.acquire(blocking=False):
            _api_error(self, 409, "Une commande est déjà en cours."); return
        started = time.monotonic(); output = bytearray(); truncated = False; timed_out = False
        proc = None
        try:
            proc = subprocess.Popen(["bash", "-lc", body["command"]], cwd=cwd, stdin=subprocess.DEVNULL,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True,
                                    close_fds=True, bufsize=0)
            fd = proc.stdout.fileno(); os.set_blocking(fd, False)
            with selectors.DefaultSelector() as sel:
                sel.register(fd, selectors.EVENT_READ)
                deadline = started + float(timeout)
                eof = False
                exited_at = None
                while not eof or proc.poll() is None:
                    if proc.poll() is not None and not eof:
                        # Un descendant sorti du groupe (setsid) peut garder stdout ouvert :
                        # on n'attend sa fin que brièvement, jamais au-delà du délai.
                        if exited_at is None: exited_at = time.monotonic()
                        elif time.monotonic() >= min(deadline, exited_at + PIPE_GRACE): break
                    if proc.poll() is None and time.monotonic() >= deadline:
                        timed_out = True
                        try: os.killpg(proc.pid, signal.SIGKILL)
                        except ProcessLookupError: pass
                        proc.wait()
                    elif proc.poll() is not None:
                        # Kill background children so they cannot outlive a completed command or hold the pipe open.
                        try: os.killpg(proc.pid, signal.SIGKILL)
                        except ProcessLookupError: pass
                    events = sel.select(0.05)
                    if not events and proc.poll() is not None and not eof:
                        try: chunk = os.read(fd, 65536)
                        except BlockingIOError: chunk = None
                        if chunk == b"": eof = True
                        elif chunk:
                            remain = MAX_RUN_OUTPUT - len(output)
                            if remain > 0: output.extend(chunk[:remain])
                            if len(chunk) > remain: truncated = True
                        continue
                    for key, _ in events:
                        try: chunk = os.read(key.fd, 65536)
                        except BlockingIOError: continue
                        if not chunk:
                            sel.unregister(key.fd); eof = True; break
                        remain = MAX_RUN_OUTPUT - len(output)
                        if remain > 0: output.extend(chunk[:remain])
                        if len(chunk) > remain: truncated = True
                    # A background descendant may retain stdout; after parent exit the group was killed above.
                code = proc.wait()
        except Exception:
            if proc and proc.poll() is None:
                try: os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError: pass
                proc.wait()
            raise
        finally:
            if proc:
                # Clean the whole session on every exit path, including descendants
                # that closed or redirected their inherited output pipe.
                try: os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError: pass
                if proc.poll() is None:
                    try: proc.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        try: os.killpg(proc.pid, signal.SIGKILL)
                        except ProcessLookupError: pass
                        proc.wait(timeout=2)
                if proc.stdout: proc.stdout.close()
            self.server.run_lock.release()
        text = output.decode("utf-8", errors="replace")
        self._json(200, {"exitCode": code, "stdout": text, "duration": round(time.monotonic() - started, 3),
                         "timedOut": timed_out, "truncated": truncated, "cwd": cwd_rel.as_posix()})

    def _workspace_zip(self, root):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            count = 0
            total_size = 0
            for base, dirs, names in os.walk(root, followlinks=False):
                dirs[:] = sorted(d for d in dirs if d not in EXCLUDED and not (Path(base) / d).is_symlink())
                for name in sorted(names):
                    f = Path(base) / name
                    if f.is_symlink() or not f.is_file(): continue
                    if f.stat().st_size > MAX_FILE: raise OverflowError("Un fichier dépasse la limite d'export.")
                    count += 1
                    if count > MAX_FILES: raise OverflowError("Trop de fichiers pour l'export.")
                    total_size += f.stat().st_size
                    if total_size > MAX_ZIP: raise OverflowError("Contenu non compressé trop volumineux pour l'export.")
                    zf.write(f, f.relative_to(root).as_posix())
                    if buffer.tell() > MAX_ZIP: raise OverflowError("Archive trop volumineuse.")
        return buffer.getvalue()

    def _static(self, path):
        if path == "/": target = BASE_DIR / "web" / "index.html"
        elif path in {"/app.js", "/styles.css"}: target = BASE_DIR / "web" / path[1:]
        elif path.startswith("/downloads/"):
            rel = self._relative_path(path[len("/downloads/"):]); target = BASE_DIR / "web" / "downloads" / rel
        elif path == "/content/courses.json" or (path.startswith("/content/") and path.endswith(".md")):
            rel = self._relative_path(path[len("/content/"):]); target = BASE_DIR / "content" / rel
        else:
            _api_error(self, 404, "Ressource introuvable."); return
        target = target.resolve(strict=True)
        allowed = [(BASE_DIR / "web").resolve(), (BASE_DIR / "content").resolve()]
        if not any(target == d or d in target.parents for d in allowed) or not target.is_file():
            _api_error(self, 404, "Ressource introuvable."); return
        data = target.read_bytes()
        mime = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
                ".css": "text/css; charset=utf-8", ".json": "application/json; charset=utf-8",
                ".md": "text/markdown; charset=utf-8", ".pdf": "application/pdf"}.get(target.suffix, "application/octet-stream")
        self.send_response(200); self.send_header("Content-Type", mime); self.send_header("Content-Length", str(len(data)))
        self.end_headers(); self.wfile.write(data)


def create_server(host=None, port=None, workspaces_dir=None, data_dir=None, lab_manager=None):
    host = host if host is not None else os.environ.get("ATELIER_HOST", "127.0.0.1")
    port = int(port if port is not None else os.environ.get("ATELIER_PORT", "8080"))
    workspaces_dir = workspaces_dir or os.environ.get("WORKSPACES_DIR", "/workspaces")
    data_dir = data_dir or os.environ.get("DATA_DIR", "/data")
    return AtelierServer((host, port), RequestHandler, workspaces_dir, data_dir, lab_manager)


def main():
    server = create_server()
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()


if __name__ == "__main__":
    main()
