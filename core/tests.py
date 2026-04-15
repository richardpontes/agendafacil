from django.test import TestCase, Client
from django.urls import reverse
from .models import Usuario
from django.contrib.auth.hashers import make_password


class AutenticacaoTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create(
            nome='Maria Silva',
            email='maria@email.com',
            senha=make_password('senha123'),
            tipo='cliente'
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

    def test_login_valido(self):
        response = self.client.post(reverse('login'), {
            'email': 'maria@email.com',
            'senha': 'senha123'
        })
        self.assertEqual(response.status_code, 302)

    def test_login_invalido(self):
        response = self.client.post(reverse('login'), {
            'email': 'maria@email.com',
            'senha': 'senhaerrada'
        })
        self.assertEqual(response.status_code, 200)