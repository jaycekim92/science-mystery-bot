#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CI 발송 — 루틴이 push한 cards-latest.json 을 슬랙 검토 채널로 발송한다 (GitHub Actions 전용).

발송(기계적 작업)은 전부 여기(Actions)서. 루틴은 글 생성 + 카드/cards-latest.json push만 한다.
webhook은 repo 시크릿 SLACK_WEBHOOK_URL (평문 노출 없음).

cards-latest.json 스키마:
  {"cards": [{"id": "5", "body": "본문 텍스트..."}, ...]}
"""
import json, os
import notify_slack


def main():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cards-latest.json")
    if not os.path.exists(path):
        print("cards-latest.json 없음 — 스킵"); return
    cards = (json.load(open(path, encoding="utf-8")) or {}).get("cards", [])
    if not cards:
        print("카드 0건 — 발송 생략"); return
    webhook = notify_slack.load_webhook()
    for c in cards:
        res = notify_slack.send_review(c["id"], c["body"], webhook)
        print(f"발송 id={c['id']}: {res}")
    print(f"슬랙 발송 완료: {len(cards)}건")


if __name__ == "__main__":
    main()
