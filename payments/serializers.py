from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Wallet, Transaction


# ─── Auth ────────────────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label='Confirm Password')

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        # Auto-create wallet for new user
        Wallet.objects.create(user=user)
        return user


# ─── Wallet ──────────────────────────────────────────────────────────────────

class WalletSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'username', 'email', 'balance', 'created_at', 'updated_at']


class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Deposit amount must be greater than zero.')
        if value > 100_000:
            raise serializers.ValidationError('Single deposit limit is $100,000.')
        return value


# ─── Transfer ────────────────────────────────────────────────────────────────

class TransferSerializer(serializers.Serializer):
    receiver_username = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    note = serializers.CharField(max_length=255, required=False, default='')

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Transfer amount must be greater than zero.')
        return value

    def validate_receiver_username(self, value):
        try:
            User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User '{value}' does not exist.")
        return value

    def validate(self, attrs):
        request = self.context.get('request')
        if request and attrs['receiver_username'] == request.user.username:
            raise serializers.ValidationError({'receiver_username': 'You cannot transfer money to yourself.'})
        return attrs


# ─── Transaction ─────────────────────────────────────────────────────────────

class TransactionSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True, default=None)
    receiver_username = serializers.CharField(source='receiver.username', read_only=True, default=None)

    class Meta:
        model = Transaction
        fields = [
            'id', 'sender_username', 'receiver_username',
            'amount', 'transaction_type', 'status', 'note', 'timestamp'
        ]
