#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""카드(GitHub raw URL) + 본문을 슬랙 incoming webhook으로 전송(검토용).

incoming webhook은 파일 첨부가 안 되므로, 카드는 리포에 push 된 뒤 raw URL로 첨부한다.
→ 실행 전 카드가 GitHub(public)에 push 돼 있어야 이미지가 보인다.

  python3 notify_slack.py <id> --body "<본문>"

환경변수:
  SLACK_WEBHOOK_URL  (필수)
  GIT_RAW_BASE       (선택; 없으면 git remote origin에서 자동 구성)
"""
import argparse, os, csv, subprocess
import requests

BASE = os.path.dirname(os.path.abspath(__file__))


def topic(cid):
    for r in csv.DictReader(open(os.path.join(BASE, "topics_pool.csv"), encoding="utf-8")):
        if r["id"] == cid:
            return r
    raise SystemExit(f"id {cid} 를 topics_pool.csv 에서 못 찾음")


def raw_base():
    """카드 raw URL의 베이스. 예: https://raw.githubusercontent.com/user/repo/main"""
    if os.environ.get("GIT_RAW_BASE"):
        return os.environ["GIT_RAW_BASE"].rstrip("/")
    try:
        url = subprocess.check_output(["git", "-C", BASE, "remote", "get-url", "origin"], text=True).strip()
        branch = subprocess.check_output(["git", "-C", BASE, "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()
        path = url.split(":", 1)[1] if url.startswith("git@") else url.split("github.com/", 1)[1]
        if path.endswith(".git"):
            path = path[:-4]
        return f"https://raw.githubusercontent.com/{path}/{branch}"
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("--body", required=True, help="루틴이 작성한 본문 텍스트")
    args = ap.parse_args()

    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook:
        raise SystemExit("환경변수 SLACK_WEBHOOK_URL 가 필요합니다")

    t = topic(args.id)
    card = os.path.join(BASE, "cards", f"card_{args.id}.png")
    if not os.path.exists(card):
        raise SystemExit(f"카드가 없습니다: {card}\n먼저: python3 generate_card.py {args.id}")

    base = raw_base()
    img_url = f"{base}/cards/card_{args.id}.png" if base else None

    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": f"검토 · {t['phenomenon']}"}},
        {"type": "context", "elements": [{"type": "mrkdwn",
         "text": f"상태: `{t['status']}`  ·  질문타입: `{t['question_type']}`  ·  {t['source']}"}]},
    ]
    if img_url:
        blocks.append({"type": "image", "image_url": img_url, "alt_text": t["phenomenon"]})
    blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": args.body}})
    blocks.append({"type": "context", "elements": [{"type": "mrkdwn",
        "text": ":white_check_mark: 승인  :pencil2: 수정요청  :frame_with_picture: 이미지교체  (댓글로)"}]})

    payload = {"text": f"검토: 그거 왜 그래? — {t['phenomenon']}", "blocks": blocks}
    r = requests.post(webhook, json=payload, timeout=15)
    print(f"슬랙 전송: {r.status_code} {r.text}")
    if not img_url:
        print("⚠️ git remote origin 이 없어 카드 이미지 URL을 못 만들었습니다 (텍스트만 전송).")


if __name__ == "__main__":
    main()
