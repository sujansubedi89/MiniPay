from django.contrib import admin
from .models import Wallet, Transaction


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'transaction_type', 'sender', 'receiver', 'amount', 'status', 'timestamp']
    list_filter = ['transaction_type', 'status']
    search_fields = ['sender__username', 'receiver__username']
    readonly_fields = ['timestamp']
