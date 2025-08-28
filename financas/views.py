from financas.models import Transacao, Meta, Profile, Categoria
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from decimal import Decimal
from django.db.models.functions import TruncMonth
from .forms import PerfilForm, SuporteForm
from .models import ContaBancaria
import re
from .models import CartaoDeCredito
from django.db.models.functions import ExtractMonth, ExtractYear
from django.utils import timezone
from django.db.models.functions import TruncMonth

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')   
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password, backend='django.contrib.auth.backends.ModelBackend')
        
        if user is not None:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Login realizado com sucesso!")
            return redirect('financas:dashboard')
        messages.error(request, "E-mail ou senha inválidos.")
    
    return render(request, 'financas/index.html')

def logout_view(request):
    logout(request)
    return redirect('inicio')  

def register_view(request):
    if request.method == "POST":
        nome_completo = request.POST.get("nome_completo")
        cpf_rg = request.POST.get("cpf_rg")
        celular = request.POST.get("celular")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirmar_senha = request.POST.get("confirmar_senha")

        if password != confirmar_senha:
            messages.error(request, "As senhas não coincidem.")
            return redirect("financas:login")
        
        if not nome_completo or not username or not email or not password:
            messages.error(request, "Todos os campos obrigatórios devem ser preenchidos.")
            return redirect("financas:login")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Este nome de usuário já está em uso.")
            return redirect("financas:login")
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Este e-mail já está em uso.")
            return redirect("financas:login")

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            
            nomes = nome_completo.split(' ', 1)
            user.first_name = nomes[0]
            if len(nomes) > 1:
                user.last_name = nomes[1]
            user.save()

            Profile.objects.create(
                user=user,
                cpf_rg=cpf_rg,
                celular=celular
            )

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect("financas:configuracao_inicial")

        except Exception as e:
            messages.error(request, f"Ocorreu um erro no cadastro: {e}")
            return redirect("financas:login")
    
    return redirect("financas:login")

@login_required
def configuracao_inicial(request):
    # Esta página pode ter um formulário para o usuário preencher dados iniciais
    return render(request, "financas/configuracao_inicial.html")

def metas(request):
    metas_do_usuario = Meta.objects.filter(usuario=request.user).order_by('ativa', 'data_limite')

    metas_ativas_count = metas_do_usuario.filter(ativa=True, concluida=False).count()
    metas_concluidas_count = metas_do_usuario.filter(concluida=True).count()
    total_economizado = metas_do_usuario.aggregate(total=Sum('valor_atual'))['total'] or 0

    context = {
        'metas': metas_do_usuario,
        'metas_ativas_count': metas_ativas_count,
        'metas_concluidas_count': metas_concluidas_count,
        'total_economizado': total_economizado
    }
    
    return render(request, 'financas/metas.html', context)

@login_required
def dashboard(request):
    try:
        # Dados para os cards
        entradas = Transacao.objects.filter(usuario=request.user, tipo='entrada').aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')
        saidas = Transacao.objects.filter(usuario=request.user, tipo='saida').aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')
        saldo = entradas - saidas

        meta = Meta.objects.filter(usuario=request.user).first()
        meta_valor = meta.valor_atual if meta else Decimal('0.00')
        meta_total = meta.valor_alvo if meta else Decimal('0.00')
        meta_progresso = (meta_valor / meta_total) * 100 if meta_total > 0 else 0

        gastos_por_categoria = Transacao.objects.filter(
            usuario=request.user,
            tipo='saida'
        ).values('categoria__nome', 'categoria__cor').annotate(
            total_gasto=Sum('valor')
        ).order_by('-total_gasto')
        
        gastos_detalhados = []
        if gastos_por_categoria:
            total_gastos_pizza = sum(item['total_gasto'] for item in gastos_por_categoria)
            for item in gastos_por_categoria:
                porcentagem = (item['total_gasto'] / total_gastos_pizza) * 100 if total_gastos_pizza > 0 else 0
                gastos_detalhados.append({
                    'nome': item['categoria__nome'],
                    'cor': item['categoria__cor'],
                    'valor': item['total_gasto'],
                    'porcentagem': porcentagem
                })
        
        expenses_labels = [g['nome'] for g in gastos_detalhados]
        expenses_data = [g['valor'] for g in gastos_detalhados]

        meses_labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago',]
        hoje = timezone.now()
        mes_atual = hoje.month
        meses_ordenados = [meses_labels[(mes_atual - 6 + i) % 12] for i in range(6)]
        
        receitas_mensais = [
            Transacao.objects.filter(
                usuario=request.user,
                tipo='entrada',
                data__year=(hoje - timezone.timedelta(days=30*i)).year,
                data__month=(hoje - timezone.timedelta(days=30*i)).month
            ).aggregate(Sum('valor'))['valor__sum'] or 0 for i in range(5, -1, -1)
        ]

        gastos_mensais = [
            Transacao.objects.filter(
                usuario=request.user,
                tipo='saida',
                data__year=(hoje - timezone.timedelta(days=30*i)).year,
                data__month=(hoje - timezone.timedelta(days=30*i)).month
            ).aggregate(Sum('valor'))['valor__sum'] or 0 for i in range(5, -1, -1)
        ]

        transacoes_recentes = Transacao.objects.filter(usuario=request.user).order_by('-data')[:6]

    except Exception as e:
        print(f"Erro ao buscar dados do dashboard: {e}")
        entradas = Decimal('0.00')
        saidas = Decimal('0.00')
        saldo = Decimal('0.00')
        meta_valor = Decimal('0.00')
        meta_total = Decimal('0.00')
        meta_progresso = 0
        expenses_labels = []
        expenses_data = []
        gastos_detalhados = []
        transacoes_recentes = []
        meses_labels = ['Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago']
        receitas_mensais = [0, 0, 0, 0, 0, 0]
        gastos_mensais = [0, 0, 0, 0, 0, 0]


    context = {
        'saldo': saldo,
        'entradas': entradas,
        'saidas': saidas,
        'meta_valor': meta_valor,
        'meta_total': meta_total,
        'meta_progresso': meta_progresso,
        'expenses_labels': expenses_labels,
        'expenses_data': expenses_data,
        'gastos_detalhados': gastos_detalhados,
        'transacoes_recentes': transacoes_recentes,
        'meses_labels': meses_labels,
        'receitas_mensais': receitas_mensais,
        'gastos_mensais': gastos_mensais,
    }

    return render(request, "financas/dashboard.html", context)

@login_required
def transacoes(request):
    # --- FILTROS ---
    transacoes_qs = Transacao.objects.filter(usuario=request.user).order_by('-data')
    categorias_qs = Categoria.objects.all()

    # Lista de nomes de meses em português
    meses_pt = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]

    # Prepara os períodos para o filtro (meses dinâmicos)
    periodos_qs = (
        transacoes_qs
        .annotate(mes=TruncMonth("data"))
        .values_list("mes", flat=True)
        .distinct()
        .order_by("-mes")
    )
    # Usa os nomes em português para a lista de períodos
    periodos = [f"{meses_pt[d.month-1]} {d.year}" for d in periodos_qs]

    q = request.GET.get("q")
    categoria = request.GET.get("categoria")
    tipo = request.GET.get("tipo")
    periodo = request.GET.get("periodo")

    # Aplica os filtros na ordem
    if q:
        transacoes_qs = transacoes_qs.filter(nome__icontains=q)
    if categoria:
        transacoes_qs = transacoes_qs.filter(categoria_id=categoria)
    if tipo:
        transacoes_qs = transacoes_qs.filter(tipo=tipo)
    if periodo and periodo != "Todos os períodos":
        try:
            mes_nome, ano = periodo.split(" ")
            meses_map = {m.lower(): i+1 for i, m in enumerate(meses_pt)}
            mes = meses_map.get(mes_nome.lower())
            ano = int(ano)
            transacoes_qs = transacoes_qs.filter(data__month=mes, data__year=ano)
        except:
            pass

    total_receitas = transacoes_qs.filter(tipo='entrada').aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')
    total_despesas = transacoes_qs.filter(tipo='saida').aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')
    saldo = total_receitas - total_despesas

    context = {
        "transacoes": transacoes_qs,
        "categorias": categorias_qs,
        "periodos": periodos,
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "saldo": saldo,
        "sem_header": True,
    }
    return render(request, "financas/transacoes.html", context)


@login_required
def categorias(request):
    return render(request, "financas/categorias.html")

@login_required
def metas_view(request):
    return render(request, "financas/metas.html")

@login_required
def criar_meta(request):
    if request.method == "POST":
        try:
            nome = request.POST.get('titulo')
            descricao = request.POST.get('descricao')
            valor_alvo = request.POST.get('valor_objetivo')
            categoria_id = request.POST.get('categoria')
            data_limite = request.POST.get('data_limite')

            categoria = Categoria.objects.get(id=categoria_id) if categoria_id else None

            Meta.objects.create(
                usuario=request.user,
                nome=nome,
                descricao=descricao,
                valor_alvo=Decimal(valor_alvo),
                data_limite=data_limite
            )
            messages.success(request, "Meta criada com sucesso!")
            return redirect('financas:metas')

        except Exception as e:
            messages.error(request, f"Ocorreu um erro ao criar a meta: {e}")
            return redirect('financas:metas')
    
    # Se não for um POST, redireciona de volta para a página de metas
    return redirect('financas:metas')

@login_required
def excluir_meta(request, meta_id):
    if request.method == "POST":
        try:
            meta = Meta.objects.get(id=meta_id, usuario=request.user)
            meta.delete()
            messages.success(request, "Meta excluída com sucesso!")
        except Meta.DoesNotExist:
            messages.error(request, "Meta não encontrada ou você não tem permissão para excluí-la.")
    return redirect('financas:metas')

@login_required
def adicionar_dinheiro(request, meta_id):
    if request.method == "POST":
        try:
            meta = Meta.objects.get(id=meta_id, usuario=request.user)
            valor_a_adicionar = request.POST.get('valor_a_adicionar')
            
            if valor_a_adicionar:
                valor_adicionado = Decimal(valor_a_adicionar)
                meta.valor_atual += valor_adicionado
                meta.save()

                messages.success(request, f"R$ {valor_adicionado} adicionado à meta {meta.nome} com sucesso!")
            
        except Meta.DoesNotExist:
            messages.error(request, "Meta não encontrada ou você não tem permissão para editá-la.")
        except Exception as e:
            messages.error(request, f"Ocorreu um erro: {e}")

    return redirect('financas:metas')

@login_required
def conexoes_bancarias(request):    
    return render(request, "financas/conexoes_bancarias.html",{
        "sem_header": True        
    })


@login_required
def nova_conexao(request):
    return render(request, "financas/nova_conexao.html",{
        "sem_header": True 
    })

@login_required
def conectar_conta(request):
    if request.method == "POST":
        banco = request.POST.get("banco")
        numero_conta = request.POST.get("numero_conta")
        agencia = request.POST.get("agencia")

        # --- Validação de Backend ---
        # 1. Verifique se os campos obrigatórios estão preenchidos
        if not banco or not numero_conta or not agencia:
            messages.error(request, "Todos os campos são obrigatórios.")
            return render(request, "financas/conectar_conta.html")
        
        # 2. Verifique o formato dos campos (exemplo)
        # O número da conta deve ter apenas números e um traço opcional
        if not re.match(r'^[0-9-]+$', numero_conta):
            messages.error(request, "O formato do número da conta é inválido.")
            return render(request, "financas/conectar_conta.html")
        
        # A agência deve ter apenas 4 ou 5 dígitos
        if not re.match(r'^[0-9]{4,5}$', agencia):
            messages.error(request, "A agência deve conter 4 ou 5 dígitos numéricos.")
            return render(request, "financas/conectar_conta.html")

        try:
            ContaBancaria.objects.create(
                usuario=request.user, 
                banco=banco, 
                numero_conta=numero_conta, 
                agencia=agencia
            )
            messages.success(request, "Conta adicionada com sucesso!")
            return redirect("financas:conexoes_bancarias")
        except Exception as e:
            messages.error(request, f"Erro ao adicionar conta: {e}")
            return render(request, "financas/conectar_conta.html")
        
    return render(request, "financas/conectar_conta.html",{
        "sem_header": True 
    })

@login_required
def conectar_cartao(request):
    if request.method == "POST":
        nome_cartao = request.POST.get("nome_cartao")
        tipo_cartao = request.POST.get("tipo_cartao") # Acessa o novo campo
        numero_cartao = request.POST.get("numero_cartao")
        validade = request.POST.get("validade") # Acessa o novo campo

        if not nome_cartao or not tipo_cartao or not numero_cartao or not validade:
            messages.error(request, "Por favor, preencha todos os campos obrigatórios.")
            return render(request, "financas/conectar_cartao.html")

        try:
            CartaoDeCredito.objects.create(
                usuario=request.user, 
                nome_cartao=nome_cartao,
                tipo=tipo_cartao,
                validade=validade,
                numero_cartao=numero_cartao
            )
            messages.success(request, "Cartão de crédito adicionado com sucesso!")
            return redirect("financas:conexoes_bancarias")
        except Exception as e:
            messages.error(request, f"Erro ao adicionar cartão: {e}")
            return render(request, "financas/conectar_cartao.html")
    
    return render(request, "financas/conectar_cartao.html",{
        "sem_header":True
    })


@login_required
def educacao_2(request):
    return render(request, "financas/educacao_2.html",{
        "sem_header": True
    })

def configuracoes(request):
    if request.method == "POST":
        if "perfil_form" in request.POST:
            perfil_form = PerfilForm(request.POST, instance=request.user)
            if perfil_form.is_valid():
                perfil_form.save()
        elif "suporte_form" in request.POST:
            suporte_form = SuporteForm(request.POST)
            if suporte_form.is_valid():
                # Aqui você pode enviar um email ou salvar no banco
                print("Assunto:", suporte_form.cleaned_data['assunto'])
                print("Mensagem:", suporte_form.cleaned_data['mensagem'])
                # redirect para evitar reenvio do form
                return redirect("configuracoes")
    else:
        perfil_form = PerfilForm(instance=request.user)
        suporte_form = SuporteForm()

    return render(request, "financas/configuracoes.html", {
        "perfil_form": perfil_form,
        "suporte_form": suporte_form,
        "sem_header": True,
    })

def inicio(request):
    planos = [
        {
            "name": "Freemium",
            "price": "Grátis",
            "description": "Para começar a organizar suas finanças",
            "features": [
                "Dashboard básico",
                "Até 3 metas financeiras",
                "Análise básica de gastos",
                "Upload de até 5 extratos por mês",
                "1 usuário (sem compartilhamento)",
                "Upload manual apenas",
                "Suporte por email"
            ],
            "popular": False,
            "cta": "Começar Grátis"
        },
        {
            "name": "Pro",
            "price": "R$ 19,90/mês",
            "description": "Controle completo das suas finanças",
            "features": [
                "Tudo do Freemium",
                "Metas ilimitadas",
                "Análises avançadas e sugestões",
                "Relatórios detalhados",
                "Categorização automática",
                "Alertas personalizados",
                "Exportação PDF/CSV",
                "Integração básica com bancos",
                "Suporte prioritário (email + chat)"
            ],
            "popular": True,
            "cta": "Assinar Pro"
        },
        {
            "name": "Premium",
            "price": "R$ 39,90/mês",
            "description": "Máximo controle + Acesso Familiar",
            "features": [
                "Tudo do Pro",
                "Até 5 usuários (Família Smart)",
                "Planejamento financeiro avançado",
                "Previsões e simulações",
                "Integração completa com bancos",
                "Consultoria financeira mensal",
                "API para integrações",
                "Permissões configuráveis",
                "Suporte telefônico"
            ],
            "popular": False,
            "cta": "Escolher Premium"
        }
    ]

    return render(request, 'financas/index.html', {"plans": planos})

def educacao(request):
    # Simulação de usuário
    user = {
        "username": "Sara",
        "plan": "freemium"  # ou "pro" / "premium"
    }
    
    is_pro = user['plan'] in ['pro', 'premium']

    basic_content = [
        {
            "title": "Como Controlar os Gastos",
            "description": "Aprenda técnicas práticas para não gastar mais do que ganha",
            "content": [
                "🎯 Regra 50-30-20: 50% necessidades, 30% desejos, 20% poupança",
                "📱 Use apps para acompanhar gastos diários",
                "🛒 Faça lista de compras e evite compras por impulso",
                "⏰ Espere 24h antes de compras não essenciais",
                "💳 Prefira débito ao crédito quando possível"
            ],
            "icon": "piggy-bank",
            "color": "blue"
        },
        {
            "title": "Criando uma Reserva de Emergência",
            "description": "Por que e como construir sua segurança financeira",
            "content": [
                "🎯 Meta: 6 meses de gastos essenciais guardados",
                "🏦 Mantenha em conta poupança ou CDB com liquidez",
                "📈 Comece com R$ 50-100 por mês",
                "🚨 Use apenas para emergências reais",
                "⚡ Reponha sempre que usar"
            ],
            "icon": "target",
            "color": "green"
        },
        {
            "title": "Planejamento Financeiro Básico",
            "description": "Primeiros passos para organizar sua vida financeira",
            "content": [
                "📊 Anote todas as receitas e despesas",
                "🎯 Defina metas financeiras claras",
                "📅 Revise seu orçamento mensalmente",
                "💰 Quite dívidas mais caras primeiro",
                "📚 Invista em educação financeira"
            ],
            "icon": "bar-chart",
            "color": "purple"
        },
        {
            "title": "Introdução aos Investimentos",
            "description": "Conceitos básicos para começar a investir",
            "content": [
                "🏦 Comece com Tesouro Direto (renda fixa)",
                "📈 Diversifique seus investimentos",
                "⏰ Invista pensando no longo prazo",
                "📚 Estude antes de investir",
                "💸 Nunca invista dinheiro que você precisa"
            ],
            "icon": "trending-up",
            "color": "orange"
        }
    ]

    pro_content = [
        {
            "title": "Análise Avançada de Mercado",
            "description": "Entenda indicadores econômicos e como afetam seus investimentos",
            "topics": ["Taxa Selic e seus impactos", "Inflação e poder de compra", "Índices de bolsa", "Análise fundamentalista"],
            "icon": "bar-chart"
        },
        {
            "title": "Estratégias de Investimento",
            "description": "Técnicas avançadas para maximizar seus rendimentos",
            "topics": ["Diversificação de carteira", "Rebalanceamento", "Dollar Cost Averaging", "Análise de risco"],
            "icon": "trending-up"
        },
        {
            "title": "Planejamento Tributário",
            "description": "Como otimizar seus impostos legalmente",
            "topics": ["Imposto de Renda em investimentos", "Regime de tributação", "Dedução de IR", "Previdência privada"],
            "icon": "calculator"
        },
        {
            "title": "Consultoria Personalizada",
            "description": "Análises específicas para seu perfil financeiro",
            "topics": ["Relatórios detalhados", "Recomendações personalizadas", "Simulações de cenários", "Acompanhamento mensal"],
            "icon": "file-text"
        }
    ]

    context = {
        "user": user,
        "is_pro": is_pro,
        "basic_content": basic_content,
        "pro_content": pro_content,
    }

    return render(request, "financas/educacao.html", context)

