import logging
from datetime import datetime
import requests
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from user_auth.models import LogSession, Token, User, LogTransaction
from user_auth.serializers import (
    UserCreateSerializer,
    UserListSerializer,
    UserLoginSerializer,
    LogTransactionSerializer
)
from Helpers.Helper import UserHelper
import environ

logger_debug = logging.getLogger('debug_info')

env = environ.Env()

# Función auxiliar para generar tokens
def generate_token(user, ip_address, keep, tz_session):
    # Calcula el tiempo de expiración basado en configuración
    exp_hours = settings.EXPIRED_TIME_HOURS + datetime.now()
    exp_weeks = settings.EXPIRED_TIME_WEEKS + datetime.now()
    defaults = {
        'ip': ip_address,
        'expired_time': exp_weeks if keep else exp_hours,
        'tz_session': tz_session
    }
    # Crea o obtiene un token existente para el usuario
    token, created = Token.objects.get_or_create(user=user, defaults=defaults)

    if not created:
        # Si el token ya existe, lo elimina y genera uno nuevo
        token.delete()
        token, _ = Token.objects.get_or_create(user=user, defaults=defaults)
    return token

# Vista para el inicio de sesión (Login)
class Login(APIView):
    permission_classes = [AllowAny]  # Permite accesos sin autenticación
    serializer_class = UserLoginSerializer  # Usa el serializer para validar datos

    def post(self, request):
        # Valida los datos recibidos del cliente
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        user, password = data['user'], data['password']
        keep = request.data.get('keep_login', False)  # Opción para mantener la sesión
        tz_session = request.data.get('tz_session', 'UTC')  # Zona horaria
        ip_address = request.META['REMOTE_ADDR']  # Dirección IP del cliente

        # Verifica si el usuario está bloqueado
        if UserHelper.is_blocked_user(user, ip_address):
            return self._response_error(102)

        # Autentica al usuario con las credenciales proporcionadas
        auth = authenticate(request, username=user, password=password)
        if auth:
            # Verifica el estado del usuario (inactivo o bloqueado)
            if auth.user_status_id in [2, 3]:
                return self._response_error(102)

            # Genera un token para el usuario
            token = generate_token(auth, ip_address, keep, tz_session)
            auth.last_login = datetime.now()
            auth.save()  # Actualiza la última fecha de inicio de sesión
            LogSession.objects.create(user_id=auth.id, ip=ip_address)  # Registra la sesión

            logger_debug.debug(f'Login exitoso para el usuario: {auth.id}')
            return Response({
                'data': {
                    'token': token.key,
                    'name': auth.full_name,
                    'role': auth.group_id,
                    'first_login': auth.first_login,
                    'last_login': auth.last_login
                }
            })

        # Maneja intentos fallidos de inicio de sesión
        self._handle_failed_login(user, ip_address)
        return self._response_error(103)

    def _response_error(self, code):
        # Devuelve una respuesta con el código de error especificado
        return Response({'error': 'Inicio de sesión fallido', 'code': code}, status=status.HTTP_400_BAD_REQUEST)

    def _handle_failed_login(self, user, ip_address):
        try:
            # Intenta obtener al usuario para verificar su existencia
            User.objects.get(pk=user)
        except ObjectDoesNotExist:
            logger_debug.warning(f'Intento de inicio de sesión fallido para: {user}')
        finally:
            # Registra el estado del intento fallido
            UserHelper.set_log_status_user(user, ip_address)

# Vista para cerrar sesión (Logout)
class Logout(APIView):
    def get(self, request):
        # Elimina todos los tokens asociados al usuario autenticado
        Token.objects.filter(user=request.user).delete()
        return Response({'message': 'Cierre de sesión exitoso'})

# ViewSet para manejo de usuarios
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().exclude(user_status=5)  # Excluye usuarios eliminados

    def get_serializer_class(self):
        # Retorna el serializer adecuado según la acción (listar o crear usuarios)
        return UserListSerializer if self.action in ['list', 'retrieve'] else UserCreateSerializer

    def get_users(self, user_status=None, user_search=None):
        # Filtra los usuarios según el estado o criterios de búsqueda
        queryset = self.get_queryset()
        if user_status:
            queryset = queryset.filter(user_status=user_status)
        if user_search:
            queryset = queryset.filter(Q(pk__contains=user_search) | Q(full_name__contains=user_search))
        return queryset

    def list(self, request, *args, **kwargs):
        # Lista los usuarios filtrados y registra la transacción
        queryset = self.get_users(request.GET.get('status_filter'), request.GET.get('search_filter'))
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        LogTransaction.objects.create(
            user_id=request.user.id,
            url_transaction='get user',
            description='Listar usuarios'
        )
        return self.get_paginated_response(serializer.data)

    def update(self, request, *args, **kwargs):
        # Actualiza un usuario y registra la transacción
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        LogTransaction.objects.create(
            user_id=request.user.id,
            url_transaction='update user',
            description=f"Actualización del usuario {user.id}"
        )
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        # Marca un usuario como eliminado en lugar de borrarlo físicamente
        user = self.get_object()
        if user.group_id != 1 and user.id != 'supervisor':
            user.user_status_id = 5
            user.save()
            LogTransaction.objects.create(
                user_id=request.user.id,
                url_transaction='Delete user',
                description=f"Eliminación del usuario {user.id}"
            )
            return Response({'message': 'Eliminación exitosa'}, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

# Vista para buscar restaurantes
class Restaurant(APIView):
    def get(self, request):
        user = request.user
        city = request.query_params.get('city')  # Obtiene la ciudad desde los parámetros de la consulta
        api_key = env("API_KEY_GOOGLE")
        geo_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city}&key={api_key}"
        geo_response = requests.get(geo_url).json()

        if geo_response.get("results"):
            # Obtiene la ubicación (latitud y longitud)
            location = geo_response["results"][0]["geometry"]["location"]
            lat, lng = location["lat"], location["lng"]

            # Solicita información de restaurantes cercanos
            places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=5000&type=restaurant&key={api_key}"
            places_response = requests.get(places_url).json()

            data = [lugar["name"] for lugar in places_response.get("results", [])]  # Lista de nombres de restaurantes
            LogTransaction.objects.create(
                user_id=user.id,
                url_transaction='get restaurant',
                description=f"Consulta de restaurantes en {city}"
            )
            return Response({'message': 'Consulta exitosa', 'data': data}, status=status.HTTP_200_OK)

        return Response({"error": "No se encontraron resultados"}, status=status.HTTP_400_BAD_REQUEST)

# ViewSet para transacciones (LogTransaction)
class LogTransactionViewSet(viewsets.ModelViewSet):
    queryset = LogTransaction.objects.all().order_by('id')  # Ordena los registros por ID
    serializer_class = LogTransactionSerializer  # Serializador utilizado
