import logging

from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.routers import DynamicRoute, Route, SimpleRouter

logger_debug = logging.getLogger('debug_info')


class TestRouter(SimpleRouter):
    """
    A router for read-only APIs, which doesn't use trailing slashes.
    """
    routes = [

        Route(
            url=r'^{prefix}/list{trailing_slash}$',
            mapping={'get': 'list'},
            name='{basename}-list',
            detail=False,
            initkwargs={'suffix': 'List'}
        ),
        Route(
            url=r'^{prefix}/create{trailing_slash}$',
            mapping={'post': 'create'},
            name='{basename}-create',
            detail=False,
            initkwargs={'suffix': 'Create'}
        ),
        # Dynamically generated list routes. Generated using
        # @action(detail=False) decorator on methods of the viewset.
        DynamicRoute(
            url=r'^{prefix}/{url_path}{trailing_slash}$',
            name='{basename}-{url_name}',
            detail=False,
            initkwargs={}
        ),
        # Detail route.
        Route(
            url=r'^{prefix}/detail/{lookup}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            detail=True,
            initkwargs={'suffix': 'Instance'}
        ),
        # Update
        Route(
            url=r'^{prefix}/detail/{lookup}{trailing_slash}$',
            mapping={'put': 'update'},
            name='{basename}-update',
            detail=True,
            initkwargs={'suffix': 'Instance'}
        ),
        # Delete
        Route(
            url=r'^{prefix}/detail/{lookup}{trailing_slash}$',
            mapping={'delete': 'destroy'},
            name='{basename}-delete',
            detail=True,
            initkwargs={'suffix': 'Instance'}
        ),
        DynamicRoute(
            url=r'^{prefix}/{lookup}/{url_path}{trailing_slash}$',
            name='{basename}-{url_name}',
            detail=True,
            initkwargs={}
        ),
    ]


class TestPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 20
    page_query_param = 'page'

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page_number': self.page.number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })
