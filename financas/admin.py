from django.contrib import admin
from .models import Transacao, Categoria,Meta, Profile
from .models import Aula, ParteAula


admin.site.register(Transacao)
admin.site.register(Categoria)
admin.site.register(Meta)
admin.site.register(Aula)
admin.site.register(ParteAula)
admin.site.register(Profile)