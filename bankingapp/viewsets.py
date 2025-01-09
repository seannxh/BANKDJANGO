from rest_framework import viewsets
from .models import Customer, BankAccount, Transaction
from .serializers import CustomerSerializer, BankAccountSerializer, TransactionSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        account_number = self.kwargs.get('accountNumber')
        if account_number:
            return Transaction.objects.filter(
                Q(sender__account_number=account_number) |
                Q(receiver__account_number=account_number) |
                Q(receiver=None, sender__account_number=account_number) |
                Q(sender=None, receiver__account_number=account_number)
            ).select_related('sender', 'receiver').order_by('-timestamp')
        return Transaction.objects.none()