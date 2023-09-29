from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.filters import OrderingFilter
from django_filters import rest_framework as filters

from .serializers import UserSerializer


class UserFilter(filters.FilterSet):
    """
    Фильтр для модели User.
    Позволяет фильтровать пользователей по имени пользователя, email, имени и фамилии.
    """
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class UserViewSet(viewsets.ModelViewSet):
    """
    Набор представлений для модели User.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filterset_class = UserFilter
    ordering_fields = ['username', 'email', 'first_name', 'last_name']
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Переопределение стандартного создания для обработки сериализатора.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def perform_create(self, serializer):
        """
        Сохранение пользователя после успешной валидации данных.
        """
        serializer.save()


@swagger_auto_schema(methods=['post'], request_body=UserSerializer, responses={201: 'Created', 400: 'Bad Request'})
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Эндпоинт для регистрации новых пользователей.
    Возвращает токен после успешной регистрации.
    """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=201)
    return Response(serializer.errors, status=400)



