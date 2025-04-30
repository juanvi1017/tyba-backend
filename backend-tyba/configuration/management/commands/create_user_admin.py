from django.core.management.base import BaseCommand
from user_auth.models import User


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='User name')
        parser.add_argument('password', type=str, help='User pass')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']

        user = User.objects.create(
            id=username,
            full_name='Admin',
            user_status_id=1,
            group_id=1,
            first_login=False,
        )

        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS('Successfully'))
