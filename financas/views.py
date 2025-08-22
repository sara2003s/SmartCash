from financas.models import Transacao, Meta, Profile
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Meta

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
    entradas = Transacao.objects.filter(usuario=request.user, tipo='entrada').aggregate(Sum('valor'))['valor__sum'] or 0
    saidas = Transacao.objects.filter(usuario=request.user, tipo='saida').aggregate(Sum('valor'))['valor__sum'] or 0
    saldo = entradas - saidas
   
    try:
        meta = Meta.objects.filter(usuario=request.user).first()
        if meta:
            meta_valor = meta.valor_atual
            meta_total = meta.valor_alvo
        else:
            meta_valor = 1000
            meta_total = 2000
    except Exception:
        meta_valor = 1000
        meta_total = 2000
        
    try:
        gastos_por_categoria = Transacao.objects.filter(
            usuario=request.user, 
            tipo='saida'
        ).values('categoria__nome', 'categoria__cor').annotate(
            total_gasto=Sum('valor')
        ).order_by('-total_gasto')

        total_gastos = sum(item['total_gasto'] for item in gastos_por_categoria)
        
        gastos_detalhados = []
        for item in gastos_por_categoria:
            porcentagem = (item['total_gasto'] / total_gastos) * 100 if total_gastos > 0 else 0
            gastos_detalhados.append({
                'nome': item['categoria__nome'],
                'cor': item['categoria__cor'], 
                'valor': item['total_gasto'],
                'porcentagem': porcentagem
            })
            
        expenses_labels = [item['categoria__nome'] for item in gastos_por_categoria]
        expenses_data = [item['total_gasto'] for item in gastos_por_categoria]

    except Exception as e:
        print(f"Erro ao buscar dados de gastos: {e}")
        expenses_labels = ['Alimentação', 'Transporte', 'Lazer', 'Saúde', 'Outros']
        expenses_data = [1200.50, 850.00, 650.00, 350.00, 209.00]
        gastos_detalhados = [
            {'nome': 'Alimentação', 'cor': '#F87171', 'valor': 1200.50, 'porcentagem': 37},
            {'nome': 'Transporte', 'cor': '#60A5FA', 'valor': 850.00, 'porcentagem': 26},
            {'nome': 'Lazer', 'cor': '#FBBE24', 'valor': 650.00, 'porcentagem': 20},
            {'nome': 'Saúde', 'cor': '#34D399', 'valor': 350.00, 'porcentagem': 11},
            {'nome': 'Outros', 'cor': '#8B5CF6', 'valor': 209.00, 'porcentagem': 6},
        ]

    try:
        transacoes_recentes = Transacao.objects.filter(usuario=request.user).order_by('-data')[:6]
    except Exception as e:
        print(f"Erro ao buscar transações recentes: {e}")
        transacoes_recentes = [
        ]

    context = {
        'saldo': f"{saldo:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'), 
        'entradas': f"{entradas:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
        'saidas': f"{saidas:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
        'meta': f"{meta_valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
        'meta_total': f"{meta_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
        'expenses_labels': expenses_labels,
        'expenses_data': expenses_data,
        'gastos_detalhados': gastos_detalhados, # Use a lista de fallback no caso de erro
        'transacoes_recentes': transacoes_recentes,
    }
    return render(request, "financas/dashboard.html", context)

@login_required
def transacoes(request):
    return render(request, "financas/transacoes.html")

@login_required
def categorias(request):
    return render(request, "financas/categorias.html")

@login_required
def metas_view(request):
    return render(request, "financas/metas.html")

@login_required
def conexoes_bancarias(request):
    return render(request, "financas/conexoes_bancarias.html")

@login_required
def configuracoes(request):
    return render(request, "financas/configuracoes.html")

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

