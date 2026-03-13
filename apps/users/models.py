from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    커스텀 유저 모델
    - 닉네임, 스트릭 기준, 주간 목표 등 타임밸런스 전용 필드 추가
    """
    nickname = models.CharField('닉네임', max_length=30, blank=True)
    streak_criteria = models.PositiveSmallIntegerField(
        '스트릭 달성 기준(%)', default=80,
        help_text='주간 목표 대비 이 비율 이상 달성하면 스트릭 +1'
    )
    streak_count = models.PositiveIntegerField('현재 스트릭(주)', default=0)
    goal_daily_seconds = models.PositiveIntegerField(
        '일별 목표(초)', default=4 * 3600,  # 4시간
    )
    goal_weekly_seconds = models.PositiveIntegerField(
        '주별 목표(초)', default=25 * 3600,  # 25시간
    )
    # 마지막으로 주간 리셋된 주의 월요일 날짜 (주 식별자)
    last_reset_week = models.DateField('마지막 리셋 주', null=True, blank=True)

    # 알림 설정
    notif_goal = models.BooleanField('목표 달성 알림', default=True)
    notif_remind = models.BooleanField('미달성 독려 알림', default=True)
    notif_balance_warn = models.BooleanField('잔고 부족 경고', default=True)

    class Meta:
        db_table = 'tb_user'
        verbose_name = '유저'
        verbose_name_plural = '유저 목록'

    def __str__(self):
        return self.username

    @property
    def display_name(self):
        return self.nickname or self.username
