from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .forms import InstrumentoForm
from .models import Instrumento


class InstrumentoFormTests(TestCase):
    def datos_validos(self, **overrides):
        datos = {
            "nombre": "Guitarra acústica",
            "marca": "Yamaha",
            "categoria": Instrumento.Categoria.CUERDA,
            "precio": "120000.00",
            "stock": "4",
            "descripcion": "Tapa de abeto",
        }
        datos.update(overrides)
        return datos

    def test_rechaza_precio_cero(self):
        form = InstrumentoForm(self.datos_validos(precio="0"))
        self.assertFalse(form.is_valid())
        self.assertIn("precio", form.errors)

    def test_acepta_limites_del_precio(self):
        for precio in ("100000", "10000000"):
            with self.subTest(precio=precio):
                form = InstrumentoForm(self.datos_validos(precio=precio))
                self.assertTrue(form.is_valid(), form.errors)

    def test_rechaza_precio_fuera_de_limites(self):
        for precio in ("99999.99", "10000000.01"):
            with self.subTest(precio=precio):
                form = InstrumentoForm(self.datos_validos(precio=precio))
                self.assertFalse(form.is_valid())
                self.assertIn("precio", form.errors)

    def test_rechaza_stock_negativo(self):
        form = InstrumentoForm(self.datos_validos(stock="-1"))
        self.assertFalse(form.is_valid())
        self.assertIn("stock", form.errors)

    def test_rechaza_stock_cero_con_mensaje(self):
        form = InstrumentoForm(self.datos_validos(stock="0"))
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["stock"],
            ["Las unidades en stock no pueden ser 0."],
        )

    def test_acepta_stock_maximo_de_cien(self):
        form = InstrumentoForm(self.datos_validos(stock="100"))
        self.assertTrue(form.is_valid(), form.errors)

    def test_rechaza_stock_mayor_a_cien_con_mensaje(self):
        form = InstrumentoForm(self.datos_validos(stock="101"))
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["stock"],
            ["Las unidades en stock no pueden superar 100."],
        )


class PruebasConContrasenasRapidas(TestCase):
    def setUp(self):
        configuracion = self.settings(
            PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"]
        )
        configuracion.enable()
        self.addCleanup(configuracion.disable)


class InstrumentoCrudTests(PruebasConContrasenasRapidas):
    def setUp(self):
        super().setUp()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="musicadmin",
            password="MusicaSegura-2026",
        )
        self.client.force_login(self.user)

    def crear_instrumento(self):
        return Instrumento.objects.create(
            nombre="Guitarra acústica",
            marca="Yamaha",
            categoria=Instrumento.Categoria.CUERDA,
            precio=Decimal("120000.00"),
            stock=4,
        )

    def test_catalogo_muestra_instrumento(self):
        instrumento = self.crear_instrumento()
        respuesta = self.client.get(reverse("instrumentos:lista"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, instrumento.nombre)

    def test_crea_instrumento_desde_formulario(self):
        respuesta = self.client.post(
            reverse("instrumentos:crear"),
            {
                "nombre": "Teclado",
                "marca": "Casio",
                "categoria": Instrumento.Categoria.TECLADO,
                "precio": "185000.00",
                "stock": "2",
                "descripcion": "",
            },
        )
        self.assertEqual(Instrumento.objects.count(), 1)
        self.assertRedirects(
            respuesta,
            reverse("instrumentos:detalle", args=[Instrumento.objects.first().pk]),
        )

    def test_edita_y_elimina_instrumento(self):
        instrumento = self.crear_instrumento()
        respuesta = self.client.post(
            reverse("instrumentos:editar", args=[instrumento.pk]),
            {
                "nombre": "Guitarra eléctrica",
                "marca": instrumento.marca,
                "categoria": Instrumento.Categoria.CUERDA,
                "precio": "150000.00",
                "stock": "3",
                "descripcion": "",
            },
        )
        instrumento.refresh_from_db()
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(instrumento.nombre, "Guitarra eléctrica")

        respuesta = self.client.post(
            reverse("instrumentos:eliminar", args=[instrumento.pk])
        )
        self.assertRedirects(respuesta, reverse("instrumentos:lista"))
        self.assertFalse(Instrumento.objects.exists())

    def test_usuario_no_autenticado_es_redirigido_al_login(self):
        self.client.logout()
        respuesta = self.client.get(reverse("instrumentos:lista"))
        self.assertRedirects(
            respuesta,
            f"{reverse('instrumentos:login')}?next={reverse('instrumentos:lista')}",
        )


class AutenticacionTokenTests(PruebasConContrasenasRapidas):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(
            username="musicadmin",
            password="MusicaSegura-2026",
        )
        self.api = APIClient()

    def test_login_api_entrega_token(self):
        respuesta_pagina = self.client.get(reverse("instrumentos:login"))
        self.assertContains(respuesta_pagina, "Iniciar sesión")

        respuesta = self.api.post(
            reverse("instrumentos:api_login"),
            {"username": "musicadmin", "password": "MusicaSegura-2026"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("token", respuesta.data)
        self.assertEqual(respuesta.data["token"], self.user.auth_token.key)
        self.assertNotIn("_auth_user_id", self.api.session)

    def test_login_web_abre_sesion_y_genera_token(self):
        respuesta = self.client.post(
            reverse("instrumentos:login"),
            {"username": "musicadmin", "password": "MusicaSegura-2026"},
        )
        self.assertRedirects(respuesta, reverse("instrumentos:lista"))
        self.assertEqual(
            self.client.session.get("_auth_user_id"),
            str(self.user.pk),
        )
        self.assertEqual(
            self.client.session.get("api_token"),
            self.user.auth_token.key,
        )

    def test_login_rechaza_credenciales_incorrectas(self):
        respuesta = self.api.post(
            reverse("instrumentos:api_login"),
            {"username": "musicadmin", "password": "incorrecta"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, 401)
        self.assertIn("error", respuesta.data)

    def test_login_exige_ambos_campos(self):
        respuesta = self.api.post(
            reverse("instrumentos:api_login"),
            {"username": "musicadmin"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, 400)

    def test_login_web_envia_csrf_y_crea_sesion(self):
        cliente = Client(enforce_csrf_checks=True)
        pagina = cliente.get(reverse("instrumentos:login"))
        csrf_token = pagina.cookies["csrftoken"].value

        respuesta = cliente.post(
            reverse("instrumentos:login"),
            {
                "username": "musicadmin",
                "password": "MusicaSegura-2026",
            },
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertRedirects(respuesta, reverse("instrumentos:lista"))
        self.assertEqual(
            cliente.session.get("_auth_user_id"),
            str(self.user.pk),
        )
        self.assertTrue(cliente.session.get("api_token"))

    def test_logout_revoca_token_y_cierra_sesion(self):
        self.client.force_login(self.user)
        token = Token.objects.create(user=self.user)
        respuesta = self.client.post(reverse("instrumentos:logout"))
        self.assertRedirects(respuesta, reverse("instrumentos:login"))
        self.assertFalse(Token.objects.filter(pk=token.pk).exists())
        self.assertIsNone(self.client.session.get("_auth_user_id"))

    def test_logout_funciona_si_la_sesion_no_tiene_token(self):
        self.client.force_login(self.user)
        respuesta = self.client.post(reverse("instrumentos:logout"))
        self.assertRedirects(respuesta, reverse("instrumentos:login"))
        self.assertIsNone(self.client.session.get("_auth_user_id"))


class InstrumentoAPITests(PruebasConContrasenasRapidas):
    def setUp(self):
        super().setUp()
        user = get_user_model().objects.create_user(
            username="apiadmin",
            password="MusicaSegura-2026",
        )
        self.token = Token.objects.create(user=user)
        self.api = APIClient()
        self.api.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        self.list_url = reverse("instrumentos:api_instrumentos")

    def datos_validos(self, **overrides):
        datos = {
            "nombre": "Guitarra acústica",
            "marca": "Yamaha",
            "categoria": Instrumento.Categoria.CUERDA,
            "precio": "120000.00",
            "stock": 4,
            "descripcion": "Tapa de abeto",
        }
        datos.update(overrides)
        return datos

    def test_token_ausente_o_invalido_no_accede_a_la_api(self):
        api_sin_token = APIClient()
        self.assertEqual(api_sin_token.get(self.list_url).status_code, 401)
        api_sin_token.credentials(HTTP_AUTHORIZATION="Token invalido")
        self.assertEqual(api_sin_token.get(self.list_url).status_code, 401)

    def test_get_lista_y_consulta_por_id(self):
        instrumento = Instrumento.objects.create(**self.datos_validos())
        respuesta_lista = self.api.get(self.list_url)
        self.assertEqual(respuesta_lista.status_code, 200)
        self.assertEqual(respuesta_lista.data[0]["id"], instrumento.pk)

        respuesta_detalle = self.api.get(
            reverse("instrumentos:api_instrumento_detalle", args=[instrumento.pk])
        )
        self.assertEqual(respuesta_detalle.status_code, 200)
        self.assertEqual(respuesta_detalle.data["nombre"], instrumento.nombre)

    def test_post_crea_registro_y_rechaza_datos_invalidos(self):
        respuesta = self.api.post(
            self.list_url,
            self.datos_validos(),
            format="json",
        )
        self.assertEqual(respuesta.status_code, 201)
        instrumento = Instrumento.objects.get(pk=respuesta.data["id"])
        self.assertEqual(instrumento.marca, "Yamaha")

        respuesta_invalida = self.api.post(
            self.list_url,
            self.datos_validos(precio="0", stock=-1),
            format="json",
        )
        self.assertEqual(respuesta_invalida.status_code, 400)
        self.assertIn("precio", respuesta_invalida.data)
        self.assertIn("stock", respuesta_invalida.data)
        self.assertEqual(Instrumento.objects.count(), 1)

    def test_api_rechaza_stock_mayor_a_cien(self):
        respuesta = self.api.post(
            self.list_url,
            self.datos_validos(stock=101),
            format="json",
        )
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("stock", respuesta.data)
        self.assertEqual(Instrumento.objects.count(), 0)

    def test_put_actualiza_y_delete_elimina_registro(self):
        instrumento = Instrumento.objects.create(**self.datos_validos())
        url = reverse("instrumentos:api_instrumento_detalle", args=[instrumento.pk])

        respuesta_actualizacion = self.api.put(
            url,
            self.datos_validos(nombre="Guitarra eléctrica", stock=2),
            format="json",
        )
        self.assertEqual(respuesta_actualizacion.status_code, 200)
        instrumento.refresh_from_db()
        self.assertEqual(instrumento.nombre, "Guitarra eléctrica")
        self.assertEqual(instrumento.stock, 2)

        respuesta_eliminacion = self.api.delete(url)
        self.assertEqual(respuesta_eliminacion.status_code, 204)
        self.assertFalse(Instrumento.objects.filter(pk=instrumento.pk).exists())

    def test_api_responde_404_para_instrumento_inexistente(self):
        respuesta = self.api.get(
            reverse("instrumentos:api_instrumento_detalle", args=[9999])
        )
        self.assertEqual(respuesta.status_code, 404)
