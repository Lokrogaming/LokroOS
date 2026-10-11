"""Manifest- und Token-Tests (statisch, ohne Root/Netzwerk)."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_tokens_structure():
    tokens = json.loads((ROOT / "branding" / "tokens.json").read_text(encoding="utf-8"))
    assert tokens["color"]["surface"]["black"] == "#06090F"
    assert tokens["color"]["accent"]["cyan"] == "#22D3EE"
    assert tokens["radius"]["lg"] == "22px"
    assert "font-family" in tokens["typography"]
    # tokens.css muss dieselben Kernfarben enthalten
    css = (ROOT / "branding" / "tokens.css").read_text(encoding="utf-8")
    assert "#06090F" in css and "#22D3EE" in css


def test_manifests_valid():
    for mf in (ROOT / "packages").glob("manifest-*.json"):
        data = json.loads(mf.read_text(encoding="utf-8"))
        assert isinstance(data.get("packages"), list) and data["packages"], mf.name


def test_verify_manifests_script():
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "verify-manifests.py"),
                        "--root", str(ROOT)], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "Manifeste OK" in r.stdout


def test_no_exe_autoassoc():
    """Sicherheitsregel: Keine .exe-Auto-Assoziation irgendwo im Repo."""
    hits = []
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        # Eigene Testdateien enthalten die Suchbegriffe per Definition – ausschließen
        if "tests" in p.parts or "node_modules" in str(p):
            continue
        if p.is_file() and p.suffix in (".py", ".md", ".json", ".desktop", ".conf", ".sh"):
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            low = text.lower()
            if "mime" in low and "exe" in low and "wine" in low and "auto" in low:
                hits.append(str(p))
    assert not hits, f"Verdacht auf .exe-Auto-Assoziation: {hits}"


def test_web_preview_files_exist():
    preview = ROOT / "shell" / "web-preview"
    for f in ("index.html", "styles.css", "app.js"):
        assert (preview / f).is_file(), f
    html = (preview / "index.html").read_text(encoding="utf-8")
    assert "welcome-overlay" in html and "launcher-grid" in html
    # Dashboard-Home (v0.2.0): Fenster, Tabs, Charts
    for marker in ("win-dashboard", "dash-tabs", "pane-overview",
                   "pane-processes", "pane-network", "c-cpu", "c-netbig",
                   "proc-list", "tab-restore"):
        assert marker in html, marker
    js = (preview / "app.js").read_text(encoding="utf-8")
    assert "Welcome back" in js and "Willkommen zurück" in js
    for marker in ("closeTab", "restoreTabs", "tickStats", "drawSpark",
                   "lokroos-stats.py"):
        assert marker in js, marker
    css = (preview / "styles.css").read_text(encoding="utf-8")
    assert "prefers-reduced-motion" in css and ".tabpane" in css


def test_stats_backend_exists():
    stats = ROOT / "shell" / "stats" / "lokroos-stats.py"
    assert stats.is_file()
    text = stats.read_text(encoding="utf-8")
    for marker in ("read_cpu_times", "read_mem", "read_net_counters",
                   "read_tasks", "read_gpu", "--loop", "supported"):
        assert marker in text, marker


def test_vm_prep_files_exist():
    script = ROOT / "tools" / "setup-vm-host.ps1"
    assert script.is_file()
    text = script.read_text(encoding="utf-8")
    for marker in ("RunAsAdministrator", "VBoxManage", "SHA256",
                   "kubuntu-24.04.5", "vmsvga", "provision-lokroos.sh"):
        assert marker in text, marker
    install = (ROOT / "docs" / "INSTALL.md").read_text(encoding="utf-8")
    for marker in ("LokroOS-Test", "provision-lokroos.sh",
                   "frisch-installiert", "Plasma (X11)"):
        assert marker in install, marker


def test_vm_host_script_syntax():
    """Echte Syntaxprüfung via PowerShell-Parser (nur Windows mit powershell.exe)."""
    ps = shutil.which("powershell")
    if ps is None:
        return  # auf Linux: still überspringen (bash -n deckt .sh ab)
    check = ("$e=$null; [void][System.Management.Automation.Language.Parser]::"
             "ParseFile('tools\\setup-vm-host.ps1',[ref]$null,[ref]$e); $e.Count")
    r = subprocess.run([ps, "-NoProfile", "-Command", check],
                       capture_output=True, text=True, timeout=60,
                       cwd=str(ROOT))
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "0", f"PS-Parser-Fehler: {r.stdout}"
