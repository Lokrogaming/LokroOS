# LokroOS ARCHITECTURE.md – Systemarchitektur (ehrlicher Stand)

Stand: 2026-10-11 · Version 0.3.0.

## 0. Leseanweisung: vier Schichten, vier Wahrheiten

LokroOS besteht aus vier klar getrennten Schichten. Wer sie vermischt („die Webseite
*ist* das OS“), trifft falsche Entscheidungen. Verbindliche Begriffe:

| # | Schicht | Was sie ist | Was sie NICHT ist | Code im Repo |
|---|---|---|---|---|
| 1 | **Visueller Prototyp (Web)** | Design-Referenz im Browser: Layout, Tabs, Charts, Animationen, DE/EN – mit **simulierten** Daten | Kein Betriebssystem, kein Systemzugriff, fließt **nie** in die ISO | `shell/web-preview/` (HTML/CSS/JS) |
| 2 | **Native Desktop-Shell (QML)** | Echte Shell **in** der Plasma-Wayland-Sitzung: Taskbar, Launcher, Dashboard – mit echten System-APIs | Keine Webseite, kein Electron, kein Ersatz für Plasma/KWin | `shell/qml/`, `shell/welcome/welcome.qml` |
| 3 | **Linux-Desktop & Systemdienste** | Stock-Ubuntu 24.04 (Kernel, systemd, SDDM, Plasma 5.27, PipeWire, NetworkManager, APT/PackageKit) + unsere **nativen Backends** (Python) + Configs | Kein Custom-Kernel (Vorgabe), kein eigenes Update-System, keine Root-Daemons | `shell/welcome/*.py`, `shell/stats/*.py`, `config/` |
| 4 | **Bootfähige Distribution** | ISO (Live/Casper + Calamares-Installer) aus reproduzierbarem Build; Abkürzung für VM-Tests: Provisionierungsskript | Kein manuell zusammengeklicktes Image | `iso/build-iso.sh`, `iso/provision-lokroos.sh`, `packages/` |

**Sprachregeln (verbindlich):** HTML/CSS/JS nur für Schicht 1 (und ggf. klar
abgegrenzte Webkomponenten) – niemals Shell-Kern, niemals Electron-Laufzeit.
Python für Schicht 3 (native Backends) sowie Tests/Build-Helfer. Bash für
Provisionierung/Build. QML (+ C++ nur bei Bedarf, siehe §3) für Schicht 2.

## 1. Real vs. simuliert – Belegmatrix (keine Behauptung ohne Beleg)

| Komponente | Status | Beleg |
|---|---|---|
| Design-Tokens | `IMPLEMENTED` | `validate-tokens.py` grün |
| Preview: Layout, Fenster, Tabs (close/min), Charts, i18n | `IMPLEMENTED` (als Preview) | Struktur-Tests grün; **Daten simuliert** (Badge „Preview-Simulation“) |
| Welcome-Backend (`lokroos-welcome.py`) | `IMPLEMENTED` + **Linux-verifiziert** | WSL Ubuntu 24.04.5: `{"user":"root","lang":"de",…}`; 6 Tests auf Win **und** Linux grün |
| Stats-Backend (`lokroos-stats.py`) | `IMPLEMENTED` + **Linux-verifiziert** | WSL: 16 Kerne, 4,9 % RAM, `eth0`, **RTX 4060 via nvidia-smi erkannt** (6 %/1199 MB); 8 Tests Win+Linux grün |
| QML-Shell (Main/Taskbar/Launcher/SystemOverview/Dashboard) | `PARTIAL`, Sitzung `UNVERIFIED` | Code vorhanden; Imports (`QtQuick 2.15`) passen zu Qt 5.15.13 auf Noble (apt-Beleg §3); kein Sitzungstest |
| Plymouth-Theme (`themes/lokroos/`) | `IMPLEMENTED`, Ziel `UNVERIFIED` | Assets deterministisch generiert (`render-assets.py --check` grün), 6 Boot-Tests; VM-Reboot-Test ausstehend |
| GRUB (ISO-Snippet schlicht + installierte Config) | `IMPLEMENTED`, Ziel `UNVERIFIED` | Einträge „Try or Install LokroOS“ als Vorlage; `GRUB_DISTRIBUTOR=LokroOS` per Provision |
| Calamares-Brand (`installer/calamares/lokroos/`) | `PARTIAL`, Ziel `UNVERIFIED` | `branding.desc` + `show.qml` (API 2, DE/EN) + Tests; `calamares -c`-Abnahme ausstehend |
| SDDM/Plasma-Configs | `PARTIAL`, Ziel `UNVERIFIED` | Geschrieben, keine Zielsession |
| Paketmanifeste | `PARTIAL` | `verify-manifests.py` grün (38 Pakete); Installation erst per Provision |
| `provision-lokroos.sh` | `PARTIAL` | `bash -n` ok, `--dry-run` ok; Echtlauf in VM ausstehend |
| ISO/live-build-Pipeline | `PLANNED` | Nur Guards implementiert |

## 2. Zielbild (Schichten 2–4)

```
Boot (Plymouth „lokroOS“) → ISO-Menü („Try or Install LokroOS“, schlicht)
 → Login (SDDM) → Welcome-Overlay (modelless, Fail-safe)
 → Plasma-Wayland + LokroOS-QML-Shell (Single-Instance, Panel Auto-Hide)
```

Drei Phasen strikt getrennt (Boot ≠ Login ≠ Post-Login-Gruß). Welcome-Datenfluss:
Autostart → `lokroos-welcome.py` → stdout-JSON → `welcome.qml` (`text:`-Binding,
XSS-sicher). Stats-Datenfluss: QML-`executable`-Datenquelle, 2-s-Polling von
`lokroos-stats.py --once` → JSON → Cards/Charts (`--loop` für Streaming).
Privilegiertes ausschließlich via `loginctl`/PolicyKit/PackageKit. VPN nur
App-Öffnung + lesender Status. Wine nur explizit („Mit Wine ausführen“/Bottles),
keine `.exe`-Auto-Assoziation (per Test erzwungen).

## 3. Shell-Technologieentscheid (verifiziert 2026-10-11, `apt-cache` auf Ubuntu 24.04)

Belegte Paketstände (Noble): `plasma-workspace 4:5.27.12` (KF5/Plasma 5.27),
`qml-module-qtquick2 5.15.13` (QtQuick 2.x), `layer-shell-qt` (Paket vorhanden),
`plasma-workspace` inkl. Systemmonitor-Engine. **Fazit: Der QML-Weg ist machbar
mit Bordmitteln, ohne Fremd-PPAs.**

| Shell-Komponente | Umsetzung | System-API |
|---|---|---|
| Taskbar/Dock | QML + `LayerShellQt` (wl-layer-shell-Layer) | Wayland-Protokoll, kein Hack |
| Launcher-Raster | QML (`FolderListModel` über `/usr/share/applications`) | .desktop-Dateien, KRunner-kompatibel |
| Dashboard-Cards | QML + `systemmonitor`-DataEngine + `executable` (unser Stats-Skript) | Belegt: Engine in plasma-workspace enthalten |
| Netzwerk/Audio/Helligkeit | QML + DataEngines (NM, PulseAudio/PipeWire, powerdevil) | D-Bus, nativ |
| Power/Reboot/Shutdown | `loginctl` via D-Bus/PolicyKit | Kein Root-Prozess |
| Updates | PackageKit/Discover (Anzeige), APT (System) | Kein eigenes Update-System |

**C++-Urteil:** Aktuell **kein C++ erforderlich** – QML + Python deckt alle
M2/M3-Komponenten ab. C++ erst bei Bedarf: eigenes Plasmoid-Plugin mit
C++-Backend oder Performance-kritische Daemons. **Kein Custom-Kernel:**
Stock-Ubuntu-Kernel (Vorgabe, kein Assembly/Kernelbau).

**Qt6/Plasma-6-Pfad:** Erst beim 26.04-Rebase (M3+). QML-Code ohne Qt6-only-APIs
schreiben, damit der Port möglich bleibt.

## 4. Single-Instance & Panel-Regel (`UNVERIFIED`, Konzept steht)

- Shell-Prozess genau einmal: `flock`-Wrapper (`lokroos-shell.sh`, M2) +
  `X-KDE-Autostart-after=panel`; Zweitinstanz beendet sich.
- KDE-Panel im LokroOS-Profil auf **Auto-Hide**, damit `Taskbar.qml` nicht
  konkurriert (`config/plasma/plasma-panel-note.conf`).

## 5. Migrationsplan – schrittweise, kein Rewrite

1. **Schicht 1 einfrieren:** Preview bleibt Referenz; jede Designänderung erst in
   `tokens.json`, dann Preview, dann QML (eine Richtung, kein Drift).
2. **Schicht 3 in VM validieren:** `provision-lokroos.sh --dry-run` → Echtlauf
   (Node/Wine/Dev-Stack **+ Plymouth-Theme + GRUB + Calamares-Brand**), Welcome +
   Stats in echter Sitzung belegen; VM-Reboot zeigt LokroOS-Splash.
3. **Schicht 2 in Sitzung bringen:** QML via `qmlscene`/Plasma-Sitzung testen,
   `executable`-Quelle an `lokroos-stats.py` hängen, Taskbar auf LayerShell.
4. **C++ nur bei Lücke:** Falls QML irgendwo prinzipiell nicht hinkommt → kleines,
   begründetes C++-Modul (kein Framework-Umbau).
5. **Schicht 4 bauen:** Cubic-ISO in der VM (`iso/cubic-preset.json` als Vorlage:
   Boot-Einträge umbenennen, Chroot = Provision) + Calamares-Brand-Abnahme, dann
   live-build-Pipeline + VM-Boot-Matrix
   (Boot/Live/Installer/Login/Desktop/Apps/Updates/Netz/Audio). Live-Initrd-Splash
   bewusst später (Original-Initrd-Einschränkung, dokumentiert in `BUILD.md`).
6. **M3+:** 26.04-/Plasma-6-Rebase evaluieren.

**Stufenregel:** Ein Status wird erst auf `IMPLEMENTED` gehoben, wenn er auf dem
Zielsystem (VM/ISO) belegt ist – Preview-Tests belegen nur Schicht 1.

## 6. ISO-Trennung

Quell-Trennung = Verzeichnisstruktur (Shell / Configs / Manifeste / Branding /
Build / Tests / Handbuch). Live (Casper) vs. installiert (Calamares-Postinstall);
`.gitignore` + Audit verhindern Dev-/Secret-Leaks ins Image.
