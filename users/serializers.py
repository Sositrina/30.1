from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор платежей."""

    class Meta:
        model = Payment
        fields = '__all__'