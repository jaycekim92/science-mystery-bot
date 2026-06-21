#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""검증된 새 소재(JSON)를 topics_pool.csv에 안전하게 추가한다.

보충 루틴(에이전트)이 Tier1 출처로 검증한 소재를 JSON으로 만들어 이 스크립트로 추가.
- id 자동 부여(기존 max+1)
- phenomenon 중복은 자동 스킵
- 필수 필드 누락도 스킵

  python3 add_topics.py --file candidates.json
  echo '[{...}]' | python3 add_topics.py

JSON 각 항목 필드(id 제외 10개):
  category, phenomenon, hook, explanation, status, source, source_url, question_type, closing_question, image_keyword
"""
import csv, json, sys, os, argparse

BASE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(BASE, "topics_pool.csv")
COLS = ["id", "category", "phenomenon", "hook", "explanation", "status",
        "source", "source_url", "question_type", "closing_question", "image_keyword"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="후보 JSON 파일 경로 (없으면 stdin)")
    args = ap.parse_args()

    raw = open(args.file, encoding="utf-8").read() if args.file else sys.stdin.read()
    cands = json.loads(raw)
    if isinstance(cands, dict):
        cands = [cands]

    rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
    existing = {r["phenomenon"].strip() for r in rows}
    max_id = max((int(r["id"]) for r in rows), default=0)

    added, skipped = [], []
    for c in cands:
        phen = (c.get("phenomenon") or "").strip()
        if not phen:
            skipped.append("(빈 phenomenon)"); continue
        if phen in existing:
            skipped.append(f"{phen} (중복)"); continue
        missing = [k for k in COLS[1:] if not c.get(k)]
        if missing:
            skipped.append(f"{phen} (필드누락: {missing})"); continue
        max_id += 1
        row = {k: c.get(k, "") for k in COLS}
        row["id"] = str(max_id)
        rows.append(row)
        existing.add(phen)
        added.append(f"{row['id']}. {phen}")

    with open(CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in COLS})

    print(f"✅ 추가 {len(added)}개")
    for a in added:
        print(f"   + {a}")
    if skipped:
        print(f"⏭️  스킵 {len(skipped)}개: {skipped}")


if __name__ == "__main__":
    main()
