"""Design-System-Tests: Light Mode, Demo-Kennzeichnung, Installer-Spec, CasaOS-Dok."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_light_tokens_exist():
    tokens = json.loads((ROOT / "branding" / "tokens.json").read_text(encoding="utf-8"))
    light = tokens["theme"]["light"]
    for group in ("surface", "text", "border", "glass", "accent", "shadow"):
        assert group in light, group
    assert light["text"]["primary"] == "#0B1526"
    assert light["surface"]["card"] == "#FFFFFF"
    # Tokens-Version folgt der Repo-Version (Konsistenz, vgl. AGENTS.md-Regel 8)
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    assert tokens["meta"]["version"] == version


def test_light_css_overrides():
    css = (ROOT / "branding" / "tokens.css").read_text(encoding="utf-8")
    assert '[data-theme="light"]' in css
    assert "#0B1526" in css and "#0891B2" in css


def test_preview_theme_toggle_and_demo_tags():
    preview = ROOT / "shell" / "web-preview"
    html = (preview / "index.html").read_text(encoding="utf-8")
    assert 'id="btn-theme"' in html
    assert html.count('class="demo-tag"') >= 4  # WLAN/Audio/Helligkeit/VPN
    js = (preview / "app.js").read_text(encoding="utf-8")
    assert "btn-theme" in js and 'data-theme' in js
    assert "theme-title" in js
    css = (preview / "styles.css").read_text(encoding="utf-8")
    assert ".demo-tag" in css and 'html[data-theme="light"]' in css


def test_installer_spec_exists():
    spec = (ROOT / "installer" / "INSTALLER_SPEC.md").read_text(encoding="utf-8")
    for step in ("Willkommen", "Partitionierung", "Benutzerkonto", "Bootloader",
                 "Abschluss"):
        assert step in spec, step
    assert "calamares -c" in spec
    assert "Nur in VMs testen" in spec  # VM-only-Regel dokumentiert


def test_casaos_design_doc():
    doc = (ROOT / "docs" / "DESIGN_CASAOS.md").read_text(encoding="utf-8")
    assert "nicht" in doc.lower()  # Abgrenzung vorhanden (keine Kopie)
    for marker in ("Dashboard-first", "App-Kacheln", "Light Mode", "Demo"):
        assert marker in doc, marker
