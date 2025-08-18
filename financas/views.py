from django.utils import timezone
from .models import Transacao
from django.db.models import Sum
from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from usuarios.forms import FormularioLogin, RegistroForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    hoje = timezone.now()

    # ---- Gráfico de Barras (Evolução Financeira) ----
    meses = []
    receitas = []
    gastos = []

    for i in range(6, 0, -1):  # últimos 6 meses
        mes = (hoje.month - i) % 12 or 12
        ano = hoje.year if hoje.month - i > 0 else hoje.year - 1
        meses.append(f"{mes:02d}/{ano}")

        receita_mes = (
            Transacao.objects.filter(tipo="receita", data__month=mes, data__year=ano)
            .aggregate(total=Sum("valor"))["total"] or 0
        )
        gasto_mes = (
            Transacao.objects.filter(tipo="gasto", data__month=mes, data__year=ano)
            .aggregate(total=Sum("valor"))["total"] or 0
        )

        receitas.append(float(receita_mes))
        gastos.append(float(gasto_mes))

    # ---- Gráfico de Pizza (Distribuição de Gastos por Categoria) ----
    gastos_categoria = (
        Transacao.objects.filter(tipo="gasto", data__month=hoje.month)
        .values("categoria")
        .annotate(total=Sum("valor"))
        .order_by("-total")
    )

    categorias = [g["categoria"] for g in gastos_categoria]
    valores = [float(g["total"]) for g in gastos_categoria]

    # ---- Recomendações Inteligentes (exemplo simples) ----
    recomendacoes = []
    if valores:
        maior_categoria = categorias[0]
        maior_valor = valores[0]
        recomendacoes.append({
            "tipo": "alerta",
            "titulo": f"Atenção aos gastos com {maior_categoria}",
            "descricao": f"Esta categoria representa {round(maior_valor / sum(valores) * 100, 1)}% dos seus gastos."
        })

    recomendacoes.append({
        "tipo": "investimento",
        "titulo": "Potencial de investimento identificado",
        "descricao": "Com saldo disponível você poderia investir em CDB (~110% CDI)."
    })

    recomendacoes.append({
        "tipo": "reserva",
        "titulo": "Construa sua reserva de emergência",
        "descricao": "Guarde pelo menos 6 meses de gastos como segurança."
    })

    context = {
        # barras
        "meses": meses,
        "receitas": receitas,
        "gastos": gastos,
        # pizza
        "categorias": categorias,
        "valores": valores,
        # recomendações
        "recomendacoes": recomendacoes,
    }
    return render(request, "financas/dashboard.html", context)

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

def registrar_usuario(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")  # redireciona pro login depois do cadastro
    else:
        form = RegistroForm()
    return render(request, "register.html", {"form": form})

def login_usuario(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Usuário ou senha inválidos.")

    return render(request, "usuarios/login.html")

def logout_usuario(request):
    logout(request)
    return redirect('usuarios:login')