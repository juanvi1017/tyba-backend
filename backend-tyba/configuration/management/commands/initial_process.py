from configuration.models import Group, Permission
from django.apps import apps
from django.core.management.base import BaseCommand
from django.urls import URLPattern, URLResolver, get_resolver


class Command(BaseCommand):
    # List that contain URLPattern object
    all_urls = list()

    def func_for_sorting(self, i):
        if i.name is None:
            i.name = ''
        return i.name

    def show_urls(self, urls):
        for url in urls.url_patterns:
            if isinstance(url, URLResolver):
                self.show_urls(url)
            elif isinstance(url, URLPattern):
                self.all_urls.append(url)

    def handle(self, *args, **kwargs):
        # We get all url clases
        urls = get_resolver()
        # We procced to resolve all url
        self.show_urls(urls)
        self.all_urls.sort(key=self.func_for_sorting, reverse=False)
        exclude_url = ['login', '']
        name_urls = [
            url.name for url in self.all_urls if url.name not in exclude_url
        ]
        current_permission = Permission.objects.all()
        # We proceed to remove the view from permission list
        for permission in current_permission:
            if permission.codename not in name_urls:
                permission.delete()
        # Now we create or update the permission
        for name in name_urls:
            Permission.objects.update_or_create(codename=name)

        items = {}
        # permissions = []
        for app in apps.get_app_configs():
            if hasattr(app, 'permissions'):
                for permission in app.permissions:
                    for role in permission['role']:
                        if role not in items.keys():
                            items[role] = permission['permissions']
                        else:
                            items[role].extend(
                                permission['permissions']
                            )
        for role, permissions in items.items():
            try:
                group = Group.objects.get(id=role)
            except Group.DoesNotExist:
                # self.stdout.write(self.style.ERROR(f"Group with id {role} does not exist."))
                return
            group.permission.clear()
            all_permission = Permission.objects.filter(codename__in=permissions)
            for permission in all_permission:
                group.permission.add(permission)

        self.stdout.write(
                self.style.WARNING(
                    '--->:::Update: process and permissions:::<---'
                )
            )
