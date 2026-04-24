from django.contrib.auth.models import User
from django.db import transaction as db_transaction
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Wallet, Transaction
from .serializers import (
    RegisterSerializer,
    WalletSerializer,
    DepositSerializer,
    TransferSerializer,
    TransactionSerializer,
)



# ─── Auth ────────────────────────────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    """POST /api/register — create account + auto-wallet"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                'message': 'Account created successfully.',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                },
            },
            status=status.HTTP_201_CREATED,
        )


# ─── Wallet ──────────────────────────────────────────────────────────────────

class WalletView(APIView):
    """GET /api/wallet — view current user's wallet"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            wallet = request.user.wallet
        except Wallet.DoesNotExist:
            return Response(
                {'error': 'Wallet not found. Please contact support.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)


# ─── Deposit ─────────────────────────────────────────────────────────────────

class DepositView(APIView):
    """POST /api/deposit — add money to own wallet"""
    permission_classes = [IsAuthenticated]

    @db_transaction.atomic
    def post(self, request):
        serializer = DepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']

        wallet = request.user.wallet
        wallet.balance += amount
        wallet.save()

        txn = Transaction.objects.create(
            receiver=request.user,
            amount=amount,
            transaction_type=Transaction.TransactionType.DEPOSIT,
            status=Transaction.Status.SUCCESS,
            note='Wallet deposit',
        )

        return Response(
            {
                'message': f'${amount} deposited successfully.',
                'new_balance': wallet.balance,
                'transaction_id': txn.id,
            },
            status=status.HTTP_200_OK,
        )


# ─── Transfer ────────────────────────────────────────────────────────────────

class TransferView(APIView):
    """POST /api/transfer — send money to another user"""
    permission_classes = [IsAuthenticated]

    @db_transaction.atomic
    def post(self, request):
        serializer = TransferSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data['amount']
        note = serializer.validated_data.get('note', '')
        receiver_username = serializer.validated_data['receiver_username']

        sender_wallet = request.user.wallet

        # Check sufficient balance
        if sender_wallet.balance < amount:
            return Response(
                {
                    'error': 'Insufficient balance.',
                    'current_balance': sender_wallet.balance,
                    'required': amount,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        receiver = User.objects.get(username=receiver_username)

        # Check receiver has a wallet (edge case)
        try:
            receiver_wallet = receiver.wallet
        except Wallet.DoesNotExist:
            return Response(
                {'error': f"Receiver '{receiver_username}' does not have a wallet."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Atomic debit / credit
        sender_wallet.balance -= amount
        receiver_wallet.balance += amount
        sender_wallet.save()
        receiver_wallet.save()

        txn = Transaction.objects.create(
            sender=request.user,
            receiver=receiver,
            amount=amount,
            transaction_type=Transaction.TransactionType.TRANSFER,
            status=Transaction.Status.SUCCESS,
            note=note,
        )

        return Response(
            {
                'message': f'${amount} transferred to {receiver_username} successfully.',
                'new_balance': sender_wallet.balance,
                'transaction_id': txn.id,
            },
            status=status.HTTP_200_OK,
        )


# ─── Transaction History ──────────────────────────────────────────────────────

class TransactionHistoryView(APIView):
    """GET /api/transactions — full history for current user"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        transactions = Transaction.objects.filter(
            sender=user
        ) | Transaction.objects.filter(
            receiver=user
        )
        transactions = transactions.order_by('-timestamp')

        serializer = TransactionSerializer(transactions, many=True)
        return Response(
            {
                'count': transactions.count(),
                'transactions': serializer.data,
            }
        )
