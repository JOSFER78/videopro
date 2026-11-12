"""Compone una imagen pequeña como lámina de 1920x1080 sobre fondo oscuro.

Uso: lamina.py <entrada> <salida> [ancho_max alto_max]
Las fotos libres de algunos objetos solo existen en tamaño pequeño; ampliadas a
pantalla completa se ven borrosas. Aquí se amplían como mucho 2,6 veces y se
centran con un marco fino, como una pieza en una vitrina.
"""
import sys
from PIL import Image, ImageDraw, ImageFilter

FONDO = (12, 13, 15)


def lamina(entrada, salida, ancho_max=1500, alto_max=820):
    img = Image.open(entrada).convert("RGB")
    escala = min(ancho_max / img.width, alto_max / img.height, 2.6)
    tam = (round(img.width * escala), round(img.height * escala))
    img = img.resize(tam, Image.LANCZOS)
    lienzo = Image.new("RGB", (1920, 1080), FONDO)
    # halo suave detrás de la pieza para que no flote en negro plano
    halo = Image.new("L", (1920, 1080), 0)
    x, y = (1920 - tam[0]) // 2, (1080 - tam[1]) // 2
    ImageDraw.Draw(halo).rectangle([x - 60, y - 60, x + tam[0] + 60, y + tam[1] + 60], fill=70)
    halo = halo.filter(ImageFilter.GaussianBlur(120))
    lienzo.paste(Image.new("RGB", (1920, 1080), (60, 58, 54)), (0, 0), halo)
    lienzo.paste(img, (x, y))
    ImageDraw.Draw(lienzo).rectangle([x - 1, y - 1, x + tam[0], y + tam[1]], outline=(243, 241, 236), width=1)
    lienzo.save(salida, quality=93)


if __name__ == "__main__":
    extra = [int(a) for a in sys.argv[3:5]]
    lamina(sys.argv[1], sys.argv[2], *extra)
