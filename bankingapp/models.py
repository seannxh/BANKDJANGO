from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.core.exceptions import ValidationError

class BankAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20, unique=True)
    account_type = models.CharField(max_length=10, choices=[("CHECKING", "Checking"), ("SAVINGS", "Savings")])
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.account_number} - {self.user.username}"
    
class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        DEPOSIT = "DEPOSIT", "Deposit"
        WITHDRAWAL = "WITHDRAWAL", "Withdrawal"
        TRANSFER = "TRANSFER", "Transfer"

    sender = models.ForeignKey(
        'BankAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_transactions",
        help_text="The account sending money. Null for deposits."
    )
    receiver = models.ForeignKey(
        'BankAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_transactions",
        help_text="The account receiving money. Null for withdrawals."
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=TransactionType.choices,
        help_text="Type of transaction: Deposit, Withdrawal, or Transfer."
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="The amount of money involved in the transaction."
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional description or notes about the transaction."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['sender']),
            models.Index(fields=['receiver']),
        ]
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def clean(self):
        """
        Ensure the transaction amount is positive.
        """
        if self.amount <= 0:
            raise ValidationError("Transaction amount must be greater than zero.")

    def __str__(self):
        return (
            f"{self.get_transaction_type_display()} | "
            f"Amount: {self.amount} | "
            f"Sender: {self.sender} | "
            f"Receiver: {self.receiver} | "
            f"Date: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer_profile")
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.full_name
