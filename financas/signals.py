from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from financas.models import Meta

@receiver(post_save, sender=User)
def criar_dados_iniciais(sender, instance, created, **kwargs):
    if created:
        Meta.objects.create(usuario=instance, valor_atual=0, valor_alvo=0)
        print(f"Dados iniciais criados para o usuário: {instance.username}")
