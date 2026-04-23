from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import Usuario, Prestador, Servico, Agendamento


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

    context = {
        'nome': request.session.get('usuario_nome'),
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

    context = {
        'nome': request.session.get('usuario_nome'),
        'prestador': prestador,
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

        Servico.objects.create(
            prestador=prestador,
            nome=nome,
            descricao=descricao,
            duracao=duracao,
            preco=preco,
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
    datas = [hoje + timedelta(days=i) for i in range(1, 31)]

    context = {
        'prestador': prestador,
        'servico': servico,
        'datas': datas,
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

    # Gera slots de horário baseado no horário do prestador
    slots = []
    import pytz
    tz = pytz.timezone('America/Sao_Paulo')
    hora_atual = tz.localize(datetime.combine(data, prestador.horario_inicio))
    hora_fim = tz.localize(datetime.combine(data, prestador.horario_fim))
    duracao = timedelta(minutes=servico.duracao)

    while hora_atual + duracao <= hora_fim:
        # Verifica se já existe agendamento nesse horário
        ocupado = Agendamento.objects.filter(
            prestador=prestador,
            data_hora=hora_atual,
            status__in=['pendente', 'confirmado']
        ).exists()

        if not ocupado:
            slots.append(hora_atual.time())
        hora_atual += duracao

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
    agendamentos = Agendamento.objects.filter(
        cliente=usuario
    ).order_by('-data_hora')

    context = {
        'agendamentos': agendamentos,
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