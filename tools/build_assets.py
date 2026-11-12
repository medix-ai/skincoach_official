#!/usr/bin/env python3
"""
홍보용자료/ 원본 캡처·영상 → assets/ 웹용 에셋 생성

필요: Python 3 + Pillow (pip install pillow), ffmpeg (libx264, libvpx-vp9)
실행: 저장소 루트에서  python3 tools/build_assets.py
      OG 이미지만 다시: python3 tools/build_assets.py og

원본 폴더(홍보용자료/)는 용량과 타사 브랜드명 노출 때문에 git에 올리지 않습니다(.gitignore).
캡처를 다시 찍으면 같은 파일명으로 덮어쓰고 이 스크립트를 다시 실행하면 됩니다.

좌표는 모두 원본 1206x2622 기준입니다.
- blur:     타사 브랜드·제품명 가림 (GaussianBlur)
- paint:    앱의 알려진 표시 문제(영어 성분 기능명)를 카드 배경색으로 덮음
- segments: 세로로 잘라 이어 붙일 구간. 상태바(0~135) 제거, 중복 경고·0/6 구간 제거에 사용
- max_h:    이어 붙인 뒤 위에서부터 이 높이까지만 사용 (사용법 4컷을 같은 비율로 맞춤)
"""
import json
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "홍보용자료")
OUT_IMG = os.path.join(ROOT, "assets", "img")
OUT_SHOT = os.path.join(OUT_IMG, "shots")
OUT_VID = os.path.join(ROOT, "assets", "video")
WEB_W = 800  # 2x 기준 폭

C02 = "02_맞춤루틴_생성/캡처/"
C03 = "03_데일리_피부체크인/캡처/"
C04 = "04_홈_대시보드/캡처/"
C06 = "06_루틴_리포트_달성현황/캡처/"
C07 = "07_화장대_성분충돌체크/캡처/"
C08 = "08_제품상세_성분정보/캡처/"
C09 = "09_성분체크/캡처/"
C10 = "10_마이페이지_생리주기/캡처/"

ROUTINE_BLUR = [(185, 1895, 940, 1965), (185, 2245, 940, 2315), (185, 2595, 940, 2622)]
# 추천 루틴: 'AI 분석 완료' 카드와 '0/6' 줄을 빼고 이어 붙임
ROUTINE_SEGS = [(165, 478), (1250, 1440), (1650, 2622)]

SHOTS = {
    # 섹션 3 핵심 기능
    "feat-routine": dict(src=C02 + "06_맞춤루틴_생성결과_AI분석.png", blur=ROUTINE_BLUR, segments=ROUTINE_SEGS),
    "feat-conflict": dict(
        src=C07 + "06_충돌이_있어요_레티놀_AHA_BHA_경고.png",
        blur=[(270, 630, 1160, 890)],
        # 같은 경고가 두 번 나오는 표시 문제: 두 번째 카드(1621~1860) 제거
        segments=[(200, 1621), (1860, 2110)],
    ),
    "feat-safe": dict(
        src=C09 + "04_안전한_조합이에요_화장대추가.png",
        blur=[(270, 630, 1100, 830), (120, 440, 700, 540)],
        segments=[(200, 1480)],
    ),
    "feat-checkin": dict(src=C03 + "04_미세먼지_나쁨_입력완료.png", segments=[(190, 2440)]),
    "feat-checkin-result": dict(src=C03 + "05_체크인_반영된_홈_오늘피부_트러블.png", segments=[(1775, 1975)]),
    # 섹션 4 사용법 (같은 비율 1206x1500)
    "step-1": dict(
        src=C07 + "02_제품추가_코스알엑스_3개선택.png",
        blur=[(330, 640, 1110, 2300), (130, 440, 640, 550)],
        segments=[(190, 1690)],
    ),
    "step-2": dict(src=C02 + "05_집중케어_미백_트러블.png", segments=[(190, 1690)]),
    "step-3": dict(src=C02 + "06_맞춤루틴_생성결과_AI분석.png", blur=ROUTINE_BLUR, segments=ROUTINE_SEGS, max_h=1500),
    "step-4": dict(src=C04 + "02_모닝루틴_6단계_선크림까지.png", segments=[(165, 1665)]),
    # 섹션 5 더 많은 기능 (약 3:2 디테일 크롭)
    "more-safety": dict(
        src=C08 + "03_성분목록_안전_주의_표시_사용법_주의사항.png",
        paint=[((140, 812, 640, 862), (249, 249, 250)),
               ((140, 1026, 640, 1076), (249, 249, 250)),
               ((140, 1240, 640, 1290), (249, 249, 250))],
        segments=[(560, 1364)],
    ),
    "more-ampm": dict(src=C08 + "05_성분상호작용_경고_AM_PM_분리사용.png", segments=[(870, 1674)]),
    "more-alarm": dict(src=C04 + "06_아침루틴_알림_ON_08시.png", segments=[(330, 1134)]),
    "more-calendar": dict(src=C06 + "05_달성현황_월간캘린더.png", segments=[(1460, 2264)]),
    "more-cycle": dict(src=C10 + "05_주기단계_캘린더_다음생리예상.png", segments=[(940, 1830)]),
}


def process_shot(spec):
    im = Image.open(os.path.join(SRC, spec["src"])).convert("RGB")
    for (x0, y0, x1, y1) in spec.get("blur", []):
        x1, y1 = min(x1, im.width), min(y1, im.height)
        region = im.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(28))
        im.paste(region, (x0, y0))
    for (box, color) in spec.get("paint", []):
        im.paste(color, box)
    segs = [im.crop((0, y0, im.width, y1)) for (y0, y1) in spec["segments"]]
    h = sum(s.height for s in segs)
    out = Image.new("RGB", (im.width, h))
    y = 0
    for s in segs:
        out.paste(s, (0, y))
        y += s.height
    if spec.get("max_h"):
        out = out.crop((0, 0, out.width, min(out.height, spec["max_h"])))
    w = WEB_W
    return out.resize((w, round(out.height * w / out.width)), Image.LANCZOS)


def build_shots(sizes):
    os.makedirs(OUT_SHOT, exist_ok=True)
    for name, spec in SHOTS.items():
        im = process_shot(spec)
        path = os.path.join(OUT_SHOT, name + ".webp")
        im.save(path, "WEBP", quality=80, method=6)
        sizes["shots/" + name + ".webp"] = im.size
        print(f"shot  {name:22s} {im.size[0]}x{im.size[1]}  {os.path.getsize(path)//1024}KB")


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def build_video(sizes):
    """히어로: 04 홈 대시보드. 상태바 제거, 540px 폭, 무음, mp4(H.264) + webm(VP9)"""
    os.makedirs(OUT_VID, exist_ok=True)
    src = os.path.join(SRC, "04_홈_대시보드", "04_홈_대시보드.mp4")
    vf = "crop=1206:2456:0:166,scale=540:-2,fps=24"
    mp4 = os.path.join(OUT_VID, "home.mp4")
    webm = os.path.join(OUT_VID, "home.webm")
    run(["ffmpeg", "-y", "-i", src, "-vf", vf, "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "22",
         "-profile:v", "high", "-pix_fmt", "yuv420p", "-movflags", "+faststart", mp4])
    run(["ffmpeg", "-y", "-i", src, "-vf", vf, "-an", "-c:v", "libvpx-vp9", "-crf", "32", "-b:v", "0",
         "-row-mt", "1", "-deadline", "good", "-cpu-used", "2", webm])
    for p in (mp4, webm):
        print(f"video {os.path.basename(p):22s} {os.path.getsize(p)/1e6:.2f}MB")
    # 포스터: 첫 프레임(원본 해상도에서 추출 후 800px)
    tmp = os.path.join(OUT_VID, "_poster.png")
    run(["ffmpeg", "-y", "-ss", "0", "-i", src, "-frames:v", "1", "-vf", "crop=1206:2456:0:166", tmp])
    im = Image.open(tmp).convert("RGB")
    im = im.resize((WEB_W, round(im.height * WEB_W / im.width)), Image.LANCZOS)
    im.save(os.path.join(OUT_SHOT, "hero-home.webp"), "WEBP", quality=82, method=6)
    os.remove(tmp)
    sizes["shots/hero-home.webp"] = im.size
    print("shot  hero-home (poster)", im.size)


def square(im, size, bg=None, pad=0.14):
    """투명 S 심볼을 정사각 캔버스 중앙에 배치"""
    canvas = Image.new("RGBA", (size, size), bg or (0, 0, 0, 0))
    inner = int(size * (1 - pad * 2))
    s = im.copy()
    s.thumbnail((inner, inner), Image.LANCZOS)
    canvas.paste(s, ((size - s.width) // 2, (size - s.height) // 2), s)
    return canvas


def build_logos(sizes):
    os.makedirs(OUT_IMG, exist_ok=True)
    s = Image.open(os.path.join(SRC, "logo", "logo_s.png")).convert("RGBA")
    # 네비게이션·푸터용 (높이 120px, 2x 이상)
    nav = s.copy()
    nav.thumbnail((400, 120), Image.LANCZOS)
    nav.save(os.path.join(OUT_IMG, "logo-s.png"), optimize=True)
    sizes["logo-s.png"] = nav.size
    big = s.copy()
    big.thumbnail((400, 540), Image.LANCZOS)
    big.save(os.path.join(OUT_IMG, "logo-s-large.png"), optimize=True)
    sizes["logo-s-large.png"] = big.size
    square(s, 32, pad=0.04).save(os.path.join(OUT_IMG, "favicon-32.png"))
    square(s, 180, bg=(255, 255, 255, 255)).convert("RGB").save(os.path.join(OUT_IMG, "apple-touch-icon.png"))
    square(s, 512, bg=(255, 255, 255, 255)).convert("RGB").save(os.path.join(OUT_IMG, "icon-512.png"))
    print("logo  logo-s, favicon-32, apple-touch-icon, icon-512")


def find_chrome():
    for p in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              shutil.which("google-chrome") or "", shutil.which("chromium") or ""):
        if p and os.path.exists(p):
            return p
    return None


def build_og():
    """tools/og.html 을 헤드리스 크롬으로 1200x630 렌더링"""
    chrome = find_chrome()
    if not chrome:
        print("og    Chrome 없음, 건너뜀")
        return
    out = os.path.join(OUT_IMG, "og.png")
    subprocess.run([chrome, "--headless=new", "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--window-size=1200,630", "--virtual-time-budget=8000",
                    f"--screenshot={out}", "file://" + os.path.join(ROOT, "tools", "og.html")],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    im = Image.open(out).convert("RGB").crop((0, 0, 1200, 630))
    im.save(out, optimize=True)
    print("og    og.png", im.size, f"{os.path.getsize(out)//1024}KB")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "og":
        build_og()
        sys.exit(0)
    if not os.path.isdir(SRC):
        sys.exit(f"원본 폴더가 없습니다: {SRC}")
    sizes = {}
    build_shots(sizes)
    build_video(sizes)
    build_logos(sizes)
    with open(os.path.join(ROOT, "tools", "asset_sizes.json"), "w") as f:
        json.dump(sizes, f, indent=1, ensure_ascii=False)
    build_og() if os.path.exists(os.path.join(ROOT, "tools", "og.html")) else None
