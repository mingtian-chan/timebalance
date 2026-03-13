from rest_framework import serializers
from .models import TimerRecord, WeeklyReset


class TimerRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = TimerRecord
        fields = ['activity', 'started_at', 'ended_at', 'duration_seconds']

    def validate_duration_seconds(self, value):
        if value < 1:
            raise serializers.ValidationError('최소 1초 이상이어야 합니다.')
        return value

    def validate(self, attrs):
        if attrs['ended_at'] <= attrs['started_at']:
            raise serializers.ValidationError('종료 시각은 시작 시각 이후여야 합니다.')
        return attrs


class TimerRecordSerializer(serializers.ModelSerializer):
    activity_display = serializers.CharField(source='get_activity_display', read_only=True)

    class Meta:
        model  = TimerRecord
        fields = [
            'id', 'activity', 'activity_display',
            'started_at', 'ended_at', 'duration_seconds',
            'week_id', 'created_at',
        ]
        read_only_fields = ['id', 'week_id', 'created_at']


class WeeklyResetSerializer(serializers.ModelSerializer):
    class Meta:
        model  = WeeklyReset
        fields = [
            'id', 'week_id',
            'study_seconds', 'ent_seconds',
            'score', 'study_stage', 'ratio_score',
            'streak_achieved', 'streak_count_after',
            'reset_at',
        ]
        read_only_fields = fields
