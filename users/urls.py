from django.urls import path
from .views import PaymentListAPIView, UserListAPIView, UserRetrieveUpdateDestroyAPIView, UserRegistrationAPIView

urlpatterns = [
    path('payments/', PaymentListAPIView.as_view(), name='payment-list'),
    path('users/', UserListAPIView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserRetrieveUpdateDestroyAPIView.as_view(), name='user-detail'),
    path('users/register/', UserRegistrationAPIView.as_view(), name='user-register'),
]
