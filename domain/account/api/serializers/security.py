"""
Serializers for security questions.
"""

from rest_framework import serializers

from domain.account.constants import PREDEFINED_SECURITY_QUESTIONS


class SecurityQuestionsConfigSerializer(serializers.Serializer):
    """Serializer for security questions configuration."""

    predefined_questions = serializers.ListField(child=serializers.CharField())
    min_required = serializers.IntegerField()
    max_allowed = serializers.IntegerField()
    allow_custom = serializers.BooleanField()


class SecurityQuestionSetupSerializer(serializers.Serializer):
    """Serializer for setting up a single security question."""

    question = serializers.CharField(min_length=10, max_length=255)
    answer = serializers.CharField(min_length=2, write_only=True)
    order = serializers.IntegerField(min_value=1, max_value=3, required=False)


class SecurityQuestionsSetupSerializer(serializers.Serializer):
    """Serializer for setting up multiple security questions."""

    questions = SecurityQuestionSetupSerializer(many=True)

    def validate_questions(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("At least 1 question is required.")
        if len(value) > 3:
            raise serializers.ValidationError("Maximum 3 questions allowed.")

        # Check for duplicate orders
        orders = [q.get("order", i + 1) for i, q in enumerate(value)]
        if len(orders) != len(set(orders)):
            raise serializers.ValidationError("Each question must have a unique order.")

        return value


class SecurityQuestionVerifyAnswerSerializer(serializers.Serializer):
    """Serializer for verifying a single answer."""

    order = serializers.IntegerField(min_value=1, max_value=3)
    answer = serializers.CharField()


class SecurityQuestionsVerifySerializer(serializers.Serializer):
    """Serializer for verifying security questions answers."""

    identifier = serializers.CharField(help_text="Email or phone number")
    answers = SecurityQuestionVerifyAnswerSerializer(many=True)

    def validate_identifier(self, value):
        return value.strip()

    def validate_answers(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("At least 2 answers are required.")
        return value


class UserSecurityQuestionsSerializer(serializers.Serializer):
    """Serializer for user's security questions (response)."""

    configured_count = serializers.IntegerField()
    questions = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of questions (without answers)",
    )


class PredefinedQuestionsSerializer(serializers.Serializer):
    """Serializer for listing predefined questions."""

    questions = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
    )

    def to_representation(self, instance):
        return {"questions": PREDEFINED_SECURITY_QUESTIONS}
