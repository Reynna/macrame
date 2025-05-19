from django.contrib import admin
from .models import Estoque, Projeto, Historico

# Registra os modelos no painel administrativo
admin.site.register(Estoque)
admin.site.register(Projeto)
admin.site.register(Historico)
