from django.utils import timezone
from financas.models import Transacao
from django.db.models import Sum
from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')   # pega do formulário
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)  # aqui usamos o backend
        if user is not None:
            messages.success(request, "Login realizado com sucesso!")
            login(request, user)
        return redirect('financas:dashboard')
    
    return render(request, 'financas/index.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Logout realizado com sucesso!")
    return redirect("index")

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Esse usuário já existe.")
            return redirect("register")

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, "Cadastro realizado com sucesso!")
        return redirect("index")

    return render(request, "financas/register.html")

@login_required
def dashboard(request):
    financial_data = {
        "balance": 2500.00,   # saldo atual
        "income": 4000.00,
        "expenses": 1500.00,
        "savings": 800.00,
        "categories": [
            {"name": "Alimentação", "percentage": 40, "color": "#f87171"},
            {"name": "Transporte", "percentage": 25, "color": "#60a5fa"},
            {"name": "Lazer", "percentage": 20, "color": "#fbbf24"},
            {"name": "Educação", "percentage": 15, "color": "#34d399"},
        ],
        "recentTransactions": [
            {"description": "Supermercado", "category": "Alimentação", "date": "2025-08-09", "amount": -150.00},
            {"description": "Salário", "category": "Receita", "date": "2025-08-10", "amount": 4000.00},
            {"description": "Uber", "category": "Transporte", "date": "2025-08-11", "amount": -45.00},
            {"description": "Cinema", "category": "Lazer", "date": "2025-08-12", "amount": -60.00},
        ]
    }

    # Ordenar transações
    transactions = sorted(financial_data["recentTransactions"], key=lambda x: x["date"])

    # 👉 Saldo inicial customizado (por exemplo: mês passado)
    saldo_inicial = 1000.00  

    saldo = saldo_inicial
    saldo_evolucao = [saldo]  # já começa com o inicial
    labels = ["Saldo inicial"]

    for tx in transactions:
        saldo += tx["amount"]
        saldo_evolucao.append(round(saldo, 2))
        labels.append(tx["date"])

    financial_data["saldo_inicial"] = saldo_inicial
    financial_data["saldo_evolucao"] = saldo_evolucao
    financial_data["saldo_labels"] = labels

    context = {"financial_data": financial_data}
    return render(request, "financas/dashboard.html", context)

@login_required
def transacoes(request):
    return render(request, "financas/transacoes.html")

@login_required
def categorias(request):
    return render(request, "financas/categorias.html")

@login_required
def metas(request):
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

