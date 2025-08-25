from django import forms
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Usuário",
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

class PerfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'email']
        labels = {
            'first_name': 'Nome completo',
            'email': 'Email',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full border rounded-md px-3 py-2 focus:ring focus:ring-blue-200 outline-none'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full border rounded-md px-3 py-2 focus:ring focus:ring-blue-200 outline-none'
            }),
        }


class SuporteForm(forms.Form):
    assunto = forms.CharField(
        label="Assunto",
        widget=forms.TextInput(attrs={
            'class': 'w-full border rounded-md px-3 py-2 focus:ring focus:ring-blue-200 outline-none',
            'placeholder': 'Ex: Dúvida sobre investimentos'
        })
    )
    mensagem = forms.CharField(
        label="Mensagem",
        widget=forms.Textarea(attrs={
            'class': 'w-full border rounded-md px-3 py-2 focus:ring focus:ring-blue-200 outline-none h-28',
            'placeholder': 'Descreva sua dúvida ou sugestão...'
        })
    )


