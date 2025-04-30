import logging

# Utilidades y bibliotecas para manejo de tiempo y traducción
import pytz  # Para trabajar con zonas horarias
from django.contrib.auth.models import AnonymousUser  # Modelo para usuarios anónimos
from django.utils import timezone  # Manejo de zonas horarias en Django
from django.utils.translation import gettext as _  # Función para traducción de texto
from django.utils.translation import gettext_lazy  # Versión "perezosa" de gettext para uso en constantes de clase

# Importación de modelos locales
from user_auth.models import Token  # Modelo de token personalizado
from rest_framework import exceptions, status  # Excepciones y estados HTTP de DRF
from rest_framework.authentication import (
    TokenAuthentication, get_authorization_header  # Autenticación basada en tokens
)

logger_debug = logging.getLogger('debug_info')  # Configura un logger para mensajes de depuración

class TokenAuthenticationTest(TokenAuthentication):
    """
    Clase personalizada de autenticación con tokens
    -----------------------------------------------
    Errores de autenticación:
    Código    Descripción
    111       El modelo no existe
    113       Token expirado
    -----------------------------------------------
    """

    model = Token  # Modelo de token a usar

    def authenticate_credentials(self, key, request):
        """
        Autentica al usuario mediante las credenciales del token.
        Parámetros:
        - key: Clave del token proporcionada en la solicitud.
        - request: Objeto de la solicitud actual.
        """
        model = self.get_model()  # Obtiene el modelo de token configurado
        anonymous_user_response = (AnonymousUser, None)  # Respuesta para usuario no autenticado

        try:
            # Intenta recuperar el token y su usuario relacionado
            token = model.objects.select_related('user').get(key=key)
            user = token.user
        except model.DoesNotExist:
            # Si el token no existe, lanza una excepción de autenticación
            msg = gettext_lazy('Invalid token header. 1')  # Mensaje de error traducido
            raise exceptions.AuthenticationFailed(
                msg, status.HTTP_401_UNAUTHORIZED
            )

        # Validar que el usuario esté activo
        if not user.is_active:
            return anonymous_user_response

        # Validar que la IP del token coincida con la IP de la solicitud
        if token.ip != request.META['REMOTE_ADDR']:
            return anonymous_user_response

        # Validar que el token no esté expirado
        if token.expired_time < timezone.now():
            msg = gettext_lazy('Invalid token header. 2')  # Mensaje de error si el token está expirado
            raise exceptions.AuthenticationFailed(
                msg, status.HTTP_401_UNAUTHORIZED
            )

        # Establece la zona horaria del cliente con base en el token
        self.set_timezone(token)

        return (user, token)  # Devuelve el usuario autenticado y el token

    def authenticate(self, request):
        """
        Autentica al usuario verificando el encabezado de autorización.
        Parámetros:
        - request: Objeto de la solicitud actual.
        """
        auth = get_authorization_header(request).split()  # Obtiene el encabezado de autorización y lo divide

        # Validar que el encabezado tenga el formato esperado
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            # Error si no se proporcionaron credenciales
            msg = gettext_lazy('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            # Error si el token contiene espacios
            msg = gettext_lazy(
                'Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            # Decodifica el token desde el encabezado
            token = auth[1].decode()
        except UnicodeError:
            # Error si el token contiene caracteres no válidos
            msg = gettext_lazy('Invalid token header. \
            Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        # Autentica las credenciales del token
        return self.authenticate_credentials(token, request)

    def set_timezone(self, token):
        """
        Configura la zona horaria activa con base en el token.
        Parámetros:
        - token: Objeto del token autenticado.
        """
        client_timezone = token.tz_session  # Obtiene la zona horaria del cliente del token
        tz = pytz.timezone(client_timezone)  # Convierte la zona horaria a un objeto pytz
        if tz:
            timezone.activate(tz)  # Activa la zona horaria en Django
        else:
            timezone.deactivate()  # Desactiva la zona horaria si no es válida
