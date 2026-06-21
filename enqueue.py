#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""로컬 발행 루틴이 만든 카드 1건을 발송 대기 큐(queue.json)에 적재한다.

생성·카드렌더(Pillow+Openverse 사진)는 로컬(컴퓨터 켤 때)이 하고 여기에 쌓아둔다.
실제 슬랙 발송은 GitHub Actions cron(publish.yml)이 큐에서 꺼내 처리한다.

사용: echo '{"id":"5","body":"본문..."}' | python3 enqueue.py
"""
import json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
Q = os.path.join(BASE, "queue.json")


def main():
    card = json.load(sys.stdin)
    if "id" not in card or "body" not in card:
        raise SystemExit("id/body 필요 — {\"id\":..., \"body\":...}")
    q = json.load(open(Q, encoding="utf-8")) if os.path.exists(Q) else []
    q.append({"id": str(card["id"]), "body": card["body"]})
    json.dump(q, open(Q, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"적재 완료 id={card['id']}, 큐 {len(q)}건")


if __name__ == "__main__":
    main()
