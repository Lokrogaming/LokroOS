#!/usr/bin/env bash
# LokroOS Build-Watchdog: startet `lb build` im Build-Root neu, bis ein ISO
# existiert oder die Versuche aufgebraucht sind. Hintergrund: Der Build starb
# 2x kommentarlos bei Chroot-APT-Laeufen (kein OOM/Platten/Fehler-Beleg) –
# statt jedes Mal von Hand neu zu starten, macht das diese Schleife.
# Gebrauch (abgekoppelt): setsid nohup ./watchdog.sh --work DIR --attempts 5 \
#   >> watchdog.log 2>&1 < /dev/null &
set -euo pipefail

WORK=""; ATTEMPTS=5
while [[ $# -gt 0 ]]; do
  case "$1" in
    --work) WORK="$2"; shift 2;;
    --attempts) ATTEMPTS="$2"; shift 2;;
    -h|--help) sed -n '1,9p' "$0"; exit 0;;
    *) echo "Unbekannte Option: $1" >&2; exit 2;;
  esac
done
[[ -n "$WORK" && -d "$WORK" ]] || { echo "--work <build-dir> fehlt." >&2; exit 2; }

cd "$WORK"
n=0
while [[ "$n" -lt "$ATTEMPTS" ]]; do
  if ls ./*.iso >/dev/null 2>&1; then
    echo "[watchdog] ISO vorhanden – fertig."
    ls -la ./*.iso
    exit 0
  fi
  n=$((n + 1))
  echo "[watchdog] Versuch $n/$ATTEMPTS – $(date '+%H:%M:%S')"
  if lb build >> "watchdog-attempt-$n.log" 2>&1; then
    echo "[watchdog] lb build Exit 0."
  else
    echo "[watchdog] lb build Exit $? – warte 30s, dann erneut."
    sleep 30
  fi
done
if ls ./*.iso >/dev/null 2>&1; then
  echo "[watchdog] ISO vorhanden – fertig."
  exit 0
fi
echo "[watchdog] FEHLER: nach $ATTEMPTS Versuchen kein ISO." >&2
exit 1
