"""Version de l'application, sur le Mac ou dans l'image Docker."""

from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess


BUILD_FILE = ".atelier-build.json"


def _commit(value: object) -> str | None:
    if isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value):
        return value
    return None


def version_info(root: str | Path | None = None) -> dict:
    """Renvoie commit, label lisible et source, sans dépendre du dossier courant."""
    directory = Path(root).resolve() if root is not None else Path(__file__).resolve().parent
    if (directory / ".git").exists():
        try:
            result = subprocess.run(
                ["git", "-C", str(directory), "rev-parse", "--verify", "HEAD"],
                capture_output=True, text=True, timeout=5, check=False,
            )
            commit = _commit(result.stdout.strip()) if result.returncode == 0 else None
            if commit:
                return {"commit": commit, "label": commit[:7], "source": "git"}
        except (OSError, subprocess.SubprocessError):
            pass
    try:
        value = json.loads((directory / BUILD_FILE).read_text(encoding="utf-8"))
        commit = _commit(value.get("commit")) if isinstance(value, dict) and value.get("version") == 1 else None
        if commit:
            return {"commit": commit, "label": commit[:7], "source": "image"}
    except (OSError, ValueError):
        pass
    return {"commit": None, "label": "développement", "source": "development"}
