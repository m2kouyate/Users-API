from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator

only_letters_validator = RegexValidator(r'^[a-zA-Z]*$', 'Only letters are allowed.')


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.
    Включает в себя валидацию для уникального email, имени пользователя и подтверждения пароля.
    """
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())],
        max_length=32,
        min_length=4
    )
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password2 = serializers.CharField(write_only=True, required=True, min_length=8)
    first_name = serializers.CharField(validators=[only_letters_validator])
    last_name = serializers.CharField(validators=[only_letters_validator])

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'password2']

    def validate(self, attrs):
        """Проверка на совпадение паролей"""
        if 'password' in attrs and 'password2' in attrs and attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        """Переопределение стандартного создания для обработки подтверждения пароля."""
        if 'password2' in validated_data:
            del validated_data['password2']
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        """Переопределение стандартного обновления, чтобы обработать подтверждение пароля."""

        if 'password2' in validated_data:
            del validated_data['password2']
        return super().update(instance, validated_data)


