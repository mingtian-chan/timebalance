from datetime import date, timedelta
from django.db.models import Sum, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.timer.models import TimerRecord, WeeklyReset, ActivityType
from apps.timer.services import current_week_id, get_week_id, calc_weekly_balance


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def daily_summary(request):
    """
    최근 N일 일별 취준/엔터 합계
    ?days=7 (기본 7)
    """
    user = request.user
    days = int(request.query_params.get('days', 7))

    result = []
    today = date.today()
    for i in range(days - 1, -1, -1):
        d = (today - timedelta(days=i)).isoformat()
        agg = (
            TimerRecord.objects
            .filter(user=user, started_at__date=d)
            .aggregate(
                study=Sum('duration_seconds', filter=Q(activity=ActivityType.STUDY)),
                ent=Sum('duration_seconds',   filter=Q(activity=ActivityType.ENT)),
            )
        )
        result.append({
            'date':          d,
            'study_seconds': agg['study'] or 0,
            'ent_seconds':   agg['ent']   or 0,
        })

    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def weekly_summary(request):
    """
    이번 주 + 대시보드용 통계
    """
    user = request.user
    wid  = current_week_id()
    agg  = (
        TimerRecord.objects
        .filter(user=user, week_id=wid)
        .aggregate(
            study=Sum('duration_seconds', filter=Q(activity=ActivityType.STUDY)),
            ent=Sum('duration_seconds',   filter=Q(activity=ActivityType.ENT)),
        )
    )
    study = agg['study'] or 0
    ent   = agg['ent']   or 0

    return Response({
        'week_id':          wid,
        'study_seconds':    study,
        'ent_seconds':      ent,
        'balance':          calc_weekly_balance(user),
        'goal_weekly':      user.goal_weekly_seconds,
        'achieve_rate':     round(study / user.goal_weekly_seconds * 100, 1) if user.goal_weekly_seconds else 0,
        'streak_count':     user.streak_count,
        'streak_criteria':  user.streak_criteria,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def today_summary(request):
    """오늘 취준 / 엔터 + 일별 목표 달성률"""
    user  = request.user
    today = date.today().isoformat()
    agg   = (
        TimerRecord.objects
        .filter(user=user, started_at__date=today)
        .aggregate(
            study=Sum('duration_seconds', filter=Q(activity=ActivityType.STUDY)),
            ent=Sum('duration_seconds',   filter=Q(activity=ActivityType.ENT)),
        )
    )
    study = agg['study'] or 0
    ent   = agg['ent']   or 0

    return Response({
        'date':           today,
        'study_seconds':  study,
        'ent_seconds':    ent,
        'goal_daily':     user.goal_daily_seconds,
        'achieve_rate':   round(study / user.goal_daily_seconds * 100, 1) if user.goal_daily_seconds else 0,
    })
