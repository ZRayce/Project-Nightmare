import os
from PIL import Image


def build_kurumi_ico():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    gif_path = os.path.abspath(os.path.join(base_dir, "..", "assets", "tokisaki-kurumi.gif"))
    ico_path = os.path.abspath(os.path.join(base_dir, "..", "assets", "kurumi.ico"))

    img = Image.open(gif_path)
    img.seek(0)
    frame = img.convert("RGBA")

    w, h = frame.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    square = frame.crop((left, top, left + side, top + side))

    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    square.save(ico_path, format="ICO", sizes=sizes)
    print(f"Saved multi-size Windows icon to: {ico_path}")


if __name__ == "__main__":
    build_kurumi_ico()