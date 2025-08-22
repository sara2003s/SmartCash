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
    # Relacionamento com o usuário que criou a meta
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    valor_alvo = models.DecimalField(max_digits=10, decimal_places=2)
    valor_atual = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    data_limite = models.DateField(null=True, blank=True)
    ativa = models.BooleanField(default=True)
    concluida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)

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

