# LokroOS Designanalyse: CasaOS als Inspiration (keine Kopie)

Stand: 2026-10-11 · Quelle: öffentlich sichtbare CasaOS-Oberfläche und -Dokumentation
(casaos.io, GitHub IceWhaleTech/CasaOS, Apache-2.0). Keine CasaOS-Codeübernahme.

## Was CasaOS ist (Einordnung)

CasaOS ist eine **webbasierte Home-Server-Oberfläche** (Dashboard im Browser:
App-Kacheln, App-Store, Dateien, Terminal, System-Widgets). LokroOS ist ein
**Desktop-Betriebssystem für Entwickler und Gamer**. Das Home-Server-Konzept
(Server-Dashboard, Docker-Store) wird daher **nicht** übernommen – nur
Bedien- und Gestaltungsprinzipien, angepasst an einen vollständigen Desktop.

## Übernommene Prinzipien (mit LokroOS-Umsetzung)

| CasaOS-Prinzip | LokroOS-Umsetzung |
|---|---|
| Dashboard-first: alles Wichtige auf einer ruhigen Startfläche | Dashboard ist Home-Fenster nach Login (`shell/web-preview`, später QML) |
| Aufgeräumte App-Kacheln statt Menüverschachtelung | Launcher-Raster mit großen Kacheln, Suche, max. 1 Klick zum Start |
| Status auf einen Blick (CPU/RAM/Disk-Widgets) | Stats-Cards (CPU/RAM/GPU/Netz) + Taskliste, echte Daten via `lokroos-stats.py` |
| Dezente Transparenz, sanfte Hover, kurze Übergänge | Glassmorphism nur wo lesbar; Motion 120/220/380 ms, `prefers-reduced-motion` |
| Einheitliche Radien/Abstände/Typo | Tokens in `branding/tokens.json` (Single Source of Truth) |
| Ein-Klick-Aktionen statt Assistenten-Marathons | Provisionierung = 1 Befehl; Installer-Schritte mit sinnvollen Defaults |
| Responsive für viele Auflösungen | Grid + Skalierungs-Presets (100/150/200 %, siehe IDEAS.md) |

## Bewusst NICHT übernommen

- Browser/Web-App-Architektur für die Shell (LokroOS-Shell wird nativ: QML).
- Docker-App-Store als Desktop-Modell (stattdessen: APT/PackageKit + Steam/Proton/Wine-Workflows).
- Helle, verspielte CasaOS-Farbwelt (LokroOS: Anthrazit/Schwarz/Tiefblau + Cyan, eigene Icons/Typo).
- Reine Deko-Elemente ohne Funktion (Verbot: Glows/Animationen nur mit Zweck).

## Designregeln (verbindlich, ergänzt Tokens)

1. Dunkles Grunddesign, **Light Mode optional** (Tokens enthalten beide Paletten).
2. Glow/Blur sparsam: max. 1 Glow-Ebene pro Sicht, Blur nur auf Glass-Flächen.
3. Jedes Bedienelement mit Funktionsversprechen führt es aus – oder trägt
   sichtbar `Demo`/`M2-VM` (Preview) bzw. fehlt (QML), bis es implementiert ist.
4. Keine Riesen-Leerflächen: Karten füllen ihr Raster, max. 5 Launcher-Spalten.
5. Kontrast: Sekundärtext mindestens 4.5:1 auf Kartengrund (Dark + Light prüfen).
