from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from requests.exceptions import RequestException

from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from .models import Payment, User
from .serializers import PaymentSerializer, UserSerializer, UserRegistrationSerializer

from .services import (create_stripe_product, create_stripe_price, create_stripe_session)
from course.models import Course


class PaymentListAPIView(ListAPIView):
    """Список платежей с фильтрацией и сортировкой."""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['paid_course', 'paid_lesson', 'payment_method']
    ordering_fields = ['payment_date']


class UserListAPIView(ListAPIView):
    """Список пользователей."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """Получение, изменение и удаление пользователя."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Возвращает только текущего пользователя."""
        return User.objects.filter(pk=self.request.user.pk)


class UserRegistrationAPIView(CreateAPIView):
    """Регистрация нового пользователя."""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class PaymentCreateAPIView(APIView):
    """Создание платежа за курс."""

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['course', 'amount', 'payment_date'],
            properties={
                'course': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID курса'
                ),
                'amount': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Сумма в USD, например 10.00'
                ),
                'payment_date': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Дата платежа в формате ГГГГ-ММ-ДД'
                ),
            }
        ),
        responses={
            201: 'Платёж создан, ссылка на оплату получена',
            400: 'Некорректные данные',
            401: 'Необходима авторизация',
            404: 'Курс не найден',
            500: 'Ошибка Stripe',
        }
    )

    def post(self, request):
        """Создаёт платёж и ссылку на оплату."""
        course = get_object_or_404(
            Course, pk=request.data.get('course')
        )

        serializer = PaymentSerializer(data={
            'user': request.user.pk,
            'paid_course': course.pk,
            'amount': request.data.get('amount'),
            'payment_date': request.data.get('payment_date'),
            'payment_method': 'transfer',
        })
        serializer.is_valid(raise_exception=True)

        try:
            product = create_stripe_product(course.title)
            price = create_stripe_price(
                product['id'],
                serializer.validated_data['amount']
            )
            session = create_stripe_session(
                price['id'],
                'http://localhost:8000/swagger/',
                'http://localhost:8000/redoc/'
            )
        except RequestException as error:
            return Response({'error': str(error)}, status=500)

        payment = serializer.save(
            stripe_product_id=product['id'],
            stripe_price_id=price['id'],
            stripe_session_id=session['id'],
            payment_url=session['url']
        )

        return Response(PaymentSerializer(payment).data, status=201)