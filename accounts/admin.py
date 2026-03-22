from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import User

class CustomUserCreationForm(UserCreationForm):
    """
    Custom form for creating users with phone number
    """
    phone_number = forms.CharField(max_length=15, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.phone_number = self.cleaned_data['phone_number']
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    """
    Custom form for updating users
    """
    class Meta:
        model = User
        fields = '__all__'


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    list_display = ['username', 'email', 'phone_number', 'is_student', 'is_admin', 'is_staff']
    list_filter = ['is_student', 'is_admin', 'is_staff', 'is_active']
    
    # Fields to display when editing an existing user
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone_number', 'is_student', 'is_admin')}),
    )
    
    # Fields to display when creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone_number', 'password1', 'password2', 'is_student', 'is_admin'),
        }),
    )
    
    search_fields = ['username', 'email', 'phone_number']
    ordering = ['username']