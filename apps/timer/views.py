from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import TimerRecord
from .serializers import (
    TimerRecordCreateSerializer,
    TimerRecordSerializer,
    WeeklyResetSerializer,
)
from .services import (
    get_week_id, current_week_id, should_reset,
    calc_weekly_balance, perform_weekly_reset,
)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_record(request):
    """
    타이머 기록 저장
    - 저장 전 주간 리셋 여부 확인 → 리셋 필요 시 자동 처리
    - 응답에 현재 주간 잔고 포함
    """
    user = request.user

    # 주간 리셋 체크
    reset_data = None
    if should_reset(user):
        reset_data = perform_weekly_reset(user)

    serializer = TimerRecordCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    started_at = serializer.validated_data['started_at']
    record = serializer.save(
        user=user,
        week_id=get_week_id(started_at),
    )

    balance = calc_weekly_balance(user)

    return Response({
        'record':  TimerRecordSerializer(record).data,
        'balance': balance,
        'reset':   reset_data,
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_records(request):
    """
    기록 목록 조회
    - ?week=YYYY-MM-DD  특정 주 필터
    - ?limit=N          최근 N건 (기본 50)
    """
    user = request.user
    qs   = user.timer_records.all()

    week = request.query_params.get('week')
    if week:
        qs = qs.filter(week_id=week)

    limit = int(request.query_params.get('limit', 50))
    qs = qs[:limit]

    return Response(TimerRecordSerializer(qs, many=True).data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_record(request, record_id):
    """기록 삭제"""
    try:
        record = TimerRecord.objects.get(id=record_id, user=request.user)
    except TimerRecord.DoesNotExist:
        return Response({'detail': '기록을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

    record.delete()
    balance = calc_weekly_balance(request.user)
    return Response({'balance': balance})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def weekly_status(request):
    """
    현재 주간 상태 조회
    - 리셋 필요 시 자동 처리 후 reset 데이터 포함
    """
    user = request.user
    reset_data = None
    if should_reset(user):
        reset_data = perform_weekly_reset(user)

    balance = calc_weekly_balance(user)

    return Response({
        'week_id': current_week_id(),
        'balance': balance,
        'reset':   reset_data,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reset_history(request):
    """주간 리셋 이력 조회"""
    resets = request.user.weekly_resets.all()[:12]  # 최근 12주
    return Response(WeeklyResetSerializer(resets, many=True).data)
