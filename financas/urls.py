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
    path("educacao/", views.educacao, name="educacao"),
    path("configuracoes/", views.configuracoes, name="configuracoes"),

]

