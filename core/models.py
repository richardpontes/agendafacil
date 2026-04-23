from django.db import models


class Usuario(models.Model):
    TIPO_CHOICES = [
        ('cliente', 'Cliente'),
        ('prestador', 'Prestador'),
    ]
    nome = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'usuario'


class Prestador(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nome_negocio = models.CharField(max_length=200)
    cep = models.CharField(max_length=9, blank=True, null=True)
    logradouro = models.CharField(max_length=200, blank=True, null=True)
    numero = models.CharField(max_length=20, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()
    # dias_funcionamento = models.CharField(max_length=50, blank=True, null=True)
    DIAS_CHOICES = [
        ('Segunda', 'Segunda'),
        ('Terça', 'Terça'),
        ('Quarta', 'Quarta'),
        ('Quinta', 'Quinta'),
        ('Sexta', 'Sexta'),
        ('Sábado', 'Sábado'),
    (   'Domingo', 'Domingo'),
    ]
    dia_inicio = models.CharField(max_length=10, choices=DIAS_CHOICES, blank=True, null=True)
    dia_fim = models.CharField(max_length=10, choices=DIAS_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.nome_negocio

    class Meta:
        db_table = 'prestador'


class Servico(models.Model):
    prestador = models.ForeignKey(Prestador, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    duracao = models.IntegerField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'servico'


class Agendamento(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
    ]
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='agendamentos_cliente')
    prestador = models.ForeignKey(Prestador, on_delete=models.CASCADE, related_name='agendamentos_prestador')
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    data_hora = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.cliente} - {self.servico} - {self.data_hora}'

    class Meta:
        db_table = 'agendamento'


class Bloqueio(models.Model):
    prestador = models.ForeignKey(Prestador, on_delete=models.CASCADE)
    data_hora_inicio = models.DateTimeField()
    data_hora_fim = models.DateTimeField()
    motivo = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f'{self.prestador} - {self.data_hora_inicio}'

    class Meta:
        db_table = 'bloqueio'