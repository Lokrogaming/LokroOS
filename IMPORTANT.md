# LokroOS IMPORTANT.md – Kritische Regeln (kompakt, zuerst lesen!)

Stand: 2026-10-11 · Version 0.1.0. Diese Datei ist **verbindlich** und geht im Zweifel vor.

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

- Host ist **Windows 11** ohne WSL-Distro/Docker/VM: ISO-Build + Plasma-Sitzungstest sind `BLOCKED` bis Build-VM steht.
- Ubuntu 26.04 LTS existiert (26.04.1, 27.08.2026), Basis bleibt bewusst **24.04 LTS** (Tooling-Reife).
- QML-Shell + SDDM/Plymouth-Configs sind geschrieben, aber **UNVERIFIED** ohne echte Wayland-Sitzung.
