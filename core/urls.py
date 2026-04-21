from django.urls import path
from . import views, api

urlpatterns = [
    path('', views.index, name='index'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/cliente/', views.dashboard_cliente, name='dashboard_cliente'),
    path('dashboard/prestador/', views.dashboard_prestador, name='dashboard_prestador'),
    path('servicos/', views.listar_servicos, name='listar_servicos'),
    path('servicos/novo/', views.novo_servico, name='novo_servico'),
    path('servicos/editar/<int:id>/', views.editar_servico, name='editar_servico'),
    path('servicos/excluir/<int:id>/', views.excluir_servico, name='excluir_servico'),
    path('agendar/', views.listar_prestadores, name='listar_prestadores'),
    path('agendar/<int:prestador_id>/', views.selecionar_servico, name='selecionar_servico'),
    path('agendar/<int:prestador_id>/<int:servico_id>/', views.selecionar_data, name='selecionar_data'),
    path('agendar/<int:prestador_id>/<int:servico_id>/<str:data_str>/', views.selecionar_horario, name='selecionar_horario'),
    path('agendar/<int:prestador_id>/<int:servico_id>/<str:data_str>/<str:horario_str>/', views.confirmar_agendamento, name='confirmar_agendamento'),
    path('meus-agendamentos/', views.meus_agendamentos, name='meus_agendamentos'),
    path('meus-agendamentos/cancelar/<int:agendamento_id>/', views.cancelar_agendamento, name='cancelar_agendamento'),
    path('api/prestadores/', api.api_prestadores, name='api_prestadores'),
    path('api/servicos/<int:prestador_id>/', api.api_servicos, name='api_servicos'),
    path('api/horarios/<int:prestador_id>/<int:servico_id>/<str:data_str>/', api.api_horarios, name='api_horarios'),
]