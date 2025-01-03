from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import transaction as db_transaction
from decimal import Decimal
from .models import BankAccount, Transaction

# Sign-up View
class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not email or not password:
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        account_number = f"{user.id:06d}{BankAccount.objects.count() + 1:04d}"

        BankAccount.objects.create(
            user=user,
            account_number=account_number,
            account_type="SAVINGS",
            balance=0.00,
        )

        return Response({"message": "User and bank account created successfully"}, status=status.HTTP_201_CREATED)

class SignOutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Signout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



# Sign-in View
class SignInView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        else:
            return Response({"error": "Invalid credentials"}, status=401)

# Get User's Bank Accounts
class UserBankAccountsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        accounts = BankAccount.objects.filter(user=request.user)
        account_data = [
            {
                "account_number": acc.account_number,
                "balance": acc.balance,
                "account_type": acc.account_type,
            }
            for acc in accounts
        ]
        return Response(account_data, status=status.HTTP_200_OK)

# Send Money Between Accounts
class SendMoneyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sender_account_number = request.data.get("sender_account")
        receiver_account_number = request.data.get("receiver_account")
        amount = request.data.get("amount")

        if not sender_account_number or not receiver_account_number or not amount:
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sender_account = BankAccount.objects.get(account_number=sender_account_number, user=request.user)
            receiver_account = BankAccount.objects.get(account_number=receiver_account_number)
        except BankAccount.DoesNotExist:
            return Response({"error": "Invalid account number"}, status=status.HTTP_404_NOT_FOUND)

        if sender_account_number == receiver_account_number:
            return Response({"error": "Cannot send money to the same account"}, status=status.HTTP_400_BAD_REQUEST)

        if sender_account.user == receiver_account.user:
            if sender_account.account_type == receiver_account.account_type:
                return Response({"error": "Cannot transfer money between accounts of the same type for the same user"}, status=status.HTTP_400_BAD_REQUEST)

        if sender_account.balance < amount:
            return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)

        with db_transaction.atomic():
            sender_account.balance -= amount
            sender_account.save()

            receiver_account.balance += amount
            receiver_account.save()

            Transaction.objects.create(sender=sender_account, receiver=receiver_account, amount=amount)

        return Response({"message": "Transaction successful"}, status=status.HTTP_200_OK)

# Deposit Money View
class DepositMoneyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        account_number = request.data.get("account_number")
        amount = request.data.get("amount")

        if not account_number or not amount:
            return Response({"error": "Account number and amount are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = BankAccount.objects.get(account_number=account_number, user=request.user)
        except BankAccount.DoesNotExist:
            return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

        account.balance += amount
        account.save()

        return Response({
            "message": "Deposit successful",
            "account_number": account.account_number,
            "new_balance": account.balance
        }, status=status.HTTP_200_OK)

# Create Bank Account View
class CreateBankAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        account_type = request.data.get("account_type")
        initial_balance = request.data.get("initial_balance", 0)

        if account_type not in ["CHECKING", "SAVINGS"]:
            return Response({"error": "Invalid account type. Must be 'CHECKING' or 'SAVINGS'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            initial_balance = float(initial_balance)
            if initial_balance < 0:
                raise ValueError
        except ValueError:
            return Response({"error": "Initial balance must be a non-negative number."}, status=status.HTTP_400_BAD_REQUEST)

        account = BankAccount.objects.create(
            user=request.user,
            account_number=f"ACC-{request.user.id}-{len(BankAccount.objects.filter(user=request.user)) + 1}",
            account_type=account_type,
            balance=initial_balance
        )

        return Response({
            "message": "Bank account created successfully.",
            "account_details": {
                "account_number": account.account_number,
                "account_type": account.account_type,
                "balance": account.balance,
            },
        }, status=status.HTTP_201_CREATED)

class UpdateBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, account_id):
        try:
            account = BankAccount.objects.get(account_number=account_id, user=request.user)
        except BankAccount.DoesNotExist:
            return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

        new_balance = request.data.get("balance")
        if new_balance is None or new_balance < 0:
            return Response({"error": "Invalid balance amount"}, status=status.HTTP_400_BAD_REQUEST)

        account.balance = new_balance
        account.save()

        return Response({
            "message": "Balance updated successfully",
            "account": {
                "account_number": account.account_number,
                "balance": account.balance,
                "account_type": account.account_type,
            }
        }, status=status.HTTP_200_OK)

from .models import BankAccount

class DeleteBankAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, account_id):
        try:
            account = BankAccount.objects.get(account_number=account_id, user=request.user)
        except BankAccount.DoesNotExist:
            return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

        account.delete()
        return Response({"message": "Bank account deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
# Protected Data View
class ProtectedDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "This is protected data!"})
