# -*- coding: utf-8 -*-
"""쉬운판(web-lite) 생성.

web/ 의 통신·GNSS 두 모듈을 가져와
  · 제목을 "전자전 재밍의 원리 이해"로 바꾸고
  · 대상 전환을 두 개(무전 통신 · 위성 항법)로 줄이고
  · 약어를 일반인이 읽을 수 있는 말로 풀고
  · 시연 단계 설명을 도구/시나리오_쉬운판.json 의 쉬운 문장으로 갈아끼우고
  · 오른쪽 수식 패널 아래에 "나오는 말" 풀이를 붙이고
  · PWA(매니페스트·서비스 워커·설치 버튼)를 들어낸다 — 쉬운판은 웹에서만 동작한다.
수식과 물리 모델은 손대지 않는다 — 원본과 같은 숫자가 나와야 한다.

    python "도구/쉬운판.py"

멱등이다. web/ 를 고치고 도구/빌드.py 를 돌린 뒤 이것을 돌리면 쉬운판이 따라온다.
"""

import json
import re
import shutil
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "web"
OUT = ROOT / "web-lite"
TOOLS = ROOT / "도구"

MODULES = ["01-comms.html", "02-gnss.html"]

TITLE = "전자전 재밍의 원리 이해"
VER = "쉬운판 v1.0"


def one(t, old, new, label, count=1):
    n = t.count(old)
    if n != count:
        print("  !! %s — %d 번 나옴 (기대 %d): %r" % (label, n, count, old[:60]))
        sys.exit(1)
    return t.replace(old, new)


# ── PWA 들어내기 ─────────────────────────────────────────────────────────
#
# 쉬운판은 "그냥 웹페이지"다. 매니페스트·서비스 워커·설치 버튼을 넣지 않는다.
# 파비콘과 theme-color 만 남긴다 — 이건 앱 설치와 무관한 보통 웹 요소다.
#
# 아래 청소 스크립트는 예전에 이 주소를 열어 서비스 워커가 등록된 브라우저를 위한 것이다.
# 그대로 두면 옛 캐시가 계속 화면을 내줄 수 있다.

HEAD_WEB = """<!-- 쉬운판: 설치용 메타 없이 파비콘만 (도구/쉬운판.py) -->
<meta name="theme-color" content="#0C141D">
<link rel="icon" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/icon-192.png">"""

BODY_WEB = """<!-- 쉬운판: 예전에 등록된 서비스 워커 청소 (도구/쉬운판.py) -->
<script>
(function(){
  'use strict';
  if (!('serviceWorker' in navigator)) return;
  navigator.serviceWorker.getRegistrations().then(function(rs){
    rs.forEach(function(r){ r.unregister(); });
  }).catch(function(){});
  if (window.caches && caches.keys) {
    caches.keys().then(function(ks){ ks.forEach(function(k){ caches.delete(k); }); }).catch(function(){});
  }
})();
</script>"""

HEAD_RX = re.compile(r"<!-- PWA:head 시작.*?<!-- PWA:head 끝 -->\n?", re.DOTALL)
BODY_RX = re.compile(r"<!-- PWA:body 시작.*?<!-- PWA:body 끝 -->\n?", re.DOTALL)


def strip_pwa(t, name):
    t, n1 = HEAD_RX.subn(HEAD_WEB + "\n", t, count=1)
    t, n2 = BODY_RX.subn(BODY_WEB + "\n", t, count=1)
    if (n1, n2) != (1, 1):
        print("  !! %s — PWA 블록을 찾지 못했습니다 (head %d, body %d)" % (name, n1, n2))
        sys.exit(1)
    return t


# ── 두 모듈에 공통으로 들어가는 바꿈 ──────────────────────────────────────
def common(t, name):
    t = one(t, "<h1>전자전 중 EA의 위험성</h1>", "<h1>%s</h1>" % TITLE, name + " h1")

    # 발표 바: 교관용 말투 → 혼자 보는 사람 말투
    t = one(t, '<span class="ea-lbl">시연 단계</span>',
            '<span class="ea-lbl">따라 하기</span>', name + " 발표바 라벨")
    t = one(t, "시연 단계 버튼을 누르면 파라미터가 그 장면으로 맞춰집니다. 슬라이더를 직접 만져도 됩니다.",
            "단계 버튼을 왼쪽부터 눌러 보세요. 화면이 그 장면으로 맞춰집니다. 왼쪽 손잡이를 직접 움직여도 됩니다.",
            name + " 발표바 안내")

    # 재머 종류: 일반인이 바로 읽을 수 있게
    t = one(t, '<button id="mNoise" aria-pressed="true">잡음</button>',
            '<button id="mNoise" aria-pressed="true">덮기(잡음)</button>', name + " 잡음 버튼")

    # 대상 전환: 네 개 → 두 개
    t = one(t, "var NAMES = ['통신','GNSS','PPI','SAR'];",
            "var NAMES = ['무전 통신','위성 항법'];", name + " NAMES")
    t = one(t, "'<dt>Q W E R</dt><dd>대상 전환 (통신 · GNSS · PPI · SAR)</dd>' +",
            "'<dt>Q W</dt><dd>대상 전환 (무전 통신 · 위성 항법)</dd>' +", name + " 단축키 도움말")

    # PWA 를 들어낸다 — 쉬운판은 웹에서만 동작한다 (설치·오프라인 없음)
    t = strip_pwa(t, name)

    # 푸터 버전
    t = one(t, "시연 버전 v0.2 · ", VER + " · ", name + " 푸터 버전")
    return t


def steps_json(mod, scen):
    s = json.dumps(scen[mod], ensure_ascii=False, separators=(",", ":"))
    if "</script" in s:
        raise ValueError("시나리오에 </script 가 들어 있습니다")
    return s


def swap_steps(t, mod, scen, name):
    rx = re.compile(r"var STEPS = \[.*?\];\n", re.DOTALL)
    if not rx.search(t):
        print("  !! %s — var STEPS 를 찾지 못했습니다" % name)
        sys.exit(1)
    return rx.sub("var STEPS = " + steps_json(mod, scen).replace("\\", "\\\\") + ";\n", t, count=1)


GLOSS_HEAD = ('<div style="margin-top:18px">'
              '<div class="group" style="margin-bottom:8px;color:var(--dim)">나오는 말</div>'
              '<div style="font-size:13px;line-height:1.75;color:var(--muted)">')
GLOSS_FOOT = "</div></div>"


def gloss(rows):
    body = "".join(
        '<p style="margin:0 0 9px"><strong style="color:var(--text)">%s</strong><br>%s</p>' % (k, v)
        for k, v in rows)
    return GLOSS_HEAD + body + GLOSS_FOOT


# ── 01 무전 통신 ──────────────────────────────────────────────────────────
def comms(t):
    t = one(t, "<title>전자전 중 EA의 위험성 — 통신 재밍 시연</title>",
            "<title>%s — 무전 통신</title>" % TITLE, "01 title")
    t = one(t, '<div class="sub">통신 음성 재밍 시연 · 링크 방정식 기반</div>',
            '<div class="sub">무전 통신 — 재머를 켜도 바로 끊기지 않는 이유</div>', "01 부제")

    t = one(t,
            '    <button aria-pressed="true">통신</button>\n'
            '    <a href="02-gnss.html">GNSS</a>\n'
            '    <a href="03-ppi.html">PPI</a>\n'
            '    <a href="04-sar.html">SAR</a>',
            '    <button aria-pressed="true">무전 통신</button>\n'
            '    <a href="02-gnss.html">위성 항법</a>', "01 대상 전환")

    # 주파수 대역: 약어를 풀어서
    t = one(t, '<button id="mDecep" aria-pressed="false">기만</button>',
            '<button id="mDecep" aria-pressed="false">속이기(기만)</button>', "01 기만 버튼")

    t = one(t, ">HF 10 MHz · AM<", ">단파(HF) 10 MHz · 진폭변조(AM)<", "01 대역 HF")
    t = one(t, ">VHF 150 MHz · FM<", ">초단파(VHF) 150 MHz · 주파수변조(FM)<", "01 대역 VHF")
    t = one(t, ">UHF 400 MHz · FM<", ">극초단파(UHF) 400 MHz · 주파수변조(FM)<", "01 대역 UHF")

    # 화면에 찍히는 변조 이름도 풀어서 (코드 값 'FM'/'AM' 은 그대로 둔다)
    MODNM = "(S.mod==='FM'?'주파수변조(FM)':'진폭변조(AM)')"
    t = one(t, "$('oF').textContent=fmtHz(S.f)+' · '+S.mod;",
            "$('oF').textContent=fmtHz(S.f)+' · '+" + MODNM + ";", "01 대역 표시")
    t = one(t, "$('thrMod').textContent = S.mod;",
            "$('thrMod').textContent = " + MODNM + ";", "01 임계값 변조 표시")
    t = one(t, '<span>임계값 (<span id="thrMod">FM</span>)</span>',
            '<span>통하기 시작하는 기준 (<span id="thrMod">주파수변조(FM)</span>)</span>', "01 임계값 라벨")

    # 비(比) 이름 풀어쓰기
    t = one(t, '<span class="nm">SNR = S − N</span>',
            '<span class="nm">신호 대 잡음비 = S − N</span>', "01 SNR 라벨")
    t = one(t, '<span class="nm">SINR = S − (N+J)</span>',
            '<span class="nm">신호 대 (잡음+재머) 비 = S − (N+J)</span>', "01 SINR 라벨")
    t = one(t, "<span>J/S −30 dB</span>", "<span>재밍 대 신호 비 −30 dB</span>", "01 게이지 왼쪽")
    t = one(t, "<span>SNR (재머 없음)</span>", "<span>신호 대 잡음비 (재머 없음)</span>", "01 결과 SNR")
    t = one(t, "<span>SINR (재머 포함)</span>", "<span>신호 대 (잡음+재머) 비</span>", "01 결과 SINR")
    t = one(t, "<span>J/S = P<sub>J</sub> − P<sub>r</sub></span>",
            "<span>재밍 대 신호 비 = P<sub>J</sub> − P<sub>r</sub></span>", "01 결과 J/S")
    t = one(t, "'재머 OFF → SNR과 같음 · 필요 SNR 12 dB'",
            "'재머 꺼짐 → 잡음비와 같음 · 알아들으려면 12 dB 필요'", "01 SINR 설명(JS)")
    t = one(t, "· 필요 SNR 12 dB", "· 알아들으려면 12 dB 필요", "01 SINR 설명2(JS)")

    # 교훈 문장
    t = one(t,
            "수신기에서 J/S가 임계값을 넘어야 효과가 나고, J/S를 키우는 방법은 재머 출력을 올리거나 거리를 줄이는 것뿐입니다. 왼쪽 두 슬라이더로 확인해 보세요.",
            "받는 쪽에 도착한 재머 세기가 교신 세기보다 일정 수준 이상 커져야 효과가 납니다. "
            "그 차이를 키우는 길은 <b>더 세게 쏘거나, 더 가까이 가거나</b> 둘뿐입니다. 왼쪽 손잡이 두 개로 확인해 보세요.",
            "01 교훈")

    # 포획 효과 설명
    t = one(t,
            "'<strong>VHF/UHF 전술망은 FM.</strong> 포획 효과 때문에 같은 채널에 들어온 두 신호 중 더 센 쪽이 수신기를 차지합니다. J/S가 −6 dB 아래면 재머가 억제되고, +6 dB를 넘으면 교신 대신 재머만 들립니다.'",
            "'<strong>군 전술 무전기는 주파수변조(FM)를 씁니다.</strong> 같은 채널에 두 소리가 들어오면 "
            "수신기는 <b>더 센 쪽만</b> 들려줍니다(포획 효과). 재머가 교신보다 4배쯤(−6 dB) 작으면 아예 묻히고, "
            "4배쯤(+6 dB) 커지면 교신 대신 재머만 들립니다.'",
            "01 FM 설명")
    t = one(t,
            "'<strong>HF 음성망은 AM(SSB).</strong> 선형 혼합이라 재머 전력이 신호와 같아지는 J/S 0 dB 부근부터 알아듣기 어려워지며, 그 아래에서도 서서히 잡음이 깔립니다.'",
            "'<strong>단파(HF) 음성망은 진폭변조(AM)를 씁니다.</strong> 두 소리가 그대로 겹쳐 들리기 때문에, "
            "재머가 교신과 비슷한 세기(0 dB)만 되어도 알아듣기 어려워지고 그 아래에서도 잡음이 서서히 깔립니다.'",
            "01 AM 설명")

    # 음성 합성 안내
    t = one(t, "음원: 브라우저 음성 합성(TTS)으로 위 교신문을 읽습니다. 파일을 올리면 그 음원으로 바뀝니다.",
            "소리: 브라우저의 음성 합성 기능이 위 교신문을 읽습니다. 녹음 파일을 올리면 그 소리로 바뀝니다.",
            "01 음원 안내")
    t = one(t, "'음원: 이 브라우저에 음성 합성이 없어 내장 합성음을 사용합니다. 좌표 구간 기만은 TTS 또는 음성 파일이 있어야 동작합니다.'",
            "'소리: 이 브라우저에 한국어 음성이 없어 대체 합성음을 씁니다. 좌표만 바꿔치기하는 장면은 "
            "음성 합성이나 녹음 파일이 있어야 동작합니다.'", "01 음원 대체 안내")

    # 가정 문구
    t = one(t,
            "가정: 재머는 채널을 감청하여 교신 형식을 알고 있고, 예고어(“좌표,”) 직후 좌표 구간에 시간 동기를 맞춰 반응합니다(반응형 재밍, look-through). 주파수 도약·암호화 통신에서는 이 가정이 성립하지 않습니다.",
            "전제: 이 장면은 재머가 <b>미리 채널을 엿듣고 있어서</b> 교신 형식을 알고, “좌표,”라는 말 직후에 "
            "맞춰 끼어들 수 있다고 가정합니다. 주파수를 계속 바꾸거나 암호를 쓰는 통신에서는 이렇게 되지 않습니다.",
            "01 가정")

    t = one(t, '<p class="lesson" id="thrNote"></p>',
            '<p class="lesson" id="thrNote"></p>' + gloss([
                ("재밍 대 신호 비 (J/S)",
                 "받는 쪽 안테나에 도착한 <b>재머 세기 ÷ 교신 세기</b>를 dB로 적은 값. "
                 "이 값이 기준을 넘어야 방해가 통합니다."),
                ("dB (데시벨)", "세기의 비를 적는 단위. 10 dB = 10배, 20 dB = 100배, 30 dB = 1000배."),
                ("dBm", "전파의 세기를 나타내는 단위. 숫자가 작을수록(−130처럼) 약한 신호입니다."),
                ("dBi", "안테나가 전파를 한쪽으로 모아 주는 정도. 6 dBi면 약 4배로 모아 줍니다."),
                ("신호 대 잡음비", "원래 신호가 주변 잡음보다 얼마나 큰지. 이 값이 12 dB쯤은 되어야 말을 알아듣습니다."),
                ("주파수변조(FM) · 진폭변조(AM)",
                 "소리를 전파에 싣는 두 가지 방식. 군 전술 무전기는 FM, 단파 음성망은 AM을 씁니다."),
                ("수신 감도", "수신기가 알아들을 수 있는 가장 약한 신호 세기. 이보다 약하면 아예 못 받습니다."),
            ]), "01 용어 풀이")
    return t


# ── 02 위성 항법 ──────────────────────────────────────────────────────────
def gnss(t):
    t = one(t, "<title>전자전 중 EA의 위험성 — GNSS 재밍 시연</title>",
            "<title>%s — 위성 항법</title>" % TITLE, "02 title")
    t = one(t, '<div class="sub">GNSS 재밍·스푸핑 시연 · 링크 방정식 기반</div>',
            '<div class="sub">위성 항법 — 화면은 멀쩡한데 위치가 틀린다</div>', "02 부제")

    t = one(t,
            '    <a href="01-comms.html">통신</a>\n'
            '    <button aria-pressed="true">GNSS</button>\n'
            '    <a href="03-ppi.html">PPI</a>\n'
            '    <a href="04-sar.html">SAR</a>',
            '    <a href="01-comms.html">무전 통신</a>\n'
            '    <button aria-pressed="true">위성 항법</button>', "02 대상 전환")

    t = one(t, '<button id="mDecep" aria-pressed="false">기만 (스푸핑)</button>',
            '<button id="mDecep" aria-pressed="false">속이기(가짜 신호)</button>', "02 기만 버튼")

    t = one(t, '<div class="group sig">GNSS 신호 (피해 측)</div>',
            '<div class="group sig">위성 항법 신호 (피해 측)</div>', "02 파라미터 제목")
    t = one(t, ">GNSS 수신기<", ">위성 항법 수신기<", "02 평면도 라벨")
    t = one(t, ">2.046 MHz · C/A<", ">2.046 MHz · C/A 코드<", "02 대역폭")
    t = one(t, "대역확산 코드라 신호가 잡음 아래에 숨어 있고, 수신기는 상관 처리로 꺼냅니다. 추적 유지에 C/N₀ ≥ 28 dB-Hz 필요(고정).",
            "위성 신호는 원래 주변 잡음보다 <b>약합니다</b>. 수신기는 약속된 코드와 맞춰 보는 방법으로 그것을 꺼냅니다. "
            "계속 따라가려면 신호 세기 지표(C/N₀)가 28 dB-Hz 이상이어야 합니다.", "02 고정 설명")
    t = one(t, "<span>위성별 C/N₀</span>", "<span>위성별 신호 세기 (C/N₀)</span>", "02 막대 제목")
    t = one(t, ">NO FIX<", ">위치 확인 불가<", "02 NO FIX")
    t = one(t, 'font-size="26" font-weight="700" text-anchor="middle" opacity="0">위치 확인 불가<',
            'font-size="19" font-weight="700" text-anchor="middle" opacity="0">위치 확인 불가<', "02 NO FIX 글자 크기")
    t = one(t, ">SAT 8/8<", ">위성 8/8<", "02 내비 위성 수")
    t = one(t, "'SAT '", "'위성 '", "02 내비 위성 수(JS)")
    # 화면 표시와 자바스크립트가 같은 문구를 쓰므로 두 곳을 함께 바꾼다
    t = one(t, "유효 C/N₀ (재머 포함)", "실제 신호 세기 C/N₀ (재머 포함)", "02 결과 라벨", count=2)
    t = one(t, "추적 임계값", "따라가기 위한 최소값", "02 임계 라벨", count=2)
    t = one(t, "<span>추적 위성 수</span>", "<span>따라가는 위성 수</span>", "02 위성 수 라벨")
    t = one(t, "'가로채기 임계값'", "'가로채는 데 필요한 세기'", "02 가로채기 라벨")
    t = one(t, "'스푸퍼 − 진짜 신호'", "'가짜 신호 − 진짜 신호'", "02 스푸퍼 라벨")

    t = one(t, '<p class="lesson" id="lesson"></p>',
            '<p class="lesson" id="lesson"></p>' + gloss([
                ("위성 항법 (GNSS)",
                 "위성 신호로 현재 위치를 알아내는 시스템을 묶어 부르는 말. 미국의 GPS가 그중 하나입니다."),
                ("C/N₀ (신호 세기 지표)",
                 "위성 신호가 주변 잡음보다 얼마나 큰지를 나타내는 값. 28 dB-Hz 아래로 떨어지면 그 위성을 놓칩니다."),
                ("dB-Hz", "위 값을 적는 단위. 숫자가 클수록 신호가 또렷합니다."),
                ("위치 확인 불가 (NO FIX)",
                 "따라가는 위성이 4개 아래로 떨어져 위치를 계산할 수 없는 상태. 화면에 경고가 뜹니다."),
                ("스푸핑 (가짜 신호)",
                 "진짜처럼 생긴 가짜 위성 신호를 보내 수신기가 엉뚱한 위치를 믿게 만드는 것. "
                 "경고가 뜨지 않는 것이 핵심입니다."),
                ("위성 배치에 따른 오차",
                 "위성이 하늘에 고르게 퍼져 있으면 위치가 정확하고, 한쪽에 몰리면 같은 신호로도 오차가 커집니다."),
                ("dBm · dBi", "전파의 세기 단위와, 안테나가 전파를 모아 주는 정도."),
            ]), "02 용어 풀이")
    return t


# 예전 판에서 만들던 PWA 파일. 남아 있으면 지운다.
STALE = ["manifest.json", "sw.js", "icons/icon-512.png", "icons/icon-512-maskable.png"]


def main():
    if not SRC.is_dir():
        print("web/ 을 찾을 수 없습니다")
        return 1
    scen = json.loads((TOOLS / "시나리오_쉬운판.json").read_text(encoding="utf-8"))
    OUT.mkdir(exist_ok=True)

    for fname, fn, mod in ((MODULES[0], comms, "01"), (MODULES[1], gnss, "02")):
        t = (SRC / fname).read_text(encoding="utf-8")
        t = common(t, fname)
        t = fn(t)
        t = swap_steps(t, mod, scen, fname)
        (OUT / fname).write_text(t, encoding="utf-8", newline="\n")
        print("  %s  단계 %d개" % (fname, len(scen[mod])))

    home = (TOOLS / "쉬운판_시작화면.html").read_text(encoding="utf-8")
    home = home.replace("</head>", HEAD_WEB + "\n</head>", 1)
    home = home.replace("</body>", BODY_WEB + "\n</body>", 1)
    (OUT / "index.html").write_text(home, encoding="utf-8", newline="\n")
    print("  index.html  (시작 화면)")

    icons = OUT / "icons"
    icons.mkdir(exist_ok=True)
    shutil.copyfile(SRC / "icons" / "icon-192.png", icons / "icon-192.png")

    gone = []
    for rel in STALE:
        p = OUT / rel
        if p.exists():
            p.unlink()
            gone.append(rel)
    if gone:
        print("\n지운 PWA 파일: " + ", ".join(gone))

    print("\n쉬운판을 %s 에 만들었습니다 (웹 전용 — 설치·오프라인 없음)." % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
