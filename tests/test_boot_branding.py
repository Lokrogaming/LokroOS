"""Boot-/Installer-Branding-Tests (statisch): Plymouth-Theme, GRUB-Snippets,
Calamares-Brand, Cubic-Vorlage, Provisionsskript-Marker. Kein Root nötig."""
import json
from pathlib import Path

try:
    from PIL import Image as PILImage
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "config" / "plymouth" / "themes" / "lokroos"
BRAND = ROOT / "installer" / "calamares" / "lokroos"


def test_plymouth_theme_complete():
    for f in ("lokroos.plymouth", "lokroos.script", "logo.png", "bar.png",
              "box.png"):
        assert (THEME / f).is_file(), f
    ply = (THEME / "lokroos.plymouth").read_text(encoding="utf-8")
    assert "Name=LokroOS" in ply
    assert "ModuleName=script" in ply
    assert "lokroos.script" in ply
    script = (THEME / "lokroos.script").read_text(encoding="utf-8")
    for asset in ("logo.png", "bar.png", "box.png"):
        assert asset in script, asset
    assert "SetBootProgressFunction" in script
    assert "SetMessageFunction" in script


def test_plymouth_pngs_valid():
    if not HAVE_PIL:
        return  # auf Systemen ohne Pillow: nur Existenz geprüft (s.o.)
    for name, size in (("logo.png", (512, 512)), ("bar.png", (400, 12)),
                       ("box.png", (400, 12))):
        with PILImage.open(THEME / name) as im:
            im.load()
            assert im.size == size, f"{name}: {im.size}"
            assert im.format == "PNG"


def test_grub_snippets():
    iso = (ROOT / "config" / "grub" / "iso-entries.cfg.snippet").read_text(
        encoding="utf-8")
    assert "Try or Install LokroOS" in iso
    assert "LokroOS (safe graphics)" in iso
    assert "Kubuntu" not in iso
    installed = (ROOT / "config" / "grub" / "installed-lokroos.cfg").read_text(
        encoding="utf-8")
    assert 'GRUB_DISTRIBUTOR="LokroOS"' in installed


def _parse_desc(path):
    """Minimaler branding.desc-Parser (Schlüssel: Wert + eine Ebene Einzug)."""
    data, current = {}, None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not raw.startswith((" ", "\t")) and ":" in line:
            key, _, val = line.partition(":")
            current = key.strip()
            data[current] = val.strip() or {}
        elif isinstance(data.get(current), dict) and ":" in line:
            key, _, val = line.strip().partition(":")
            data[current][key.strip()] = val.strip()
    return data


def test_calamares_brand():
    desc = _parse_desc(BRAND / "branding.desc")
    for key in ("componentName", "productName", "version", "slideshow",
                "slideshowAPI"):
        assert key in desc and desc[key], key
    assert desc["componentName"] == "lokroos"
    assert desc["productName"] == "LokroOS"
    assert desc["slideshowAPI"] == "2"
    assert (BRAND / desc["slideshow"]).is_file()
    assert (BRAND / "logo.svg").is_file()
    for f in ("branding.desc", "show.qml"):
        text = (BRAND / f).read_text(encoding="utf-8")
        assert "Kubuntu" not in text and "kubuntu" not in text.lower(), f
    qml = (BRAND / "show.qml").read_text(encoding="utf-8")
    assert "onActivate" in qml and "onLeave" in qml  # API 2
    assert "Qt.locale" in qml  # DE/EN-Laufzeitwahl


def test_cubic_preset_valid():
    preset = json.loads((ROOT / "iso" / "cubic-preset.json").read_text(
        encoding="utf-8"))
    assert "LokroOS" in preset.get("volume_id", "")
    assert "Try or Install LokroOS" in preset["boot_entries"]["entries"]
    assert any("provision" in s for s in preset["chroot_steps"])


def test_provision_deploys_boot_branding():
    prov = (ROOT / "iso" / "provision-lokroos.sh").read_text(encoding="utf-8")
    for marker in ("plymouth-set-default-theme", "installed-lokroos.cfg",
                   "update-grub", "calamares/branding",
                   "settings.conf.lokroos-bak", "lokroos.script"):
        assert marker in prov, marker
