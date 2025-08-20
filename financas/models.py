from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
	nome = models.CharField(max_length=100)
	descricao = models.TextField(null=True, blank=True)
	cor = models.CharField(max_length=7, default="#000000")  # Cor em formato hexadecimal

	def __str__(self):
		return self.nome

class Transacao(models.Model):
	TIPOS = (
		("receita", "Receita"),
		("gasto", "Gasto"),
	)
	valor = models.DecimalField(max_digits=10, decimal_places=2)
	tipo = models.CharField(max_length=10, choices=TIPOS)
	data = models.DateField()
	categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)


	def __str__(self):
		return f"{self.tipo} - {self.valor} em {self.data}"
	
class Meta:
    ordering = ['-data']
	
class Gasto(models.Model):
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

def __str__(self):
		return f"{self.descricao} - {self.valor} em {self.data}"

