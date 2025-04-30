import logging
from django.urls import resolve
from rest_framework.permissions import BasePermission


class TestModelPermissions(BasePermission):

    def has_permission(self, request, view):
        response_has = False
        # we verify user
        logger_debug = logging.getLogger('debug_info')
        logger_debug.debug(
            f'{resolve(request.path_info).url_name}: {request.path}'
        )
        view_name = resolve(request.path_info).url_name
        if (not request.user.is_anonymous and request.user.is_authenticated
                and request.user.has_perm(view_name)):
            response_has = True
        return response_has
