# Calamares-LokroOS-Brand – Integration (für ISO-Build + Provisionierung)

## Dateien

- `branding.desc` – Produktname, Version, Links, Slideshow (`show.qml`, API 2),
  Sidebar-Farben. Konservative Schlüssel (Calamares 3.3 auf Noble).
- `show.qml` – Slideshow (QtQuick 2.15, passt zu Calamares auf Ubuntu 24.04).
  Sprache zur Laufzeit via `Qt.locale()` (DE/EN, kein .ts/.qm-Pipeline nötig für v1).
- `logo.svg` – Kopie von `branding/lokroos-logo.svg` (eine Quelle, hier gespiegelt).

## Einbindung (macht `iso/provision-lokroos.sh` automatisch)

1. Verzeichnis nach `/etc/calamares/branding/lokroos/` kopieren.
2. In `/etc/calamares/settings.conf` (Backup!) den Schlüssel `branding:` auf
   `lokroos` setzen – die Kubuntu-Modulsequenz bleibt unangetastet (kein Fork).
3. Test ohne ISO-Neubau: `sudo calamares -c /etc/calamares/settings.conf`.

## Warum kein komplettes settings.conf im Repo?

Die Modulsequenz hängt von der installierten Calamares-Version ab. Eine
handgeschriebene Komplettdatei würde beim nächsten Calamares-Update brechen.
Chirurgisches Patchen des `branding:`-Schlüssels ist robust – siehe Provisionsskript.
