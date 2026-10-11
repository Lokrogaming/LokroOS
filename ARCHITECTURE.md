# LokroOS ARCHITECTURE.md – Systemarchitektur

Stand: 2026-10-11 · Version 0.1.0.

## 1. Zielbild

```
┌──────────────────────────────────────────────────────┐
│ Boot (Plymouth lokroos) → Login (SDDM lokroos-sddm)  │
│ → Welcome-Overlay (lokroos-welcome, modelless)       │
│ → Plasma-Wayland + LokroOS-QML-Shell (Single-Inst.)  │
└──────────────────────────────────────────────────────┘
         │                    │                   │
   Plymouth-Theme        SDDM-Conf         Autostart-.desktop
   config/plymouth/      config/sddm/      shell/welcome/
```

Drei Phasen sind strikt getrennt (Boot-Splash ≠ Login ≠ Post-Login-Gruß).
Jede Phase nutzt die passende Systemkomponente; ein Absturz der Welcome-Schicht
kann Login/Desktop **niemals** blockieren (Fail-safe: Exit 0, modelless Overlay,
`LOKROOS_NO_ANIM=1` und `prefers-reduced-motion` → sofort Desktop).

## 2. Komponenten & Verantwortlichkeiten

| Komponente | Pfad | Verantwortung | Schnittstellen |
|---|---|---|---|
| Design-Tokens | `branding/tokens.json` (+ `.css`) | Single Source of Truth (Farben, Radien, Motion) | QML, CSS, Docs |
| Web-Preview | `shell/web-preview/` | Ausführbarer M1-Prototyp (Glass Cards, Launcher, i18n DE/EN, Uhr, Toasts) | keine System-APIs (Browser) |
| Welcome-Backend | `shell/welcome/lokroos-welcome.py` | User via `getpass`, Sprache via `$LANG`, JSON-Payload | stdout-JSON → QML |
| Welcome-QML | `shell/welcome/welcome.qml` | Overlay (Fade/Reveal/Loader), `text:`-Binding (XSS-sicher) | Plasma-Autostart |
| Shell-QML | `shell/qml/Main|Taskbar|Launcher|SystemOverview.qml` | Taskbar, Launcher-Raster, System-Cards | D-Bus (NM), PipeWire, PackageKit, loginctl |
| System-Configs | `config/{plasma,sddm,plymouth}/` | Dark-Theme, Panel-AutoHide (kein Doppel-Panel), Login, Boot | Zielsystem `/etc` |
| Paketmanifeste | `packages/manifest-*.json` | Versionierte Paketlisten (base/dev/gaming/vpn) | `verify-manifests.py`, ISO-Build |
| ISO-Build | `iso/build-iso.sh` | Guards + Manifest-Check + live-build-Pipeline (M2) | Ubuntu-Build-VM |
| Skripte/Tests | `scripts/`, `tests/` | Env-Check, Manifest-/Token-Validierung, pytest (11 Tests) | CI, Pre-Build |

## 3. Kommunikation

- **Shell ↔ System:** ausschließlich native Schnittstellen (D-Bus/NetworkManager,
  PipeWire, PackageKit/Discover, `loginctl` via PolicyKit). Kein eigener Root-Daemon,
  kein konkurrierendes Update-System.
- **Welcome → Shell:** Einweg-JSON (`{user, lang, message, animations}`), kein Passwort,
  keine Secrets, keine Rückkanäle.
- **VPN:** App-Öffnung + lesender Status; Credentials verwaltet ausschließlich die
  offizielle ProtonVPN-App.
- **Gaming:** Steam (multiverse) + Proton-Updates via Steam; Wine nur über explizites
  „Mit Wine ausführen“ (keine `.exe`-Auto-Assoziation – per Test erzwungen).

## 4. Single-Instance & Panel-Regel

- Shell-Prozess genau einmal: `flock`-Wrapper (`lokroos-shell.sh`, M2) + Autostart-
  Bedingung `X-KDE-Autostart-after=panel`; bei Doppelstart beendet sich die zweite
  Instanz.
- KDE-Panel läuft im LokroOS-Profil auf **Auto-Hide**, damit `Taskbar.qml` nicht
  konkurriert (siehe `config/plasma/plasma-panel-note.conf`).

## 5. ISO-Trennung (M2)

Quell-Trennung: Shell-Code / Desktop-Config / Manifeste / Branding / Systemconfig /
Build-Skripte / Tests / Handbuch (Verzeichnisstruktur = Trennung). Live-System
(Casper) vs. installiertes System (Calamares-Postinstall); `.gitignore` + Audit
verhindern Dev-/Secret-Leaks ins Image.
