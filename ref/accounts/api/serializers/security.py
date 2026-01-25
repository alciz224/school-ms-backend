# domain/accounts/api/serializers/security.py

"""
Serializers pour les questions de sécurité.
"""

from rest_framework import serializers


class SecurityQuestionsConfigSerializer(serializers.Serializer):
    """Serializer pour la configuration des questions."""

    predefined_questions = serializers.ListField(child=serializers.CharField())
    min_required = serializers.IntegerField()
    max_allowed = serializers.IntegerField()
    allow_custom = serializers.BooleanField()


class SecurityQuestionItemSerializer(serializers.Serializer):
    """Serializer pour une question (affichage)."""

    order = serializers.IntegerField()
    question = serializers.CharField()


class UserSecurityQuestionsSerializer(serializers.Serializer):
    """Serializer pour les questions d'un utilisateur."""

    configured_count = serializers.IntegerField()
    questions = SecurityQuestionItemSerializer(many=True)


class SecurityQuestionSetupSerializer(serializers.Serializer):
    """Serializer pour une question lors de la configuration."""

    question = serializers.CharField(min_length=10, max_length=255)
    answer = serializers.CharField(min_length=2, max_length=100)


class SecurityQuestionsSetupSerializer(serializers.Serializer):
    """Serializer pour configurer les questions de sécurité."""

    questions = SecurityQuestionSetupSerializer(many=True)

    def validate_questions(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Au moins 2 questions sont requises.")
        if len(value) > 3:
            raise serializers.ValidationError("Maximum 3 questions autorisées.")
        return value


class SecurityQuestionVerifyAnswerSerializer(serializers.Serializer):
    """Serializer pour une réponse de vérification."""

    order = serializers.IntegerField(min_value=1, max_value=3)
    answer = serializers.CharField(min_length=1)


class SecurityQuestionsVerifySerializer(serializers.Serializer):
    """Serializer pour vérifier les réponses aux questions."""

    identifier = serializers.CharField()
    answers = SecurityQuestionVerifyAnswerSerializer(many=True)

    def validate_identifier(self, value):
        return value.strip()

    def validate_answers(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Au moins 2 réponses sont requises.")
        return value
