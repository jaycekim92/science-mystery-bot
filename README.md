# 그거 왜 그래? — 일상 미스터리 과학 봇

누구나 겪지만 설명 못 하는 일상 현상(데자뷰·하품·소름…)을 짧게 풀고 **댓글을 유도**하는 커뮤니티(아고라) 발행봇.

## 동작 구조

```
[claude.ai 클라우드 루틴 · 매일]  ← 글 생성 + push (앱 꺼져도)
  pick_topic.py      소재 1개 선택 (+ 이력)
  (루틴이 본문 작성)   POST_GUIDE.md 톤대로
  generate_card.py   카드 PNG
  cards-latest.json 작성 → git push
      ▼
[GitHub Actions · post.yml]  ← cards-latest.json push 감지 (앱 무관)
  ci_post.py → 슬랙 검토 발송 (webhook = repo 시크릿)
      ▼
  [사람이 슬랙에서 승인/수정] → 아고라 발행 (다음 단계)
```

글 생성·push는 **claude.ai 클라우드 루틴**, 슬랙 발송은 **GitHub Actions**. 둘 다 앱 꺼져도 돈다.
(이슈공분봇 `~/issue-aggro-bot` 과 동일 패턴)

## 파일
| 파일 | 역할 |
|---|---|
| `topics_pool.csv` | 소재 27개 (Tier1 출처 검증) — 봇의 연료 |
| `pick_topic.py` | 미사용 소재 선택 + `state/history.json` 기록 |
| `generate_card.py` | 카드 이미지 생성 (이미지/도형 자동, 무료이미지=Openverse) |
| `notify_slack.py` | 카드+본문 슬랙 검토 전송 |
| `POST_GUIDE.md` | 본문 톤·포맷 가이드 (루틴이 따름) |
| `ROUTINE_PROMPT.md` | 루틴 등록용 프롬프트 |
| `add_topics.py` | 검증된 새 소재를 CSV에 추가 (id 자동·중복 스킵) |
| `ADD_TOPICS_PROMPT.md` | 소재 보충 루틴 프롬프트 (주 1회) |
| `preview_post.py` | 피드 게시물 미리보기 목업 |

## 로컬 테스트
```bash
pip3 install -r requirements.txt
python3 pick_topic.py --peek          # 소재 미리보기
python3 generate_card.py 5            # 카드 생성
SLACK_BOT_TOKEN=xxx SLACK_CHANNEL=C123 \
  python3 notify_slack.py 5 --body "본문..."   # 슬랙 전송
```

## ⚙️ 설정 (1회, 사용자 작업)
1. **GitHub public 푸시** — 완료 (카드 raw URL + Actions용). ✅
2. **repo 시크릿** — `gh secret set SLACK_WEBHOOK_URL` 로 검토 채널 webhook 등록. Actions 발송용. ✅
3. **발행 루틴 (claude.ai·매일)** — `ROUTINE_PROMPT.md` 내용으로 claude.ai 클라우드 루틴 등록 + 리포 git push 권한 (이슈공분봇과 동일).
4. **소재 보충 (로컬·주 1회)** — `ADD_TOPICS_PROMPT.md` 따라 로컬에서 직접 실행.

## 소재 보충 (2단 체계)
- **풀 게이지**: 발행 메시지에 "남은 소재 N/전체" 표시, 7개 이하면 ⚠️ 보충 경고.
- **보충 루틴**: 주 1회 새 소재 발굴 → Tier1 검증 → `add_topics.py`로 추가 → 슬랙 보고.
  추가된 소재도 발행 시 다시 검토되므로 "검증 후 자동 추가 + 사후 보고"로 운영.

> 카드 이미지는 슬랙 incoming webhook의 파일첨부 불가 제약 때문에, 리포에 push 된 카드의 GitHub raw URL을 image 블록으로 첨부한다.

## 다음 단계
- 아고라 자동 발행(승인 후 게시) 연동 — 게시 방법 확정 후.
- 도형 소재(이명·꿈 등)도 분위기 사진으로 전환 (`generate_card.py` 의 `MODE_OVERRIDE`).
