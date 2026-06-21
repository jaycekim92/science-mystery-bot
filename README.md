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
1. **GitHub 푸시** — 이 리포를 원격에 올린다 (루틴이 `git pull` 하려면 필요).
2. **슬랙 봇** — `files:write`, `chat:write` 권한 봇 생성 → `SLACK_BOT_TOKEN`, `SLACK_CHANNEL` 확보.
3. **루틴 등록** — `ROUTINE_PROMPT.md` 내용으로 Claude 루틴 등록 + 위 환경변수 설정.

## 다음 단계
- 아고라 자동 발행(승인 후 게시) 연동 — 게시 방법 확정 후.
- 도형 소재(이명·꿈 등)도 분위기 사진으로 전환 (`generate_card.py` 의 `MODE_OVERRIDE`).
