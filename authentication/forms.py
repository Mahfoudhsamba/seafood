# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Permission
from .models import User, Role


class UserCreateForm(UserCreationForm):
    """Formulaire de création d'utilisateur"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'})
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'})
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'})
    )
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'role', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom d'utilisateur"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mot de passe'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'})


class UserUpdateForm(forms.ModelForm):
    """Formulaire de mise à jour d'utilisateur"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Aucun rôle"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'avatar', 'role', 'is_staff', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'avatar': 'Photo de profil',
            'is_staff': 'Accès au portail (Staff)',
            'is_active': 'Compte actif',
        }


class AdminPasswordResetForm(forms.Form):
    """Formulaire pour réinitialiser le mot de passe d'un utilisateur par un admin"""
    new_password1 = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nouveau mot de passe'})
    )
    new_password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'})
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les deux mots de passe ne correspondent pas.")

        return cleaned_data


class RoleForm(forms.ModelForm):
    """Formulaire de création/modification de rôle"""
    class Meta:
        model = Role
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du rôle'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description du rôle'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Nom du rôle',
            'description': 'Description',
            'is_active': 'Rôle actif',
        }


class RolePermissionsForm(forms.Form):
    """Formulaire pour gérer les permissions d'un rôle"""
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all().select_related('content_type').order_by('content_type__app_label', 'codename'),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        role = kwargs.pop('role', None)
        super().__init__(*args, **kwargs)

        if role:
            self.fields['permissions'].initial = role.permissions.all()

    def get_permissions_by_app(self):
        """Retourne les permissions groupées par application"""
        permissions_dict = {}
        for perm in self.fields['permissions'].queryset:
            app_label = perm.content_type.app_label
            if app_label not in permissions_dict:
                permissions_dict[app_label] = []
            permissions_dict[app_label].append(perm)
        return permissions_dict
