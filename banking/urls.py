from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from bankingapp.viewsets import CustomerViewSet, BankAccountViewSet, TransactionViewSet
from bankingapp.views import SignUpView, SignInView, UserBankAccountsView, SendMoneyView, SignOutView, DepositMoneyView, CreateBankAccountView, UpdateBalanceView, DeleteBankAccountView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.http import HttpResponse

# Define a root response for the home page
def home(request):
    return HttpResponse("Welcome to the Banking App API. Use /api/signup/ to sign up, /api/signin/ to sign in, or /api/token/ for JWT authentication.")

# Set up the router for viewsets
router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'accounts', BankAccountViewSet, basename='account')
router.register(r'transactions', TransactionViewSet, basename='transaction')

# Define all URL patterns
urlpatterns = [
    path("", home, name="home"),  # Root URL with welcome message
    path("admin/", admin.site.urls),  # Admin panel
    path("api/", include(router.urls)),  # API endpoints for viewsets
    path("api/signup/", SignUpView.as_view(), name="signup"),  # Sign-up endpoint
    path("api/signin/", SignInView.as_view(), name="signin"),  # Sign-in endpoint
    path("api/user-accounts/", UserBankAccountsView.as_view(), name="user-accounts"),  # User accounts
    path("api/send-money/", SendMoneyView.as_view(), name="send-money"),  # Send money
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),  # JWT access and refresh token
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/deposit-money/", DepositMoneyView.as_view(), name="deposit-money"),
    path("api/create-bank-account/", CreateBankAccountView.as_view(), name="create-bank-account"),
    path('api/user-accounts/update-balance/<str:account_id>/', UpdateBalanceView.as_view(), name='update-balance'),
    path('api/user-accounts/delete-bank-account/<str:account_id>/', DeleteBankAccountView.as_view(), name='delete-bank-account'),
    path('api/user-accounts/<str:account_id>/transactions/', TransactionViewSet.as_view({'get': 'list'}), name='account-transactions'),
    path("api/signout/", SignOutView.as_view(), name="signout"),
]
