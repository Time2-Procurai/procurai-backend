from django import forms
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'username', 'email', 'cpf', 'foto', 'telefone', 'endereco', 'interesses']