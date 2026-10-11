"""live-build-Scaffolding-Tests: Generator-Quellen, Hook, GRUB-Rename, Preset."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LB = ROOT / "iso" / "live-build"


def test_scaffolding_files_exist():
    for f in ("generate.sh", "build.sh", "rename-grub.py",
              "extra-packages.txt", "README.md",
              "hooks/0900-lokroos-brand.hook.chroot"):
        assert (LB / f).is_file(), f


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
              "iso/live-build/rename-grub.py",
              "iso/live-build/extra-packages.txt",
              "iso/live-build/README.md",
              "iso/live-build/hooks/0900-lokroos-brand.hook.chroot"):
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
                   "hooks/0900-lokroos-brand.hook.chroot"):
        r = subprocess.run([bash, "-n", str(LB / script)],
                           capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, f"{script}: {r.stderr}"


def test_hook_deploys_brand_parts():
    hook = (LB / "hooks" / "0900-lokroos-brand.hook.chroot").read_text(
        encoding="utf-8")
    for marker in ("set -e", "plymouth-set-default-theme",
                   "installed-lokroos.cfg", "calamares/branding",
                   "lokroos-install.desktop", "settings.conf.lokroos-bak",
                   "/etc/hostname"):
        assert marker in hook, marker


def test_build_uses_lb3_options():
    build = (LB / "build.sh").read_text(encoding="utf-8")
    for marker in ("--bootloader grub", "--bootappend-failsafe",
                   "--volatile true", "--initramfs casper",
                   "username=lokro", "hostname=lokroos",
                   "rename-grub.py"):
        assert marker in build, marker
    for stale in ("--bootloaders ", "--bootappend-live-failsafe",
                  "--username ", "--hostname ", "--image-name ",
                  "--updates "):
        assert stale not in build, f"veraltete lb-Option: {stale}"


def test_grub_rename_on_fixture(tmp_path):
    work = tmp_path / "build"
    dest = work / "config" / "bootloaders" / "grub-pc"
    dest.mkdir(parents=True)
    (dest / "grub.cfg").write_text(
        (Path(__file__).parent / "fixtures" / "grub-sample.cfg").read_text(
            encoding="utf-8"), encoding="utf-8")
    r = subprocess.run([sys.executable, str(LB / "rename-grub.py"), str(work)],
                       capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stdout + r.stderr
    out = (dest / "grub.cfg").read_text(encoding="utf-8")
    assert '"Try or Install LokroOS"' in out
    assert '"LokroOS (safe graphics)"' in out
    assert "Ubuntu" not in out.replace("LokroOS", "")


def test_grub_rename_fails_without_entries(tmp_path):
    work = tmp_path / "build"
    dest = work / "config" / "bootloaders" / "grub-pc"
    dest.mkdir(parents=True)
    (dest / "grub.cfg").write_text("# leer\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(LB / "rename-grub.py"), str(work)],
                       capture_output=True, text=True, timeout=30)
    assert r.returncode != 0  # fail-fast, kein falsches ISO


def test_cubic_preset_consistent():
    preset = json.loads((ROOT / "iso" / "cubic-preset.json").read_text(
        encoding="utf-8"))
    assert "Try or Install LokroOS" in preset["boot_entries"]["entries"]
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    assert version in preset.get("volume_id", "")
