#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""슬랙 검토 카드 발송 (이슈공분봇 패턴).

- 발송(기계적)은 GitHub Actions(ci_post.py)에서. webhook은 repo secret SLACK_WEBHOOK_URL.
- 루틴은 글 생성 + cards-latest.json/카드 push만. 발송 안 함.

CLI(로컬 테스트용):  python3 notify_slack.py <id> --body "<본문>"
라이브러리:          send_review(id, body, webhook)  ← ci_post.py 가 사용
환경변수:            SLACK_WEBHOOK_URL (또는 HOME/.env)
"""
import argparse, os, csv, subprocess, json, ssl
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))

try:
    import certifi
    _SSL = ssl.create_default_context(cafile=certifi.where())
except Exception:
    _SSL = ssl.create_default_context()


def load_webhook():
    """HOME/.env 우선, 없으면 os.environ (bot-monitor/이슈공분봇 규약)"""
    path = os.path.join(BASE, ".env")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line.startswith("SLACK_WEBHOOK_URL="):
                return line.split("=", 1)[1].strip()
    return os.environ.get("SLACK_WEBHOOK_URL")


def topic(cid):
    for r in csv.DictReader(open(os.path.join(BASE, "topics_pool.csv"), encoding="utf-8")):
        if r["id"] == cid:
            return r
    raise SystemExit(f"id {cid} 를 topics_pool.csv 에서 못 찾음")


def pool_status():
    rows = list(csv.DictReader(open(os.path.join(BASE, "topics_pool.csv"), encoding="utf-8")))
    total = len(rows)
    try:
        st = json.load(open(os.path.join(BASE, "state", "history.json"), encoding="utf-8"))
        rem = total - len(set(st.get("posted", [])))
    except Exception:
        rem = total
    return total, rem


def raw_base():
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


def build_blocks(cid, body):
    t = topic(cid)
    base = raw_base()
    img_url = f"{base}/cards/card_{cid}.png" if base else None
    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": f"검토 · {t['phenomenon']}"}},
        {"type": "context", "elements": [{"type": "mrkdwn",
         "text": f"상태: `{t['status']}`  ·  질문타입: `{t['question_type']}`  ·  {t['source']}"}]},
    ]
    if img_url:
        blocks.append({"type": "image", "image_url": img_url, "alt_text": t["phenomenon"]})
    blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": body}})
    total, rem = pool_status()
    pool_line = f"📊 남은 소재 {rem}/{total}" + ("   ·   ⚠️ 소재 보충 필요" if rem <= 7 else "")
    blocks.append({"type": "context", "elements": [{"type": "mrkdwn",
        "text": ":white_check_mark: 승인  :pencil2: 수정요청  :frame_with_picture: 이미지교체"}]})
    blocks.append({"type": "context", "elements": [{"type": "mrkdwn", "text": pool_line}]})
    return blocks, t["phenomenon"]


def post(webhook, payload):
    req = urllib.request.Request(webhook, data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, context=_SSL, timeout=15) as r:
        return r.status, r.read().decode()


def send_review(cid, body, webhook=None):
    webhook = webhook or load_webhook()
    if not webhook:
        raise SystemExit("SLACK_WEBHOOK_URL 가 필요합니다")
    blocks, phen = build_blocks(cid, body)
    status, text = post(webhook, {"text": f"검토: 그거 왜 그래? — {phen}", "blocks": blocks})
    return f"{status} {text}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("--body", required=True)
    args = ap.parse_args()
    print("슬랙 전송:", send_review(args.id, args.body))


if __name__ == "__main__":
    main()
