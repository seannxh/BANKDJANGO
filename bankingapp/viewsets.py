from .models import Customer, BankAccount, Transaction
from .serializers import CustomerSerializer, BankAccountSerializer, TransactionSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action  
from django.db.models import Q
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db import transaction as db_transaction
from .serializers import TransactionSerializer
from django.db.models import Q


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer


class TransactionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, accountNumber=None):
        """
        List transactions for a specific account number.
        """
        if not accountNumber:
            return Response({"error": "Account number is required."}, status=400)

        # Verify that the account belongs to the authenticated user
        try:
            user_accounts = BankAccount.objects.filter(customer__user=request.user).values_list('account_number', flat=True)
            if accountNumber not in user_accounts:
                return Response({"error": "Unauthorized access to this account."}, status=403)
        except BankAccount.DoesNotExist:
            return Response({"error": "Invalid account number."}, status=404)

        # Fetch transactions involving the account
        transactions = Transaction.objects.filter(
            Q(sender__account_number=accountNumber) | Q(receiver__account_number=accountNumber)
        ).select_related('sender', 'receiver').order_by('-created_at')

        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)