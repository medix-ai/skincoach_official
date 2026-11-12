# 스킨코치 공식 홈페이지

정적 사이트(HTML·CSS·JS)입니다. 빌드 도구 없이 GitHub Pages로 바로 배포됩니다.

- 현재 주소: https://medix-ai.github.io/skincoach_official/
- 개인정보 처리방침: `/privacy/` · 이용약관: `/terms/`

## 폴더 구성

| 경로 | 내용 |
|---|---|
| `index.html` | 랜딩 페이지 (섹션 01~08 + 푸터) |
| `assets/css/site.css` | 전체 스타일. 색상 토큰은 맨 위 `:root` |
| `assets/js/site.js` | App Store·인스타그램 링크 설정, 분석 이벤트, 히어로 영상 |
| `assets/img/shots/` | 앱 캡처 WebP (브랜드명 블러·상태바 제거 완료) |
| `assets/video/` | 히어로 영상 (mp4 + webm, 각 1MB 미만) |
| `privacy/`, `terms/` | 법적 고지 페이지 (앱 저장소 `docs/` 원문을 그대로 옮김) |
| `tools/` | 에셋 생성·법적 고지 동기화 스크립트, OG 이미지 원본 |

## 출시할 때 바꿀 것

`assets/js/site.js` 맨 위 두 값만 채우면 됩니다.

```js
var SITE = {
  appStoreUrl: "https://apps.apple.com/kr/app/id0000000000",
  instagramUrl: "https://www.instagram.com/계정이름/"
};
```

- `appStoreUrl`이 비어 있으면 다운로드 버튼이 모두 'App Store 출시 준비 중'(링크 없음)으로 보입니다.
- `instagramUrl`이 비어 있으면 인스타그램 링크가 숨겨집니다.
- `index.html`의 `apple-itunes-app` 메타 태그 주석을 풀고 앱 ID를 넣으면 아이폰 사파리에 스마트 앱 배너가 뜹니다.
- 정식 출시 후에는 Apple 공식 'App Store에서 다운로드' 배지 이미지로 버튼을 바꾸는 것을 권장합니다(Apple 마케팅 가이드라인).

## GitHub Pages 설정 (최초 1회)

저장소 Settings → Pages → Build and deployment
- Source: **Deploy from a branch**
- Branch: **main** / **(root)** → Save

1~2분 뒤 위 주소로 열립니다. 이후에는 main에 push할 때마다 자동으로 반영됩니다.

## 도메인 연결 (도메인 구매 후)

1. 저장소 Settings → Pages → Custom domain에 도메인 입력 후 Save (루트에 `CNAME` 파일이 자동 생성됨)
2. 도메인 업체 DNS 설정
   - 루트 도메인(예: `skincoach.kr`): A 레코드 4개 `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - `www` 서브도메인: CNAME → `medix-ai.github.io`
3. DNS 반영 후 Settings → Pages에서 **Enforce HTTPS** 체크
4. 사이트 안의 절대 주소를 새 도메인으로 일괄 교체

   ```sh
   grep -rl "medix-ai.github.io/skincoach_official/" --include=*.html --include=*.xml --include=*.txt . \
     | xargs sed -i '' 's#https://medix-ai.github.io/skincoach_official/#https://새도메인/#g'
   ```

   대상: `index.html`(canonical, og:url, og:image), `sitemap.xml`, `robots.txt`

페이지 안의 링크·이미지는 모두 상대 경로라 도메인이 바뀌어도 그대로 동작합니다.

## 분석 도구

GA4 등을 정하면 `index.html` `<head>`의 표시된 위치에 스니펫을 넣으세요. 아래 이벤트가 이미 `gtag`/`dataLayer`로 전송되도록 연결되어 있습니다.

| 이벤트 | 시점 | 파라미터 |
|---|---|---|
| `download_click` | 다운로드 버튼 클릭 (출시 전 버튼은 제외) | `section`: nav / hero / final |
| `instagram_click` | 인스타그램 링크 클릭 | `section`: final / footer |
| `howto_click` | '어떻게 쓰는지 보기' 클릭 | `section` |
| `faq_open` | FAQ 펼침 | `question` |
| `video_complete` | 히어로 영상 한 바퀴 재생 | `video` |

## 에셋 다시 만들기

캡처를 다시 찍었거나 블러 위치를 바꿀 때:

1. 원본 폴더를 저장소 루트에 `홍보용자료/` 이름으로 둡니다 (git에는 올라가지 않음)
2. `pip install pillow`, `brew install ffmpeg`
3. `python3 tools/build_assets.py`

블러·크롭 좌표는 `tools/build_assets.py`의 `SHOTS`에 있습니다 (원본 1206x2622 기준). 처리 내용:
- 타사 브랜드·제품명 블러 (제품 추가, 충돌 경고, 안전 조합, 추천 루틴)
- 상태바·다이내믹 아일랜드 제거
- 추천 루틴의 'AI 분석 완료' 카드와 0/6 줄 제거, 충돌 화면의 중복 경고 제거
- 성분 목록의 영어 기능명(brightening 등) 가림

OG 이미지만 다시 만들 때: `python3 tools/build_assets.py og` (`tools/og.html`을 크롬으로 렌더링)

법적 고지 원문이 바뀌었을 때: `python3 tools/sync_legal.py ../skincoach_app/docs`

## 아직 확정되지 않은 것

| 항목 | 지금 상태 | 바꿀 곳 |
|---|---|---|
| App Store 링크 | '출시 준비 중' 표시 | `site.js` `appStoreUrl` |
| 인스타그램 계정 | 링크 숨김 | `site.js` `instagramUrl` |
| 운영 주체·사업자 정보 | 'MediX'로 표기 | `index.html` 푸터 |

공식 문의 이메일은 `medix.ai.team@gmail.com` 입니다 (푸터, 개인정보 처리방침, 이용약관 공통). 바꿀 때는 `index.html` 푸터와 `tools/sync_legal.py`의 `CONTACT_EMAIL`을 함께 수정하세요.

| FAQ: 가격·안드로이드·미등록 제품·광고 여부 | 답이 정해지지 않아 페이지에서 뺌 | `index.html` FAQ 끝 주석 |
| 올리브영 명칭 사용 | 사실 설명('올리브영 판매 제품 3,100여 개')으로만 사용 | `index.html` 05.6, FAQ Q.02 |
| 개인정보 처리방침·약관 | 앱 저장소 v1.2 원문 게시. 리전·업체 등 실제와 일치하는지 법무 확인 필요 | 원문 수정 후 `sync_legal.py` |
| 로고 SVG | PNG 사용 중 | `assets/img/logo-s*.png` |
| 앱 재촬영 | 08 영어 기능명은 가림 처리, 06 리포트(0/6)는 사용 안 함 | 재촬영 후 `build_assets.py` |
