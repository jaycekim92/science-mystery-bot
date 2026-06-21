# 발행 루틴 (claude.ai 클라우드 루틴 · 매일)

**claude.ai의 스케줄 루틴**에 등록한다(이슈공분봇과 동일 패턴).
클라우드 실행이라 **앱/노트북이 꺼져 있어도 매일 자동으로 돈다.**
루틴은 **글 생성 + push만** 한다. 슬랙 발송은 GitHub Actions(`post.yml`)가
`cards-latest.json` push를 감지해 자동으로 처리한다(webhook은 repo 시크릿).

(소재 보충은 별개 — 로컬에서 주 1회. `ADD_TOPICS_PROMPT.md` 참고)

---

매일 오전 9시:

1. `science-mystery-bot` 리포를 clone/pull 한다 (github.com/jaycekim92/science-mystery-bot).
   `pip install -r requirements.txt`
2. `python3 pick_topic.py` → 오늘의 소재 JSON 한 줄을 받는다.
3. `POST_GUIDE.md` 의 3단 구조·톤 규칙대로 **본문을 작성**한다.
   (단정 금지·"가장 유력한 설명은~"·통념반전·"모른다" 표현 금지)
4. `python3 generate_card.py <id>` → 카드 이미지를 생성한다.
5. `cards-latest.json` 을 작성한다:
   `{"cards": [{"id": "<id>", "body": "<작성한 본문>"}]}`
6. `git add cards/card_<id>.png cards-latest.json state/history.json`
   `&& git commit -m "post <id>" && git push`

push가 끝나면 **GitHub Actions가 자동으로 슬랙 검토 카드를 발송**한다(루틴은 발송하지 않는다).

---

## 전제
- claude.ai 루틴 환경에 이 리포 **git push 권한**(이슈공분봇과 동일 설정).
- repo 시크릿 `SLACK_WEBHOOK_URL` 등록(발송용, Actions가 사용).
