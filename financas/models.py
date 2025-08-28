from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Categoria(models.Model):
	nome = models.CharField(max_length=100)
	cor = models.CharField(max_length=7, default="#000000") 
	def __str__(self):
		return self.nome

class Transacao(models.Model):
	TIPOS = (
		("entrada", "Entrada"),
		("saida", "Saida"),
	)
	usuario = models.ForeignKey(User, on_delete=models.CASCADE) 
	valor = models.DecimalField(max_digits=10, decimal_places=2)
	tipo = models.CharField(max_length=10, choices=TIPOS)
	categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
	data = models.DateField()


	def __str__(self):
		return f"{self.tipo} - {self.valor} em {self.data}"
	
class Meta(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    valor_alvo = models.DecimalField(max_digits=10, decimal_places=2)
    valor_atual = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    data_limite = models.DateField(null=True, blank=True)
    ativa = models.BooleanField(default=True)
    concluida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)

    def porcentagem_progresso(self):
        if self.valor_alvo > 0:
            return (self.valor_atual / self.valor_alvo) * 100
        return 0

    def __str__(self):
        return self.nome
    
class Gasto(models.Model):
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

def __str__(self):
		return f"{self.descricao} - {self.valor} em {self.data}"

class Profile(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cpf_rg = models.CharField(max_length=20, blank=True)
    celular = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.user.username
    
class ContaBancaria(models.Model):

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    banco = models.CharField(max_length=100)
    agencia = models.CharField(max_length=20)
    numero_conta = models.CharField(max_length=30)
    data_conectar = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.banco} - {self.numero_conta}"
    
class CartaoDeCredito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nome_cartao = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, blank=True)
    validade = models.CharField(max_length=5, blank=True) 
    numero_cartao = models.CharField(max_length=16) 
    data_conectar = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome_cartao} - **** {self.numero_cartao[-4:]}"