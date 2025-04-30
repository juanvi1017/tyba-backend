from configuration.models import (
    Group,
    UserStatus,
)
from django.core.management.base import BaseCommand

from backend.data_initial import (
    TEST_ROLES,
    TEST_USER_STATUS,
)


class Command(BaseCommand):

    def handle(self, *args, **options):
        """dictionarys with default data"""

        # Updating the Group model with the data in TEST_ROLES.
        print(':::Creating roles:::')

        for rol in TEST_ROLES:
            _, is_new = Group.objects.update_or_create(
                id=rol['id'],
                defaults={"name": rol['name']},
            )
        self.stdout.write(self.style.SUCCESS('Successfully created roles'))

        # Updating the UserStatus model with the data in TEST_USER_STATUS.
        print(':::Creating user status:::')
        for status in TEST_USER_STATUS:
            _, is_new = UserStatus.objects.update_or_create(
                id=status['id'],
                defaults={"description": status['description']},
            )
        self.stdout.write(self.style.SUCCESS(
            'Successfully created user status'))


        self.stdout.write(
            self.style.SUCCESS(
                '-----> Update: initial configurations <-----'
            )
        )
