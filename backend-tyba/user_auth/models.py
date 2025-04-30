from configuration.models import Group, UserStatus
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import models
from rest_framework.authtoken.models import Token as TokenDRF


class UserStatusLog(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.CharField(max_length=100)  # Nombre del usuario que generó el registro
    ip = models.GenericIPAddressField(null=True)  # Dirección IP del usuario
    user_status = models.ForeignKey('configuration.UserStatus', models.PROTECT)  # Estado del usuario (referencia externa)
    attempt = models.IntegerField(default=0)  # Número de intentos realizados por el usuario
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación del registro
    updated_at = models.DateTimeField(auto_now=True)  # Fecha de última actualización del registro


class UserManager(BaseUserManager):
    def create_user(self, user, group, password, status, name):
        """
        Crea y guarda un usuario con los datos proporcionados.
        """
        if not user or not password or not name:
            raise ValueError('Valores no definidos')
        # Busca la instancia del rol o grupo asociado
        group_model = Group.objects.filter(id=group).first()
        if group_model is None:
            raise ValueError('El rol %s no existe' % str(group))
        # Busca la instancia del estado del usuario
        model_status = UserStatus.objects.filter(id=status).first()
        if model_status is None:
            raise ValueError('El estado del usuario %s no existe' % str(status))
        # Crea el usuario en la base de datos
        user = self.model(
            id=user,
            user_status=model_status,
            group=group_model,
            full_name=str(name).capitalize()
        )
        user.set_password(password)  # Establece la contraseña del usuario
        user.save(using=self._db)  # Guarda el usuario en la base de datos
        return user


class User(AbstractBaseUser):
    id = models.CharField(
        verbose_name='usuario',
        max_length=300,
        primary_key=True  # Define el campo como llave primaria
    )
    first_login = models.BooleanField(default=False)  # Indica si es la primera vez que el usuario inicia sesión
    user_status = models.ForeignKey('configuration.UserStatus', models.PROTECT)  # Estado del usuario
    full_name = models.CharField(max_length=600, default="")  # Nombre completo del usuario
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación del usuario
    updated_at = models.DateTimeField(auto_now=True)  # Fecha de última actualización del usuario
    group = models.ForeignKey('configuration.Group', models.PROTECT)  # Grupo asociado al usuario
    session_key = models.CharField(max_length=32, null=True, blank=True)  # Clave de la sesión del usuario
    objects = UserManager()  # Define el administrador del modelo

    USERNAME_FIELD = 'id'  # Campo utilizado como identificador único para el usuario
    REQUIRED_FIELDS = []  # Campos requeridos al crear un usuario

    def __str__(self):
        return self.id  # Devuelve la representación del usuario como su ID

    def has_perm(self, perm, obj=None):
        """
        Verifica si el usuario tiene un permiso específico.
        """
        is_allowed = True
        try:
            # Busca si el usuario tiene el permiso asociado al grupo
            User.objects.get(pk=self.id, group__permission__codename=perm)
        except ObjectDoesNotExist:
            is_allowed = False
        except MultipleObjectsReturned:
            is_allowed = False
        return is_allowed

    def has_module_perms(self, app_label):
        """
        Verifica si el usuario tiene permisos para ver la aplicación `app_label`.
        """
        return True

    class Meta:
        ordering = ['id']  # Ordena los usuarios por su ID


class LogSession(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', models.PROTECT)  # Usuario asociado a la sesión
    ip = models.GenericIPAddressField()  # Dirección IP utilizada en la sesión
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación de la sesión


class Token(TokenDRF):
    ip = models.GenericIPAddressField(null=True)  # Dirección IP vinculada al token
    expired_time = models.DateTimeField(null=True)  # Fecha y hora de expiración del token
    tz_session = models.CharField(max_length=100, default="UTC")  # Zona horaria de la sesión asociada al token


class LogTransaction(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', models.PROTECT)  # Usuario asociado a la transacción
    url_transaction = models.CharField(max_length=600, default="")  # URL que originó la transacción
    description = models.CharField(max_length=600, default="")  # Descripción de la transacción
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación de la transacción
