#!/usr/bin/env bash
# LokroOS Provisionierung – verwandelt ein frisches Ubuntu 24.04 (Desktop/VM)
# in LokroOS: Node 22 LTS + npm (EINE Version), Wine/Wine32/Winetricks,
# Dev-Basis, LokroOS-Shell (Welcome, Stats, QML, Configs).
#
# Gebrauch IN DER VM (Ubuntu 24.04, mit sudo):
#   sudo ./iso/provision-lokroos.sh [--dry-run] [--yes]
#
# - --dry-run: zeigt nur, was passieren würde (ändert nichts).
# - Ohne --yes: fragt vor den APT-Eingriffen um Bestätigung.
# - Idempotent: kann mehrfach laufen; bereits Erledigtes wird übersprungen.
# - Guards: nur Linux + Ubuntu 24.04 + Root; sonst Abbruch OHNE Änderung.
set -euo pipefail

DRY_RUN=0
ASSUME_YES=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --yes) ASSUME_YES=1 ;;
    -h|--help) sed -n '1,12p' "$0"; exit 0 ;;
    *) echo "Unbekannte Option: $arg" >&2; exit 2 ;;
  esac
done

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
log() { echo "[lokroos-provision] $*"; }
run() { if [[ "$DRY_RUN" -eq 1 ]]; then echo "  [dry-run] $*"; else "$@"; fi; }
fail() { echo "[lokroos-provision][FEHLER] $*" >&2; exit 1; }

# --- Guards (niemals auf falschem System loslaufen) ---
[[ "$(uname -s)" == "Linux" ]] || fail "Nur Linux (Ubuntu 24.04 in VM). Aktuell: $(uname -s)"
[[ "$(id -u)" -eq 0 ]] || fail "Bitte mit sudo starten: sudo ./iso/provision-lokroos.sh"
# shellcheck disable=SC1091
. /etc/os-release
[[ "${ID:-}" == "ubuntu" && "${VERSION_ID:-}" == "24.04" ]] \
  || fail "Erwartet Ubuntu 24.04, gefunden: ${ID:-?} ${VERSION_ID:-?}"

if [[ "$ASSUME_YES" -ne 1 && "$DRY_RUN" -ne 1 ]]; then
  echo "LokroOS-Provisionierung: Repos + Pakete (node, wine, dev-tools) installieren,"
  echo "Shell nach /usr/lib/lokroos + Autostart + Configs deployen. Fortfahren? [j/N]"
  read -r answer
  [[ "$answer" == "j" || "$answer" == "J" ]] || { log "Abgebrochen – keine Änderung."; exit 0; }
fi

log "Manifeste prüfen …"
run python3 "$ROOT/scripts/verify-manifests.py" --root "$ROOT"

# --- 32-Bit-Architektur (Steam/Wine/Proton brauchen i386) ---
if ! dpkg --print-foreign-architectures | grep -q i386; then
  log "Aktiviere i386-Architektur …"
  run dpkg --add-architecture i386
else
  log "i386 bereits aktiv."
fi

# --- Offizielle Fremd-Repos (mit Keyrings, keine Secrets) ---
add_repo() {  # $1=name $2=key-url $3=key-path $4=source-line
  if [[ -f "/etc/apt/sources.list.d/$1.sources" || -f "/etc/apt/sources.list.d/$1.list" ]]; then
    log "Repo $1 bereits vorhanden."
    return 0
  fi
  log "Richte Repo $1 ein …"
  if [[ "$DRY_RUN" -eq 1 ]]; then echo "  [dry-run] repo $1 <- $2"; return 0; fi
  curl -fsSL "$2" | gpg --dearmor -o "$3"
  chmod 644 "$3"
  echo "$4" > "/etc/apt/sources.list.d/$1.sources"
}
add_repo "nodesource" "https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key" \
  "/usr/share/keyrings/nodesource.gpg" \
  "Types: deb
URIs: https://deb.nodesource.com/node_22.x
Suites: nodistro
Components: main
Architectures: amd64
Signed-By: /usr/share/keyrings/nodesource.gpg"
add_repo "vscode" "https://packages.microsoft.com/keys/microsoft.asc" \
  "/usr/share/keyrings/vscode.gpg" \
  "Types: deb
URIs: https://packages.microsoft.com/repos/code
Suites: stable
Components: main
Architectures: amd64
Signed-By: /usr/share/keyrings/vscode.gpg"
add_repo "gh-cli" "https://cli.github.com/packages/githubcli-archive-keyring.gpg" \
  "/usr/share/keyrings/githubcli.gpg" \
  "Types: deb
URIs: https://cli.github.com/packages
Suites: stable
Components: main
Architectures: amd64
Signed-By: /usr/share/keyrings/githubcli.gpg"

log "Paketlisten aktualisieren …"
run apt-get update

# --- Kern-Installation: Node/npm + Wine + Dev-Basis (Fokus dieser Iteration) ---
CORE_PKGS=(nodejs git gh code build-essential python3 python3-venv python3-pip
  curl wget unzip openssh-client wine64 wine32 winetricks mesa-vulkan-drivers
  vulkan-tools gamemode mangohud konsole)
log "Installiere Kern-Pakete: ${CORE_PKGS[*]}"
# shellcheck disable=SC2068
run apt-get install -y ${CORE_PKGS[@]}

# --- Verifikation (Versionsmatrix, node+npm müssen zusammenpassen) ---
log "Verifiziere …"
for cmd in "node --version" "npm --version" "git --version" "gh --version" \
           "code --version" "python3 --version" "wine --version" \
           "winetricks --version"; do
  if [[ "$DRY_RUN" -eq 1 ]]; then echo "  [dry-run] $cmd"; else $cmd || fail "$cmd fehlgeschlagen"; fi
done

# --- LokroOS-Shell deployen ---
LIB="/usr/lib/lokroos"
log "Deploye Shell nach $LIB …"
run mkdir -p "$LIB" /etc/sddm.conf.d /etc/plymouth /etc/skel/.config/autostart \
  /usr/share/plasma/look-and-feel /usr/share/lokroos
run cp "$ROOT/shell/welcome/lokroos-welcome.py" "$ROOT/shell/stats/lokroos-stats.py" "$LIB/"
run chmod 755 "$LIB/lokroos-welcome.py" "$LIB/lokroos-stats.py"
run cp "$ROOT/shell/welcome/lokroos-welcome.desktop" /etc/skel/.config/autostart/
run cp "$ROOT/config/sddm/lokroos.conf" /etc/sddm.conf.d/
run cp "$ROOT/config/plymouth/plymouthd.conf" /etc/plymouth/
run cp -r "$ROOT/shell/qml" /usr/share/lokroos/
run cp "$ROOT/branding/lokroos-logo.svg" /usr/share/lokroos/
run cp "$ROOT/config/plasma/kdeglobals" /etc/skel/.config/

# --- Boot-Branding: Plymouth-Theme + installierter GRUB + Calamares-Brand ---
THEME_SRC="$ROOT/config/plymouth/themes/lokroos"
if [[ -f "$THEME_SRC/lokroos.plymouth" ]]; then
  log "Deploye Plymouth-Theme …"
  run mkdir -p /usr/share/plymouth/themes/lokroos
  run cp "$THEME_SRC/"lokroos.plymouth "$THEME_SRC/"lokroos.script \
    "$THEME_SRC/"logo.png "$THEME_SRC/"bar.png "$THEME_SRC/"box.png \
    /usr/share/plymouth/themes/lokroos/
  if command -v plymouth-set-default-theme >/dev/null 2>&1; then
    run plymouth-set-default-theme -R lokroos
  else
    log "WARN: plymouth nicht vorhanden – Theme nur abgelegt."
  fi
fi
log "Setze installierten GRUB auf LokroOS …"
run mkdir -p /etc/default/grub.d
run cp "$ROOT/config/grub/installed-lokroos.cfg" /etc/default/grub.d/lokroos.cfg
if command -v update-grub >/dev/null 2>&1; then
  run update-grub
else
  log "WARN: update-grub nicht vorhanden (z.B. Container/WSL ohne Bootloader)."
fi
if [[ -d /etc/calamares ]]; then
  log "Deploye Calamares-Brand …"
  run mkdir -p /etc/calamares/branding/lokroos
  run cp "$ROOT/installer/calamares/lokroos/branding.desc" \
    "$ROOT/installer/calamares/lokroos/show.qml" \
    "$ROOT/installer/calamares/lokroos/logo.svg" \
    /etc/calamares/branding/lokroos/
  run cp /etc/calamares/settings.conf /etc/calamares/settings.conf.lokroos-bak
  if grep -q '^branding:' /etc/calamares/settings.conf; then
    run sed -i 's/^branding:.*/branding: lokroos/' /etc/calamares/settings.conf
  else
    run bash -c 'echo "branding: lokroos" >> /etc/calamares/settings.conf'
  fi
else
  log "WARN: /etc/calamares fehlt – Brand übersprungen (Calamares-Paket nötig)."
fi

log "Fertig. Neustarten, einloggen → Welcome-Gruß → Dashboard (Home)."
log "Stats prüfen: /usr/lib/lokroos/lokroos-stats.py --check"
