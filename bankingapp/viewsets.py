from rest_framework import viewsets
from .models import Customer, BankAccount, Transaction
from .serializers import CustomerSerializer, BankAccountSerializer, TransactionSerializer
from rest_framework.permissions import IsAuthenticated

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        account_number = self.kwargs.get('accountNumber')
        if account_number:
            queryset = Transaction.objects.filter(
                sender__account_number=account_number
            ) | Transaction.objects.filter(
                receiver__account_number=account_number
            )
            print(f"Queryset for account {account_number}: {queryset}")  # Debugging
            return queryset
        return super().get_queryset()
