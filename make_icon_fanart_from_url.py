import os
import io
import requests
from PIL import Image

def download_image(url):
    print(f"Downloading image from: {url}")
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    return Image.open(io.BytesIO(resp.content)).convert("RGB")

def save_icon_and_fanart(img, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    w, h = img.size
    print(f"Original size: {w}x{h}")

    # -------- ICON: square 512x512 (center crop) --------
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    right = left + side
    bottom = top + side

    square = img.crop((left, top, right, bottom))
    icon = square.resize((512, 512), Image.LANCZOS)
    icon_path = os.path.join(out_dir, "icon.png")
    icon.save(icon_path, format="PNG")
    print("Saved icon:", icon_path)

    # -------- FANART: 16:9 1280x720 (center crop) --------
    target_ratio = 16 / 9
    current_ratio = w / h

    if current_ratio > target_ratio:
        # too wide, crop width
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        right = left + new_w
        top = 0
        bottom = h
    else:
        # too tall, crop height
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        bottom = top + new_h
        left = 0
        right = w

    fanart_crop = img.crop((left, top, right, bottom))
    fanart = fanart_crop.resize((1280, 720), Image.LANCZOS)
    fanart_path = os.path.join(out_dir, "fanart.jpg")
    fanart.save(fanart_path, format="JPEG", quality=90)
    print("Saved fanart:", fanart_path)

def main():
    image_url = input("Paste DIRECT image URL here: ").strip()
    out_dir = input("Output folder (e.g. F:\\plugin.video.nollywood_movies): ").strip()

    img = download_image(image_url)
    save_icon_and_fanart(img, out_dir)

if __name__ == "__main__":
    main()
