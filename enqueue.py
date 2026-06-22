#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""로컬 발행 루틴이 만든 카드 1건을 발송 대기 큐(queue.json)에 적재한다.

적재할 때마다 큐를 검사한다(위생점검): 같은 소재 id 중복 제거.
일상 과학이라 시의성이 낮아 시간 만료는 두지 않는다.
실제 슬랙 발송은 GitHub Actions cron(publish.yml)이 큐에서 꺼내 처리한다.

사용: echo '{"id":"5","body":"본문..."}' | python3 enqueue.py
"""
import json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
Q = os.path.join(BASE, "queue.json")


def load():
    return json.load(open(Q, encoding="utf-8")) if os.path.exists(Q) else []


def sanitize(q):
    out, seen = [], set()
    for c in q:
        cid = str(c.get("id"))
        if cid in seen:
            continue
        seen.add(cid); out.append(c)
    return out, len(q) - len(out)


def main():
    card = json.load(sys.stdin)
    if "id" not in card or "body" not in card:
        raise SystemExit("id/body 필요 — {\"id\":..., \"body\":...}")
    cid = str(card["id"])
    q, dropped = sanitize(load())
    if any(str(c.get("id")) == cid for c in q):
        print(f"이미 큐에 있음 id={cid} (대기 {len(q)}건, 중복정리 {dropped})")
    else:
        q.append({"id": cid, "body": card["body"]})
        print(f"적재 완료 id={cid}, 큐 {len(q)}건 (중복정리 {dropped})")
    json.dump(q, open(Q, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
