from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class BankAccount(models.Model):
    """
    Represents a bank account owned by a user.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="The user who owns this bank account."
    )
    account_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique account number for the bank account."
    )
    account_type = models.CharField(
        max_length=10,
        choices=[("CHECKING", "Checking"), ("SAVINGS", "Savings")],
        help_text="Type of the bank account (Checking or Savings)."
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Current balance of the bank account."
    )

    class Meta:
        verbose_name = "Bank Account"
        verbose_name_plural = "Bank Accounts"

    def __str__(self):
        return f"{self.account_number} - {self.user.username}"


class Transaction(models.Model):
    """
    Represents a financial transaction between bank accounts.
    """

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
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp of when the transaction was created."
    )

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["sender"]),
            models.Index(fields=["receiver"]),
        ]
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def clean(self):
        """
        Validate the transaction data.
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
    """
    Represents a customer profile linked to a Django user.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="customer_profile",
        help_text="The Django user associated with this customer profile."
    )
    full_name = models.CharField(
        max_length=255,
        help_text="The full name of the customer."
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="The customer's phone number."
    )
    address = models.TextField(
        blank=True,
        null=True,
        help_text="The customer's address."
    )

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return self.full_name
