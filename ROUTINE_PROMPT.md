# 루틴 등록용 프롬프트

아래 내용을 그대로 Claude 루틴(scheduled cloud agent)에 등록한다.
루틴은 **트리거 + 글 작성**만 하고, 나머지 기계적 작업은 깃 스크립트가 처리한다.

---

매일 오전 9시, 커뮤니티 봇 "그거 왜 그래?"의 검토용 초안 1건을 만든다. 순서:

1. `cd ~/science-mystery-bot && git pull` 로 최신 상태로 맞춘다.
   (클라우드 새 환경이면 이어서 `pip3 install -r requirements.txt` 로 의존성 설치)
2. `python3 pick_topic.py` 를 실행해 오늘의 소재 JSON 한 줄을 받는다.
   (id, phenomenon, hook, explanation, status, source, question_type, closing_question 포함)
3. `POST_GUIDE.md` 의 3단 구조·톤 규칙을 **반드시 지켜** 피드 본문을 작성한다.
   - 단정 금지(가설은 "가장 유력한 설명은~"), "과학자도 아직 몰라요"식 표현 금지, 통념반전 적극 활용.
4. `python3 generate_card.py <id>` 로 카드 이미지를 생성한다.
5. `python3 notify_slack.py <id> --body "<작성한 본문>"` 로 슬랙 검토 채널에 전송한다.
6. 발행 이력이 바뀌었으면 `git add state/history.json && git commit -m "log: <id>" && git push` 로 기록을 보존한다.

게시(아고라 발행)는 사람이 슬랙에서 승인한 뒤 하므로, 루틴은 5번까지만 한다.

---

## 필요 환경변수 (루틴 실행 환경에 설정)
- `SLACK_BOT_TOKEN` — 슬랙 봇 토큰 (files:write, chat:write 권한)
- `SLACK_CHANNEL` — 검토 채널 ID 또는 이름
