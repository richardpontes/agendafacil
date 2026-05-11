from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import Usuario, Prestador, Servico, Agendamento, Bloqueio


def index(request):
    return render(request, 'core/index.html')


def cadastro(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        telefone = request.POST.get('telefone')
        tipo = request.POST.get('tipo')

        if senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'core/cadastro.html')

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Este e-mail já está cadastrado.')
            return render(request, 'core/cadastro.html')

        usuario = Usuario.objects.create(
            nome=nome,
            email=email,
            senha=make_password(senha),
            telefone=telefone,
            tipo=tipo,
        )

        if tipo == 'prestador':
            nome_negocio = request.POST.get('nome_negocio')
            cep = request.POST.get('cep')
            logradouro = request.POST.get('logradouro')
            numero = request.POST.get('numero')
            complemento = request.POST.get('complemento')
            bairro = request.POST.get('bairro')
            cidade = request.POST.get('cidade')
            estado = request.POST.get('estado')
            horario_inicio = request.POST.get('horario_inicio')
            horario_fim = request.POST.get('horario_fim')
            # dias_funcionamento = request.POST.get('dias_funcionamento')
            dia_inicio = request.POST.get('dia_inicio')
            dia_fim = request.POST.get('dia_fim')

            Prestador.objects.create(
                usuario=usuario,
                nome_negocio=nome_negocio,
                cep=cep,
                logradouro=logradouro,
                numero=numero,
                complemento=complemento,
                bairro=bairro,
                cidade=cidade,
                estado=estado,
                horario_inicio=horario_inicio,
                horario_fim=horario_fim,
                # dias_funcionamento=dias_funcionamento,
                dia_inicio=dia_inicio,
                dia_fim=dia_fim,
            )

        messages.success(request, 'Cadastro realizado com sucesso! Faça login para continuar.')
        return redirect('login')

    return render(request, 'core/cadastro.html')


def login_view(request):
    email_salvo = request.COOKIES.get('email_lembrado', '')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        lembrar = request.POST.get('lembrar')

        try:
            usuario = Usuario.objects.get(email=email)
            if check_password(senha, usuario.senha):
                request.session['usuario_id'] = usuario.id
                request.session['usuario_nome'] = usuario.nome
                request.session['usuario_tipo'] = usuario.tipo

                if usuario.tipo == 'cliente':
                    response = redirect('dashboard_cliente')
                else:
                    response = redirect('dashboard_prestador')
                
                if lembrar:
                    response.set_cookie('email_lembrado', email, max_age=30*24*60*60)
                else:
                    response.delete_cookie('email_lembrado')
                return response
            else:
                messages.error(request, 'E-mail ou senha incorretos.')
        except Usuario.DoesNotExist:
            messages.error(request, 'E-mail ou senha incorretos.')

    return render(request, 'core/login.html', {'email_salvo': email_salvo})


def logout_view(request):
    request.session.flush()
    return redirect('login')


def dashboard_cliente(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario = Usuario.objects.get(id=request.session.get('usuario_id'))
    hoje = date.today()

    agendamentos_futuros = Agendamento.objects.filter(
        cliente=usuario,
        data_hora__date__gte=hoje,
        status__in=['pendente', 'confirmado']
    ).count()

    agendamentos_realizados = Agendamento.objects.filter(
        cliente=usuario,
        data_hora__date__lt=hoje,
        status='confirmado'
    ).count()

    aguardando_confirmacao = Agendamento.objects.filter(
        cliente=usuario,
        status='pendente',
        data_hora__date__gte=hoje
    ).count()

    proximos_agendamentos = Agendamento.objects.filter(
        cliente=usuario,
        data_hora__date__gte=hoje,
        status__in=['pendente', 'confirmado']
    ).order_by('data_hora')[:5]

    context = {
        'nome': request.session.get('usuario_nome'),
        'agendamentos_futuros': agendamentos_futuros,
        'agendamentos_realizados': agendamentos_realizados,
        'aguardando_confirmacao': aguardando_confirmacao,
        'proximos_agendamentos': proximos_agendamentos,
    }
    return render(request, 'core/dashboard_cliente.html', context)

def dashboard_prestador(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    if request.session.get('usuario_tipo') != 'prestador':
        return redirect('dashboard_cliente')

    try:
        usuario = Usuario.objects.get(id=request.session.get('usuario_id'))
        prestador = Prestador.objects.get(usuario=usuario)
    except (Usuario.DoesNotExist, Prestador.DoesNotExist):
        return redirect('login')

    hoje = date.today()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    fim_semana = inicio_semana + timedelta(days=6)

    agendamentos_hoje = Agendamento.objects.filter(
        prestador=prestador,
        data_hora__date=hoje,
    ).exclude(status='cancelado').count()

    pendentes_confirmacao = Agendamento.objects.filter(
        prestador=prestador,
        status='pendente',
        data_hora__date__gte=hoje,
    ).count()

    clientes_semana = Agendamento.objects.filter(
        prestador=prestador,
        data_hora__date__range=[inicio_semana, fim_semana],
        status='confirmado',
    ).values('cliente').distinct().count()

    servicos_cadastrados = Servico.objects.filter(prestador=prestador).count()

    agendamentos_hoje_lista = Agendamento.objects.filter(
        prestador=prestador,
        data_hora__date=hoje,
    ).exclude(status='cancelado').order_by('data_hora')

    context = {
        'nome': request.session.get('usuario_nome'),
        'prestador': prestador,
        'agendamentos_hoje': agendamentos_hoje,
        'pendentes_confirmacao': pendentes_confirmacao,
        'clientes_semana': clientes_semana,
        'servicos_cadastrados': servicos_cadastrados,
        'agendamentos_hoje_lista': agendamentos_hoje_lista,
        'hoje': hoje,
    }
    return render(request, 'core/dashboard_prestador.html', context)

def listar_servicos(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    if request.session.get('usuario_tipo') != 'prestador':
        return redirect('dashboard_cliente')

    usuario = Usuario.objects.get(id=request.session.get('usuario_id'))
    prestador = Prestador.objects.get(usuario=usuario)
    servicos = Servico.objects.filter(prestador=prestador)

    context = {
        'servicos': servicos,
        'nome': request.session.get('usuario_nome'),
    }
    return render(request, 'core/servicos.html', context)


def novo_servico(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    if request.session.get('usuario_tipo') != 'prestador':
        return redirect('dashboard_cliente')

    if request.method == 'POST':
        usuario = Usuario.objects.get(id=request.session.get('usuario_id'))
        prestador = Prestador.objects.get(usuario=usuario)

        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        duracao = request.POST.get('duracao')
        preco = request.POST.get('preco')
        profissional = request.POST.get('profissional')

        Servico.objects.create(
            prestador=prestador,
            nome=nome,
            descricao=descricao,
            duracao=duracao,
            preco=preco,
            profissional=profissional,
        )
        messages.success(request, 'Serviço cadastrado com sucesso!')
        return redirect('listar_servicos')

    return render(request, 'core/novo_servico.html', {'nome': request.session.get('usuario_nome')})


def editar_servico(request, id):
    if not request.session.get('usuario_id'):
        return redirect('login')
    if request.session.get('usuario_tipo') != 'prestador':
        return redirect('dashboard_cliente')

    servico = Servico.objects.get(id=id)

    if request.method == 'POST':
        servico.nome = request.POST.get('nome')
        servico.descricao = request.POST.get('descricao')
        servico.duracao = request.POST.get('duracao')
        servico.preco = request.POST.get('preco').replace(',', '.')
        servico.ativo = request.POST.get('ativo') == 'on'
        servico.profissional = request.POST.get('profissional')
        servico.save()
        messages.success(request, 'Serviço atualizado com sucesso!')
        return redirect('listar_servicos')

    context = {
        'servico': servico,
        'nome': request.session.get('usuario_nome'),
    }
    return render(request, 'core/editar_servico.html', context)


def excluir_servico(request, id):
    if not request.session.get('usuario_id'):
        return redirect('login')
    if request.session.get('usuario_tipo') != 'prestador':
        return redirect('dashboard_cliente')

    servico = Servico.objects.get(id=id)
    servico.delete()
    messages.success(request, 'Serviço excluído com sucesso!')
    return redirect('listar_servicos')

def listar_prestadores(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    if request.session.get('usuario_tipo') != 'cliente':
        return redirect('dashboard_prestador')

    prestadores = Prestador.objects.filter(
        servico__ativo=True
    ).distinct()

    context = {
        'prestadores': prestadores,
        'nome': request.session.get('usuario_nome'),
    }
    return render(request, 'core/prestadores.html', context)

def selecionar_servico(request, prestador_id):
    if not request.session.get('usuario_id'):
        return redirect('login')
    if request.session.get('usuario_tipo') != 'cliente':
        return redirect('dashboard_prestador')

    prestador = Prestador.objects.get(id=prestador_id)
    servicos = Servico.objects.filter(prestador=prestador, ativo=True)

    context = {
        'prestador': prestador,
        'servicos': servicos,
        'nome': request.session.get('usuario_nome'),
    }
    return render(request, 'core/selecionar_servico.html', context)

from datetime import date, datetime, timedelta

def selecionar_data(request, prestador_id, servico_id):
    if not request.session.get('usuario_id'):
        return redirect('login')
    if request.session.get('usuario_tipo') != 'cliente':
        return redirect('dashboard_prestador')

    prestador = Prestador.objects.get(id=prestador_id)
    servico = Servico.objects.get(id=servico_id)

    # Gera os próximos 30 dias
    hoje = date.today()
    # datas = [hoje + timedelta(days=i) for i in range(1, 31)]

    context = {
        'prestador': prestador,
        'servico': servico,
        # 'datas': datas,
        'nome': request.session.get('usuario_nome'),
    }
    return render(request, 'core/selecionar_data.html', context)

def selecionar_horario(request, prestador_id, servico_id, data_str):
    if not request.session.get('usuario_id'):
        return redirect('login')
    if request.session.get('usuario_tipo') != 'cliente':
        return redirect('dashboard_prestador')

    prestador = Prestador.objects.get(id=prestador_id)
    servico = Servico.objects.get(id=servico_id)
    data = date.fromisoformat(data_str)

    import pytz
    tz = pytz.timezone('America/Sao_Paulo')
    hora_inicio = tz.localize(datetime.combine(data, prestador.horario_inicio))
    hora_fim = tz.localize(datetime.combine(data, prestador.horario_fim))
    slot_base = timedelta(minutes=15)
    duracao = timedelta(minutes=servico.duracao)
    slots_necessarios = servico.duracao // 15

    # Busca todos os agendamentos da profissional naquele dia
    agendamentos_profissional = Agendamento.objects.filter(
        prestador=prestador,
        servico__profissional=servico.profissional,
        data_hora__date=data,
        status__in=['pendente', 'confirmado']
    ).select_related('servico')

    # Busca bloqueios da profissional que interceptam o dia
    bloqueios_profissional = Bloqueio.objects.filter(
        prestador=prestador,
        profissional=servico.profissional,
        data_hora_inicio__date__lte=data,
        data_hora_fim__date__gte=data,
    )

    # Monta conjunto de slots de 15 min ocupados
    slots_ocupados = set()

    for ag in agendamentos_profissional:
        inicio_ag = ag.data_hora
        slots_ag = ag.servico.duracao // 15
        for i in range(slots_ag):
            slots_ocupados.add(inicio_ag + timedelta(minutes=15 * i))

    for bloqueio in bloqueios_profissional:
        slot_atual = bloqueio.data_hora_inicio
        while slot_atual < bloqueio.data_hora_fim:
            slots_ocupados.add(slot_atual)
            slot_atual += timedelta(minutes=15)

    # Gera slots disponíveis
    slots = []
    hora_atual = hora_inicio
    while hora_atual + duracao <= hora_fim:
        # Verifica se todos os slots necessários estão livres
        livre = all(
            hora_atual + timedelta(minutes=15 * i) not in slots_ocupados
            for i in range(slots_necessarios)
        )
        if livre:
            slots.append(hora_atual.time())
        hora_atual += slot_base

    context = {
        'prestador': prestador,
        'servico': servico,
        'data': data,
        'slots': slots,
        'nome': request.session.get('usuario_nome'),
    }
    return render(request, 'core/selecionar_horario.html', context)

def confirmar_agendamento(request, prestador_id, servico_id, data_str, horario_str):
    if not request.session.get('usuario_id'):
        return redirect('login')
    if request.session.get('usuario_tipo') != 'cliente':
        return redirect('dashboard_prestador')

    prestador = Prestador.objects.get(id=prestador_id)
    servico = Servico.objects.get(id=servico_id)
    data = date.fromisoformat(data_str)
    horario = datetime.strptime(horario_str, '%H:%M').time()
    data_hora = datetime.combine(data, horario)

    if request.method == 'POST':
        usuario = Usuario.objects.get(id=request.session.get('usuario_id'))
        Agendamento.objects.create(
            cliente=usuario,
            prestador=prestador,
            servico=servico,
            data_hora=data_hora,
            status='pendente',
        )
        messages.success(request, 'Agendamento realizado com sucesso!')
        return redirect('meus_agendamentos')

    context = {
        'prestador': prestador,
        'servico': servico,
        'data': data,
        'horario': horario,
        'data_hora': data_hora,
        'nome': request.session.get('usuario_nome'),
    }
    return render(request, 'core/confirmar_agendamento.html', context)

def meus_agendamentos(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    if request.session.get('usuario_tipo') != 'cliente':
        return redirect('dashboard_prestador')

    usuario = Usuario.objects.get(id=request.session.get('usuario_id'))
    hoje = date.today()

    proximos = Agendamento.objects.filter(
        cliente=usuario,
        data_hora__date__gte=hoje,
        status__in=['pendente', 'confirmado']
    ).order_by('data_hora')

    realizados = Agendamento.objects.filter(
        cliente=usuario,
        data_hora__date__lt=hoje,
        status='confirmado'
    ).order_by('-data_hora')

    cancelados = Agendamento.objects.filter(
        cliente=usuario,
        status='cancelado'
    ).order_by('-data_hora')

    context = {
        'proximos': proximos,
        'realizados': realizados,
        'cancelados': cancelados,
        'nome': request.session.get('usuario_nome'),
    }
    return render(request, 'core/meus_agendamentos.html', context)

def cancelar_agendamento(request, agendamento_id):
    if not request.session.get('usuario_id'):
        return redirect('login')
    if request.session.get('usuario_tipo') != 'cliente':
        return redirect('dashboard_prestador')

    agendamento = Agendamento.objects.get(id=agendamento_id)
    agendamento.status = 'cancelado'
    agendamento.save()
    messages.success(request, 'Agendamento cancelado com sucesso!')
    return redirect('meus_agendamentos')

def listar_bloqueios(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    if request.session.get('usuario_tipo') != 'prestador':
        return redirect('dashboard_cliente')

    usuario = Usuario.objects.get(id=request.session.get('usuario_id'))
    prestador = Prestador.objects.get(usuario=usuario)
    bloqueios = Bloqueio.objects.filter(prestador=prestador).order_by('data_hora_inicio')

    context = {
        'bloqueios': bloqueios,
        'nome': request.session.get('usuario_nome'),
        'prestador': prestador,
    }
    return render(request, 'core/bloqueios.html', context)


def novo_bloqueio(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    if request.session.get('usuario_tipo') != 'prestador':
        return redirect('dashboard_cliente')

    usuario = Usuario.objects.get(id=request.session.get('usuario_id'))
    prestador = Prestador.objects.get(usuario=usuario)

    # Lista de profissionais únicas do prestador
    profissionais = Servico.objects.filter(
        prestador=prestador
    ).values_list('profissional', flat=True).distinct()

    if request.method == 'POST':
        profissional = request.POST.get('profissional')
        data_hora_inicio = request.POST.get('data_hora_inicio')
        data_hora_fim = request.POST.get('data_hora_fim')
        motivo = request.POST.get('motivo')

        import pytz
        tz = pytz.timezone('America/Sao_Paulo')
        data_hora_inicio_dt = tz.localize(datetime.fromisoformat(data_hora_inicio))
        data_hora_fim_dt = tz.localize(datetime.fromisoformat(data_hora_fim))

        # Verifica se há agendamentos conflitantes
        agendamentos_conflito = Agendamento.objects.filter(
            prestador=prestador,
            servico__profissional=profissional,
            status__in=['pendente', 'confirmado'],
        ).select_related('servico')

        conflito = any(
            ag.data_hora < data_hora_fim_dt and
            ag.data_hora + timedelta(minutes=ag.servico.duracao) > data_hora_inicio_dt
            for ag in agendamentos_conflito
        )

        if conflito:
            messages.error(request, 'Existe um agendamento nesse período para essa profissional. Bloqueio não cadastrado.')
            context = {
                'nome': request.session.get('usuario_nome'),
                'prestador': prestador,
                'profissionais': profissionais,
                'profissional_selecionado': profissional,
                'data_hora_inicio': data_hora_inicio,
                'data_hora_fim': data_hora_fim,
                'motivo': motivo,
            }
            return render(request, 'core/novo_bloqueio.html', context)

        Bloqueio.objects.create(
            prestador=prestador,
            profissional=profissional,
            data_hora_inicio=data_hora_inicio,
            data_hora_fim=data_hora_fim,
            motivo=motivo,
        )
        messages.success(request, 'Bloqueio cadastrado com sucesso!')
        return redirect('listar_bloqueios')

    context = {
        'nome': request.session.get('usuario_nome'),
        'prestador': prestador,
        'profissionais': profissionais,
    }
    return render(request, 'core/novo_bloqueio.html', context)


def excluir_bloqueio(request, bloqueio_id):
    if not request.session.get('usuario_id'):
        return redirect('login')
    if request.session.get('usuario_tipo') != 'prestador':
        return redirect('dashboard_cliente')

    bloqueio = Bloqueio.objects.get(id=bloqueio_id)
    bloqueio.delete()
    messages.success(request, 'Bloqueio removido com sucesso!')
    return redirect('listar_bloqueios')

def agenda_prestador(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    if request.session.get('usuario_tipo') != 'prestador':
        return redirect('dashboard_cliente')

    usuario = Usuario.objects.get(id=request.session.get('usuario_id'))
    prestador = Prestador.objects.get(usuario=usuario)

    data_filtro = request.GET.get('data', str(date.today()))
    data = date.fromisoformat(data_filtro)

    agendamentos = Agendamento.objects.filter(
        prestador=prestador,
        data_hora__date=data,
    ).exclude(status='cancelado').order_by('data_hora')

    context = {
        'prestador': prestador,
        'agendamentos': agendamentos,
        'data': data,
        'nome': request.session.get('usuario_nome'),
    }
    return render(request, 'core/agenda_prestador.html', context)


def confirmar_agendamento_prestador(request, agendamento_id):
    if not request.session.get('usuario_id'):
        return redirect('login')
    if request.session.get('usuario_tipo') != 'prestador':
        return redirect('dashboard_cliente')

    agendamento = Agendamento.objects.get(id=agendamento_id)
    agendamento.status = 'confirmado'
    agendamento.save()
    messages.success(request, 'Agendamento confirmado com sucesso!')
    return redirect('agenda_prestador')


def cancelar_agendamento_prestador(request, agendamento_id):
    if not request.session.get('usuario_id'):
        return redirect('login')
    if request.session.get('usuario_tipo') != 'prestador':
        return redirect('dashboard_cliente')

    agendamento = Agendamento.objects.get(id=agendamento_id)
    agendamento.status = 'cancelado'
    agendamento.save()
    messages.success(request, 'Agendamento cancelado com sucesso!')
    return redirect('agenda_prestador')