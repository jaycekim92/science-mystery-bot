#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""오늘 발행할 소재 1개 선택 + 발행 이력 기록. 선택 결과를 JSON 한 줄로 출력.

루틴이 이 출력(JSON)을 받아 POST_GUIDE.md 톤대로 본문을 작성한다.
  python3 pick_topic.py          # 소재 선택 + 이력 기록
  python3 pick_topic.py --peek   # 미리보기(이력 기록 안 함)
"""
import csv, json, os, random, sys

BASE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(BASE, "topics_pool.csv")
STATE = os.path.join(BASE, "state", "history.json")


def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE, encoding="utf-8"))
    return {"posted": [], "last_run": None}


def save_state(st):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def main():
    peek = "--peek" in sys.argv
    rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
    st = load_state()
    used = set(st["posted"])

    pool = [r for r in rows if r["id"] not in used]
    cycled = False
    if not pool:                      # 27개 다 돌았으면 한 바퀴 리셋
        st["posted"] = []
        pool = rows
        cycled = True

    pick = random.choice(pool)
    if not peek:
        st["posted"].append(pick["id"])
        save_state(st)

    out = dict(pick)
    out["_cycle_reset"] = cycled
    out["_remaining"] = len(pool) - 1
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
