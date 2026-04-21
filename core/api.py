from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Prestador, Servico, Agendamento
from .serializers import ServicoSerializer, PrestadorSerializer, AgendamentoSerializer
from datetime import date, datetime, timedelta
import pytz


@api_view(['GET'])
def api_prestadores(request):
    prestadores = Prestador.objects.filter(servico__ativo=True).distinct()
    serializer = PrestadorSerializer(prestadores, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def api_servicos(request, prestador_id):
    servicos = Servico.objects.filter(prestador_id=prestador_id, ativo=True)
    serializer = ServicoSerializer(servicos, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def api_horarios(request, prestador_id, servico_id, data_str):
    try:
        prestador = Prestador.objects.get(id=prestador_id)
        servico = Servico.objects.get(id=servico_id)
        data = date.fromisoformat(data_str)

        tz = pytz.timezone('America/Sao_Paulo')
        hora_atual = tz.localize(datetime.combine(data, prestador.horario_inicio))
        hora_fim = tz.localize(datetime.combine(data, prestador.horario_fim))
        duracao = timedelta(minutes=servico.duracao)

        slots = []
        while hora_atual + duracao <= hora_fim:
            ocupado = Agendamento.objects.filter(
                prestador=prestador,
                data_hora=hora_atual,
                status__in=['pendente', 'confirmado']
            ).exists()

            if not ocupado:
                slots.append(hora_atual.strftime('%H:%M'))
            hora_atual += duracao

        return Response({
            'prestador': prestador.nome_negocio,
            'servico': servico.nome,
            'duracao': servico.duracao,
            'data': data_str,
            'horarios_disponiveis': slots
        })

    except (Prestador.DoesNotExist, Servico.DoesNotExist):
        return Response({'erro': 'Prestador ou serviço não encontrado.'}, status=status.HTTP_404_NOT_FOUND)