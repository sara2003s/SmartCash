from django.urls import path
from . import views 

app_name = 'financas'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('educacao/', views.educacao, name='educacao'),
    path('dashboard/', views.dashboard, name='dashboard'),
]

