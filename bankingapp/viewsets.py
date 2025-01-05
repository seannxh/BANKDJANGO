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
        account_number = self.kwargs.get('accountNumber')  # Fetch accountNumber from URL
        if account_number:
            # Fetch transactions where the account is either the sender or the receiver
            return Transaction.objects.filter(
                sender__account_number=account_number
            ) | Transaction.objects.filter(
                receiver__account_number=account_number
            )
        return super().get_queryset()
