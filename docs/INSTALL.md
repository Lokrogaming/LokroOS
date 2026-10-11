# LokroOS Installations- & Benutzerhandbuch

> Stand 2026-10-11 (v0.2.0). Die finale Endbenutzer-Installation (LokroOS-ISO → USB
> → Calamares) folgt mit der ISO-Pipeline. Der **VM-Weg (Abschnitt B)** ist der
> aktuell schnellste Weg zu einem laufenden LokroOS.

## A. Prototyp ausprobieren (jetzt möglich, ohne VM)

1. `shell/web-preview/index.html` im Browser öffnen.
2. Welcome-Animation abwarten (ca. 1,8 s, bei reduzierter Bewegung sofort Desktop).
3. Dashboard prüfen (Home-Fenster öffnet automatisch): Tabs schließen/wiederherstellen,
   Fenster minimieren/schließen, DE/EN-Umschalter, Uhr.

## B. LokroOS in Oracle VM VirtualBox (empfohlen für Tests)

### B0. Voraussetzungen (Host)

- Windows 10/11 Pro, **Admin-Rechte** (einmalig für die VirtualBox-Installation),
  mind. 8 GB freies RAM, ca. 60 GB freier Plattenplatz, Internet (5,1 GB ISO-Download).
- Hinweis: Das Agent-Terminal läuft **ohne** Admin – die Einrichtung braucht **einen**
  manuellen Start mit Admin (unten). Danach ist alles skriptgesteuert.

### B1. Host vorbereiten – Option 1: Skript (empfohlen)

In einer PowerShell **als Administrator**:

```powershell
cd C:\Users\lokro\projekte\lokroos
.\tools\setup-vm-host.ps1
```

Das Skript installiert VirtualBox (winget), lädt
`kubuntu-24.04.5-desktop-amd64.iso` (SHA256-geprüft), erstellt die VM
`LokroOS-Test` (8 GB RAM, 4 CPUs, 40 GB VDI, VMSVGA + 3D, NAT, Zwischenablage
bidirektional) und startet sie. Erneut laufen lassen ist ungefährlich
(Vorhandenes wird übersprungen; `-Recreate` baut neu).

### B1. Host vorbereiten – Option 2: manuell

1. VirtualBox ≥ 7.0 von virtualbox.org installieren (inkl. Extension Pack optional).
2. ISO laden: `https://cdimage.ubuntu.com/kubuntu/releases/24.04/release/kubuntu-24.04.5-desktop-amd64.iso`
   + `SHA256SUMS` aus demselben Verzeichnis; per `Get-FileHash -Algorithm SHA256` vergleichen.
3. Neue VM: Typ Linux / Version Ubuntu (64-bit); **8192 MB RAM, 4 CPUs, 128 MB Grafikspeicher**,
   Grafikcontroller **VMSVGA**, **3D-Beschleunigung an**, 40 GB VDI (dynamisch),
   Netzwerk **NAT**, Audio HDA, Zwischenablage + Drag'n'Drop **bidirektional**.
4. ISO als optisches Laufwerk einhängen, VM starten.

### B2. Kubuntu in der VM installieren

1. „Try or Install Kubuntu“ → **Install Kubuntu** (Normale Installation,
   „Drittanbieter-Software“ **an**, Updates beim Installieren: an).
2. Benutzer anlegen (eigener Name, kein Hersteller-Account nötig) → Neustart →
   ISO aushängen (Geräte → Optische Laufwerke → Medium entfernen).
3. Einloggen, Terminal öffnen, **Snapshot** anlegen (Maschine → Snapshot erstellen:
   `frisch-installiert`) – Rückfallpunkt vor der Provisionierung.
4. Optional: Gasterweiterungen (Geräte → Gasterweiterungen einlegen, dann in der VM
   `sudo apt install -y build-essential dkms && sudo /media/$USER/VBox_GAs_*/VBoxLinuxAdditions.run`).

### B3. LokroOS-Provisionierung (in der VM)

```bash
sudo apt update && sudo apt install -y git
git clone https://github.com/Lokrogaming/LokroOS.git && cd LokroOS
sudo ./iso/provision-lokroos.sh --dry-run   # zeigt nur, was passieren würde
sudo ./iso/provision-lokroos.sh             # fragt einmal um Bestätigung
/usr/lib/lokroos/lokroos-stats.py --check   # echte Werte prüfen
node --version && npm --version && wine --version
sudo reboot
```

Nach dem Neustart: SDDM-Login → Welcome-Gruß → Plasma-Desktop (Dashboard-Anbindung
der QML-Shell folgt in M2; `lokroos-stats.py --loop` liefert live JSON).

### B4. Testmatrix (bitte abhaken)

- [ ] Boot → Login → Welcome-Gruß erscheint
- [ ] `lokroos-stats.py --check` zeigt echte CPU/RAM/Net-Werte (+ GPU falls vorhanden)
- [ ] `node`, `npm`, `wine`, `git`, `gh`, `code` starten (Terminal + Launcher)
- [ ] Netzwerk + Audio funktionieren
- [ ] Updates via Discover / `sudo apt upgrade` laufen

### B5. Ehrliche Einschränkung: Wayland in VirtualBox

VMSVGA + 3D läuft mit Plasma-Wayland in VirtualBox 7.x alltagstauglich, aber nicht
perfekt. Bei Grafikfehlern: am SDDM-Login unten links die Sitzung auf
**„Plasma (X11)“** umstellen und dort testen – Bug dann bitte mit Sitzungsart melden.

## C. ISO-Installation (geplant, ISO-Pipeline)

1. ISO von GitHub-Releases laden, Checksumme prüfen.
2. USB-Stick mit Balena Etcher / `dd` erstellen.
3. Vom USB booten → „LokroOS ausprobieren“ (Live) oder „Installieren“ (Calamares).
4. Sprache (DE/EN), Zeitzone, Benutzer anlegen – **kein Hersteller-Account nötig**.
5. Nach Neustart: SDDM-Login → Welcome-Gruß → Plasma-Desktop mit LokroOS-Shell.

## D. Windows-Programme (Wine-Leitfaden, sicher)

- `.exe` **nicht** doppelklicken-assoziieren. Stattdessen: Rechtsklick → „Mit Wine ausführen“
  oder in **Bottles** eine Flasche anlegen und die `.exe` dort starten.
- Downloads als potenziell unsicher behandeln; nur vertrauenswürdige Quellen.
- Anti-Cheat-Spiele (Vanguard, manche EAC-Titel) laufen unter Linux ggf. nicht – Steam zeigt
  Kompatibilität (ProtonDB) vor dem Kauf prüfen.

## E. VPN (optional)

ProtonVPN aus dem Launcher öffnen, in der offiziellen App anmelden, verbinden.
Ohne VPN funktioniert LokroOS vollständig normal.
