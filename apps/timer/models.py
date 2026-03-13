from django.db import models
from django.conf import settings
from django.utils import timezone


class ActivityType(models.TextChoices):
    STUDY = 'study', '취업 준비'
    ENT   = 'ent',   '엔터테인먼트'


class TimerRecord(models.Model):
    """
    타이머 기록 한 건
    - 시작/종료 시각, 활동 유형, 지속 시간(초)을 저장
    - 주간 잔고는 이 테이블을 집계해서 실시간 계산
    """
    user      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='timer_records',
        verbose_name='유저',
    )
    activity  = models.CharField('활동 유형', max_length=10, choices=ActivityType.choices)
    started_at  = models.DateTimeField('시작 시각')
    ended_at    = models.DateTimeField('종료 시각')
    duration_seconds = models.PositiveIntegerField('지속 시간(초)')
    # 어떤 주에 속하는지 (월요일 기준 YYYY-MM-DD)
    week_id   = models.CharField('주 식별자', max_length=10, db_index=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)

    class Meta:
        db_table  = 'tb_timer_record'
        ordering  = ['-started_at']
        verbose_name = '타이머 기록'
        verbose_name_plural = '타이머 기록 목록'
        indexes = [
            models.Index(fields=['user', 'week_id']),
            models.Index(fields=['user', 'started_at']),
        ]

    def __str__(self):
        return f'{self.user} | {self.get_activity_display()} | {self.duration_seconds}초'

    @property
    def duration_hours(self):
        return round(self.duration_seconds / 3600, 2)


class WeeklyReset(models.Model):
    """
    주간 리셋 이력
    - 리셋 시 지난 주 통계 스냅샷, 점수, 스트릭 결과를 저장
    """
    user           = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='weekly_resets',
        verbose_name='유저',
    )
    week_id        = models.CharField('주 식별자(월요일)', max_length=10)
    study_seconds  = models.PositiveIntegerField('취준 시간(초)', default=0)
    ent_seconds    = models.PositiveIntegerField('엔터 시간(초)', default=0)
    score          = models.PositiveSmallIntegerField('주간 점수(0~50)', default=0)
    study_stage    = models.PositiveSmallIntegerField('취준 단계(1~5)', default=1)
    ratio_score    = models.PositiveSmallIntegerField('비율 점수(1~10)', default=0)
    streak_achieved = models.BooleanField('스트릭 달성 여부', default=False)
    streak_count_after = models.PositiveIntegerField('리셋 후 스트릭', default=0)
    reset_at       = models.DateTimeField('리셋 시각', auto_now_add=True)

    class Meta:
        db_table  = 'tb_weekly_reset'
        ordering  = ['-week_id']
        unique_together = ['user', 'week_id']
        verbose_name = '주간 리셋'
        verbose_name_plural = '주간 리셋 목록'

    def __str__(self):
        return f'{self.user} | {self.week_id} | {self.score}점'
