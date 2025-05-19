from django.contrib import admin
from django.urls import path
from app_cad_usuario import views

urlpatterns = [
    path('', views.home, name='home'),  # Página inicial
    path('usuario/', views.listagem_usuario, name='usuario'),
    path('pagina-inicial/', views.pagina_inicial, name='pagina_inicial'),
    path('login/', views.login_view, name='login'),
    path('excluir-usuario/<int:id>/', views.excluir_usuario, name='excluir_usuario'),
    path('alterar-email/', views.alterar_email, name='alterar_email'),
    path('alterar-senha/', views.alterar_senha, name='alterar_senha'),
    path('logout/', views.logout_view, name='logout'),
    path('projetos/', views.projetos, name='projetos'),
    path('historico/', views.historico, name='historico'),
    path('estoque/', views.estoque, name='estoque'),
    path('editar-projeto/', views.editar_projeto, name='editar_projeto'),
    path('estoque/excluir/<int:id>/', views.excluir_item, name='excluir_item'),
    path('estoque/editar/', views.editar_item, name='editar_item'),
    path('projetos/concluir/<int:id>/', views.concluir_projeto, name='concluir_projeto'),
    path('projetos/excluir/<int:id>/', views.excluir_projeto, name='excluir_projeto'),
    path('projetos/adicionar/', views.adicionar_projeto, name='adicionar_projeto'),
    path('alterar_nome/', views.alterar_nome, name='alterar_nome'),
    path('admin/', admin.site.urls),  # Adiciona o painel administrativo

]