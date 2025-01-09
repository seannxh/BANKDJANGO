from .models import Customer, BankAccount, Transaction
from .serializers import CustomerSerializer, BankAccountSerializer, TransactionSerializer
from rest_framework.permissions import IsAuthenticated
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


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_accounts = BankAccount.objects.filter(customer__user=self.request.user)
        account_numbers = user_accounts.values_list('account_number', flat=True)
        return Transaction.objects.filter(
            Q(sender__account_number__in=account_numbers) | Q(receiver__account_number__in=account_numbers)
        ).select_related('sender', 'receiver').order_by('-created_at')

    def create(self, request, *args, **kwargs):
        sender_account_number = request.data.get('sender_account')
        receiver_account_number = request.data.get('receiver_account')
        amount = request.data.get('amount')

        if not amount or float(amount) <= 0:
            return Response({"error": "Amount must be greater than zero."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sender_account = BankAccount.objects.get(account_number=sender_account_number, customer__user=request.user)
            receiver_account = BankAccount.objects.get(account_number=receiver_account_number)

            if sender_account.balance < float(amount):
                return Response({"error": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)

            with db_transaction.atomic():
                sender_account.balance -= float(amount)
                sender_account.save()

                receiver_account.balance += float(amount)
                receiver_account.save()

                transaction = Transaction.objects.create(
                    sender=sender_account,
                    receiver=receiver_account,
                    amount=amount,
                    transaction_type="TRANSFER"
                )

            serializer = self.get_serializer(transaction)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except BankAccount.DoesNotExist:
            return Response({"error": "Invalid account number"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)