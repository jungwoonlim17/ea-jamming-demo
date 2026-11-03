# -*- coding: utf-8 -*-
"""갤러리 등록용 썸네일(1280×800)을 그린다.

쉬운판 화면과 같은 팔레트를 쓰고, 두 모듈의 핵심 장면을 한 장에 담는다.
    python "도구/썸네일.py"
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# web-lite/ 는 쉬운판.py 가 만드는 폴더라 여기에 두지 않는다. 작업 폴더 루트에 만든다.
OUT = Path(__file__).resolve().parent.parent / "썸네일_갤러리.png"

W, H = 1280, 800
S = 2  # 2배로 그린 뒤 줄여서 글자를 또렷하게

BG = (12, 20, 29)          # --bg
CARD = (18, 29, 41)        # --card
PANEL = (15, 26, 37)       # --panel
LINE = (31, 44, 58)        # --line
LINE2 = (43, 58, 74)       # --line2
TEXT = (230, 237, 243)     # --text
MUTED = (180, 194, 207)    # --muted
DIM = (143, 162, 180)      # --dim
SIG = (127, 184, 255)      # --sig
JAM = (230, 184, 74)       # --jam
OK = (127, 227, 182)       # --ok
BAD = (255, 138, 122)      # --bad
SCOPE = (7, 20, 15)        # 장비 화면 배경

REG = r"C:\Windows\Fonts\malgun.ttf"
BOLD = r"C:\Windows\Fonts\malgunbd.ttf"


def f(path, size):
    return ImageFont.truetype(path, size * S)


im = Image.new("RGB", (W * S, H * S), BG)
d = ImageDraw.Draw(im)


def box(x, y, w, h, fill, outline=LINE, r=16, width=2):
    d.rounded_rectangle([x * S, y * S, (x + w) * S, (y + h) * S],
                        radius=r * S, fill=fill, outline=outline, width=width * S)


def txt(x, y, s, font, fill=TEXT, anchor=None):
    d.text((x * S, y * S), s, font=font, fill=fill, anchor=anchor)


def tw(s, font):
    return d.textlength(s, font=font) / S


F_TITLE = f(BOLD, 62)
F_SUB = f(REG, 29)
F_CARDH = f(BOLD, 30)
F_CARDS = f(REG, 20)
F_BIG = f(BOLD, 44)
F_NOTE = f(REG, 19)
F_TINY = f(REG, 15)
F_TINYB = f(BOLD, 16)
F_FOOT = f(REG, 20)

# ── 머리말 ────────────────────────────────────────────────────────────────
txt(64, 58, "전자전 재밍의 원리 이해", F_TITLE)
txt(64, 148, "방해 전파를 쏘면 통신은 정말 바로 끊길까?", F_SUB, OK)

d.rectangle([64 * S, 206 * S, 1216 * S, 207 * S], fill=LINE)

PY, PH, PW = 236, 440, 560
AX, BX = 64, 656

# ── 왼쪽: 무전 통신 ───────────────────────────────────────────────────────
box(AX, PY, PW, PH, CARD)
txt(AX + 32, PY + 28, "무전 통신", F_CARDH)
txt(AX + 32, PY + 72, "재머를 켜도 바로 끊기지 않는다", F_CARDS, DIM)

gx, gy, gw, gh = AX + 32, PY + 136, PW - 64, 24
d.rounded_rectangle([gx * S, gy * S, (gx + gw) * S, (gy + gh) * S],
                    radius=(gh // 2) * S, fill=PANEL, outline=LINE2, width=1 * S)
# J/S = +10.9 dB → (10.9+30)/60
fill_w = int(gw * (10.9 + 30) / 60)
d.rounded_rectangle([gx * S, gy * S, (gx + fill_w) * S, (gy + gh) * S],
                    radius=(gh // 2) * S, fill=JAM)
# 임계선 +6 dB
mx = gx + int(gw * (6 + 30) / 60)
d.rectangle([(mx - 1) * S, (gy - 7) * S, (mx + 2) * S, (gy + gh + 7) * S], fill=BAD)

# 맑은 고딕에 U+2212(−) 글리프가 없어 보통 하이픈을 쓴다
txt(gx, gy + 40, "재밍 대 신호 비 -30 dB", F_TINY, DIM)
txt(mx, gy + 40, "임계 +6 dB", F_TINY, BAD, anchor="ma")
txt(gx + gw, gy + 40, "+30 dB", F_TINY, DIM, anchor="ra")

txt(AX + 32, PY + 228, "두절", F_BIG, BAD)
txt(AX + 32 + tw("두절", F_BIG) + 18, PY + 246, "재머가 교신을 덮었다", F_NOTE, MUTED)

for i, (a, b, c) in enumerate([
        ("1 W · 150 km", "그대로 들린다", OK),
        ("50 W · 150 km", "두절", BAD),
        ("1 W · 40 km", "두절 — 거리도 같은 레버", BAD)]):
    y = PY + 310 + i * 36
    txt(AX + 32, y, a, F_TINYB, TEXT)
    txt(AX + 190, y, "→", F_NOTE, DIM)
    txt(AX + 224, y, b, F_NOTE, c)

# ── 오른쪽: 위성 항법 ─────────────────────────────────────────────────────
box(BX, PY, PW, PH, CARD)
txt(BX + 32, PY + 28, "위성 항법", F_CARDH)
txt(BX + 32, PY + 72, "화면은 멀쩡한데 위치가 틀린다", F_CARDS, DIM)

SW_, SH_ = 232, 196
sy = PY + 126
for i, (label, col) in enumerate((("운전자 화면", OK), ("실제 상황", BAD))):
    sx = BX + 32 + i * (SW_ + 32)
    box(sx, sy, SW_, SH_, SCOPE, LINE2, r=10, width=1)
    txt(sx + 14, sy + 12, label, F_TINYB, col)

# 왼쪽 화면: 곧게 가는 경로 + 위성 8/8
sx = BX + 32
txt(sx + 14, sy + 40, "위성 8/8 · 정확도 양호", F_TINY, OK)
d.line([(sx + 24) * S, (sy + 150) * S, (sx + 200) * S, (sy + 86) * S], fill=OK, width=3 * S)
d.ellipse([(sx + 18) * S, (sy + 144) * S, (sx + 30) * S, (sy + 156) * S], fill=OK)

# 오른쪽 화면: 금지구역으로 꺾이는 경로
sx = BX + 32 + SW_ + 32
d.rectangle([(sx + 130) * S, (sy + 44) * S, (sx + 214) * S, (sy + 112) * S],
            fill=(60, 26, 24), outline=BAD, width=1 * S)
txt(sx + 172, sy + 70, "금지구역", F_TINY, BAD, anchor="ma")
d.line([(sx + 24) * S, (sy + 150) * S, (sx + 120) * S, (sy + 120) * S], fill=DIM, width=3 * S)
d.line([(sx + 120) * S, (sy + 120) * S, (sx + 176) * S, (sy + 104) * S], fill=BAD, width=3 * S)
d.ellipse([(sx + 18) * S, (sy + 144) * S, (sx + 30) * S, (sy + 156) * S], fill=DIM)
d.ellipse([(sx + 170) * S, (sy + 98) * S, (sx + 182) * S, (sy + 110) * S], fill=BAD)

txt(BX + 32, PY + 344, "가짜 위성 신호 10 mW", F_TINYB, JAM)
txt(BX + 32, PY + 374, "경고는 끝까지 뜨지 않는다", F_NOTE, MUTED)

# ── 꼬리말 ────────────────────────────────────────────────────────────────
txt(64, 712, "설치도 가입도 없이 브라우저에서 바로 · 출력과 거리를 직접 움직여 보는 교육자료",
    F_FOOT, MUTED)
txt(1216, 712, "교육용 가상 값", F_FOOT, DIM, anchor="ra")

im.resize((W, H), Image.LANCZOS).save(OUT, "PNG")
print("만들었습니다:", OUT, "%d×%d" % (W, H))
