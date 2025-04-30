from django.db import models
from django.utils.translation import gettext_lazy as _



class Permission(models.Model):
    id = models.AutoField(primary_key=True)
    codename = models.CharField(max_length=100)


class Group(models.Model):
    """
        1 Administrador
        2 Usuario
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    permission = models.ManyToManyField(
        Permission,
        verbose_name=_('permissions'),
        blank=True,
    )


class UserStatus(models.Model):
    # 1. activo, 2.inactivo, 3. bloqueado, 4. suspendido 5. Desahabilitado
    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.descripcion


