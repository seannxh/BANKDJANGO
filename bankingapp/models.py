from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class BankAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20, unique=True)
    account_type = models.CharField(max_length=10, choices=[("CHECKING", "Checking"), ("SAVINGS", "Savings")])
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.account_number} - {self.user.username}"


class Transaction(models.Model):
    sender = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, related_name="sent_transactions", null=True, blank=True)
    receiver = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, related_name="received_transactions", null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=[("DEPOSIT", "Deposit"), ("WITHDRAWAL", "Withdrawal"), ("TRANSFER", "Transfer")])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - ${self.amount}"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer_profile")
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.full_name
