from rest_framework import serializers
from .models import Customer, BankAccount, Transaction

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    sender_account = serializers.CharField(source='sender.account_number', read_only=True)
    receiver_account = serializers.CharField(source='receiver.account_number', read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'transaction_type', 'amount', 'sender_account', 'receiver_account', 'created_at']