# 소재 보충 — 로컬 실행 가이드 (주 1회)

발행 루틴은 원격(cloud)이지만, **보충은 로컬에서 주 1회 직접 실행**한다.
새 소재가 풀에 **영구 추가**되므로, 자동으로 흘려보내지 말고 네 눈을 한 번 거치는 게 안전하다.
(발행 메시지에 "⚠️ 소재 보충 필요"가 뜨면 그때 돌려도 된다.)

실행 방법: 매주 1회, 로컬에서 claude에게 아래를 시키거나 직접 진행한다.

1. `cd ~/science-mystery-bot && git pull` (최초 1회만 `pip3 install -r requirements.txt`)
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
6. `python3 add_topics.py --file candidates.json` (CSV에 추가, id 자동·중복 자동 스킵).
7. **추가된 소재를 직접 눈으로 검토한다** (로컬이니 바로 확인 가능). 이상 없으면:
   `git add topics_pool.csv && git commit -m "topics: +N" && git push`
   → push 해야 원격 발행 루틴이 새 소재를 받는다.

로컬 실행이라 사후 보고가 따로 필요 없다(네가 바로 보니까). 발행 단계의 검토와 합쳐 **이중 안전망**.
