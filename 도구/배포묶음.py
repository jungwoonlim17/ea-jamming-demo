# -*- coding: utf-8 -*-
"""인터넷 없이 쓰는 배포용 zip 두 개를 만든다.

    python "도구/배포묶음.py"

받는 사람은 압축을 풀고 index.html 을 더블클릭하면 끝이다. 설치도 서버도 필요 없다.
web/ 와 web-lite/ 안에는 fetch·모듈·워커가 없고 서비스 워커 등록은 프로토콜로 막혀 있어
file:// 에서 그대로 동작한다. 바깥에서 받아 오는 것은 Google Fonts 하나뿐이고,
그게 막히면 글꼴만 기본 글꼴로 바뀌고 기능은 같다.

멱등하다. web/ 이나 web-lite/ 를 고친 뒤 다시 돌리면 묶음도 따라 바뀐다.
"""
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "배포"

# 묶음 안에서 제외할 것 — 썸네일은 갤러리 등록용이라 받는 사람에게 필요 없다.
SKIP = {"thumb.png"}

READ_FULL = """전자전 중 EA의 위험성 — 재밍 시연 교육자료 (학부 전자전공용)

■ 여는 법
   이 폴더의 index.html 을 더블클릭하세요. 그게 전부입니다.
   설치할 것도, 인터넷도 필요 없습니다.
   (Chrome 또는 Edge 를 권합니다.)

■ 들어 있는 것
   index.html      시작 화면 — 여기서 네 가지 중 하나를 고릅니다
   01-comms.html   음성 통신 재밍 (소리가 납니다)
   02-gnss.html    위성항법 재밍·스푸핑
   03-ppi.html     탐색 레이더(PPI) 재밍
   04-sar.html     SAR 영상 재밍

■ 쓰는 법
   왼쪽 손잡이로 재머 출력과 거리를 움직이면, 가운데 화면과
   오른쪽 수식의 숫자가 같이 바뀝니다.
   위쪽 발표 바의 단계 버튼을 누르면 정해진 시연 장면이 그대로 재현됩니다.

   단축키   , .  단계 이동    Space 재머 켜고 끄기
            1 2  잡음/기만    Q W E R 대상 전환    T 밝게/어둡게    ? 도움말

■ 인터넷에서 바로 열려면
   https://ea-jamming-demo.vercel.app
   (같은 내용이고, 휴대폰에 앱으로 설치할 수도 있습니다.)

■ 알아 둘 것
   모든 제원은 교육용 가상 값이며 실제 장비와 무관합니다.
   인터넷이 없으면 글꼴만 기본 글꼴로 바뀌고 기능은 그대로입니다.

   만든이 임정운 · 공군사관학교
   소스 https://github.com/jungwoonlim17/ea-jamming-demo
"""

READ_LITE = """전자전 재밍의 원리 이해 — 교육자료 (일반 공개용)

■ 여는 법
   이 폴더의 index.html 을 더블클릭하세요. 그게 전부입니다.
   설치할 것도, 인터넷도 필요 없습니다.
   (Chrome 또는 Edge 를 권합니다.)

■ 들어 있는 것
   index.html                시작 화면
   01-comms.html             무전 통신 — 방해 전파를 쏘면 바로 끊길까?
   02-gnss.html              위성 항법 — 화면은 멀쩡한데 위치가 틀린다
   교안_전자전_재밍의_원리_이해.pdf
                             시연을 진행하는 사람을 위한 10분짜리 교안입니다.
                             순서, 그대로 읽어도 되는 대사, 화면에서 짚어 줄 숫자,
                             배경지식, 예상 질문이 들어 있습니다.

■ 쓰는 법
   손잡이로 재머 출력과 거리를 움직여 보세요. 받는 쪽에 닿는 세기가 바로 바뀝니다.
   위쪽 단계 버튼을 1번부터 순서대로 누르면 시연 장면이 그대로 재현됩니다.
   무전 통신에서는 소리가 납니다 — 음량을 미리 확인하세요.

■ 인터넷에서 바로 열려면
   https://ea-jamming-basic.vercel.app

■ 알아 둘 것
   모든 제원은 교육용 가상 값이며 실제 장비와 무관합니다.
   인터넷이 없으면 글꼴만 기본 글꼴로 바뀌고 기능은 그대로입니다.

   만든이 임정운 · 공군사관학교
   소스 https://github.com/jungwoonlim17/ea-jamming-demo
"""


def pack(zip_name, top, src_dir, readme, extras=()):
    """src_dir 안을 top/ 아래로 넣고, 읽어보기와 덤 파일을 더한다."""
    OUT.mkdir(exist_ok=True)
    path = OUT / zip_name
    n = 0
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(src_dir.rglob("*")):
            if f.is_dir() or f.name in SKIP:
                continue
            z.write(f, "%s/%s" % (top, f.relative_to(src_dir).as_posix()))
            n += 1
        for extra in extras:
            if not extra.exists():
                print("  !! 없는 파일이라 건너뜀:", extra.name)
                continue
            z.write(extra, "%s/%s" % (top, extra.name))
            n += 1
        # Windows 메모장이 한글을 바로 읽도록 BOM 을 붙인다.
        z.writestr("%s/읽어보기.txt" % top, "﻿" + readme.replace("\n", "\r\n"))
        n += 1
    print("  %s — 파일 %d개 · %.1f MB" % (zip_name, n, path.stat().st_size / 1048576))


print("배포 묶음을 만듭니다 →", OUT)
pack("전자전_재밍_시연자료_수업용.zip", "전자전_재밍_시연자료", ROOT / "web", READ_FULL)
pack("전자전_재밍의_원리_이해_공개용.zip", "전자전_재밍의_원리_이해", ROOT / "web-lite", READ_LITE,
     extras=[ROOT / "교안_전자전_재밍의_원리_이해.pdf"])
print("끝났습니다. 압축을 풀고 index.html 을 더블클릭하면 됩니다.")
