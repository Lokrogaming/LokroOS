#!/usr/bin/env bash
# LokroOS ISO-Build (live-build) – läuft NUR auf Ubuntu 24.04 als root (WSL/VM).
#   sudo ./iso/live-build/build.sh --root <repo> --work ~/lokroos-build
# Schritte: generate.sh -> lb config -> GRUB-Titel umbenennen (fail-fast) -> lb build.
# lb baut in Stufen (bootstrap/chroot/binary); Wiederaufruf setzt fort.
# Log: <work>/build-<version>-<datum>.log
set -euo pipefail

ROOT=""; WORK=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) ROOT="$2"; shift 2;;
    --work) WORK="$2"; shift 2;;
    -h|--help) sed -n '1,7p' "$0"; exit 0;;
    *) echo "Unbekannte Option: $1" >&2; exit 2;;
  esac
done
[[ -n "$ROOT" && -n "$WORK" ]] || { echo "--root und --work sind Pflicht." >&2; exit 2; }

log() { echo "[lokroos-iso] $*"; }
fail() { echo "[lokroos-iso][FEHLER] $*" >&2; exit 1; }

[[ "$(uname -s)" == "Linux" ]] || fail "Nur Linux."
[[ "$(id -u)" -eq 0 ]] || fail "Bitte als root (sudo)."
# shellcheck disable=SC1091
. /etc/os-release
[[ "${ID:-}" == "ubuntu" && "${VERSION_ID:-}" == "24.04" ]] || \
  fail "Erwartet Ubuntu 24.04, gefunden: ${ID:-?} ${VERSION_ID:-?}"
command -v lb >/dev/null 2>&1 || fail "'lb' fehlt: apt-get install -y live-build"
export DEBIAN_FRONTEND=noninteractive

VERSION="$(cat "$ROOT/VERSION")"
mkdir -p "$WORK"
LOG="$WORK/build-$VERSION-$(date +%Y%m%d-%H%M%S).log"
log "Version $VERSION – Log: $LOG – Arbeit: $WORK"

"$ROOT/iso/live-build/generate.sh" --root "$ROOT" --out "$WORK" 2>&1 | tee -a "$LOG"

cd "$WORK"
if [[ ! -f .stage/config ]]; then
  log "lb config …"
  # Optionen passend zu live-build 3.0 (Noble): --bootloader (singular),
  # --bootappend-failsafe, --volatile statt --updates, --initramfs casper.
  # Live-User/Hostname via Casper-Bootparameter (kein lb-Schalter in 3.x).
  lb config \
    --mode ubuntu --distribution noble \
    --archive-areas "main restricted universe multiverse" \
    --security true --volatile true \
    --binary-images iso-hybrid \
    --bootloader grub \
    --grub-splash none \
    --debian-installer false \
    --initramfs casper \
    --firmware-binary false --firmware-chroot false \
    --bootappend-live "boot=casper username=lokro hostname=lokroos quiet splash ---" \
    --bootappend-failsafe "boot=casper username=lokro nomodeset quiet splash ---" \
    --iso-application "LokroOS $VERSION" --iso-preparer "LOKRO" \
    --iso-publisher "LOKRO" --iso-volume "LokroOS" 2>&1 | tee -a "$LOG"
fi

# lb 3.x: --bootloader kennt nur grub|syslinux|yaboot, doch der casper-faehige
# grub2-Pfad (lb_binary_grub2) laeuft nur mit LB_BOOTLOADER=grub2.
# ACHTUNG: lb liest mehrere Config-Dateien (spaetere gewinnen) – darum in
# common UND binary setzen, sonst baut der Legacy-Pfad (grub-legacy -> E:).
log "Bootloader auf grub2 zwingen …"
for cfg in config/common config/binary; do
  if grep -q '^LB_BOOTLOADER=' "$cfg" 2>/dev/null; then
    sed -i 's/^LB_BOOTLOADER=.*/LB_BOOTLOADER="grub2"/' "$cfg"
  else
    echo 'LB_BOOTLOADER="grub2"' >> "$cfg"
  fi
done
grep -h '^LB_BOOTLOADER=' config/common config/binary | sort -u | tee -a "$LOG"
[[ "$(grep -h '^LB_BOOTLOADER=' config/common config/binary | sort -u)" == 'LB_BOOTLOADER="grub2"' ]] \
  || fail "LB_BOOTLOADER-Override fehlgeschlagen (Abbruch, kein falsches ISO)"

# GRUB-Titel: übernimmt der Binary-Hook 0910-* (läuft nach lb_binary_grub2,
# vor lb_binary_iso) – siehe iso/live-build/hooks/. Hier nur Präsenz prüfen:
[[ -f config/hooks/0910-lokroos-grub-titles.binary ]] \
  || fail "GRUB-Binary-Hook fehlt im Buildbaum."

log "lb build (dauert je nach Netz/Maschine 30–90 Min) …"
lb build 2>&1 | tee -a "$LOG"
log "Fertig. ISO-Dateien:"
ls -la ./*.iso 2>&1 | tee -a "$LOG"
