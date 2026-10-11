# LokroOS IDEAS.md – Produktideen & Roadmap

> Unverbindliche Vorschläge vs. bestätigte Entscheidungen trennen. Status nur auf
> `umgesetzt` setzen, wenn implementiert **und** überprüft. Vor Neueinträgen auf
> Duplikate prüfen. Stand: 2026-10-11.

## Desktop & visuelles Design

- **LokroOS-Icon-Theme (Cyan-Line)** – eigene App-/System-Icons im Cyan-Linien-Stil.
  Nutzen: Identität. Abhängigkeit: Design-Tokens. Aufwand: groß. Priorität: mittel. Status: Idee.
- **Dynamische Akzentfarbe** – Cyan ↔ Hellblau ↔ Systemfarbe wählbar.
  Nutzen: Personalisierung ohne Identitätsverlust. Aufwand: klein. Priorität: niedrig. Status: Idee.
- **4K-/HiDPI-Auto-Skalierung** – Profil-Presets für 100/150/200 %.
  Nutzen: Schärfe auf allen Displays. Aufwand: mittel. Priorität: mittel. Status: Idee.

## Animationen & Nutzererlebnis

- **Welcome mit System-Sound** – dezenter Klang + Reveal, abschaltbar.
  Nutzen: Premium-Gefühl. Aufwand: klein. Priorität: niedrig. Status: Idee.
- **Fenster-Reveal-Animation** – sanftes Einblenden nach Welcome.
  Nutzen: flüssiger Übergang. Aufwand: mittel (KWin-Effekte). Priorität: niedrig. Status: Idee.

## Gaming & Windows-Kompatibilität

- **ProtonUp-Qt vorinstallieren** – GE-Proton-Updates per Klick.
  Nutzen: aktuelle Kompatibilität. Aufwand: klein. Priorität: hoch. Status: geplant.
- **Bottles-Standardflaschen** – Gaming-/Office-Presets.
  Nutzen: einfacher Wine-Workflow. Aufwand: mittel. Priorität: mittel. Status: Idee.
- **MangoHud-Profile** – FPS-Overlay-Presets pro Spiel.
  Nutzen: Performance-Sichtbarkeit. Aufwand: klein. Priorität: niedrig. Status: Idee.

## Entwicklerwerkzeuge

- **Dev-Umgebungs-Setup-Assistent** – Git/gh/VS-Code/Node-Erstkonfiguration per GUI.
  Nutzen: Onboarding. Aufwand: mittel. Priorität: mittel. Status: Idee.
- **Container-Tooling (Docker/Podman)** – optionales Profil im Installer.
  Nutzen: moderne Dev-Workflows. Aufwand: mittel. Priorität: mittel. Status: Idee.

## Netzwerk & VPN

- **VPN-Status in Systemübersicht** – lesende Anzeige (Kill-Switch-Status optional lesend).
  Nutzen: Sichtbarkeit ohne Secret-Handling. Aufwand: klein. Priorität: mittel. Status: geplant.

## Systemverwaltung

- **Stats-Dashboard (CPU/RAM/GPU/Netz/Tasks, Tabs schließ-/minimierbar)** – Backend
  `shell/stats/lokroos-stats.py` + Preview-Dashboard fertig und Linux-verifiziert.
  Nutzen: Systemübersicht (Kap. 8 Pflicht). Aufwand: mittel. Priorität: hoch.
  Status: umgesetzt (Backend + Preview), QML-Anbindung in Arbeit.
- **LokroOS-Info-Center** – Version (LokroOS+Ubuntu), Speicher, Hardware, Update-Shortcuts.
  Nutzen: Übersicht (Kap. 8 Pflicht). Aufwand: mittel. Priorität: hoch. Status: geplant.
- **Treiber-Assistent** – `ubuntu-drivers`-Frontend (NVIDIA nur bei HW-Nachweis).
  Nutzen: sichere Treiberwahl. Aufwand: mittel. Priorität: mittel. Status: Idee.

## Installer & ISO

- **Calamares-LokroOS-Brand + QML-Slideshow** – `installer/calamares/lokroos/` steht
  (branding.desc, show.qml API 2, DE/EN). Nutzen: eigener Install-Screen.
  Aufwand: mittel. Priorität: hoch. Status: in Arbeit (Abnahme per `calamares -c` fehlt).
- **Plymouth-LokroOS-Theme + GRUB-Branding** – Theme-Dateien generiert, installierter
  GRUB schlicht gebrandet. Nutzen: Boot-Identität. Aufwand: klein. Priorität: hoch.
  Status: umgesetzt (Dateien + Tests), VM-Reboot-Test in Arbeit.
- **Unbeaufsichtigte OEM-Installation** – Preseed-Profil für Flotten.
  Nutzen: Deployments. Aufwand: mittel. Priorität: niedrig. Status: Idee.
- **Delta-Updates für ISO** – zsync-Torrents für Releases.
  Nutzen: Bandbreite. Aufwand: mittel. Priorität: niedrig. Status: Idee.

## Performance & Sicherheit

- **Härtungs-Profil** – Firewall-Default, unattended-upgrades, Secure-Boot-Doku.
  Nutzen: Sicherheit out-of-box. Aufwand: mittel. Priorität: hoch. Status: geplant.
- **Gamemode-Auto-Profil** – Spieleliste mit Auto-Optimierung.
  Nutzen: FPS. Aufwand: klein. Priorität: niedrig. Status: Idee.

## Personalisierung & Barrierefreiheit

- **Kontrast-/Reduzierte-Bewegung-Profile** – ein-Klick-Barrierefreiheit.
  Nutzen: Zugänglichkeit. Aufwand: klein. Priorität: mittel. Status: Idee.
- **DE/EN-Live-Umschaltung** – Shell-Sprache ohne Re-Login.
  Nutzen: Mehrsprachigkeit. Aufwand: klein. Priorität: niedrig. Status: Idee.

## Langfristige Distribution

- **ARM64-Port** – Raspberry-Pi-/ARM-Laptop-Image.
  Nutzen: Reichweite. Aufwand: groß. Priorität: niedrig. Status: Idee.
- **26.04-Rebase evaluieren** – nach M2-Stabilität Tooling auf Resolute prüfen.
  Nutzen: Langzeit-Support bis 2031. Aufwand: groß. Priorität: mittel. Status: geplant.
