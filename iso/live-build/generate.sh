#!/usr/bin/env bash
# LokroOS live-build Generator: baut aus Repo-Quellen einen lb-Buildbaum.
#   ./iso/live-build/generate.sh --root <repo> --out <build-dir>
# Erzeugt: config/package-lists/lokroos.list.chroot (Manifeste + Extras, dedup),
# config/includes.chroot/opt/lokroos/ (Brand-Quellen), config/hooks/ (Hooks flach).
# Aendert nichts am Repo, nur im Build-Verzeichnis. Idempotent (leert Ziel zuerst).
set -euo pipefail

ROOT=""; OUT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) ROOT="$2"; shift 2;;
    --out) OUT="$2"; shift 2;;
    -h|--help) sed -n '1,6p' "$0"; exit 0;;
    *) echo "Unbekannte Option: $1" >&2; exit 2;;
  esac
done
[[ -n "$ROOT" && -n "$OUT" ]] || { echo "--root und --out sind Pflicht." >&2; exit 2; }
[[ -f "$ROOT/VERSION" ]] || { echo "Kein Repo-Root: $ROOT" >&2; exit 2; }

log() { echo "[lokroos-generate] $*"; }
VERSION="$(cat "$ROOT/VERSION")"

log "Version $VERSION – Buildbaum: $OUT"
rm -rf "$OUT/config"
mkdir -p "$OUT/config/package-lists" "$OUT/config/includes.chroot/opt/lokroos" \
  "$OUT/config/hooks"

# --- 1. Paketliste aus Manifesten + Extras - Excludes (eine Wahrheit) ---
python3 "$ROOT/iso/live-build/make_packagelist.py" "$ROOT" \
  "$OUT/config/package-lists/lokroos.list.chroot"

# --- 2. Brand-Quellen für den Chroot-Hook ---
for d in branding config installer shell packages; do
  cp -r "$ROOT/$d" "$OUT/config/includes.chroot/opt/lokroos/"
done
cp "$ROOT/VERSION" "$OUT/config/includes.chroot/opt/lokroos/"

# --- 3. Hooks flach nach config/hooks/ (lb-3.x-Pfade: *.chroot,
# *.chroot_early, *.binary – KEIN normal/-Unterverzeichnis!) ---
cp "$ROOT/iso/live-build/hooks/"* "$OUT/config/hooks/"
chmod +x "$OUT/config/hooks/"*.chroot "$OUT/config/hooks/"*.chroot_early \
  "$OUT/config/hooks/"*.binary

log "Fertig: $(wc -l < "$OUT/config/package-lists/lokroos.list.chroot") Paketzeilen."
