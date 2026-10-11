# LokroOS MAINTENANCE.md – Wartung und Updates

Stand: 2026-10-11.

## Updates (kein eigenes Update-System!)

- Desktop: **Plasma Discover** (PackageKit) für grafische Updates.
- Terminal: `sudo apt update && sudo apt upgrade`.
- Node: via NodeSource-Repo (`sudo apt upgrade nodejs`).
- Proton (Steam): Steam → Einstellungen → Kompatibilität; GE-Proton optional via ProtonUp-Qt.
- VS Code / gh: über ihre offiziellen APT-Repos wie alle Systempakete.

## Versionierung

- `VERSION`-Datei (SemVer) + Git-Tags (`v0.1.0`, …). Jede ISO trägt die Version im Dateinamen.
- Manifeste (`packages/*.json`) sind die versionierte Paketwahrheit; Änderungen nur per PR + `verify-manifests.py`.

## Backup vor Release

- `git tag vX.Y.Z && git push origin vX.Y.Z`; ISO + `.log` aus `iso/output/` an GitHub-Release hängen.
- Niemals Dev-Dateien oder Secrets ins Image (Audit: `.gitignore` + Manifest-Check im Build-Skript).
