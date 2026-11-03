# -*- coding: utf-8 -*-
"""
전자전 재밍 시연 자료 빌드.

하는 일
  1) web/ 의 네 모듈에 공통 발표 도구 블록을 주입한다.
     (마커 <!-- 공통블록:시작 --> ~ <!-- 공통블록:끝 --> 사이를 교체, 없으면 </body> 앞에 삽입)
  2) 그 결과를 artifact/ 으로 복사하면서
     상단 "대상" 전환 링크를 claude.ai 아티팩트 URL로 바꾸고 "시작 화면" 버튼을 뺀다.

멱등이다. 몇 번 돌려도 같은 결과가 나온다.

    python "도구/빌드.py"
"""

import json
import re
import sys
from pathlib import Path

# 윈도우 기본 콘솔(cp949)에서도 한글이 깨지지 않게
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent.parent
OFF = ROOT / "web"
ON = ROOT / "artifact"
TOOLS = ROOT / "도구"

# 모듈 번호 → 파일명 (web/ 과 artifact/ 공통)
MODULES = {
    "01": "01-comms.html",
    "02": "02-gnss.html",
    "03": "03-ppi.html",
    "04": "04-sar.html",
}

# 온라인판 대상 전환 링크. 아티팩트를 다시 올려 주소가 바뀌면 여기와 README 표를 같이 고친다.
ARTIFACTS = {
    "01": "https://claude.ai/artifact/6uoBfwWCLGsUpvtGbnhQLq",
    "02": "https://claude.ai/artifact/1m5DDF53C9qRFgrgAFejro",
    "03": "https://claude.ai/artifact/7aLMDrEKJRRB1rz1Dfu1ci",
    "04": "https://claude.ai/artifact/31DYoHhwGm9YemREk25rt5",
}

HOME_OFFLINE = "index.html"
HOME_ONLINE = ""  # 온라인판에는 시작 화면이 없다

START = "<!-- 공통블록:시작"
END = "<!-- 공통블록:끝 -->"
BLOCK_RE = re.compile(
    re.escape(START) + r".*?" + re.escape(END) + r"\n?",
    re.DOTALL,
)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def write(p: Path, s: str) -> bool:
    """내용이 달라졌을 때만 쓴다. 바뀌었으면 True."""
    if p.exists() and read(p) == s:
        return False
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8", newline="\n")
    return True


def render_block(template: str, mod: str, steps: list, home: str) -> str:
    steps_json = json.dumps(steps, ensure_ascii=False, separators=(",", ":"))
    if "</script" in steps_json:
        raise ValueError("시나리오에 </script 가 들어 있어 스크립트가 깨집니다")
    return (
        template.replace("__STEPS_JSON__", steps_json)
        .replace("__MOD__", mod)
        .replace("__HOME__", home)
    )


def inject(html: str, block: str) -> str:
    """마커가 있으면 교체, 없으면 </body> 앞에 삽입."""
    if BLOCK_RE.search(html):
        return BLOCK_RE.sub(lambda _: block + "\n", html, count=1)
    if "</body>" not in html:
        raise ValueError("</body> 가 없어 주입할 자리를 찾지 못했습니다")
    return html.replace("</body>", block + "\n</body>", 1)


def to_online(html: str, mod: str) -> str:
    """대상 전환 링크를 아티팩트 URL로. 모듈 파일명 → URL 단순 치환."""
    for other, fname in MODULES.items():
        if other == mod:
            continue
        url = ARTIFACTS[other]
        html = html.replace('href="%s"' % fname, 'href="%s"' % url)
    return html


def main() -> int:
    if not OFF.is_dir():
        print("오프라인 폴더를 찾을 수 없습니다: %s" % OFF)
        return 1

    template = read(TOOLS / "공통블록.html").rstrip("\n")
    scen = json.loads(read(TOOLS / "시나리오.json"))

    changed = []
    for mod, fname in MODULES.items():
        src = OFF / fname
        if not src.exists():
            print("  건너뜀 (없음): %s" % fname)
            continue

        steps = scen.get(mod)
        if not steps:
            print("  경고: 시나리오.json 에 '%s' 단계가 없습니다" % mod)
            steps = []

        base = read(src)

        off_html = inject(base, render_block(template, mod, steps, HOME_OFFLINE))
        if write(src, off_html):
            changed.append("오프라인/" + fname)

        on_html = to_online(
            inject(base, render_block(template, mod, steps, HOME_ONLINE)), mod
        )
        if write(ON / fname, on_html):
            changed.append("온라인/" + fname)

        # 치환이 실제로 먹었는지 확인 — 파일명이 남아 있으면 링크가 깨진 것
        leftover = [f for m, f in MODULES.items() if m != mod and ('href="%s"' % f) in on_html]
        if leftover:
            print("  경고: 온라인판 %s 에 상대 링크가 남았습니다: %s" % (fname, leftover))

        print("  %s  단계 %d개" % (fname, len(steps)))

    # 시작 페이지는 오프라인 전용이라 그대로 둔다
    home = OFF / HOME_OFFLINE
    print("\n시작 페이지: %s" % ("있음" if home.exists() else "없음 — web/index.html 을 만들어 주세요"))

    if changed:
        print("\n바뀐 파일 %d개:" % len(changed))
        for c in changed:
            print("  " + c)
    else:
        print("\n바뀐 파일 없음 (이미 최신)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
