from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import transaction as db_transaction
from django.db import transaction
from decimal import Decimal
from .models import BankAccount, Transaction

# Signup
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

# Signin
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

# Get
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

# Send
class SendMoneyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sender_account_number = request.data.get("sender_account")
        receiver_account_number = request.data.get("receiver_account")
        amount = request.data.get("amount")

        try:
            sender_account = BankAccount.objects.get(account_number=sender_account_number, user=request.user)
            receiver_account = BankAccount.objects.get(account_number=receiver_account_number)

            if sender_account.balance < Decimal(amount):
                return Response({"error": "Insufficient balance"}, status=400)

            with db_transaction.atomic():
                sender_account.balance -= Decimal(amount)
                sender_account.save()

                receiver_account.balance += Decimal(amount)
                receiver_account.save()

                # Create transaction record with type "TRANSFER"
                Transaction.objects.create(
                    sender=sender_account,
                    receiver=receiver_account,
                    amount=Decimal(amount),
                    transaction_type="TRANSFER"
                )

            return Response({"message": "Transfer successful"})
        except BankAccount.DoesNotExist:
            return Response({"error": "Invalid account number"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


# Deposit
class DepositMoneyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        account_number = request.data.get("account_number")
        amount = request.data.get("amount")

        try:
            account = BankAccount.objects.get(account_number=account_number, user=request.user)
            with db_transaction.atomic():
                account.balance += Decimal(amount)
                account.save()

                # Create transaction record with type "DEPOSIT"
                Transaction.objects.create(
                    sender=None,
                    receiver=account,
                    amount=Decimal(amount),
                    transaction_type="DEPOSIT"
                )

            return Response({"message": "Deposit successful", "new_balance": account.balance})
        except BankAccount.DoesNotExist:
            return Response({"error": "Account not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
        
from rest_framework import status

#Withdraw
class WithdrawMoneyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        account_number = request.data.get("account_number")
        amount = request.data.get("amount")

        try:
            account = BankAccount.objects.get(account_number=account_number, user=request.user)
            if account.balance < Decimal(amount):
                return Response({"error": "Insufficient funds"}, status=400)

            with transaction.atomic():
                account.balance -= Decimal(amount)
                account.save()

                Transaction.objects.create(
                    sender=account,
                    receiver=None,
                    amount=Decimal(amount),
                    transaction_type="WITHDRAWAL"
                )

            return Response({"message": "Withdrawal successful", "new_balance": account.balance})
        except BankAccount.DoesNotExist:
            return Response({"error": "Account not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


    
#Account View
class CreateBankAccountView(APIView):
    permission_classes = [IsAuthenticated]
    MAX_ACCOUNTS_PER_USER = 3

    def post(self, request):
        account_type = request.data.get("account_type")
        initial_balance = request.data.get("initial_balance", 0)

        if account_type not in ["CHECKING", "SAVINGS"]:
            return Response(
                {"error": "Invalid account type. Must be 'CHECKING' or 'SAVINGS'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            initial_balance = float(initial_balance)
            if initial_balance < 0:
                raise ValueError
        except ValueError:
            return Response(
                {"error": "Initial balance must be a non-negative number."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_account_count = BankAccount.objects.filter(user=request.user).count()
        if user_account_count >= self.MAX_ACCOUNTS_PER_USER:
            return Response(
                {"error": f"Sorry, We limit 3 Accounts per User."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        account = BankAccount.objects.create(
            user=request.user,
            account_number=f"ACC-{request.user.id}-{user_account_count + 1}",
            account_type=account_type,
            balance=initial_balance,
        )

        return Response(
            {
                "message": "Bank account created successfully.",
                "account_details": {
                    "account_type": account.account_type,
                    "account_number": account.account_number,
                    "balance": account.balance,
                },
            },
            status=status.HTTP_201_CREATED,
        )


#Delete
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


