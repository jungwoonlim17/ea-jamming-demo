# -*- coding: utf-8 -*-
"""
PWA 앱 아이콘 생성.

web/index.html 헤더의 레이더 심볼(바깥 원 · 안쪽 원 · 스위프 선)을 그대로 PNG로 그린다.
4배로 그린 뒤 줄여서 테두리를 매끄럽게 만든다.

    python "도구/아이콘생성.py"

결과: web/icons/icon-192.png, icon-512.png, icon-512-maskable.png
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "web" / "icons"

BG = (12, 20, 29)        # --bg  #0C141D
FG = (127, 227, 182)     # --ok  #7FE3B6
SS = 4                   # 수퍼샘플링 배율


def draw_icon(size: int, scale: float) -> Image.Image:
    """scale = 바깥 원의 반지름 / 아이콘 변 길이.

    일반 아이콘은 0.36, maskable 은 가장자리가 잘릴 수 있어 0.28 로 줄인다.
    """
    s = size * SS
    img = Image.new("RGB", (s, s), BG)
    d = ImageDraw.Draw(img)
    c = s / 2
    r_out = s * scale
    r_in = r_out * (7 / 12)            # 헤더 SVG 의 비율 (r=7 / r=12)
    w = max(SS, round(r_out * 0.135))  # 선 두께

    def ring(r):
        d.ellipse([c - r, c - r, c + r, c + r], outline=FG, width=w)

    ring(r_out)
    ring(r_in)

    # 스위프 선: 중심에서 오른쪽 위로. 헤더 SVG 의 (14,14)→(24,6) 방향
    ex, ey = 10 / 12, -8 / 12
    L = r_out * 1.07
    d.line([c, c, c + ex * L, c + ey * L], fill=FG, width=w)

    # 중심점
    dot = w * 1.15
    d.ellipse([c - dot, c - dot, c + dot, c + dot], fill=FG)

    return img.resize((size, size), Image.LANCZOS)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [
        ("icon-192.png", 192, 0.36),
        ("icon-512.png", 512, 0.36),
        ("icon-512-maskable.png", 512, 0.28),
    ]
    for name, size, scale in jobs:
        p = OUT / name
        draw_icon(size, scale).save(p, "PNG", optimize=True)
        print("  %-24s %4dpx  %s bytes" % (name, size, p.stat().st_size))
    print("\n%s 에 %d개 생성" % (OUT.relative_to(ROOT), len(jobs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
