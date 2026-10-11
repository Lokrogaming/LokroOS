#!/usr/bin/env python3
"""LokroOS Welcome-Erlebnis – zeigt nach Login „Willkommen zurück, {user}!“.

Design (verpflichtend):
- Username dynamisch via getpass.getuser(), KEIN Passwort-Handling.
- Sprache via $LANG (de/* → Deutsch, sonst Englisch).
- Keine künstlichen Wartezeiten, blockiert den Desktop nie.
- Bei reduzierten Animationen (GTK/Plasma reduce-animations Flag oder
  LOKROOS_NO_ANIM=1) sofort beenden (Exit 0), Desktop bleibt nutzbar.
- Jeder Fehler → still beenden (Exit 0), Login/Desktop funktionieren immer.
- Ausgabe als JSON auf stdout für die QML-Shell; Fallback: reines Textfenster.

Verwendung (Plasma-Autostart, siehe lokroos-welcome.desktop):
    lokroos-welcome.py [--no-anim] [--json-only]

Status: IMPLEMENTED (Logik), UNVERIFIED (echte Plasma-Wayland-Sitzung steht aus).
"""
import getpass
import json
import locale
import os
import sys


MESSAGES = {
    "de": "Willkommen zurück, {user}!",
    "en": "Welcome back, {user}!",
}


def detect_lang() -> str:
    """Systemsprache auswerten: de/* → de, alles andere → en."""
    try:
        lang = (os.environ.get("LANG") or os.environ.get("LANGUAGE") or "")
        if not lang:
            loc = locale.getlocale()[0] if hasattr(locale, "getlocale") else ""
            lang = loc or ""
        lang = lang.lower()
    except Exception:
        lang = ""
    return "de" if lang.startswith("de") else "en"


def detect_user() -> str:
    """Angemeldeten Benutzer sicher ermitteln (niemals Passwort)."""
    for probe in (lambda: getpass.getuser(),
                  lambda: os.environ.get("USER", ""),
                  lambda: os.environ.get("USERNAME", "")):
        try:
            name = (probe() or "").strip()
            if name and name.lower() != "unknown":
                return name
        except Exception:
            continue
    return "gast"


def animations_disabled(cli_no_anim: bool = False) -> bool:
    if cli_no_anim or os.environ.get("LOKROOS_NO_ANIM") == "1":
        return True
    # GNOME/Plasma-Reduce-Flags respektieren
    for key in ("GTK_REDUCE_ANIMATIONS", "PLASMA_REDUCE_ANIMATIONS",
                "REDUCED_MOTION"):
        if os.environ.get(key) == "1":
            return True
    return False


def build_payload(user: str, lang: str, no_anim: bool) -> dict:
    template = MESSAGES.get(lang, MESSAGES["en"])
    return {
        "user": user,
        "lang": lang,
        "message": template.format(user=user),
        "animations": not no_anim,
        "durations_ms": {"fade_in": 0 if no_anim else 600,
                         "reveal": 0 if no_anim else 900,
                         "loader": 0 if no_anim else 1200},
    }


def main(argv: list) -> int:
    try:
        cli_no_anim = "--no-anim" in argv
        user = detect_user()
        lang = detect_lang()
        payload = build_payload(user, lang, animations_disabled(cli_no_anim))
        # Sicher darstellen: JSON ist escapet, QML nutzt text: statt HTML
        sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
        sys.stdout.flush()
        if "--json-only" in argv:
            return 0
        # Echte Fensterintegration übernimmt welcome.qml (Plasma);
        # ohne Display-Server ist stdout-Payload das verifizierbare Ergebnis.
        return 0
    except Exception:
        # Darf Login/Desktop niemals blockieren
        return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
