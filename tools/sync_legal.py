#!/usr/bin/env python3
"""
앱 저장소의 개인정보 처리방침·이용약관 원문을 이 사이트 디자인으로 감싸서 복사합니다.
본문은 그대로 옮기고(수정하지 않음), 머리말·꼬리말만 사이트 공통 형식으로 바꿉니다.

실행: python3 tools/sync_legal.py [원문 폴더]
      기본 원문 폴더: ../skincoach_app/docs  (privacy.html, terms.html)
결과: privacy/index.html, terms/index.html
"""
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "..", "skincoach_app", "docs")

PAGES = [
    ("privacy.html", "privacy", "개인정보 처리방침"),
    ("terms.html", "terms", "서비스 이용약관"),
]

TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} - 스킨코치</title>
  <meta name="description" content="스킨코치 {title}">
  <meta name="theme-color" content="#EAF7F1">
  <link rel="icon" href="../assets/img/favicon-32.png" sizes="32x32" type="image/png">
  <link rel="apple-touch-icon" href="../assets/img/apple-touch-icon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=IBM+Plex+Mono:wght@500;600&display=swap">
  <link rel="stylesheet" href="../assets/css/site.css">
</head>
<body>
  <a class="skip" href="#main">본문으로 건너뛰기</a>
  <header class="nav">
    <div class="wrap nav__in">
      <a class="brand" href="../" aria-label="스킨코치 홈으로">
        <img src="../assets/img/logo-s.png" alt="" width="83" height="120">
        <span class="brand__ko">스킨코치</span>
        <span class="brand__en">SkinCoach</span>
      </a>
      <a class="link-arrow" href="../">← 홈으로</a>
    </div>
  </header>
  <main id="main">
    <div class="legal-hero">
      <div class="wrap">
        <h1>{title}</h1>
        <p class="meta">{meta}</p>
      </div>
    </div>
    <article class="wrap legal">
<!-- 원문: skincoach_app/docs/{src} (tools/sync_legal.py 로 복사). 본문 수정은 원문에서 하고 다시 실행하세요. -->
{body}
    </article>
  </main>
  <footer class="foot">
    <div class="wrap">
      <ul class="foot__links">
        <li><a href="../privacy/">개인정보 처리방침</a></li>
        <li><a href="../terms/">서비스 이용약관</a></li>
      </ul>
      <div class="foot__legal">
        <p>© 2026 SkinCoach. All rights reserved.</p>
      </div>
    </div>
  </footer>
</body>
</html>
"""


def extract(raw):
    meta = re.search(r'<div class="meta">(.*?)</div>', raw, re.S)
    meta = re.sub(r"\s+", " ", html.unescape(meta.group(1))).strip() if meta else ""
    start = raw.index('<div class="container">') + len('<div class="container">')
    end = raw.index("<footer")
    body = raw[start:end]
    body = body[: body.rindex("</div>")]  # container 닫는 태그 제거
    body = body.replace('href="index.html"', 'href="../"')
    body = body.replace('href="privacy.html"', 'href="../privacy/"').replace('href="terms.html"', 'href="../terms/"')
    return meta, body.rstrip()


for src, slug, title in PAGES:
    path = os.path.join(SRC, src)
    with open(path, encoding="utf-8") as f:
        meta, body = extract(f.read())
    out_dir = os.path.join(ROOT, slug)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(TEMPLATE.format(title=title, meta=html.escape(meta), body=body, src=src))
    print("ok", slug, "|", meta)
