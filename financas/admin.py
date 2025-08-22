from django.contrib import admin
from .models import Transacao, Categoria,Meta

admin.site.register(Transacao)
admin.site.register(Categoria)
admin.site.register(Meta)