from django.apps import AppConfig

# Permisos asignados a los roles
class userAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_auth'

    permissions = [
        {
            'role': [1],
            'permissions': [
                'user-list',
                'user-detail',
                'user-create',
                'user-update',
                'user-delete',
                'logout',
                'restaurant',
                'log'
            ]
        },
        {
            'role': [2],
            'permissions': [
                'user-list',
                'user-detail',
                'user-create',
                'user-update',
                'user-delete',
                'logout',
                'restaurant',
                'log'
            ]
        }
    ]
