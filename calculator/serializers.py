from rest_framework import serializers
from decimal import Decimal

from .models import Loan, Payment


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ('__all__')

    def to_representation(self, obj):
        return {
            'id': str(obj.id),
            'installment': round(float(obj.installment), 2)
        }


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'