from rest_framework import viewsets
from .models import Customer, BankAccount, Transaction
from .serializers import CustomerSerializer, BankAccountSerializer, TransactionSerializer
from rest_framework import permissions
from django.db.models import Q


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        account_number = self.kwargs.get('accountNumber')
        print(f"Fetching transactions for account: {account_number}")  # Debug
        if account_number:
            return Transaction.objects.filter(
                Q(sender__account_number=account_number) |
                Q(receiver__account_number=account_number)
            ).select_related('sender', 'receiver').order_by('-created_at')
        return Transaction.objects.none()