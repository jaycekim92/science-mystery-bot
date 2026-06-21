# 소재 보충 루틴 프롬프트

발행 루틴과 **별개**의 루틴. 주 1회(또는 슬랙에 "소재 보충 필요" 경고가 뜰 때) 실행해
소재 풀이 마르지 않게 새 소재를 발굴·검증·추가한다.

등록 주기 권장: **주 1회** (예: 매주 월요일 오전 10시).

---

커뮤니티 봇 "그거 왜 그래?"의 소재 풀을 보충한다. 순서:

1. `cd ~/science-mystery-bot && git pull` (클라우드 새 환경이면 `pip3 install -r requirements.txt`)
2. `topics_pool.csv` 를 읽어 **기존 phenomenon 목록**과 **category·question_type 분포**를 파악한다.
3. **부족한 category / question_type을 우선** 채우는 방향으로, 기존과 겹치지 않는
   "일상 미스터리 과학" 소재 **5~8개**를 발굴한다.
   - 기준: 누구나 겪지만 설명 못 하는 현상. (우주·먼 트리비아 ✗ / 일상 경험 ✓)
4. 각 소재를 **Tier1 출처로 검증**한다.
   - 허용: peer-reviewed 학술지(Nature·Science·Cell 등) / 공인기관(NIH·NASA·기상청 등). 블로그·위키 ✗
   - 학계 상태 분류: 정설 / 유력가설 / 논쟁중 / 미스터리. 단정 회피.
   - ⚠️ "과학자도 아직 잘 몰라요"식 표현 금지. 가설은 "가장 유력한 설명은~"으로.
5. 검증된 소재를 10필드 JSON 배열로 `candidates.json` 에 저장한다:
   `[{category, phenomenon, hook, explanation, status, source, source_url, question_type, closing_question, image_keyword}]`
   - image_keyword: 무료스톡 영어 2~3개. **사람이 주인공인 주제는 portrait/face/person** 계열로.
6. `python3 add_topics.py --file candidates.json` 실행 (CSV에 추가, id 자동·중복 자동 스킵).
7. `git add topics_pool.csv && git commit -m "topics: +N" && git push`
8. `add_topics.py` 가 출력한 "추가된 소재 목록"을 `SLACK_WEBHOOK_URL` 로 전송해 사람이 사후 확인하게 한다.

추가된 소재도 **실제 발행 시 슬랙 검토를 한 번 더 거치므로**(이중 안전망),
이 단계는 "검증 후 자동 추가 + 사후 보고"로 운영한다.

---

## 필요 환경변수
- `SLACK_WEBHOOK_URL` — 보충 결과 보고용 (발행 루틴과 동일)
