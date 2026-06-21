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

# 추상 소재(기본 도형)지만 분위기 사진이 의미 전달에 더 나은 예외 — id: (mode, keyword)
MODE_OVERRIDE = {
    "1": ("image", "foggy empty street"),   # 데자뷰 = 안개 낀 거리
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
    mode = st["mode"]
    kw = row["image_keyword"].split(",")[0].strip()
    ov = MODE_OVERRIDE.get(row["id"])
    if ov:
        mode, kw = ov
    credit = f"출처 · {row['source']}"
    photo_credit = ""

    img = Image.new("RGB", (W, H), st["bg"])

    if mode == "image":
        got = fetch_image(kw)
        if got:
            content, attribution = got
            try:
                photo = Image.open(io.BytesIO(content)).convert("RGB")
                photo = ImageOps.fit(photo, (W, H), Image.LANCZOS)
                img.paste(photo, (0, 0))
                img = gradient_overlay(img)
                photo_credit = f"사진 · {attribution}"
            except Exception as e:
                print(f"  [이미지 처리 실패] {e}", file=sys.stderr); mode = "shape"
        else:
            mode = "shape"

    if mode == "shape":
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        cx, cy, r = W // 2, 470, 190
        d.ellipse([cx-55-r, cy-r, cx-55+r, cy+r], fill=st["c1"] + (140,))
        d.ellipse([cx+55-r, cy-r, cx+55+r, cy+r], fill=st["c2"] + (140,))
        d.ellipse([cx-9, cy-9, cx+9, cy+9], fill=(255, 255, 255, 230))
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")

    draw = ImageDraw.Draw(img)
    K = (0, 0, 0)  # 외곽선(stroke) 색 — 어떤 배경에서도 글씨가 또렷하게
    TX = 110       # 제목 좌측(악센트 바 공간)
    brand = os.environ.get("BRAND_LABEL", "그거 왜 그래?")  # 상단 브랜드 라벨

    # 상단 라벨: 우측 정렬 (브랜드 + 부제)
    subtitle = os.environ.get("BRAND_SUB", "흥미로운 과학 이야기")
    RX = W - 64  # 우측 기준선
    if mode == "image":
        pill_w = max(draw.textlength(brand, font=font(40)),
                     draw.textlength(subtitle, font=font(24))) + 52
        x2 = W - 38
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(ov).rounded_rectangle([x2 - pill_w, 70, x2, 176], radius=22, fill=(0, 0, 0, 120))
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
        draw = ImageDraw.Draw(img)

    draw.text((RX, 82), brand, font=font(40), anchor="ra", fill=(255, 255, 255),
              stroke_width=2, stroke_fill=K)
    draw.text((RX, 134), subtitle, font=font(24), anchor="ra", fill=(255, 217, 138),
              stroke_width=1, stroke_fill=K)

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
        m = STYLE.get(row["category"], {}).get("mode")
        print(f"[{i}] {row['phenomenon']} ({row['category']}/{m}) ...")
        img = build(row)
        path = os.path.join(OUT, f"card_{i}.png")
        img.save(path, "PNG")
        print(f"   -> {path}")


if __name__ == "__main__":
    main()
