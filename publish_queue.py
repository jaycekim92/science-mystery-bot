#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""큐(queue.json)에서 가장 오래된 N건을 꺼내 슬랙 검토채널로 발송하고 큐에서 제거한다.

발송(기계적 작업)은 GitHub Actions cron 전용. 생성·카드렌더·적재는 로컬이 한다.
이미지는 repo가 public이라 raw.githubusercontent.com 직링크로 실린다(별도 미러 불필요).
webhook은 repo 시크릿 SLACK_WEBHOOK_URL.

사용: python publish_queue.py [N]   (기본 1)
"""
import json, os, sys
import notify_slack

BASE = os.path.dirname(os.path.abspath(__file__))
Q = os.path.join(BASE, "queue.json")


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    q = json.load(open(Q, encoding="utf-8")) if os.path.exists(Q) else []
    if not q:
        print("큐 비어있음 — 발송 생략"); return
    webhook = notify_slack.load_webhook()
    if not webhook:
        raise SystemExit("SLACK_WEBHOOK_URL 필요")
    batch = q[:n]
    for c in batch:
        res = notify_slack.send_review(c["id"], c["body"], webhook)
        print(f"발송 id={c['id']}: {res}")
    rest = q[n:]
    json.dump(rest, open(Q, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"발송 {len(batch)}건, 큐 잔여 {len(rest)}건")


if __name__ == "__main__":
    main()
