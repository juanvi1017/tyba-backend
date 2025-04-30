# Django
from django.urls import include, path

# Vistas locales de la aplicación
from user_auth.views import (
    Login,  # Vista para el inicio de sesión
    Logout,  # Vista para cerrar sesión
    UserViewSet,  # ViewSet para la gestión de usuarios
    Restaurant,  # Vista para consultar restaurantes
    LogTransactionViewSet  # ViewSet para  listar transacciones
)
from rest_framework import routers 
from utils.test_utils import TestRouter

# Crea una instancia del router personalizado (sin barra diagonal al final de las rutas)
router = TestRouter(trailing_slash=False)
router.register(r'user', UserViewSet, basename='user')

# Crea un router simple estándar sin barra diagonal al final
router_simple = routers.SimpleRouter(trailing_slash=False)

# Definición de las URLs del proyecto
urlpatterns = [
    # Incluye todas las rutas generadas por el router personalizado
    path('', include(router.urls)),
    path(
        route='login', 
        view=Login.as_view(),
        name='login' 
    ),
    path(
        route='logout', 
        view=Logout.as_view(),
        name='logout'
    ),
    path(
        route='restaurant',
        view=Restaurant.as_view(),
        name='restaurant'
    ),
    path(
        route='log',
        view=LogTransactionViewSet.as_view({'get': 'list'}),
        name='log'
    )
]
