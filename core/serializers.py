from rest_framework import serializers
from .models import Agendamento, Servico, Prestador


class ServicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servico
        fields = ['id', 'nome', 'descricao', 'duracao', 'preco', 'ativo']


class PrestadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prestador
        fields = ['id', 'nome_negocio', 'bairro', 'cidade', 'horario_inicio', 'horario_fim', 'dia_inicio', 'dia_fim']


class AgendamentoSerializer(serializers.ModelSerializer):
    servico = ServicoSerializer(read_only=True)
    prestador = PrestadorSerializer(read_only=True)

    class Meta:
        model = Agendamento
        fields = ['id', 'servico', 'prestador', 'data_hora', 'status', 'criado_em']