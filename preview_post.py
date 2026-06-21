#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""실제 아고라 피드 게시물 미리보기 목업 (카드 + 본문 + 예상 댓글)"""
import csv, os, sys
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
FONT = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
W = 860
PAD = 44
INK = (26, 26, 26)
SUB = (140, 140, 140)
ACC = (29, 111, 224)


def f(s): return ImageFont.truetype(FONT, s)


def wrap(draw, text, fnt, mw):
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            lines.append(cur); cur = ""; continue
        if draw.textlength(cur + ch, font=fnt) <= mw:
            cur += ch
        else:
            lines.append(cur); cur = ch
    if cur:
        lines.append(cur)
    return lines


def main():
    cid = sys.argv[1] if len(sys.argv) > 1 else "5"
    rows = {r["id"]: r for r in csv.DictReader(open(os.path.join(BASE, "topics_pool.csv"), encoding="utf-8"))}
    row = rows[cid]

    # 예상 댓글(시연용 — 실제 아님)
    comments = [
        ("민지", "헐 그럼 내가 아는 내 목소리가 가짜였던 거야...?"),
        ("회색곰", "녹음 들을 때마다 손발 오그라들던 이유가 이거였네 ㅋㅋ"),
    ]

    card = Image.open(os.path.join(BASE, "cards", f"card_{cid}.png")).convert("RGB")
    cw = W - PAD * 2
    ch = int(card.height * cw / card.width)
    card = card.resize((cw, ch), Image.LANCZOS)
    mask = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, cw, ch], radius=28, fill=255)

    f_name, f_meta, f_body, f_q = f(31), f(24), f(31), f(32)
    f_cu, f_ct = f(26), f(28)

    # --- 높이 계산용 더미 ---
    dummy = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    body_lines = wrap(dummy, row["explanation"], f_body, cw)
    q_lines = wrap(dummy, row["closing_question"], f_q, cw)

    y = 44
    y += 80                                  # 헤더
    y += len(body_lines) * 44 + 22           # 본문
    y += len(q_lines) * 46 + 30              # 질문
    y += ch + 28                             # 카드
    y += 64                                   # 액션바
    y += 28                                   # 구분선 여백
    for _ in comments:
        y += 2 * 38 + 30
    H = y + 30

    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)

    # 헤더: 아바타 + 계정명
    d.ellipse([PAD, 44, PAD + 64, 108], fill=(43, 60, 110))
    d.text((PAD + 18, 60), "왜", font=f(30), fill=(255, 255, 255))
    d.text((PAD + 84, 50), "그거 왜 그래?", font=f_name, fill=INK)
    d.text((PAD + 84, 88), "@geugeo_why · 2시간", font=f_meta, fill=SUB)

    y = 140
    for ln in body_lines:
        d.text((PAD, y), ln, font=f_body, fill=INK); y += 44
    y += 22
    for ln in q_lines:
        d.text((PAD, y), ln, font=f_q, fill=ACC); y += 46
    y += 8

    img.paste(card, (PAD, y), mask)
    y += ch + 24

    # 액션바
    d.text((PAD, y), "♥ 공감 142     댓글 38     공유", font=f(27), fill=SUB)
    y += 56
    d.line([PAD, y, W - PAD, y], fill=(230, 230, 230), width=2)
    y += 26
    d.text((PAD, y - 2), "예상 댓글", font=f(22), fill=(180, 180, 180))
    y += 34

    for name, text in comments:
        d.ellipse([PAD, y, PAD + 40, y + 40], fill=(210, 214, 224))
        d.text((PAD + 56, y - 2), name, font=f_cu, fill=INK)
        cl = wrap(d, text, f_ct, cw - 56)
        yy = y + 32
        for ln in cl:
            d.text((PAD + 56, yy), ln, font=f_ct, fill=(60, 60, 60)); yy += 36
        y = yy + 22

    out = os.path.join(BASE, "cards", f"post_{cid}.png")
    img.save(out, "PNG")
    print(out)


if __name__ == "__main__":
    main()
