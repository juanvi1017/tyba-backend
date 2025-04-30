
from datetime import datetime


from user_auth.models import UserStatusLog

from backend.settings import TEST_AUTH_EXPIRED_TIME
from backend.settings import TEST_AUTH_LOGIN_FAILURE_LIMIT as LIMIT

LETTERS = 'abcdefghijklmnopqrstuvwxyz'


class UserHelper:
    # se verifica que el rol exista en la BD

    @staticmethod
    def check_password_string(password=''):
        special_char = ['$', '@', '#', '%', '*', '_', '-', '!', '/', ':']
        if len(password) < 8:
            return {
                'valid': False,
                'message': 'Password debe ser de al menos 8 digitos'
            }
        if len(password) > 25:
            return {
                'valid': False,
                'message': 'Password debe no debe ser superior a 20 digitos'
            }
        if len(password.split(' ')) > 1:
            return {
                'valid': False,
                'message': 'Password no debe tener espacios'
            }
        if not any(char.isdigit() for char in password):
            return {
                'valid': False,
                'message': 'Password debe contener un número'
            }
        if not any(char.isupper() for char in password):
            return {
                'valid': False,
                'message': 'Password debe contener una letra mayúsculas'
            }
        if not any(char.islower() for char in password):
            return {
                'valid': False,
                'message': 'Password debe contener un letra minúscula'
            }
        if not any(char in special_char for char in password):
            return {
                'valid': False,
                'message': 'Password debe contener un caracter especial: ' + ', '.join(special_char) # noqa
            }
        return {'valid': True}


    @staticmethod
    def set_log_status_user(user, ip):
        time_expired = datetime.now() - TEST_AUTH_EXPIRED_TIME
        user_log, created = UserStatusLog.objects.get_or_create(
            user=user,
            updated_at__gte=time_expired,
            defaults={
                'ip': ip,
                'user_status_id': 1,
                'attempt': 1
            }
        )
        attempts = user_log.attempt + 1
        if not created and attempts <= LIMIT:
            user_log.user = user
            user_log.ip = ip
            user_log.user_status_id = 3 if attempts >= LIMIT else 1
            user_log.attempt = attempts
            user_log.save()

    @staticmethod
    def is_blocked_user(user: str, ip: str) -> bool:
        time_expired = datetime.now() - TEST_AUTH_EXPIRED_TIME
        user_status = UserStatusLog.objects.filter(
            user=user, user_status_id=3, updated_at__gte=time_expired
        ).first()
        return False if user_status is None else True
