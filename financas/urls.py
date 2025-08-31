from django.urls import path
from . import views 


app_name = 'financas'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('educacao/', views.educacao, name='educacao'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path('register/', views.register_view, name='register'),
    path("transacoes/", views.transacoes, name="transacoes"),
    path("metas/", views.metas, name="metas"),
    path("conexoes_bancarias/", views.conexoes_bancarias, name="conexoes_bancarias"),
    path("educacao_2/", views.educacao_2, name="educacao_2"),
    path("configuracoes/", views.configuracoes, name="configuracoes"),
    path('configuracao-inicial/', views.configuracao_inicial, name='configuracao_inicial'),
    path('conexoes/nova/', views.nova_conexao, name='nova_conexao'),
    path('conectar-conta/', views.conectar_conta, name='conectar_conta' ),
    path('conectar-cartao/', views.conectar_cartao, name='conectar_cartao'),
    path('metas/criar/', views.criar_meta, name='criar_meta'),
    path('metas/excluir/<int:meta_id>/', views.excluir_meta, name='excluir_meta'),
    path('metas/adicionar-dinheiro/<int:meta_id>/', views.adicionar_dinheiro, name='adicionar_dinheiro'),
    path('configuracoes/exportar-dados/', views.exportar_dados, name='exportar_dados'),
    path('aulas/', views.pagina_aulas, name='aulas'),
]

