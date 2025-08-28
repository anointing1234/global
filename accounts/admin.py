from django.contrib import admin
from django.utils.html import format_html
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import logging
from django.shortcuts import get_object_or_404
from django.templatetags.static import static
import base64
from django.core.files import File
from io import BytesIO
from PIL import Image
import os
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.contrib.staticfiles.storage import staticfiles_storage
import json
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django import forms
from django.urls import path
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Account, AccountBalance, Card, LoanRequest, 
    Exchange, ResetPassword, TransferCode, Transaction,Deposit,PaymentGateway,Transfer,LoanRequest,
    ExchangeRate, Beneficiary
)
from django.db import transaction
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from django.template.response import TemplateResponse
import random
import uuid
from django.core.exceptions import ValidationError


def generate_unique_account_number():
    """
    Generate a unique 10-digit account number.
    """
    while True:
        acct_num = "".join(str(random.randint(0, 9)) for _ in range(10))
        if not Account.objects.filter(account_number=acct_num).exists():
            return acct_num



# forms.py or admin.py (depending on where you keep it)
class AccountCreationForm(forms.ModelForm):
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Confirm Password"), widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'account_type', 'status')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Passwords do not match"))
        return password2

    def save(self, commit=True):
        account = super().save(commit=False)
        account.set_password(self.cleaned_data["password1"])
        if not account.account_number:
            account.account_number = generate_unique_account_number()
        if commit:
            account.save()
        return account


class AccountAdmin(BaseUserAdmin, UnfoldModelAdmin):
    ordering = ('email',)
    list_display = (
        'account_id', 'pin', 'email', 'first_name', 'last_name',
        'phone_number', 'account_type', 'status', 'is_staff'
    )
    list_filter = ('is_staff', 'status', 'account_type', 'account_id')
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {
            'fields': (
                'first_name', 'last_name', 'phone_number', 'account_type',
                'account_number', 'country', 'city', 'gender'
            )
        }),
        ('Account Status', {'fields': ('status',)}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name', 'phone_number',
                'account_type', 'status', 'password1', 'password2'
            ),
        }),
    )

    search_fields = ('email', 'first_name', 'last_name')
    filter_horizontal = ('groups', 'user_permissions',)

    # Use the custom form for adding new users
    add_form = AccountCreationForm

    # Custom admin actions for status
    actions = ['make_active', 'make_disabled', 'make_blocked']

    def make_active(self, request, queryset):
        queryset.update(status='active')
        self.message_user(request, "Selected accounts marked as Active")
    make_active.short_description = "Mark selected users as Active"

    def make_disabled(self, request, queryset):
        queryset.update(status='disabled')
        self.message_user(request, "Selected accounts marked as Disabled")
    make_disabled.short_description = "Mark selected users as Disabled"

    def make_blocked(self, request, queryset):
        queryset.update(status='blocked')
        self.message_user(request, "Selected accounts marked as Blocked")
    make_blocked.short_description = "Mark selected users as Blocked"

    def changelist_view(self, request, extra_context=None):
        User = get_user_model()
        total_users = User.objects.count()
        messages.info(request, f'Total number of users: {total_users}')
        return super().changelist_view(request, extra_context=extra_context)


# Register the AccountAdmin
admin.site.register(Account, AccountAdmin)




# @admin.register(AccountBalance)
# class AccountBalanceAdmin(UnfoldModelAdmin):
#     list_display = ('account', 'available_balance', 'loan_balance', 'total_credits', 'total_debits','gbp','eur','checking_balance')
#     search_fields = ('account__email',)




@admin.register(AccountBalance)
class AccountBalanceAdmin(UnfoldModelAdmin):
    list_display = ['account', 'available_balance', 'loan_balance', 'total_credits', 'total_debits','gbp','eur','checking_balance']
    list_editable = ['available_balance', 'loan_balance','gbp','eur','checking_balance']  # ✅ balances editable in list view
    search_fields = ['account__email', 'account__username']
    list_per_page = 25
    autocomplete_fields = ['account']

    def save_model(self, request, obj, form, change):
        balance_changes = {}

        if change:  # Editing existing record
            old_obj = AccountBalance.objects.get(pk=obj.pk)

            if obj.checking_balance != old_obj.checking_balance:
                balance_changes['CHECKING'] = obj.checking_balance - old_obj.checking_balance
            if obj.available_balance != old_obj.available_balance:
                balance_changes['AVAILABLE'] = obj.available_balance - old_obj.available_balance
            if obj.loan_balance != old_obj.loan_balance:
                balance_changes['LOAN'] = obj.loan_balance - old_obj.loan_balance
            if obj.gbp != old_obj.gbp:
                balance_changes['GBP'] = obj.gbp - old_obj.gbp
            if obj.eur != old_obj.eur:
                balance_changes['EUR'] = obj.eur - old_obj.eur    

        else:
            # New record
            if obj.checking_balance > 0:
                balance_changes['CHECKING'] = obj.checking_balance
            if obj.available_balance > 0:
                balance_changes['AVAILABLE'] = obj.available_balance
            if obj.loan_balance > 0:
                balance_changes['LOAN'] = obj.loan_balance
            if obj.gbp > 0:
                balance_changes['GBP'] = obj.gbp
            if obj.eur > 0:
                balance_changes['EUR'] = obj.eur        

        # Save object AFTER tracking changes
        super().save_model(request, obj, form, change)

        # Map internal keys to Deposit.account choices
        account_map = {
            "AVAILABLE": "Savings_Account",
            "CHECKING": "Checking_Account",
            "LOAN": "Checking_Account",  # or Savings, depending on your design
            "GBP": "Savings_Account",
            "EUR": "Savings_Account",
        }

        # Create Deposit & Transaction for positive changes
        for account_type, change_amount in balance_changes.items():
            txn_ref = str(uuid.uuid4()).replace('-', '')[:10].upper()
            if change_amount > 0:
                Deposit.objects.create(
                    user=obj.account,
                    amount=change_amount,
                    network="Admin Deposit",
                    account=account_map.get(account_type, "Savings_Account"),  # ✅ safe mapping
                    TNX=txn_ref,
                    status="completed",
                    date=timezone.now()
                )

                Transaction.objects.create(
                    user=obj.account,
                    amount=change_amount,
                    transaction_type="deposit",
                    description=f"Admin deposit to {account_type} balance",
                    status="completed",
                    institution="Payment Gateway",
                    region="International",
                    from_account="N/A",
                    transaction_date=timezone.now(),
                    to_account=str(obj.account.id),
                    reference=txn_ref  # ✅ use correct field
                )


    def save_related(self, request, form, formsets, change):
        """
        Ensures balance changes done in list_editable also trigger deposits/transactions.
        """
        super().save_related(request, form, formsets, change)
        self.save_model(request, form.instance, form, change)







@admin.register(Card)
class CardAdmin(UnfoldModelAdmin):
    list_display = ('user', 'vendor', 'card_type', 'account', 'status','expiry_date')
    search_fields = ('user__email', 'account')


class LoanRequestAdmin(UnfoldModelAdmin):
    list_display = ('user', 'amount', 'currency', 'loan_type', 'status', 'date', 'approval_date', 'disbursement_date')
    list_filter = ('status', 'loan_type', 'currency')
    search_fields = ('user__email', 'loan_type', 'status', 'reason')
    ordering = ('-date',)
    readonly_fields = ('date', 'approval_date', 'disbursement_date', 'interest_rate')

    actions = ['approve_loans', 'decline_loans']  # Add custom actions

    def approve_loans(self, request, queryset):
        for loan_request in queryset:
            loan_request.status = 'approved'
            loan_request.approval_date = timezone.now()
            loan_request.disbursement_date = timezone.now()  # Set disbursement date to now
            
            # Update the user's account balance
            account_balance = AccountBalance.objects.get(account=loan_request.user)
            account_balance.loan_balance += loan_request.amount  # Update loan balance
            account_balance.available_balance += loan_request.amount  # Deduct from available balance
            
            # Save the updated account balance
            account_balance.save()
            loan_request.save()  # Save the loan request
            
            messages.success(request, f'Loan request for {loan_request.user.email} approved.')
    
    approve_loans.short_description = "Approve selected loan requests"

    def decline_loans(self, request, queryset):
        for loan_request in queryset:
            loan_request.status = 'declined'
            loan_request.approval_date = None  # Clear approval date if declined
            loan_request.disbursement_date = None  # Clear disbursement date if declined
            loan_request.save()  # Save the loan request
            
            messages.success(request, f'Loan request for {loan_request.user.email} declined.')

    decline_loans.short_description = "Decline selected loan requests"

# Register the LoanRequest model with the admin
admin.site.register(LoanRequest, LoanRequestAdmin)

@admin.register(Exchange)
class ExchangeAdmin(UnfoldModelAdmin):
    list_display = ('user', 'amount', 'from_currency', 'to_currency', 'status', 'date')
    search_fields = ('user',)
    list_filter = ('status', 'from_currency', 'to_currency', 'date')


@admin.register(ResetPassword)
class ResetPasswordAdmin(UnfoldModelAdmin):
    list_display = ('email','reset_code','created_at')


@admin.register(TransferCode)
class TransferCodeAdmin(UnfoldModelAdmin):
    list_display = ('user','tac_code', 'tax_code', 'imf_code', 'created_at', 'expires_at', 'used')
    search_fields = ('transfer_code', 'tac_code', 'tax_code', 'imf_code', 'user__email')  # Allows searching by user email
    list_filter = ('used', 'created_at')  # Allows filtering by used status and creation date

@admin.register(Transaction)
class TransactionAdmin(UnfoldModelAdmin):
    list_display = (
        'user', 
        'transaction_date', 
        'amount', 
        'transaction_type', 
        'status', 
        'reference', 
        'institution', 
        'region', 
        'from_account', 
        'to_account'
    )
    search_fields = (
        'user__email', 
        'reference', 
        'institution', 
        'region', 
        'from_account', 
        'to_account'
    )
    list_filter = (
        'transaction_type', 
        'status', 
        'institution', 
        'region'
    )
    # ✅ Allow admin to edit this field in the form
    fields = (
        'user', 
        'transaction_date', 
        'amount', 
        'transaction_type', 
        'status', 
        'reference', 
        'institution', 
        'region', 
        'from_account', 
        'to_account'
    )


@admin.register(Deposit)
class DepositAdmin(UnfoldModelAdmin):
    list_display = (
        'user', 'amount', 'TNX', 'network', 'account', 'rate',
        'date', 'status', 'confirm_button', 'cancel_button'
    )
    search_fields = ('user__email', 'TNX', 'network')
    list_editable = ['date']
    list_filter = ('status', 'network', 'date')
    actions = ['confirm_deposit', 'cancel_deposit']

    def save_model(self, request, obj, form, change):
        """
        Trigger logic when admin saves a deposit.
        """
        super().save_model(request, obj, form, change)

        if obj.status == 'completed':
            if not Transaction.objects.filter(
                user=obj.user,
                amount=obj.amount,
                transaction_type='deposit',
                reference=obj.TNX
            ).exists():
                self.confirm_single_deposit(obj)

        elif obj.status == 'failed':
            self.cancel_single_deposit(obj)

    def get_changeform_initial_data(self, request):
        """Auto-fill TNX when admin is creating a new deposit."""
        initial_data = super().get_changeform_initial_data(request)
        initial_data['TNX'] = f"ADM-{uuid.uuid4().hex[:10].upper()}"  # generate unique TNX
        return initial_data
    
    

    def confirm_button(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<a href="?confirm_deposit={}" style="padding: 6px 12px; background-color: #28a745; color: white; border-radius: 5px; text-decoration: none; font-weight: bold;">Confirm</a>',
                obj.id
            )
        return format_html(
            '<span style="padding: 6px 12px; background-color: #6c757d; color: white; border-radius: 5px; font-weight: bold;">Confirmed</span>'
        )
    confirm_button.short_description = 'Confirm'

    def cancel_button(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<a href="?cancel_deposit={}" style="padding: 6px 12px; background-color: #dc3545; color: white; border-radius: 5px; text-decoration: none; font-weight: bold;">Cancel</a>',
                obj.id
            )
        return format_html(
            '<span style="padding: 6px 12px; background-color: #6c757d; color: white; border-radius: 5px; font-weight: bold;">Canceled</span>'
        )
    cancel_button.short_description = 'Cancel'

    def get_queryset(self, request):
        """Handles confirmation or cancellation via URL parameters."""
        qs = super().get_queryset(request)

        confirm_id = request.GET.get('confirm_deposit')
        cancel_id = request.GET.get('cancel_deposit')

        if confirm_id:
            deposit = get_object_or_404(Deposit, id=confirm_id)
            if deposit.status == 'pending':
                self.confirm_single_deposit(deposit)
                messages.success(request, f"Deposit {deposit.id} has been confirmed.")

        if cancel_id:
            deposit = get_object_or_404(Deposit, id=cancel_id)
            if deposit.status == 'pending':
                self.cancel_single_deposit(deposit)
                messages.warning(request, f"Deposit {deposit.id} has been canceled.")

        return qs

    def confirm_single_deposit(self, deposit):
        """Confirm a single deposit and update balance based on the selected account."""
        user_balance = AccountBalance.objects.get(account=deposit.user)

        if deposit.account == 'Savings_Account':
            user_balance.available_balance += deposit.amount
        elif deposit.account == 'Checking_Account':
            user_balance.checking_balance += deposit.amount
        elif deposit.account == 'Loan_Account':
            user_balance.loan_balance += deposit.amount
        elif deposit.account == 'GBP_Account':
            user_balance.gbp += deposit.amount
        elif deposit.account == 'EUR_Account':
            user_balance.eur += deposit.amount

        # always increase total credits
        user_balance.total_credits += deposit.amount
        user_balance.save()

        deposit.status = 'completed'
        deposit.save()

        # update/create transaction record
        transaction, created = Transaction.objects.get_or_create(
            user=deposit.user,
            amount=deposit.amount,
            transaction_type='deposit',
            reference=deposit.TNX or f"ADM-{deposit.id}",
            defaults={'status': 'completed'}
        )
        if not created:
            transaction.status = 'completed'
            transaction.save()


    def cancel_single_deposit(self, deposit):
        """Cancel a single deposit."""
        deposit.status = 'failed'
        deposit.save()

        transaction = Transaction.objects.filter(
            user=deposit.user, amount=deposit.amount, transaction_type='deposit'
        ).first()
        if transaction:
            transaction.status = 'failed'
            transaction.save()

    def confirm_deposit(self, request, queryset):
        """Bulk confirm deposits."""
        for deposit in queryset:
            if deposit.status == 'pending':
                self.confirm_single_deposit(deposit)
        messages.success(request, "Selected deposits have been confirmed.")
    confirm_deposit.short_description = "Confirm selected deposits"

    def cancel_deposit(self, request, queryset):
        """Bulk cancel deposits."""
        for deposit in queryset:
            if deposit.status == 'pending':
                self.cancel_single_deposit(deposit)
        messages.warning(request, "Selected deposits have been canceled.")
    cancel_deposit.short_description = "Cancel selected deposits"




class TransferAdminForm(forms.ModelForm):
    BALANCE_CHOICES = [
        ("Savings_Account", "Savings Account"),
        ("Checking_Account", "Checking Account"),
        ("Loan_Account", "Loan Account"),
        ("GBP_Account", "GBP Account"),
        ("EUR_Account", "EUR Account"),
    ]
    balance = forms.ChoiceField(choices=BALANCE_CHOICES, label="Select Account")

    class Meta:
        model = Transfer
        fields = "__all__"


@admin.register(Transfer)
class TransferAdmin(UnfoldModelAdmin):
    form = TransferAdminForm

    list_display = (
        "reference", "user", "beneficiary_display", "amount", "balance", "status", "date",
        "confirm_button", "cancel_button"
    )
    list_filter = ("status", "balance", "date", "beneficiary")
    search_fields = (
        "reference",
        "user__username",
        "beneficiary__full_name",
        "beneficiary__bank_name",
        "beneficiary__account_number",
    )
    ordering = ("-date",)
    readonly_fields = ("reference","charge")

    fieldsets = (
        ("Transfer Details", {
            "fields": (
                "reference", "user", "beneficiary", "amount", "balance",
                "charge", "reason", "status"
            )
        }),
    )

    actions = ["approve_transfer", "reject_transfer"]

    # -------------------------
    # 🔹 Handle Admin Save
    # -------------------------
    def save_model(self, request, obj, form, change):
        """
        When admin saves a transfer:
        - Auto-generate reference if missing
        - Validate user has enough balance
        - If status is 'completed', deduct balance and create transaction.
        - If status is 'failed', mark transaction failed.
        """
        if not obj.reference:  # Auto-generate unique TXN reference
            obj.reference = f"TXN-{uuid.uuid4().hex[:10].upper()}"

        # 🔹 Check user balance before saving
        try:
            user_balance = AccountBalance.objects.get(account=obj.user)
        except AccountBalance.DoesNotExist:
            messages.error(request, "⚠️ This user does not have an account balance record.")
            return  # stop saving

        # Match selected balance type
        insufficient = False
        if obj.balance == "Savings_Account" and obj.amount > user_balance.available_balance:
            insufficient = True
        elif obj.balance == "Checking_Account" and obj.amount > user_balance.checking_balance:
            insufficient = True
        elif obj.balance == "Loan_Account" and obj.amount > user_balance.loan_balance:
            insufficient = True
        elif obj.balance == "GBP_Account" and obj.amount > user_balance.gbp:
            insufficient = True
        elif obj.balance == "EUR_Account" and obj.amount > user_balance.eur:
            insufficient = True

        if insufficient:
            messages.error(request, "⚠️ Insufficient funds in the selected account balance.")
            return  # ❌ stop saving instead of crashing

        # ✅ Save only if valid
        super().save_model(request, obj, form, change)

        if obj.status == "completed":
            self.confirm_single_transfer(obj)
        elif obj.status == "failed":
            self.cancel_single_transfer(obj)

    # -------------------------
    # 🔹 Beneficiary Display
    # -------------------------
    def beneficiary_display(self, obj):
        """Custom display of beneficiary information."""
        if obj.beneficiary:
            return format_html(
                "{}<br><small>{} - {}</small>",
                obj.beneficiary.full_name,
                obj.beneficiary.bank_name,
                obj.beneficiary.account_number,
            )
        return "-"
    beneficiary_display.short_description = "Beneficiary"

    def confirm_button(self, obj):
        if obj.status == "pending":
            return format_html(
                '<a href="?confirm_transfer={}" style="padding:6px 12px; background-color:#28a745; color:white; border-radius:5px; text-decoration:none; font-weight:bold;">Confirm</a>',
                obj.id,
            )
        return format_html(
            '<span style="padding:6px 12px; background-color:#6c757d; color:white; border-radius:5px; font-weight:bold;">Confirmed</span>'
        )
    confirm_button.short_description = "Confirm"

    def cancel_button(self, obj):
        if obj.status == "pending":
            return format_html(
                '<a href="?cancel_transfer={}" style="padding:6px 12px; background-color:#dc3545; color:white; border-radius:5px; text-decoration:none; font-weight:bold;">Cancel</a>',
                obj.id,
            )
        return format_html(
            '<span style="padding:6px 12px; background-color:#6c757d; color:white; border-radius:5px; font-weight:bold;">Canceled</span>'
        )
    cancel_button.short_description = "Cancel"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        confirm_id = request.GET.get("confirm_transfer")
        cancel_id = request.GET.get("cancel_transfer")

        if confirm_id:
            transfer = get_object_or_404(Transfer, id=confirm_id)
            if transfer.status == "pending":
                self.confirm_single_transfer(transfer)
                messages.success(request, f"Transfer {transfer.reference} has been confirmed.")
        if cancel_id:
            transfer = get_object_or_404(Transfer, id=cancel_id)
            if transfer.status == "pending":
                self.cancel_single_transfer(transfer)
                messages.warning(request, f"Transfer {transfer.reference} has been canceled.")

        return qs

    # -------------------------
    # 🔹 Main Confirm Logic
    # -------------------------
    def confirm_single_transfer(self, transfer):
        """Confirm transfer, deduct balance, and create full transaction record."""
        user_balance = AccountBalance.objects.get(account=transfer.user)

        # Deduct from the selected account balance
        if transfer.balance == "Savings_Account":
            user_balance.available_balance -= transfer.amount
            from_acc = "Savings Account"
        elif transfer.balance == "Checking_Account":
            user_balance.checking_balance -= transfer.amount
            from_acc = "Checking Account"
        elif transfer.balance == "Loan_Account":
            user_balance.loan_balance -= transfer.amount
            from_acc = "Loan Account"
        elif transfer.balance == "GBP_Account":
            user_balance.gbp -= transfer.amount
            from_acc = "GBP Account"
        elif transfer.balance == "EUR_Account":
            user_balance.eur -= transfer.amount
            from_acc = "EUR Account"
        else:
            from_acc = "Unknown Account"

        user_balance.total_debits += transfer.amount
        user_balance.save()

        # Mark transfer as completed
        transfer.status = "completed"
        transfer.save()

        # Fill transaction details
        transaction, created = Transaction.objects.get_or_create(
            user=transfer.user,
            reference=transfer.reference,
            transaction_type="transfer",
            defaults={
                "amount": transfer.amount,
                "status": "completed",
                "description": transfer.reason or f"Transfer to {transfer.beneficiary.full_name if transfer.beneficiary else 'Unknown Beneficiary'}",
                "institution": transfer.beneficiary.bank_name if transfer.beneficiary else None,
                "region": transfer.region,
                "from_account": from_acc,
                "to_account": f"{transfer.beneficiary.full_name} - {transfer.beneficiary.account_number}" if transfer.beneficiary else None,
            },
        )

        if not created:
            # Update existing transaction if already created
            transaction.amount = transfer.amount
            transaction.status = "completed"
            transaction.description = transfer.reason or transaction.description
            transaction.institution = transfer.beneficiary.bank_name if transfer.beneficiary else transaction.institution
            transaction.region = transfer.region
            transaction.from_account = from_acc
            transaction.to_account = f"{transfer.beneficiary.full_name} - {transfer.beneficiary.account_number}" if transfer.beneficiary else transaction.to_account
            transaction.save()


    # -------------------------
    # 🔹 Cancel Logic
    # -------------------------
    def cancel_single_transfer(self, transfer):
        """Cancel transfer and mark transaction as failed."""
        transfer.status = "failed"
        transfer.save()

        transaction = Transaction.objects.filter(
            user=transfer.user,
            amount=transfer.amount,
            transaction_type="transfer",
            reference=transfer.reference,
        ).first()
        if transaction:
            transaction.status = "failed"
            transaction.save()

    # -------------------------
    # 🔹 Bulk Actions
    # -------------------------
    def approve_transfer(self, request, queryset):
        for transfer in queryset:
            if transfer.status == "pending":
                self.confirm_single_transfer(transfer)
        messages.success(request, "Selected transfers have been approved.")
    approve_transfer.short_description = "Approve selected transfers"

    def reject_transfer(self, request, queryset):
        for transfer in queryset:
            if transfer.status == "pending":
                self.cancel_single_transfer(transfer)
        messages.warning(request, "Selected transfers have been rejected.")
    reject_transfer.short_description = "Reject selected transfers"



@admin.register(PaymentGateway)
class PaymentGatewayAdmin(UnfoldModelAdmin):
    list_display = ('network', 'deposit_address', 'instructions')
    search_fields = ('network', 'deposit_address')
    list_filter = ('network',)






@admin.register(ExchangeRate)
class ExchangeRateAdmin(UnfoldModelAdmin):
    list_display = ('eur_usd', 'gbp_usd', 'eur_gbp', 'updated_at')
    search_fields = ('eur_usd', 'gbp_usd', 'eur_gbp')
    list_filter = ('updated_at',)


@admin.register(Beneficiary)
class BeneficiaryAdmin(UnfoldModelAdmin):
    list_display = (
        "id", "user", "full_name", "account_number", "bank_name", "swift_code","routing_transit_number","bank_address","created_at"
    )
    list_filter = ("user", "bank_name", "created_at")
    search_fields = ("full_name", "account_number", "bank_name")
    ordering = ("-created_at",)