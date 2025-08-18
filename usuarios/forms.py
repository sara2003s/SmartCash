from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class RegistroForm(UserCreationForm):
    nome = forms.CharField(
        max_length=150,
        required=True,
        label="Nome completo",
        widget=forms.TextInput(attrs={"placeholder": "Digite seu nome completo"})
    )
    cpf = forms.CharField(
        max_length=14,
        required=True,
        label="CPF/RG",
        widget=forms.TextInput(attrs={"placeholder": "000.000.000-00"})
    )
    telefone = forms.CharField(
        max_length=15,
        required=True,
        label="Celular",
        widget=forms.TextInput(attrs={"placeholder": "(00) 00000-0000"})
    )
    email = forms.EmailField(
        required=True,
        label="E-mail",
        widget=forms.EmailInput(attrs={"placeholder": "seu@email.com"})
    )

    class Meta:
        model = User
        fields = ["nome", "cpf", "telefone", "username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["nome"]
        if commit:
            user.save()
        return user


class FormularioLogin(AuthenticationForm):
    username = forms.CharField(
        label="Usuário",
        widget=forms.TextInput(attrs={"placeholder": "Digite seu usuário"})
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={"placeholder": "Digite sua senha"})
    )
