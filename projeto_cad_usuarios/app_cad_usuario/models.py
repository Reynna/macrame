from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User


class Usuario(models.Model):
    nome = models.CharField(max_length=100)  # Adicione este campo
    login = models.CharField(max_length=100)
    senha = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Estoque(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relaciona o estoque ao usuário
    material = models.CharField(max_length=100)  # Nome do material
    cor = models.CharField(max_length=50)  # Cor do material
    quantidade_metros = models.FloatField(default=0)  # Quantidade disponível em metros

    def __str__(self):
        return f"{self.material} ({self.cor})"

class Projeto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relaciona o projeto ao usuário
    nome = models.CharField(max_length=100)
    material = models.ForeignKey('Estoque', on_delete=models.CASCADE)  # Relacionamento com Estoque
    cor = models.CharField(max_length=50)
    quantidade = models.IntegerField(default=1)  # Quantidade de unidades do projeto
    metros_por_unidade = models.FloatField(default=0)  # Metros de material por unidade do projeto

    def __str__(self):
        return self.nome

class Historico(models.Model):
    ACAO_CHOICES = [
        ('adicionado', 'Adicionado'),
        ('editado', 'Editado'),
        ('excluido', 'Excluído'),
        ('concluido', 'Concluído'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Usuário que realizou a ação
    tabela = models.CharField(max_length=100)  # Nome da tabela afetada
    acao = models.CharField(max_length=20, choices=ACAO_CHOICES)  # Tipo de ação
    descricao = models.TextField()  # Descrição da ação
    data_hora = models.DateTimeField(auto_now_add=True)  # Data e hora da ação

    def __str__(self):
        return f"{self.tabela} - {self.acao} - {self.data_hora}"

