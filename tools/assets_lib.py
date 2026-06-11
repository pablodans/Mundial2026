# -*- coding: utf-8 -*-
"""Utilidades de dibujo (Pillow) para generar los PNG del README con paleta pastel.

Solo se usa para regenerar imagenes de docs/ ; NO es parte del modelo (que es stdlib pura).
Requiere Pillow:  python -m pip install Pillow
"""
from PIL import Image, ImageDraw, ImageFont

S = 2  # supersampling: se dibuja a 2x y se reduce con LANCZOS para bordes/textos nitidos

_FONTS = {
    "reg": "C:/Windows/Fonts/segoeui.ttf",
    "sb": "C:/Windows/Fonts/seguisb.ttf",
    "bold": "C:/Windows/Fonts/segoeuib.ttf",
}


def font(kind, size):
    return ImageFont.truetype(_FONTS[kind], int(size * S))


def lienzo(w, h, bg):
    img = Image.new("RGB", (int(w * S), int(h * S)), bg)
    return img, ImageDraw.Draw(img)


def finalizar(img, w, h, ruta):
    img = img.resize((int(w), int(h)), Image.LANCZOS)
    img.save(ruta)
    return ruta


def gradiente_vertical(draw, w, h, c0, c1):
    for y in range(int(h * S)):
        t = y / (h * S)
        r = round(c0[0] + (c1[0] - c0[0]) * t)
        g = round(c0[1] + (c1[1] - c0[1]) * t)
        b = round(c0[2] + (c1[2] - c0[2]) * t)
        draw.line([(0, y), (int(w * S), y)], fill=(r, g, b))


def rrect(draw, x, y, w, h, rad, fill=None, outline=None, width=1):
    draw.rounded_rectangle(
        [x * S, y * S, (x + w) * S, (y + h) * S], radius=rad * S,
        fill=fill, outline=outline, width=max(1, int(width * S)))


def _ancho(draw, text, fnt):
    b = draw.textbbox((0, 0), text, font=fnt)
    return (b[2] - b[0]) / S, (b[3] - b[1]) / S


def texto(draw, x, y, text, fnt, fill, anchor="la"):
    draw.text((x * S, y * S), text, font=fnt, fill=fill, anchor=anchor)


def texto_ajustado(draw, cx, cy, text, kind, size, fill, max_w, anchor="mm", min_size=8):
    """Dibuja texto centrado reduciendo el tamano hasta caber en max_w."""
    s = size
    while s > min_size:
        f = font(kind, s)
        w, _ = _ancho(draw, text, f)
        if w <= max_w:
            break
        s -= 0.5
    texto(draw, cx, cy, text, font(kind, s), fill, anchor=anchor)


def linea(draw, pts, fill, width=2):
    draw.line([(px * S, py * S) for px, py in pts], fill=fill, width=max(1, int(width * S)))
