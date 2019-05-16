from rest_framework import serializers
from decimal import Decimal
from datetime import datetime, timezone

from .models import Loan, Payment, Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"

    def to_representation(self, obj):
        return {"client_id": str(obj.id)}


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = "__all__"

    def to_representation(self, obj):
        return {"id": str(obj.id), "installment": round(float(obj.instalment), 2)}

    def validate_client(self, client):
        if client.is_indebted:
            raise serializers.ValidationError("Denied loan request")
        return client


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

    def to_representation(self, obj):
        return {}

    def validate(self, data):
        
        load = data['loan_id']
        if data['date'] < load.date_initial:
            raise serializers.ValidationError("Date of a payment before the creation date of its loan.")
        
        if data['amount'] > load.get_balance():
            raise serializers.ValidationError("Payment amount higher than its loan balance.")
        
        return data

class BalanceSerializer(serializers.Serializer):
    date = serializers.DateTimeField(
        "Date base to balance",
        required=False,
        allow_null=True,
        default=datetime.now().astimezone(tz=timezone.utc),
    )
    loan_id = serializers.CharField(max_length=None)

    def to_representation(self, obj):
        if not obj["date"]:
            obj["date"] = datetime.now().astimezone(tz=timezone.utc)
        return {"balance": Loan.objects.get(pk=obj["loan_id"]).get_balance(obj["date"])}
