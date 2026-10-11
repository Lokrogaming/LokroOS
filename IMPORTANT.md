# LokroOS IMPORTANT.md – Kritische Regeln (kompakt, zuerst lesen!)

Stand: 2026-10-11 · Version 0.4.0. Diese Datei ist **verbindlich** und geht im Zweifel vor.

## 1. Hostschutz (nicht verhandelbar)

- **Niemals** Bootloader, Partitionen oder Netzwerk des Entwickler-PCs anfassen.
- ISO-Builds **nur** auf Ubuntu-24.04-Build-VM (`iso/build-iso.sh` erzwingt das per Guard).
- Vor irreversiblen Aktionen: anhalten + Bestätigung einholen.

## 2. Secrets

- **Keine** API-Keys, Tokens, Passwörter in Code, Docs oder Commits.
- `gh` ist mit Keyring-Auth (`Lokrogaming`) eingerichtet – Token nie auslesen/einbetten.
- VPN-/Store-Credentials verwaltet ausschließlich die jeweilige offizielle App.

## 3. Wayland / Plasma-Fallen (verifiziert relevant)

- KDE-Panel **nicht** duplizieren: LokroOS-Profil = Auto-Hide, Shell = Single-Instance (`flock`).
- Welcome-Overlay ist **modelless** und darf den Desktop nie blockieren (Fail-safe Exit 0).
- `prefers-reduced-motion` / `LOKROOS_NO_ANIM=1` → Animationen überspringen.
- Username nur via `text:` binden (QML) / `textContent` (JS) – **nie** als HTML.

## 4. Paket-/Treiber-Regeln

- **Eine** Node-Version (NodeSource 22 LTS + gebündeltes npm), kein nvm-Mix im Image.
- NVIDIA-Treiber **nur** bei erkannter NVIDIA-Hardware (`ubuntu-drivers`), nie blind.
- Keine `.exe`-Auto-Assoziation (Test `test_no_exe_autoassoc` wacht darüber).
- Kein eigenes Update-System – PackageKit/Discover + APT bleiben zuständig.

## 5. Doku-Pflege (verbindlicher Prozess)

- Architektur/Schnittstellen/Build/Feature-Status ändern → `AGENTS.md` aktualisieren.
- Idee priorisiert/begonnen/umgesetzt/verworfen → `IDEAS.md` aktualisieren.
- Neues kritisches Risiko / neue Sicherheitsregel → **diese Datei** aktualisieren.
- Veraltete Warnungen mit Datum entfernen, sobald nachweislich behoben.

## 6. Aktuelle verifizierte Risiken (2026-10-11)

- WSL-`Ubuntu-24.04` läuft (Backends Linux-verifiziert); **Plasma-Sitzungstest,
  Installer-Abnahme und ISO-Boot** brauchen weiter die Nutzer-VM mit Display.
- Ubuntu 26.04 LTS existiert (26.04.1, 27.08.2026), Basis bleibt bewusst **24.04 LTS** (Tooling-Reife).
- QML-Shell + SDDM/Plymouth/Calamares-Abnahme sind geschrieben, aber **UNVERIFIED**
  ohne echte Wayland-Sitzung. Es existiert **kein** bootfähiges LokroOS-ISO –
  das wird behauptet erst, wenn die VM-Boot-Matrix grün ist.

## 7. Installer- und Identitätssicherheit

- Installer: **nie** ohne bestätigte Änderungsübersicht (Schritt 5 der
  `installer/INSTALLER_SPEC.md`) formatieren; nur in VMs testen.
- Kein CasaOS-Code, kein CasaOS-Clone: nur übernommene Prinzipien
  (`docs/DESIGN_CASAOS.md`), eigene Tokens/Icons/Typo.
- Funktionsversprechen einhalten: Preview-Schalter ohne Backend tragen `Demo`,
  QML ohne Backend fehlt – nie umgekehrt.
- Light Mode: Kontrast 4.5:1 für Sekundärtext in beiden Paletten wahren.
