"""Tests für shell/welcome/lokroos-welcome.py – ohne Display-Server ausführbar."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WELCOME = ROOT / "shell" / "welcome" / "lokroos-welcome.py"


def load_module():
    spec = importlib.util.spec_from_file_location("lokroos_welcome", WELCOME)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_json_output_de(monkeypatch, capsys):
    mod = load_module()
    monkeypatch.setenv("LANG", "de_DE.UTF-8")
    # getpass.getuser() löst auf Linux per UID auf (ignoriert $USER) –
    # deshalb den Login-Namen direkt mocken (Produkt nutzt bewusst getpass zuerst).
    monkeypatch.setattr(mod.getpass, "getuser", lambda: "testnutzer")
    assert mod.main(["--json-only"]) == 0
    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["user"] == "testnutzer"
    assert payload["lang"] == "de"
    assert payload["message"] == "Willkommen zurück, testnutzer!"


def test_json_output_en(monkeypatch, capsys):
    mod = load_module()
    monkeypatch.setenv("LANG", "en_US.UTF-8")
    monkeypatch.setattr(mod.getpass, "getuser", lambda: "alice")
    assert mod.main(["--json-only"]) == 0
    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["message"] == "Welcome back, alice!"


def test_no_anim_flag(monkeypatch, capsys):
    mod = load_module()
    monkeypatch.setenv("LANG", "de_DE.UTF-8")
    assert mod.main(["--json-only", "--no-anim"]) == 0
    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["animations"] is False
    assert payload["durations_ms"]["fade_in"] == 0


def test_env_no_anim(monkeypatch, capsys):
    mod = load_module()
    monkeypatch.setenv("LOKROOS_NO_ANIM", "1")
    assert mod.main(["--json-only"]) == 0
    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["animations"] is False


def test_never_crashes(monkeypatch, capsys):
    """Selbst mit kaputter Umgebung: Exit 0, Login wird nie blockiert."""
    mod = load_module()
    monkeypatch.delenv("LANG", raising=False)
    monkeypatch.delenv("USER", raising=False)
    monkeypatch.delenv("USERNAME", raising=False)
    assert mod.main(["--json-only"]) == 0
    payload = json.loads(capsys.readouterr().out.strip())
    assert "message" in payload


def test_subprocess_runs():
    r = subprocess.run([sys.executable, str(WELCOME), "--json-only"],
                       capture_output=True, text=True, timeout=15)
    assert r.returncode == 0
    assert "message" in json.loads(r.stdout.strip())
