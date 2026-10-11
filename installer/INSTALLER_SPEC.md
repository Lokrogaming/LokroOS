# LokroOS Installer-Spezifikation (10 Schritte → Calamares-Module)

Stand: 2026-10-11 · Status: `PARTIAL` (Brand + Slideshow vorhanden, Abnahme in VM fehlt).
Der Installer ist Teil des LokroOS-Projekts (eigenes Brand, eigene Slideshow, eigene
Defaults) und nutzt darunter bewährte Calamares-Module – keine Low-Level-Neuimplementierung.

## Schritt-Mapping (verbindlich für das Brand)

| # | LokroOS-Schritt | Calamares-Modul | LokroOS-Anpassung |
|---|---|---|---|
| 1 | Willkommen + Sprache | `welcome` | Brand-Strings DE/EN, `de_DE`-Default, LokroOS-Logo |
| 2 | Hardware- + Voraussetzungsprüfung | `welcome` (Requirements-Check) | min. RAM/Platte/UEFI-Check, klare Fehltexte DE/EN |
| 3 | Lizenz- + Installationsinfo | `license` (optional) / Welcome-Text | eigene Lizenzinfo, Link auf Release Notes |
| 4 | Laufwerk + Partitionierung | `partition` | Default: geführte Installation; manuell für Experten |
| 5 | Änderungsübersicht vor Bestätigung | `summary` | **Pflicht**: destruktive Aktionen rot markiert, Bestätigungs-Checkbox |
| 6 | Basissystem + Pakete installieren | `unpackfs`, `packages` | `packages/manifest-*.json` als Paketwahrheit |
| 7 | Benutzerkonto | `users` | kein Hersteller-Account, sudo-Gruppe, starke-Passwort-Hinweise |
| 8 | Zeitzone/Sprache/Tastatur | `locale`, `keyboard`, `timezone` | Defaults aus Schritt 1 übernehmen |
| 9 | Bootloader | `bootloader`, `grubcfg` | GRUB mit `GRUB_DISTRIBUTOR=LokroOS` (vgl. `config/grub/`) |
| 10 | Abschluss + Neustart | `finished` | LokroOS-Slideshow-Ende, „Jetzt neu starten“, Log-Hinweis |

## Sicherheitsregeln (nicht verhandelbar)

- **Nie** ohne ausdrückliche Bestätigung (Schritt 5) formatieren/partitionieren.
- Bei Fehlern: kontrollierter Abbruch + Log (`/var/log/calamares/` bzw. Installer-Log
  in der Live-Session sichern) – kein stilles Weiterlaufen.
- **Nur in VMs testen**, bis die Matrix in `docs/INSTALL.md` vollständig abgehakt ist.
- Bootloader-Installation validieren (Schritt 9 schlägt bei EFI-Fehlern laut fehl).

## Technische Anbindung

- Brand: `installer/calamares/lokroos/` → `/etc/calamares/branding/lokroos/`
  (deployt `iso/provision-lokroos.sh` vollautomatisch, inkl. `settings.conf`-Backup).
- Test ohne ISO: `sudo calamares -c /etc/calamares/settings.conf` in der VM.
- Slideshow: `show.qml` (API 2, DE/EN via `Qt.locale()`, 8-s-Takt, Dots-Indikator).
