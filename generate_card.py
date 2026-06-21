#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"그거 왜 그래?" 일상 미스터리 과학 봇 — 카드 생성기 (Pillow 버전)

topics_pool.csv 한 행 -> 피드용 카드 PNG (1080x1350, 4:5).
- 이미지 모드: Openverse(무료 CC 이미지) 검색 -> 다운로드 -> 배경 합성
- 도형 모드 : 추상 소재(뇌·기억)는 카테고리별 도형 일러스트
의존: Pillow, requests  (외부 변환기 불필요)
사용:  python3 generate_card.py 9 23 1      # csv id 지정
       python3 generate_card.py             # 샘플 3개
"""
import csv, sys, os, io
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

BASE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(BASE, "topics_pool.csv")
OUT = os.path.join(BASE, "cards")
os.makedirs(OUT, exist_ok=True)

W, H = 1080, 1350
UA = {"User-Agent": "science-mystery-bot/0.1 (curiosity cards)"}


def _font_path():
    # 리포 동봉 폰트 우선 → 환경(리눅스 클라우드 등) 무관하게 한글 렌더
    for p in (os.path.join(BASE, "fonts", "NanumGothic.ttf"),
              "/System/Library/Fonts/Supplemental/AppleGothic.ttf"):
        if os.path.exists(p):
            return p
    raise SystemExit("한글 폰트를 찾을 수 없습니다 (fonts/NanumGothic.ttf 를 두세요)")


FONT = _font_path()

STYLE = {
    "뇌·기억":   {"bg": (32, 38, 55),  "c1": (91, 108, 184), "c2": (75, 168, 154), "mode": "shape"},
    "사회·심리": {"bg": (43, 34, 48),  "c1": (193, 102, 138),"c2": (224, 168, 95), "mode": "image"},
    "몸·감각":   {"bg": (45, 38, 32),  "c1": (224, 137, 75), "c2": (217, 193, 75), "mode": "image"},
    "자연·물리": {"bg": (27, 39, 51),  "c1": (75, 134, 193), "c2": (75, 193, 184), "mode": "image"},
}
BADGE = {"정설": "과학적 사실", "유력가설": "유력한 가설",
         "논쟁중": "아직 논쟁 중", "미스터리": "아직 미스터리"}

# 무조건 이미지. 일부 소재는 기본 키워드보다 나은 분위기 키워드를 우선 시도.
KEYWORD_OVERRIDE = {
    "1": "foggy empty street",   # 데자뷰 = 안개 낀 거리
}


def font(sz):
    return ImageFont.truetype(FONT, sz)


def wrap_px(draw, text, fnt, max_w, by_word=False):
    """픽셀 폭 기준 줄바꿈. by_word=True면 어절(띄어쓰기) 단위 — 한국어 제목용"""
    if by_word:
        lines, cur = [], ""
        for w in text.split(" "):
            t = (cur + " " + w).strip()
            if not cur or draw.textlength(t, font=fnt) <= max_w:
                cur = t
            else:
                lines.append(cur); cur = w
        if cur:
            lines.append(cur)
        return lines or [""]
    lines, cur = [], ""
    for ch in text:
        if draw.textlength(cur + ch, font=fnt) <= max_w:
            cur += ch
        else:
            lines.append(cur); cur = ch
    if cur:
        lines.append(cur)
    return lines


def fetch_image(keyword):
    try:
        r = requests.get("https://api.openverse.org/v1/images/",
                         params={"q": keyword, "page_size": 8,
                                 "license_type": "commercial,modification"},
                         headers=UA, timeout=15)
        for item in r.json().get("results", []):
            # Flickr 등 원본 CDN은 hotlink 차단(429) -> Openverse thumbnail 프록시 우선
            src = item.get("thumbnail") or item.get("url")
            if not src:
                continue
            try:
                img = requests.get(src, headers=UA, timeout=20)
            except Exception:
                continue
            if img.ok and len(img.content) > 3000:
                cred = item.get("creator") or "Unknown"
                lic = (item.get("license") or "cc").upper()
                return img.content, f"{cred} / CC {lic} · Openverse"
    except Exception as e:
        print(f"  [이미지 검색 실패] {keyword}: {e}", file=sys.stderr)
    return None


def gradient_overlay(img, start_y=505, strength=0.93, top_h=255, top_strength=0.58):
    """하단(텍스트용) + 상단(브랜드 라벨용) 검정 그라데이션 오버레이"""
    mask = Image.new("L", (1, H), 0)
    for y in range(H):
        a = 0
        if y > start_y:  # 하단
            a = int(255 * strength * ((y - start_y) / (H - start_y)) ** 1.3)
        elif y < top_h:  # 상단
            a = int(255 * top_strength * ((top_h - y) / top_h))
        mask.putpixel((0, y), min(max(a, 0), 255))
    mask = mask.resize((W, H))
    img.paste(Image.new("RGB", (W, H), (0, 0, 0)), (0, 0), mask)
    return img


def build(row):
    cat = row["category"]
    st = STYLE.get(cat, STYLE["뇌·기억"])
    # 무조건 이미지: 키워드를 순차로 시도해 사진을 반드시 찾는다 (도형 모드 없음).
    keywords = [k.strip() for k in row["image_keyword"].split(",") if k.strip()]
    ovkw = KEYWORD_OVERRIDE.get(row["id"])
    if ovkw:
        keywords = [ovkw] + keywords
    credit = f"출처 · {row['source']}"
    photo_credit = ""

    img = Image.new("RGB", (W, H), st["bg"])

    got = None
    for kw in keywords:
        got = fetch_image(kw)
        if got:
            break
    if got:
        content, attribution = got
        try:
            photo = Image.open(io.BytesIO(content)).convert("RGB")
            photo = ImageOps.fit(photo, (W, H), Image.LANCZOS)
            img.paste(photo, (0, 0))
            img = gradient_overlay(img)
            photo_credit = f"사진 · {attribution}"
        except Exception as e:
            print(f"  [이미지 처리 실패] {e}", file=sys.stderr)
    else:
        print(f"  [경고] 이미지 못 찾음 → 단색 배경: {row['phenomenon']}", file=sys.stderr)

    draw = ImageDraw.Draw(img)
    K = (0, 0, 0)  # 외곽선(stroke) 색 — 어떤 배경에서도 글씨가 또렷하게
    TX = 110       # 제목 좌측(악센트 바 공간)
    brand = os.environ.get("BRAND_LABEL", "그거 왜 그래?")  # 상단 브랜드 라벨

    # 상단 라벨: 우측 정렬 (브랜드 + 부제) — 배경 박스 없이 텍스트만, 외곽선으로 가독성 확보
    subtitle = os.environ.get("BRAND_SUB", "일상 속 과학 미스터리")
    RX = W - 64  # 우측 기준선
    draw.text((RX, 82), brand, font=font(40), anchor="ra", fill=(255, 255, 255),
              stroke_width=3, stroke_fill=K)
    draw.text((RX, 134), subtitle, font=font(24), anchor="ra", fill=(255, 217, 138),
              stroke_width=2, stroke_fill=K)

    # 하단: 제목(phenomenon, 강조) + 후킹(hook)
    f_title, f_hook, f_src = font(66), font(36), font(22)
    title_lines = wrap_px(draw, row["phenomenon"], f_title, W - TX - 70, by_word=True)
    hook_lines = wrap_px(draw, row["hook"], f_hook, W - 160, by_word=True)

    src_y = H - 112
    hook_h = len(hook_lines) * 46
    title_h = len(title_lines) * 78
    hook_y = src_y - 42 - hook_h
    title_y = hook_y - 26 - title_h

    # 제목 강조용 컬러 악센트 바
    draw.rounded_rectangle([80, title_y + 10, 93, title_y + title_h - 8],
                           radius=6, fill=st["c2"])

    y = title_y
    for ln in title_lines:
        draw.text((TX, y), ln, font=f_title, fill=(255, 255, 255),
                  stroke_width=2, stroke_fill=K); y += 78
    y = hook_y
    for ln in hook_lines:
        draw.text((80, y), ln, font=f_hook, fill=(245, 243, 237),
                  stroke_width=1, stroke_fill=K); y += 46
    draw.text((80, src_y), credit[:70], font=f_src, fill=(228, 228, 228),
              stroke_width=1, stroke_fill=K)
    if photo_credit:
        draw.text((80, src_y + 32), photo_credit[:70], font=font(19),
                  fill=(205, 205, 205), stroke_width=1, stroke_fill=K)

    return img


def main():
    ids = sys.argv[1:] or ["9", "23", "1"]
    rows = {r["id"]: r for r in csv.DictReader(open(CSV, encoding="utf-8"))}
    for i in ids:
        row = rows.get(i)
        if not row:
            print(f"id {i} 없음"); continue
        print(f"[{i}] {row['phenomenon']} ({row['category']}) ...")
        img = build(row)
        path = os.path.join(OUT, f"card_{i}.png")
        img.save(path, "PNG")
        print(f"   -> {path}")


if __name__ == "__main__":
    main()
