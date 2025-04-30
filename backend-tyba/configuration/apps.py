from django.apps import AppConfig


class ConfigurationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'configuration'

    permissions = [
        {
            'role': [1, 2],
            'permissions': [
                'group-list',
                'group-detail',
                'group-create',
                'group-update',
                'group-delete',
                'permission-list'
            ]
        }
    ]
