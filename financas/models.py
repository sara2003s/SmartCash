from django.db import models

class Transacao(models.Model):
	TIPOS = (
		("receita", "Receita"),
		("gasto", "Gasto"),
	)
	valor = models.DecimalField(max_digits=10, decimal_places=2)
	tipo = models.CharField(max_length=10, choices=TIPOS)
	data = models.DateField()
	categoria = models.CharField(max_length=100, null=True, blank=True)

	def __str__(self):
		return f"{self.tipo} - {self.valor} em {self.data}"
