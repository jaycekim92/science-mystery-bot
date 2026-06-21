#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""생성된 카드 + 루틴이 작성한 본문을 슬랙으로 전송(검토용).
승인/수정/이미지교체는 사람이 슬랙에서 판단한다(건강반장 패턴).

  python3 notify_slack.py <id> --body "<본문 텍스트>"

환경변수: SLACK_BOT_TOKEN, SLACK_CHANNEL
"""
import argparse, os, csv

BASE = os.path.dirname(os.path.abspath(__file__))


def topic(cid):
    for r in csv.DictReader(open(os.path.join(BASE, "topics_pool.csv"), encoding="utf-8")):
        if r["id"] == cid:
            return r
    raise SystemExit(f"id {cid} 를 topics_pool.csv 에서 못 찾음")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("--body", required=True, help="루틴이 작성한 본문 텍스트")
    args = ap.parse_args()

    token = os.environ.get("SLACK_BOT_TOKEN")
    channel = os.environ.get("SLACK_CHANNEL")
    if not token or not channel:
        raise SystemExit("환경변수 SLACK_BOT_TOKEN, SLACK_CHANNEL 가 필요합니다")

    t = topic(args.id)
    card = os.path.join(BASE, "cards", f"card_{args.id}.png")
    if not os.path.exists(card):
        raise SystemExit(f"카드가 없습니다: {card}\n먼저: python3 generate_card.py {args.id}")

    comment = (
        f"*[검토] 그거 왜 그래? — {t['phenomenon']}*\n"
        f"상태: `{t['status']}` · 질문타입: `{t['question_type']}` · 출처: {t['source']}\n\n"
        f"{args.body}\n\n"
        f"───\n:white_check_mark: 승인  :pencil2: 수정요청  :frame_with_picture: 이미지교체  (댓글로 알려주세요)"
    )

    from slack_sdk import WebClient
    client = WebClient(token=token)
    client.files_upload_v2(
        channel=channel,
        file=card,
        filename=f"card_{args.id}.png",
        title=t["phenomenon"],
        initial_comment=comment,
    )
    print(f"슬랙 전송 완료 → #{channel} : {t['phenomenon']}")


if __name__ == "__main__":
    main()
