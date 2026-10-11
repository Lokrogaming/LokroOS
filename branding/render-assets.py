#!/usr/bin/env python3
"""LokroOS Boot-Asset-Generator – rendert Plymouth-PNGs deterministisch aus Code.

Warum kein SVG-Export: Auf Build-/Zielsystemen ist kein SVG-Renderer garantiert.
Dieses Skript braucht nur Pillow und erzeugt reproduzierbar (kein Zufall):
  config/plymouth/themes/lokroos/logo.png  (512x512, LOKRO-L auf dunklem Glass-Chip)
  config/plymouth/themes/lokroos/bar.png   (400x12, Cyan-Verlauf, Fortschritt)
  config/plymouth/themes/lokroos/box.png   (400x12, Track für Fortschritt)

Gebrauch:  python3 branding/render-assets.py [--check]
  --check: rendert nach stdout-Vergleich? Nein – prüft nur, dass alle Assets
           vorhanden und gültige PNGs in erwarteter Größe sind (Exit 0/1).
"""
import os
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("FEHLER: Pillow fehlt (pip install pillow).")
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "config" / "plymouth" / "themes" / "lokroos"

BG_TOP = (6, 9, 15)
BG_BOTTOM = (11, 27, 51)
CYAN = (34, 211, 238)
CYAN_DIM = (14, 165, 233)
TEXT_LIGHT = (241, 245, 249)

EXPECTED = {"logo.png": (512, 512), "bar.png": (400, 12), "box.png": (400, 12)}


def rounded_rect(draw, box, radius, fill):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def vertical_gradient(size, top, bottom):
    w, h = size
    base = Image.new("RGB", (1, h))
    px = base.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        px[0, y] = tuple(round(a + (b - a) * t) for a, b in zip(top, bottom))
    return base.resize(size)


def render_logo():
    s = 512
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    chip = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(chip)
    d.rounded_rectangle([56, 56, s - 56, s - 56], radius=112,
                        fill=BG_TOP + (255,))
    # dezenter Cyan-Rahmen
    d.rounded_rectangle([56, 56, s - 56, s - 56], radius=112,
                        outline=CYAN_DIM + (110,), width=5)
    img = Image.alpha_composite(img, chip)
    d = ImageDraw.Draw(img)
    # L: Vertikalbalken + Fuss, runde Kappen
    w = 46
    d.line([196, 150, 196, 350], fill=CYAN + (255,), width=w, joint="curve")
    d.line([196, 350, 330, 350], fill=CYAN + (255,), width=w, joint="curve")
    for xy in ((196, 150), (196, 350), (330, 350)):
        r = w // 2
        d.ellipse([xy[0] - r, xy[1] - r, xy[0] + r, xy[1] + r],
                  fill=CYAN + (255,))
    # Glow-Punkt oben rechts
    for r, a in ((46, 40), (32, 90), (20, 255)):
        d.ellipse([352 - r, 128 - r, 352 + r, 128 + r],
                  fill=CYAN + (a,))
    return img


def render_bar():
    w, h = 400, 12
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    grad = vertical_gradient((w, 1), CYAN_DIM, CYAN).convert("RGBA")
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=6,
                                           fill=255)
    img.paste(grad.resize((w, h)), (0, 0), mask)
    return img


def render_box():
    w, h = 400, 12
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=6,
                        fill=(6, 9, 15, 170), outline=(148, 197, 255, 70),
                        width=2)
    return img


def main(argv):
    if "--check" in argv:
        ok = True
        for name, size in EXPECTED.items():
            p = THEME / name
            try:
                with Image.open(p) as im:
                    im.load()
                    good = im.size == size and im.format == "PNG"
            except OSError:
                good = False
            print(f"{name}: {'OK' if good else 'FEHLT/KAPUTT'}")
            ok = ok and good
        return 0 if ok else 1
    THEME.mkdir(parents=True, exist_ok=True)
    render_logo().save(THEME / "logo.png")
    render_bar().save(THEME / "bar.png")
    render_box().save(THEME / "box.png")
    print("Assets gerendert:", ", ".join(EXPECTED))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
