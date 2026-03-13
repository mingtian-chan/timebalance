# ⚖️ 타임밸런스 — Django 백엔드

취업 준비 시간을 적립하고 엔터테인먼트 시간을 차감하는 주간 시간 관리 서비스.

---

## 📁 프로젝트 구조

```
timebalance/
├── config/                  # 프로젝트 설정
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── users/               # 유저 인증 & 프로필
│   │   ├── models.py        # 커스텀 User 모델
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── admin.py
│   ├── timer/               # 타이머 기록 & 주간 리셋
│   │   ├── models.py        # TimerRecord, WeeklyReset
│   │   ├── services.py      # 핵심 비즈니스 로직
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── admin.py
│   └── stats/               # 통계 조회
│       ├── views.py
│       └── urls.py
├── templates/
├── static/
├── manage.py
├── requirements.txt
└── .env.example
```

---

## 🗄️ DB 테이블 구조

| 테이블 | 설명 |
|---|---|
| `tb_user` | 커스텀 유저 (목표, 스트릭 기준, 알림 설정 포함) |
| `tb_timer_record` | 타이머 기록 1건 (활동 유형, 시작/종료, 지속 시간, 주 식별자) |
| `tb_weekly_reset` | 주간 리셋 이력 (점수, 스트릭 결과 스냅샷) |

---

## 🚀 초기 세팅 방법

### 1. 가상환경 생성 & 패키지 설치
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. MySQL DB 생성
```sql
CREATE DATABASE timebalance CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. 환경변수 설정
```bash
cp .env.example .env
# .env 파일 편집 — DB 비밀번호 등 입력
```

### 4. 마이그레이션 & 슈퍼유저
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 5. 서버 실행
```bash
python manage.py runserver
```

---

## 📡 API 엔드포인트

### 인증 (`/api/auth/`)
| 메서드 | URL | 설명 |
|---|---|---|
| POST | `/api/auth/register/` | 회원가입 |
| POST | `/api/auth/login/` | 로그인 |
| POST | `/api/auth/logout/` | 로그아웃 |
| GET/PATCH | `/api/auth/profile/` | 프로필 조회/수정 |
| PATCH | `/api/auth/goals/` | 목표·스트릭 기준 설정 |

### 타이머 (`/api/timer/`)
| 메서드 | URL | 설명 |
|---|---|---|
| POST | `/api/timer/records/` | 기록 저장 (자동 리셋 체크) |
| GET | `/api/timer/records/list/` | 기록 목록 조회 |
| DELETE | `/api/timer/records/<id>/delete/` | 기록 삭제 |
| GET | `/api/timer/weekly-status/` | 현재 주간 상태 + 잔고 |
| GET | `/api/timer/reset-history/` | 주간 리셋 이력 |

### 통계 (`/api/stats/`)
| 메서드 | URL | 설명 |
|---|---|---|
| GET | `/api/stats/today/` | 오늘 요약 |
| GET | `/api/stats/weekly/` | 이번 주 요약 + 달성률 |
| GET | `/api/stats/daily/?days=7` | 최근 N일 일별 통계 |

---

## ✅ 이후 작업 지시사항 (우선순위 순)

### Phase 1 — 기본 동작 확인
```
[ ] 1-1. MySQL 연결 확인 후 makemigrations / migrate 실행
[ ] 1-2. admin 접속해서 tb_user, tb_timer_record, tb_weekly_reset 테이블 확인
[ ] 1-3. /api/auth/register/ 로 회원가입 테스트 (Postman 또는 curl)
[ ] 1-4. /api/timer/records/ 로 기록 저장 테스트
[ ] 1-5. /api/timer/weekly-status/ 로 잔고 계산 확인
```

### Phase 2 — 온보딩 API 연동
```
[ ] 2-1. 회원가입 시 goal_daily_seconds, goal_weekly_seconds, streak_criteria
         를 함께 받아 저장하도록 RegisterSerializer 수정
[ ] 2-2. last_reset_week를 회원가입 시점의 current_week_id() 로 자동 설정
[ ] 2-3. 프론트 온보딩 모달 → /api/auth/register/ 연동
```

### Phase 3 — 주간 리셋 고도화
```
[ ] 3-1. perform_weekly_reset() 에 대한 단위 테스트 작성
         (tests/timer/test_services.py)
[ ] 3-2. 리셋 API를 별도 엔드포인트로 분리: POST /api/timer/reset/
[ ] 3-3. 주간 리셋 모달 데이터를 프론트에서 받아 표시하는 로직 연동
```

### Phase 4 — 30일 자동 삭제 (Management Command)
```
[ ] 4-1. apps/timer/management/commands/purge_old_records.py 생성
         python manage.py purge_old_records 로 실행
[ ] 4-2. cron 또는 celery beat 로 매일 새벽 자동 실행 등록
         # crontab 예시:
         # 0 3 * * * /path/to/venv/bin/python manage.py purge_old_records
```

### Phase 5 — 프론트 연동 (현재 HTML → API 교체)
```
[ ] 5-1. 현재 localStorage 기반 저장 → API 호출로 전면 교체
[ ] 5-2. 세션 쿠키 기반 인증 적용 (CSRF 토큰 포함)
[ ] 5-3. 페이지 로드 시 /api/timer/weekly-status/ 호출로 초기 상태 로드
[ ] 5-4. 타이머 정지 시 /api/timer/records/ POST 호출
[ ] 5-5. 기록 삭제 시 /api/timer/records/<id>/delete/ 호출
[ ] 5-6. 대시보드 /api/stats/daily/?days=7 + /api/stats/weekly/ 연동
```

### Phase 6 — 보안 & 배포
```
[ ] 6-1. DEBUG=False 전환 후 동작 확인
[ ] 6-2. SECRET_KEY 교체 (python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
[ ] 6-3. ALLOWED_HOSTS 서버 도메인으로 설정
[ ] 6-4. gunicorn + nginx 설정
         pip install gunicorn
         gunicorn config.wsgi:application --bind 0.0.0.0:8000
[ ] 6-5. SSL 인증서 적용 (Let's Encrypt)
[ ] 6-6. 환경변수를 시스템 환경 또는 secrets manager로 이전
```

### Phase 7 (선택) — 기능 확장
```
[ ] 7-1. 소셜 로그인 (Google OAuth2) — django-allauth
[ ] 7-2. 이메일 인증 회원가입
[ ] 7-3. 푸시 알림 (FCM) — 목표 달성 / 잔고 부족
[ ] 7-4. 주간 리포트 이메일 자동 발송
[ ] 7-5. 친구 기능 — 서로의 주간 점수 비교
```

---

## 💡 주간 리셋 로직 핵심 규칙

- **주 식별자**: 해당 주의 월요일 날짜 (예: `2026-03-09`)
- **월요일 05:00 기준**: 월요일 05시 이전(00:00~04:59)은 전주, 05시 이후는 새 주
- **잔고 계산**: DB 기반 실시간 집계 (localStorage 방식과 달리 항상 정합성 보장)
- **리셋 트리거**: API 요청 시 `should_reset()` 자동 체크 → `perform_weekly_reset()` 호출
- **리셋 후 잔고**: 자동으로 0이 됨 (이번 주 기록이 없으므로 집계 결과 = 0)
