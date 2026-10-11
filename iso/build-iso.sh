#!/usr/bin/env bash
# LokroOS ISO-Build – reproduzierbarer Ubuntu-Live-Build (läuft NUR auf Ubuntu 24.04, NIE auf dem Dev-Host direkt).
# - Verwendet Cubic (Prototyp, interaktiv) ODER live-build (automatisiert, bevorzugt ab M2).
# - Erkennt fehlende Root-Rechte / falsches OS früh, fragt vor irreversiblen Schritten.
# - Schreibt Logs nach iso/output/, versionierte Abhängigkeiten via packages/manifest-*.json.
# Gebrauch (auf Ubuntu-Build-VM): sudo ./iso/build-iso.sh --profile noble --out iso/output
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/iso/output"
PROFILE="noble"
VERSION="$(cat "$ROOT/VERSION" 2>/dev/null || echo 0.1.0)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile) PROFILE="${2:-noble}"; shift 2;;
    --out) OUT="$2"; shift 2;;
    -h|--help) sed -n '1,12p' "$0"; exit 0;;
    *) echo "Unbekannte Option: $1" >&2; exit 2;;
  esac
done

log() { echo "[lokroos-build] $*"; }
fail() { echo "[lokroos-build][FEHLER] $*" >&2; exit 1; }

# --- Guards: kein destruktiver Host-Eingriff ---
if [[ "$(uname -s)" != "Linux" ]]; then
  fail "ISO-Build nur auf Linux (Ubuntu 24.04-Build-VM). Aktuell: $(uname -s). Siehe BUILD.md."
fi
if [[ "$(id -u)" -ne 0 ]]; then
  fail "Bitte mit Root-Rechten auf der Build-VM starten (sudo). Host-Bootloader wird nie angefasst."
fi
if ! grep -qi "ubuntu" /etc/os-release 2>/dev/null; then
  fail "Kein Ubuntu-Build-Host (/etc/os-release). Abgebrochen – keine Änderungen vorgenommen."
fi

mkdir -p "$OUT"
LOG="$OUT/build-$VERSION-$PROFILE-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$LOG") 2>&1

log "LokroOS $VERSION – Profil $PROFILE – Log: $LOG"
log "Manifeste prüfen …"
python3 "$ROOT/scripts/verify-manifests.py" --root "$ROOT"

# Werkzeugwahl dokumentieren: Cubic für Prototyp, live-build für Releases
if command -v lb >/dev/null 2>&1; then
  log "live-build gefunden – automatisierter Build (Implementierung M2, hier Vorab-Check OK)."
else
  log "HINWEIS: 'lb' (live-build) nicht installiert. Für M1-Prototyp: Cubic auf der Build-VM nutzen (siehe BUILD.md)."
  log "Abbruch ohne Änderungen – installiere live-build oder nutze Cubic manuell."
  exit 3
fi

log "Build-Implementierung (live-build-Pipeline) folgt in Meilenstein 2. Guards + Manifest-Check: OK."
