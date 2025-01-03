from django.db import models
from django.contrib.auth.models import User

class BankAccount(models.Model):
    ACCOUNT_TYPES = [
        ('SAVINGS', 'Savings'),
        ('CHECKING', 'Checking'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bank_accounts")
    account_number = models.CharField(max_length=20, unique=True)
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPES, default='SAVINGS')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.account_number} - {self.user.username}"


class Transaction(models.Model):
    sender = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name="sent_transactions")
    receiver = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name="received_transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction from {self.sender.account_number} to {self.receiver.account_number}"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer_profile")
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.full_name
