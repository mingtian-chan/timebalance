from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'nickname']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password_confirm': '비밀번호가 일치하지 않습니다.'})
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError('아이디 또는 비밀번호가 올바르지 않습니다.')
        if not user.is_active:
            raise serializers.ValidationError('비활성화된 계정입니다.')
        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'nickname',
            'streak_criteria', 'streak_count',
            'goal_daily_seconds', 'goal_weekly_seconds',
            'last_reset_week',
            'notif_goal', 'notif_remind', 'notif_balance_warn',
        ]
        read_only_fields = ['id', 'username', 'streak_count', 'last_reset_week']


class GoalSettingsSerializer(serializers.ModelSerializer):
    """목표 및 스트릭 기준만 업데이트"""
    class Meta:
        model = User
        fields = [
            'goal_daily_seconds', 'goal_weekly_seconds',
            'streak_criteria',
            'notif_goal', 'notif_remind', 'notif_balance_warn',
        ]
