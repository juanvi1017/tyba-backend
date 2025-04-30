from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from configuration.models import Group, UserStatus, Permission
from user_auth.models import LogTransaction, Token

class AuthTests(APITestCase):
    def setUp(self):
        # Crea datos requeridos por el UserManager
        group = Group.objects.create(id="2") #usuario
        status = UserStatus.objects.create(id="1") #activo
        UserStatus.objects.create(id="5") # Eliminado (deshabilitado)


        # Crea los permisos
        permissions = [
            "user-list",
            "user-update",
            "user-detail",
            "user-delete",
            "restaurant",
            "logout",
            "log"
        ]

        # Crea los permisos de manera eficiente en un solo bucle
        permission_objects = [Permission.objects.create(codename=perm) for perm in permissions]

        # Asocia todos los permisos al grupo
        group.permission.add(*permission_objects)

        self.user = get_user_model().objects.create_user(
            user="admin123",
            group=group.id,
            password="12345678",
            status=status.id,
            name="Administrador"
        )

    def test_login(self):
        response = self.client.post("/user_auth/login", {
            "user": "admin123",
            "password": "12345678"
        }, format='json')  # Asegura que se envía como JSON

        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data["data"])

    def test_list_users(self):
        # login para obtener el token
        login_response = self.client.post("/user_auth/login", {
            "user": "admin123",
            "password": "12345678"
        }, format='json')

        token = login_response.data["data"]["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        # listar usuarios
        response = self.client.get("/user_auth/user/list", format='json')

        # Verifica que el estado de la respuesta sea 200
        self.assertEqual(response.status_code, 200)

        # Verifica que la clave 'results' sea una lista
        self.assertIsInstance(response.data['results'], list)

        # comprobar que hay al menos un usuario listado
        self.assertGreater(len(response.data['results']), 0)

    def test_update_user(self):
        # login para obtener el token
        login_response = self.client.post("/user_auth/login", {
            "user": "admin123",
            "password": "12345678"
        }, format='json')

        token = login_response.data["data"]["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        # Datos para actualizar el usuario
        updated_data = {
            "user_status": 1,  # Cambiar el estado del usuario si es necesario
            "full_name": "Nuevo Nombre"  # Cambiar el nombre completo
        }

        url = f"/user_auth/user/detail/{self.user.id}"

        # Actualizar el usuario (usamos el ID 'admin123' como ejemplo)
        response = self.client.put(url, updated_data, format='json')

        # Verifica que la respuesta tenga el estado 200
        self.assertEqual(response.status_code, 200)

        # Verifica que el nombre del usuario haya sido actualizado correctamente
        self.assertEqual(response.data['full_name'], "Nuevo Nombre")
        self.assertEqual(response.data['user_status'], 1)

    def test_delete_user(self):
        # login para obtener el token
        login_response = self.client.post("/user_auth/login", {
            "user": "admin123",
            "password": "12345678"
        }, format='json')

        token = login_response.data["data"]["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        
        url = f"/user_auth/user/detail/{self.user.id}"

        # Elimina el usuario
        response = self.client.delete(url, format='json')

        # Verifica que la respuesta tenga el estado 200 (Eliminación exitosa)
        self.assertEqual(response.status_code, 200)

        # Verifica que el estado del usuario haya cambiado a 'eliminado' (status_id=5)
        self.user.refresh_from_db()  # Actualiza el usuario con la base de datos
        self.assertEqual(self.user.user_status_id, 5)  

        # Verifica que la respuesta contenga el mensaje de eliminación exitosa
        self.assertEqual(response.data['message'], 'Eliminación exitosa')


    def test_transaction_log_created_on_user_list(self):
        # Login para obtener el token
        login_response = self.client.post("/user_auth/login", {
            "user": "admin123",
            "password": "12345678"
        }, format='json')

        token = login_response.data["data"]["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        # Asegúrate de que no haya logs antes
        initial_log_count = LogTransaction.objects.count()

        # Realiza la acción que genera el log
        response = self.client.get("/user_auth/user/list", format='json')

        # Verifica que la respuesta sea exitosa
        self.assertEqual(response.status_code, 200)

        # Verifica que se haya creado un nuevo log
        self.assertEqual(LogTransaction.objects.count(), initial_log_count + 1)

        # Verifica que el contenido del log sea correcto
        log = LogTransaction.objects.last()
        self.assertEqual(log.user.id, self.user.id)
        self.assertEqual(log.url_transaction, "get user")
        self.assertEqual(log.description, "Listar usuarios")

    @patch("user_auth.views.requests.get")
    def test_get_restaurants_by_city(self, mock_get):
        # Simula respuesta de geocoding
        mock_get.side_effect = [
            # Primera llamada: geocoding
            MockResponse({
                "results": [{
                    "geometry": {
                        "location": {
                            "lat": 4.710989,
                            "lng": -74.072090
                        }
                    }
                }]
            }),
            # Segunda llamada: places nearby
            MockResponse({
                "results": [
                    {"name": "Restaurante A"},
                    {"name": "Restaurante B"}
                ]
            })
        ]

        # Login y autenticación
        login_response = self.client.post("/user_auth/login", {
            "user": "admin123",
            "password": "12345678"
        }, format='json')
        token = login_response.data["data"]["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        # Llamada al endpoint
        response = self.client.get("/user_auth/restaurant?city=Bogota", format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "Consulta exitosa")
        self.assertIn("Restaurante A", response.data["data"])
        self.assertIn("Restaurante B", response.data["data"])

        # Verifica que se haya creado un LogTransaction
        self.assertTrue(LogTransaction.objects.filter(user=self.user, url_transaction='get restaurant').exists())


    def test_logout_successful(self):
        # Login para obtener token
        login_response = self.client.post("/user_auth/login", {
            "user": "admin123",
            "password": "12345678"
        }, format='json')
        token = login_response.data["data"]["token"]

        # Verifica que el token exista
        self.assertTrue(Token.objects.filter(user=self.user).exists())

        # Autenticación con token
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        # Llamada al logout
        response = self.client.get("/user_auth/logout")

        # Verifica que el token haya sido eliminado
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "Cierre de sesión exitoso")
        self.assertFalse(Token.objects.filter(user=self.user).exists())


class MockResponse:
    def __init__(self, json_data, status_code=200):
        self._json_data = json_data
        self.status_code = status_code

    def json(self):
        return self._json_data