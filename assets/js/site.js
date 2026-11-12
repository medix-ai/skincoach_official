/* 스킨코치 공식 홈페이지 스크립트 */
(function () {
  "use strict";

  /* ===== 설정: 출시·계정 확정 후 이 두 값만 채우면 됩니다 =====
     appStoreUrl  비어 있으면 모든 다운로드 버튼이 'App Store 출시 준비 중'(링크 없음)으로 보입니다.
     instagramUrl 비어 있으면 인스타그램 링크를 숨깁니다. */
  var SITE = {
    appStoreUrl: "",   // 예: "https://apps.apple.com/kr/app/id0000000000"
    instagramUrl: ""   // 예: "https://www.instagram.com/계정이름/"
  };

  /* ===== 분석 이벤트 =====
     GA4(gtag) 스니펫을 index.html <head>에 넣으면 그대로 전송됩니다. 없으면 dataLayer에만 쌓입니다. */
  function track(name, params) {
    params = params || {};
    try {
      if (typeof window.gtag === "function") window.gtag("event", name, params);
      window.dataLayer = window.dataLayer || [];
      var evt = { event: name };
      for (var k in params) evt[k] = params[k];
      window.dataLayer.push(evt);
    } catch (e) { /* 분석 실패는 페이지 동작에 영향 없음 */ }
  }
  window.scTrack = track;

  /* App Store 버튼 */
  if (SITE.appStoreUrl) {
    document.querySelectorAll("[data-store]").forEach(function (el) {
      el.setAttribute("href", SITE.appStoreUrl);
      el.setAttribute("rel", "noopener");
      el.classList.remove("is-soon");
      var label = el.querySelector("[data-store-label]");
      if (label) label.textContent = "App Store에서 다운로드";
    });
  }

  /* 인스타그램 링크 */
  if (SITE.instagramUrl) {
    document.querySelectorAll("[data-instagram]").forEach(function (el) {
      el.setAttribute("href", SITE.instagramUrl);
      var box = el.closest("[data-instagram-box]") || el;
      box.hidden = false;
    });
  }

  /* 클릭 이벤트: data-track="이벤트명" data-section="섹션" */
  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-track]");
    if (!t) return;
    if (t.hasAttribute("data-store") && !t.getAttribute("href")) return; // 출시 전 버튼은 집계 안 함
    track(t.getAttribute("data-track"), {
      section: t.getAttribute("data-section") || "",
      link_url: t.getAttribute("href") || ""
    });
  });

  /* FAQ 열기 */
  document.querySelectorAll("details[data-faq]").forEach(function (d) {
    d.addEventListener("toggle", function () {
      if (d.open) track("faq_open", { question: d.getAttribute("data-faq") });
    });
  });

  /* 히어로 영상: 동작 줄이기·데이터 절약 설정이면 포스터 이미지만 */
  var video = document.querySelector("video[data-lazy]");
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var saveData = navigator.connection && navigator.connection.saveData;
  if (video && !reduce && !saveData && "IntersectionObserver" in window) {
    [["data-webm", "video/webm"], ["data-mp4", "video/mp4"]].forEach(function (s) {
      var src = video.getAttribute(s[0]);
      if (!src) return;
      var el = document.createElement("source");
      el.src = src;
      el.type = s[1];
      video.appendChild(el);
    });
    video.load();
    new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          var p = video.play();
          if (p && p.catch) p.catch(function () {});
        } else {
          video.pause();
        }
      });
    }, { threshold: 0.2 }).observe(video);

    var last = 0, done = false;
    video.addEventListener("timeupdate", function () {
      if (!done && video.currentTime + 1 < last) { // 루프가 한 바퀴 돌았을 때 = 재생 완료
        done = true;
        track("video_complete", { video: "hero_home" });
      }
      last = video.currentTime;
    });
  }

  /* 도장 찍히는 효과 */
  var reveals = document.querySelectorAll("[data-reveal]");
  if (reduce || !("IntersectionObserver" in window)) {
    reveals.forEach(function (el) { el.classList.add("is-in"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          en.target.classList.add("is-in");
          io.unobserve(en.target);
        }
      });
    }, { threshold: 0.35 });
    reveals.forEach(function (el) { io.observe(el); });
  }
})();
