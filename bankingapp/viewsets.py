from rest_framework import viewsets
from .models import Customer, BankAccount, Transaction
from .serializers import CustomerSerializer, BankAccountSerializer, TransactionSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_queryset(self):
        account_id = self.kwargs.get('account_id')
        account_number = self.kwargs.get('account_number')

        if account_id:
            return Transaction.objects.filter(account__id=account_id)
        elif account_number:
            return Transaction.objects.filter(account__account_number=account_number)
        return super().get_queryset()
