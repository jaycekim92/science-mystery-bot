# 그거 왜 그래? — 일상 미스터리 과학 봇

누구나 겪지만 설명 못 하는 일상 현상(데자뷰·하품·소름…)을 짧게 풀고 **댓글을 유도**하는 커뮤니티(아고라) 발행봇.

## 동작 구조

```
[루틴: 매일 정해진 시간]  ← 트리거 + 본문 작성 (클라우드, 앱 꺼져도 동작)
      │  git pull
      ▼
  pick_topic.py     미사용 소재 1개 선택 (+ 이력 기록)
  (루틴이 본문 작성)  POST_GUIDE.md 톤·포맷 따라
  generate_card.py  카드 PNG 생성
  notify_slack.py   슬랙 검토 채널로 [카드 + 본문] 전송
      ▼
  [사람이 슬랙에서 승인/수정] → 아고라 발행 (다음 단계)
```

루틴은 **트리거 + 글 작성**만, 나머지 기계적 작업은 전부 이 리포의 스크립트가 한다.

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
1. **GitHub public 푸시** — 이 리포를 원격(public)에 올린다. 카드 이미지를 raw URL로 슬랙에 띄우려면 public 필요.
2. **슬랙 webhook** — 검토 채널의 incoming webhook URL → `SLACK_WEBHOOK_URL`.
3. **발행 루틴 등록** — `ROUTINE_PROMPT.md` 내용으로 Claude 루틴 등록(매일) + 환경변수 설정.
4. **소재 보충 루틴 등록** — `ADD_TOPICS_PROMPT.md` 내용으로 주 1회 루틴 등록 (소재 풀 자동 확장).

## 소재 보충 (2단 체계)
- **풀 게이지**: 발행 메시지에 "남은 소재 N/전체" 표시, 7개 이하면 ⚠️ 보충 경고.
- **보충 루틴**: 주 1회 새 소재 발굴 → Tier1 검증 → `add_topics.py`로 추가 → 슬랙 보고.
  추가된 소재도 발행 시 다시 검토되므로 "검증 후 자동 추가 + 사후 보고"로 운영.

> 카드 이미지는 슬랙 incoming webhook의 파일첨부 불가 제약 때문에, 리포에 push 된 카드의 GitHub raw URL을 image 블록으로 첨부한다.

## 다음 단계
- 아고라 자동 발행(승인 후 게시) 연동 — 게시 방법 확정 후.
- 도형 소재(이명·꿈 등)도 분위기 사진으로 전환 (`generate_card.py` 의 `MODE_OVERRIDE`).
