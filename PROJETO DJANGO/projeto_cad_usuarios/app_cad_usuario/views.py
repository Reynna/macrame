from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .models import Usuario, Estoque, Projeto, Historico
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now

def home(request):
    if request.method == 'POST':
        nome = request.POST['nome']
        email = request.POST['login']  # Altere para 'login' para corresponder ao campo do formulário
        senha = request.POST['senha']

        # Verifica se o email já está em uso
        if User.objects.filter(username=email).exists():
            return render(request, 'usuario/home.html', {'error': 'Email já está em uso.'})

        # Cria o novo usuário
        usuario = User.objects.create_user(username=email, password=senha, first_name=nome)
        usuario.save()
        return redirect('login')  # Redireciona para a página de login após o cadastro

    return render(request, 'usuario/home.html')

def usuario(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('login')
        senha = request.POST.get('senha')

        # Cria um novo usuário
        user = User.objects.create_user(username=email, email=email, password=senha)
        user.first_name = nome
        user.save()

        # Redireciona para a página inicial
        return redirect('pagina_inicial')

def cadastrar_usuario(request):
    if request.method == 'POST':
        nome = request.POST['nome']
        email = request.POST['email']
        senha = request.POST['senha']

        # Verifica se o email já está em uso
        if User.objects.filter(username=email).exists():
            return render(request, 'usuario/cadastrar_usuario.html', {'error': 'Email já está em uso.'})

        # Cria o novo usuário
        usuario = User.objects.create_user(username=email, password=senha, first_name=nome)
        usuario.save()
        return redirect('login')  # Redireciona para a página de login após o cadastro

    return render(request, 'usuario/cadastrar_usuario.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST['login']
        senha = request.POST['senha']

        # Autentica o usuário
        user = authenticate(request, username=email, password=senha)

        if user is not None:
            login(request, user)  # Faz o login do usuário
            return redirect('pagina_inicial')  # Redireciona para a página inicial
        else:
            return render(request, 'usuario/login.html', {'error': 'Login ou senha inválidos.'})

    return render(request, 'usuario/login.html')

def listagem_usuario(request):
    # Busca todos os usuários cadastrados
    usuarios = User.objects.all()

    # Renderiza o template 'usuario.html' com a lista de usuários
    return render(request, 'usuario/usuario.html', {'usuarios': usuarios})

def excluir_usuario(request, id):
    usuario = get_object_or_404(User, id=id)
    usuario.delete()  # Exclui o usuário do banco de dados
    return redirect('usuario')  # Redireciona para a lista de usuários
    
def alterar_email(request):
    if request.method == 'POST':
        novo_email = request.POST.get('email')
        if novo_email:  # Verifica se o novo e-mail foi fornecido
            request.user.email = novo_email
            request.user.save()  # Salva as alterações no banco de dados
            return redirect('pagina_inicial')  # Redireciona para a página inicial
    return render(request, 'usuario/alterar_email.html')

def alterar_senha(request):
    if request.method == 'POST':
        nova_senha = request.POST.get('senha')
        if nova_senha:  # Verifica se a nova senha foi fornecida
            request.user.set_password(nova_senha)
            request.user.save()  # Salva as alterações no banco de dados
            update_session_auth_hash(request, request.user)  # Mantém o usuário logado após alterar a senha
            return redirect('pagina_inicial')  # Redireciona para a página inicial
    return render(request, 'usuario/alterar_senha.html')

def logout_view(request):
    logout(request)
    return redirect('login')  # Redireciona para a página de login após deslogar

@login_required
def projetos(request):
    if request.method == 'POST':
        nome = request.POST['nome']
        material_id = request.POST['material']
        quantidade = int(request.POST['quantidade'])
        metros_por_unidade = float(request.POST['metros_por_unidade'])

        # Busca o material selecionado no estoque
        material = Estoque.objects.get(id=material_id, user=request.user)

        # Verifica se há material suficiente no estoque
        if material.quantidade_metros < quantidade * metros_por_unidade:
            projetos = Projeto.objects.filter(user=request.user)
            materiais = Estoque.objects.filter(user=request.user)
            return render(request, 'usuario/projetos.html', {
                'projetos': projetos,
                'materiais': materiais,
                'error': 'Quantidade insuficiente no estoque para este projeto.'
            })

        # Cria o projeto
        Projeto.objects.create(
            user=request.user,
            nome=nome,
            material=material,
            cor=material.cor,
            quantidade=quantidade,
            metros_por_unidade=metros_por_unidade
        )

        # Atualiza o estoque
        material.quantidade_metros -= quantidade * metros_por_unidade
        material.save()

        # Verifica se o estoque está baixo
        if material.quantidade_metros <= 50:
            request.session['estoque_baixo'] = f"O material '{material.material}' ({material.cor}) está com estoque baixo: {material.quantidade_metros} metros."

        return redirect('projetos')

    # Exibe os projetos e materiais disponíveis
    projetos = Projeto.objects.filter(user=request.user)
    materiais = Estoque.objects.filter(user=request.user)
    alerta_estoque = request.session.pop('estoque_baixo', None)  # Recupera o alerta de estoque baixo
    return render(request, 'usuario/projetos.html', {
        'projetos': projetos,
        'materiais': materiais,
        'alerta_estoque': alerta_estoque
    })

@login_required
def concluir_projeto(request, id):
    projeto = get_object_or_404(Projeto, id=id, user=request.user)

    print(f"Concluindo projeto: {projeto.nome}")  # Depuração

    Historico.objects.create(
        user=request.user,
        tabela="Projeto",
        acao="concluido",
        descricao=f"O projeto '{projeto.nome}' foi concluído."
    )

    projeto.delete()

    return redirect('projetos')

def concluir_projeto_remover(request, id):
    projeto = get_object_or_404(Projeto, id=id)

    # Registra no histórico
    Historico.objects.create(
        tabela='Projeto',
        acao='concluido',
        descricao=f"Projeto '{projeto.nome}' foi concluído.",
        data_hora=now()
    )

    # Marca o projeto como concluído (adiciona um campo 'concluido' se necessário)
    projeto.concluido = True
    projeto.save()

    return redirect('projetos')  # Redireciona para a página de projetos
    return redirect('projetos')  # Redireciona para a página de projetos

from django.core.paginator import Paginator  # Import Paginator

def historico(request):
    registros = Historico.objects.filter(user=request.user).order_by('-data_hora')  # Filtra pelo usuário autenticado
    paginator = Paginator(registros, 10)  # Mostra 10 registros por página
    page_number = request.GET.get('page')  # Obtém o número da página da URL
    page_obj = paginator.get_page(page_number)  # Obtém os registros da página atual
    return render(request, 'usuario/historico.html', {'page_obj': page_obj})
    return render(request, 'usuario/historico.html', {'registros': registros})

@login_required
def estoque(request):
    if request.method == 'POST':
        # Obtém os dados do formulário
        material = request.POST.get('material')
        cor = request.POST.get('cor')
        quantidade_metros = request.POST.get('quantidade')

        # Cria um novo item no estoque
        Estoque.objects.create(
            user=request.user,  # Associa o item ao usuário autenticado
            material=material,
            cor=cor,
            quantidade_metros=quantidade_metros
        )
        return redirect('estoque')  # Redireciona para a página de estoque após adicionar o item

    # Exibe os itens do estoque do usuário autenticado
    itens = Estoque.objects.filter(user=request.user)
    return render(request, 'usuario/estoque.html', {'itens': itens})

def editar_projeto(request):
    return render(request, 'usuario/editar_projeto.html')

def excluir_item(request, id):
    item = get_object_or_404(Estoque, id=id)
    Historico.objects.create(
        tabela='Estoque',
        acao='excluido',
        descricao=f"Item '{item.material}' excluído do estoque.",
    )
    item.delete()
    return redirect('estoque')

def editar_item(request):
    if request.method == 'POST':
        item = get_object_or_404(Estoque, id=request.POST.get('id'))
        item.material = request.POST.get('material')
        item.cor = request.POST.get('cor')
        item.quantidade_metros = request.POST.get('quantidade')  # Corrige o campo para quantidade_metros
        item.save()  # Salva as alterações no banco de dados
    return redirect('estoque')

@login_required
def adicionar_projeto(request):
    if request.method == 'POST':
        nome = request.POST['nome']
        material_id = request.POST['material']  # ID do material selecionado
        cor = request.POST['cor']
        quantidade = int(request.POST['quantidade'])
        metros_por_unidade = float(request.POST['metros_por_unidade'])

        # Busca o material selecionado no estoque do usuário autenticado
        material = get_object_or_404(Estoque, id=material_id, user=request.user)

        # Verifica se há material suficiente no estoque
        if material.quantidade_metros < quantidade * metros_por_unidade:
            return render(request, 'usuario/adicionar_projeto.html', {
                'materiais': Estoque.objects.filter(user=request.user),
                'error': 'Quantidade insuficiente no estoque para este projeto.'
            })

        # Cria o projeto
        Projeto.objects.create(
            user=request.user,  # Associa o projeto ao usuário autenticado
            nome=nome,
            material=material,
            cor=cor,
            quantidade=quantidade,
            metros_por_unidade=metros_por_unidade
        )

        # Atualiza o estoque
        material.quantidade_metros -= quantidade * metros_por_unidade
        material.save()

        return redirect('projetos')

    # Filtra os materiais disponíveis no estoque do usuário autenticado
    materiais = Estoque.objects.filter(user=request.user)
    return render(request, 'usuario/adicionar_projeto.html', {'materiais': materiais})

@login_required
def alterar_nome(request):
    if request.method == 'POST':
        novo_nome = request.POST.get('novo_nome')
        if novo_nome:
            # Atualiza o nome do usuário logado
            usuario = request.user
            usuario.first_name = novo_nome
            usuario.save()
            return redirect('pagina_inicial')  # Redireciona para a página inicial após a alteração
    return render(request, 'usuario/alterar_nome.html')  # Renderiza o formulário

@login_required
def excluir_projeto(request, id):
    # Obtém o projeto associado ao ID
    projeto = get_object_or_404(Projeto, id=id, user=request.user)

    # Restaura a quantidade de material no estoque
    material = projeto.material  # Relacionamento com o modelo Estoque
    material.quantidade_metros += projeto.quantidade * projeto.metros_por_unidade
    material.save()

    # Exclui o projeto
    projeto.delete()

    return redirect('projetos')  # Redireciona para a página de projetos

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from app_cad_usuario.models import Projeto, Estoque, Historico

@login_required
def pagina_inicial(request):
    projetos_ativos = Projeto.objects.filter(user=request.user).count()
    itens_estoque = Estoque.objects.filter(user=request.user).count()
    registros_total = Historico.objects.filter(user=request.user).count()

    return render(request, 'usuario/pagina_inicial.html', {
        'projetos_ativos': projetos_ativos,
        'itens_estoque': itens_estoque,
        'registros_total': registros_total,
    })

