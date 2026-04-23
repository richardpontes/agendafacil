from django.test import TestCase, Client
from django.urls import reverse
from .models import Usuario, Prestador
from django.contrib.auth.hashers import make_password


class AutenticacaoTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.usuario_cliente = Usuario.objects.create(
            nome='Maria Silva',
            email='maria@email.com',
            senha=make_password('senha123'),
            tipo='cliente'
        )
        self.usuario_prestador = Usuario.objects.create(
            nome='Ana Paula Oliveira',
            email='anapaula@email.com',
            senha=make_password('senha123'),
            tipo='prestador'
        )
        self.prestador = Prestador.objects.create(
            usuario=self.usuario_prestador,
            nome_negocio='Salão Beleza & Charme',
            cep='90040-060',
            logradouro='Avenida Paulo Gama',
            numero='110',
            bairro='Farroupilha',
            cidade='Porto Alegre',
            estado='RS',
            horario_inicio='09:00',
            horario_fim='18:00',
            # dias_funcionamento='Segunda a Sábado'
            dia_inicio='Segunda',
            dia_fim='Sábado'
        )

    def test_pagina_inicial(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_pagina_login(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_pagina_cadastro(self):
        response = self.client.get(reverse('cadastro'))
        self.assertEqual(response.status_code, 200)

    def test_cadastro_cliente(self):
        response = self.client.post(reverse('cadastro'), {
            'nome': 'João Santos',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'confirmar_senha': 'senha123',
            'telefone': '(51) 99999-9999',
            'tipo': 'cliente'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Usuario.objects.filter(email='joao@email.com').exists())

    def test_cadastro_prestador(self):
        response = self.client.post(reverse('cadastro'), {
            'nome': 'Carlos Barbeiro',
            'email': 'carlos@email.com',
            'senha': 'senha123',
            'confirmar_senha': 'senha123',
            'telefone': '(51) 98888-7777',
            'tipo': 'prestador',
            'nome_negocio': 'Barbearia do Carlos',
            'cep': '90040-060',
            'logradouro': 'Avenida Paulo Gama',
            'numero': '110',
            'bairro': 'Farroupilha',
            'cidade': 'Porto Alegre',
            'estado': 'RS',
            'horario_inicio': '09:00',
            'horario_fim': '18:00',
            # 'dias_funcionamento': 'Segunda a Sábado'
            'dia_inicio': 'Segunda',
            'dia_fim': 'Sábado'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Usuario.objects.filter(email='carlos@email.com').exists())
        self.assertTrue(Prestador.objects.filter(nome_negocio='Barbearia do Carlos').exists())

    def test_login_cliente_redireciona_dashboard_cliente(self):
        response = self.client.post(reverse('login'), {
            'email': 'maria@email.com',
            'senha': 'senha123'
        })
        self.assertRedirects(response, reverse('dashboard_cliente'))

    def test_login_prestador_redireciona_dashboard_prestador(self):
        response = self.client.post(reverse('login'), {
            'email': 'anapaula@email.com',
            'senha': 'senha123'
        })
        self.assertRedirects(response, reverse('dashboard_prestador'))

    def test_login_invalido(self):
        response = self.client.post(reverse('login'), {
            'email': 'maria@email.com',
            'senha': 'senhaerrada'
        })
        self.assertEqual(response.status_code, 200)

    def test_senhas_diferentes_no_cadastro(self):
        response = self.client.post(reverse('cadastro'), {
            'nome': 'Teste',
            'email': 'teste@email.com',
            'senha': 'senha123',
            'confirmar_senha': 'senhadiferente',
            'tipo': 'cliente'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Usuario.objects.filter(email='teste@email.com').exists())

    def test_email_duplicado_no_cadastro(self):
        response = self.client.post(reverse('cadastro'), {
            'nome': 'Outro Maria',
            'email': 'maria@email.com',
            'senha': 'senha123',
            'confirmar_senha': 'senha123',
            'tipo': 'cliente'
        })
        self.assertEqual(response.status_code, 200)

    def test_dashboard_cliente_sem_login(self):
        response = self.client.get(reverse('dashboard_cliente'))
        self.assertRedirects(response, reverse('login'))

    def test_dashboard_prestador_sem_login(self):
        response = self.client.get(reverse('dashboard_prestador'))
        self.assertRedirects(response, reverse('login'))