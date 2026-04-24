from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # Auth
    path('register', views.RegisterView.as_view(), name='register'),
    path('login', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),

    # Wallet
    path('wallet', views.WalletView.as_view(), name='wallet'),
    path('deposit', views.DepositView.as_view(), name='deposit'),
    path('transfer', views.TransferView.as_view(), name='transfer'),

    # History
    path('transactions', views.TransactionHistoryView.as_view(), name='transactions'),
]
