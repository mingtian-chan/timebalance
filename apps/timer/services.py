"""
타임밸런스 핵심 비즈니스 로직
- 주 식별자 계산
- 주간 잔고 계산
- 점수 / 멘트 계산
- 주간 리셋 처리
"""
from datetime import date, timedelta
from django.utils import timezone
from django.db.models import Sum, Q

from .models import TimerRecord, WeeklyReset, ActivityType


# ── 주 식별자 유틸 ────────────────────────────────────────

def get_week_id(dt=None) -> str:
    """
    주어진 datetime 기준으로 주 식별자(월요일 날짜 문자열) 반환.
    월요일 05:00 이후 ~ 다음 월요일 05:00 전까지를 같은 주로 취급.
    즉, 월요일 00:00~04:59 는 전주에 속함.
    """
    if dt is None:
        dt = timezone.localtime(timezone.now())

    # 월요일(weekday=0) 05시 이전이면 전주(= 전 월요일 기준) 취급
    if dt.weekday() == 0 and dt.hour < 5:
        dt = dt - timedelta(days=7)

    # 해당 주 월요일 계산
    days_to_monday = dt.weekday()  # 월=0, 화=1, ... 일=6
    monday = dt.date() - timedelta(days=days_to_monday)
    return monday.isoformat()


def current_week_id() -> str:
    return get_week_id()


def should_reset(user) -> bool:
    """마지막 리셋 주와 현재 주가 다르면 리셋 필요"""
    if not user.last_reset_week:
        return False
    return user.last_reset_week.isoformat() != current_week_id()


# ── 잔고 계산 ─────────────────────────────────────────────

def calc_weekly_balance(user) -> int:
    """이번 주 잔고(초) = 취준 합계 - 엔터 합계"""
    wid = current_week_id()
    agg = (
        TimerRecord.objects
        .filter(user=user, week_id=wid)
        .aggregate(
            study=Sum('duration_seconds', filter=Q(activity=ActivityType.STUDY)),
            ent=Sum('duration_seconds',   filter=Q(activity=ActivityType.ENT)),
        )
    )
    study = agg['study'] or 0
    ent   = agg['ent']   or 0
    return study - ent


# ── 점수 / 멘트 ───────────────────────────────────────────

def calc_score(study_sec: int, ent_sec: int) -> dict:
    """
    취준 단계(1~5) × 공부 비중 점수(1~10) = 최대 50점
    """
    study_h = study_sec / 3600

    if study_h < 5:    stage = 1
    elif study_h < 10: stage = 2
    elif study_h < 15: stage = 3
    elif study_h < 20: stage = 4
    else:              stage = 5

    total = study_sec + ent_sec
    if total == 0:
        ratio_score = 0
    else:
        ratio_score = max(1, min(10, round(study_sec / total * 10)))

    return {
        'stage':       stage,
        'ratio_score': ratio_score,
        'total':       stage * ratio_score,
    }


def get_study_comment(study_sec: int) -> str:
    h = study_sec / 3600
    if h < 5:    return '이번 주는 좀 쉬었네요.'
    if h < 10:   return '조금씩 시작하고 있어요.'
    if h < 15:   return '꾸준히 하고 있네요 👍'
    if h < 20:   return '정말 열심히 했어요!'
    return '이번 주 완전히 불태웠네요 🔥'


def get_ratio_comment(study_sec: int, ent_sec: int) -> str:
    total = study_sec + ent_sec
    if total == 0:
        return '기록이 없는 한 주였어요.'
    pct = study_sec / total
    if pct >= 0.8: return '거의 공부만 했군요, 대단한 집중력!'
    if pct >= 0.6: return '공부에 집중한 한 주였어요.'
    if pct >= 0.4: return '공부와 휴식의 균형이 좋았어요 ⚖️'
    if pct >= 0.2: return '휴식도 충분히 취했네요.'
    return '많이 쉬었어요 — 충전 완료! 😄'


def build_comment(study_sec: int, ent_sec: int) -> str:
    study_c = get_study_comment(study_sec)
    ratio_c = get_ratio_comment(study_sec, ent_sec)

    study_h = study_sec / 3600
    total   = study_sec + ent_sec
    pct     = study_sec / total if total else 0

    # 많이 공부 + 많이 쉼
    if study_h >= 15 and pct < 0.5:
        return f'{study_c} 그러면서도 {ratio_c} 열심히 달리고 열심히 쉰 주였어요!'
    # 많이 공부 + 고집중
    if study_h >= 15 and pct >= 0.7:
        return f'{study_c} {ratio_c}'
    return f'{study_c} 또한, {ratio_c}'


# ── 주간 리셋 ─────────────────────────────────────────────

def perform_weekly_reset(user) -> dict:
    """
    주간 리셋 처리:
    1. 지난 주 통계 집계
    2. 스트릭 판정
    3. WeeklyReset 레코드 생성
    4. user.streak_count, user.last_reset_week 업데이트
    5. 결과 dict 반환
    """
    prev_wid = user.last_reset_week.isoformat() if user.last_reset_week else current_week_id()

    # 지난 주 기록 집계
    agg = (
        TimerRecord.objects
        .filter(user=user, week_id=prev_wid)
        .aggregate(
            study=Sum('duration_seconds', filter=Q(activity=ActivityType.STUDY)),
            ent=Sum('duration_seconds',   filter=Q(activity=ActivityType.ENT)),
        )
    )
    study_sec = agg['study'] or 0
    ent_sec   = agg['ent']   or 0

    # 달성률 & 스트릭
    achieve_rate = (study_sec / user.goal_weekly_seconds * 100) if user.goal_weekly_seconds else 0
    achieved = achieve_rate >= user.streak_criteria
    user.streak_count = user.streak_count + 1 if achieved else 0

    # 점수
    score_data = calc_score(study_sec, ent_sec)
    comment    = build_comment(study_sec, ent_sec)

    # 리셋 이력 저장
    WeeklyReset.objects.update_or_create(
        user=user, week_id=prev_wid,
        defaults=dict(
            study_seconds=study_sec,
            ent_seconds=ent_sec,
            score=score_data['total'],
            study_stage=score_data['stage'],
            ratio_score=score_data['ratio_score'],
            streak_achieved=achieved,
            streak_count_after=user.streak_count,
        )
    )

    # 유저 업데이트
    from datetime import date
    new_wid = current_week_id()
    user.last_reset_week = date.fromisoformat(new_wid)
    user.save(update_fields=['streak_count', 'last_reset_week'])

    return {
        'prev_week_id':   prev_wid,
        'study_seconds':  study_sec,
        'ent_seconds':    ent_sec,
        'achieve_rate':   round(achieve_rate, 1),
        'streak_achieved': achieved,
        'streak_count':   user.streak_count,
        'score':          score_data,
        'comment':        comment,
    }
