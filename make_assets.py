"""Regenerates whip-gag assets (whipcrack.wav, whip.cur) from scratch.
Run on any machine with `python make_assets.py` — no assets are checked in as binaries
that can't be reproduced, so this is what claude-sync actually carries forward.
"""
import math
import os
import random
import struct
import wave

HERE = os.path.dirname(os.path.abspath(__file__))


def make_whipcrack_wav(path, sample_rate=44100):
    # Sharp transient "crack" + fast-decaying filtered noise "tail", like a whip.
    duration = 0.35
    n = int(sample_rate * duration)
    samples = []
    prev = 0.0
    for i in range(n):
        t = i / sample_rate
        # Initial crack: very short high-amplitude burst (first ~4ms)
        crack_env = math.exp(-t * 900) if t < 0.02 else 0.0
        # Tail: longer, quieter, filtered noise
        tail_env = 0.35 * math.exp(-t * 18)
        noise = random.uniform(-1, 1)
        raw = noise * (crack_env * 1.0 + tail_env)
        # simple one-pole low-pass to soften harshness into a "whoosh"
        filtered = prev + 0.35 * (raw - prev)
        prev = filtered
        samples.append(filtered)

    peak = max(abs(s) for s in samples) or 1.0
    frames = bytearray()
    for s in samples:
        v = int(max(-1.0, min(1.0, s / peak)) * 32767)
        frames += struct.pack("<h", v)

    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(bytes(frames))


def make_whip_cursor(path, size=32):
    from PIL import Image, ImageDraw

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Coiled whip: a spiral polyline from center-ish out to a handle tip.
    pts = []
    turns = 2.4
    steps = 60
    cx, cy = size * 0.62, size * 0.38
    for i in range(steps):
        frac = i / (steps - 1)
        angle = frac * turns * 2 * math.pi
        radius = 2 + frac * 11
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle) * 0.85
        pts.append((x, y))
    # taper the whip's tail out to a handle at bottom-left
    pts.append((size * 0.12, size * 0.92))

    for i in range(len(pts) - 1):
        w = max(1, 3 - i // 20)
        d.line([pts[i], pts[i + 1]], fill=(40, 30, 20, 255), width=w)
    # handle grip
    d.rectangle([size * 0.05, size * 0.85, size * 0.22, size * 0.97], fill=(60, 40, 20, 255))
    # hotspot marker (top-left-ish, where the "tip" strikes) — not drawn, just for clarity

    ico_tmp = path.replace(".cur", "_tmp.png")
    img.save(ico_tmp)

    # Build a real .cur (ICO-format header with hotspot fields) from the PNG-as-BMP data.
    # Pillow can't write .cur directly with a custom hotspot, so hand-roll the ICONDIR.
    bmp = Image.open(ico_tmp).convert("RGBA")
    width, height = bmp.size
    pixels = bmp.tobytes("raw", "BGRA")

    # BITMAPINFOHEADER (40 bytes) + XOR (BGRA) + AND mask (1bpp, padded to 32-bit rows)
    and_row_bytes = ((width + 31) // 32) * 4
    and_mask = bytes(and_row_bytes * height)  # fully opaque -> AND mask all zero

    bmih = struct.pack(
        "<IiiHHIIiiII",
        40, width, height * 2, 1, 32, 0, len(pixels) + len(and_mask), 0, 0, 0, 0,
    )
    # rows bottom-up
    row_size = width * 4
    rows = [pixels[r * row_size:(r + 1) * row_size] for r in range(height)]
    xor_data = b"".join(reversed(rows))

    image_data = bmih + xor_data + and_mask

    hotspot_x, hotspot_y = 4, 2  # tip of the whip, top-left area
    entry = struct.pack(
        "<BBBBHHII",
        width if width < 256 else 0,
        height if height < 256 else 0,
        0, 0,
        hotspot_x, hotspot_y,
        len(image_data),
        6 + 16,
    )
    header = struct.pack("<HHH", 0, 2, 1)  # reserved, type=2 (cursor), count=1

    with open(path, "wb") as f:
        f.write(header + entry + image_data)

    os.remove(ico_tmp)


if __name__ == "__main__":
    wav_path = os.path.join(HERE, "whipcrack.wav")
    cur_path = os.path.join(HERE, "whip.cur")
    make_whipcrack_wav(wav_path)
    make_whip_cursor(cur_path)
    print(f"wrote {wav_path}")
    print(f"wrote {cur_path}")
