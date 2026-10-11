# LokroOS Installations- & Benutzerhandbuch (M1-Vorabstand)

> Die finale Endbenutzer-Installation (ISO → USB → Calamares) folgt mit M2.
> Dieses Dokument beschreibt den **Prototyp-Start** und die geplanten ISO-Schritte.

## A. Prototyp ausprobieren (jetzt möglich)

1. `shell/web-preview/index.html` im Browser öffnen.
2. Welcome-Animation abwarten (ca. 1,8 s, bei reduzierter Bewegung sofort Desktop).
3. Launcher durchsuchen, DE/EN-Umschalter testen, Uhr und Schnelleinstellungen prüfen.

## B. ISO-Installation (geplant, M2)

1. ISO von GitHub-Releases laden, Checksumme prüfen.
2. USB-Stick mit Balena Etcher / `dd` erstellen.
3. Vom USB booten → „LokroOS ausprobieren“ (Live) oder „Installieren“ (Calamares).
4. Sprache (DE/EN), Zeitzone, Benutzer anlegen – **kein Hersteller-Account nötig**.
5. Nach Neustart: SDDM-Login → Welcome-Gruß → Plasma-Desktop mit LokroOS-Shell.

## C. Windows-Programme (Wine-Leitfaden, sicher)

- `.exe` **nicht** doppelklicken-assoziieren. Stattdessen: Rechtsklick → „Mit Wine ausführen“
  oder in **Bottles** eine Flasche anlegen und die `.exe` dort starten.
- Downloads als potenziell unsicher behandeln; nur vertrauenswürdige Quellen.
- Anti-Cheat-Spiele (Vanguard, manche EAC-Titel) laufen unter Linux ggf. nicht – Steam zeigt
  Kompatibilität (ProtonDB) vor dem Kauf prüfen.

## D. VPN (optional)

ProtonVPN aus dem Launcher öffnen, in der offiziellen App anmelden, verbinden.
Ohne VPN funktioniert LokroOS vollständig normal.
