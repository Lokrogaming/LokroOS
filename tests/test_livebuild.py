"""live-build-Scaffolding-Tests: Generator-Quellen, Hook, GRUB-Rename, Preset."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LB = ROOT / "iso" / "live-build"


def test_scaffolding_files_exist():
    for f in ("generate.sh", "build.sh", "make_packagelist.py",
              "extra-packages.txt", "exclude-iso.txt", "README.md",
              "hooks/0900-lokroos-brand.chroot",
              "hooks/0000-lokroos-repos.chroot_early",
              "hooks/0910-lokroos-grub-titles.binary"):
        assert (LB / f).is_file(), f


def test_packagelist_builder():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "make_packagelist", LB / "make_packagelist.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    pkgs = mod.build(str(ROOT))
    for need in ("kubuntu-desktop", "linux-image-generic", "linux-firmware",
                 "casper", "calamares", "nodejs", "steam-installer",
                 "wine32", "mesa-vulkan-drivers:i386"):
        assert need in pkgs, need
    for banned in ("bottles", "proton-vpn-gnome-desktop", "steam"):
        assert banned not in pkgs, f"darf nicht ins ISO: {banned}"
    assert len(pkgs) == len(set(pkgs))  # keine Duplikate


def test_pipeline_sources_are_git_tracked():
    """Regression: .gitignore darf Pipeline-Quellen nie wieder schlucken."""
    git = shutil.which("git")
    if git is None:
        return
    r = subprocess.run([git, "ls-files", "iso/live-build"],
                       capture_output=True, text=True, timeout=30,
                       cwd=str(ROOT))
    assert r.returncode == 0, r.stderr
    tracked = set(r.stdout.split())
    for f in ("iso/live-build/generate.sh", "iso/live-build/build.sh",
              "iso/live-build/make_packagelist.py",
              "iso/live-build/extra-packages.txt",
              "iso/live-build/exclude-iso.txt",
              "iso/live-build/README.md",
              "iso/live-build/hooks/0900-lokroos-brand.chroot",
              "iso/live-build/hooks/0000-lokroos-repos.chroot_early",
              "iso/live-build/hooks/0910-lokroos-grub-titles.binary"):
        assert f in tracked, f"nicht getrackt (gitignore?): {f}"


def test_extra_packages_sane():
    lines = [ln.split("#", 1)[0].strip() for ln in
             (LB / "extra-packages.txt").read_text(encoding="utf-8").splitlines()]
    pkgs = [ln for ln in lines if ln]
    for need in ("kubuntu-desktop", "linux-image-generic", "casper",
                 "calamares"):
        assert need in pkgs, need
    assert len(pkgs) == len(set(pkgs))  # keine Duplikate


def _find_bash():
    """Echte Bash finden (Windows: NICHT C:\\Windows\\System32\\bash.exe = WSL-Stub)."""
    import os
    bash = shutil.which("bash")
    if bash and "system32" in bash.lower():
        git_bash = os.path.join(os.environ.get("PROGRAMFILES", ""),
                                "Git", "bin", "bash.exe")
        bash = git_bash if os.path.isfile(git_bash) else None
    return bash


def test_bash_syntax():
    bash = _find_bash()
    if bash is None:
        return  # keine echte Bash: Skip (WSL-Run prueft mit)
    for script in ("generate.sh", "build.sh",
                   "hooks/0900-lokroos-brand.chroot"):
        r = subprocess.run([bash, "-n", str(LB / script)],
                           capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, f"{script}: {r.stderr}"


def test_hook_deploys_brand_parts():
    hook = (LB / "hooks" / "0900-lokroos-brand.chroot").read_text(
        encoding="utf-8")
    for marker in ("set -e", "plymouth-set-default-theme",
                   "installed-lokroos.cfg", "calamares/branding",
                   "lokroos-install.desktop", "settings.conf.lokroos-bak",
                   "/etc/hostname"):
        assert marker in hook, marker


def test_build_uses_lb3_options():
    build = (LB / "build.sh").read_text(encoding="utf-8")
    for marker in ("--bootloader grub", "--grub-splash none",
                   "--bootappend-failsafe", "--volatile true",
                   "--initramfs casper", "username=lokro", "hostname=lokroos",
                   'LB_BOOTLOADER="grub2"', "0910-lokroos-grub-titles",
                   "--firmware-chroot false"):
        assert marker in build, marker
    for stale in ("--bootloaders ", "--bootappend-live-failsafe",
                  "--username ", "--hostname ", "--image-name ",
                  "--updates ", "rename-grub.py"):
        assert stale not in build, f"veraltet/entfernt: {stale}"


def test_generate_places_hooks_flat():
    """Regression: lb 3.x findet Hooks NUR flach unter config/hooks/
    (*.chroot, *.chroot_early, *.binary) – normal/-Unterverzeichnis ist tot."""
    gen = (LB / "generate.sh").read_text(encoding="utf-8")
    assert "config/hooks/" in gen
    assert "hooks/normal" not in gen, "Ablage in hooks/normal/ wird von lb 3.x ignoriert"
    for suffix in (".chroot", ".chroot_early", ".binary"):
        assert suffix in gen, suffix


def test_grub_binary_hook_on_fixture(tmp_path):
    """Der ECHTE Binary-Hook gegen lb-nahe Debian-Titel (Build-Root nachstellen)."""
    bash = _find_bash()
    if bash is None:
        return
    grub_dir = tmp_path / "binary" / "boot" / "grub"
    grub_dir.mkdir(parents=True)
    (grub_dir / "grub.cfg").write_text(
        (Path(__file__).parent / "fixtures" / "grub-sample.cfg").read_text(
            encoding="utf-8"), encoding="utf-8")
    hook = str(LB / "hooks" / "0910-lokroos-grub-titles.binary")
    r = subprocess.run([bash, hook], capture_output=True, text=True,
                       timeout=30, cwd=str(tmp_path))
    assert r.returncode == 0, r.stdout + r.stderr
    out = (grub_dir / "grub.cfg").read_text(encoding="utf-8")
    assert '"Try or Install LokroOS"' in out
    assert '"LokroOS (safe graphics)"' in out
    assert "Debian GNU/Linux" not in out


def test_grub_binary_hook_fails_cleanly(tmp_path):
    bash = _find_bash()
    if bash is None:
        return
    hook = str(LB / "hooks" / "0910-lokroos-grub-titles.binary")
    # 1. fehlende grub.cfg -> Exit != 0
    r = subprocess.run([bash, hook], capture_output=True, text=True,
                       timeout=30, cwd=str(tmp_path))
    assert r.returncode != 0
    # 2. grub.cfg ohne Pflicht-Titel -> Exit != 0
    grub_dir = tmp_path / "binary" / "boot" / "grub"
    grub_dir.mkdir(parents=True)
    (grub_dir / "grub.cfg").write_text('menuentry "Other" {\n}\n',
                                       encoding="utf-8")
    r = subprocess.run([bash, hook], capture_output=True, text=True,
                       timeout=30, cwd=str(tmp_path))
    assert r.returncode != 0  # fail-fast, kein falsches ISO


def test_cubic_preset_consistent():
    preset = json.loads((ROOT / "iso" / "cubic-preset.json").read_text(
        encoding="utf-8"))
    assert "Try or Install LokroOS" in preset["boot_entries"]["entries"]
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    assert version in preset.get("volume_id", "")
