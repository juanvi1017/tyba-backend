from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler


class CustomAPIException(APIException):
    status_code = 400
    default_detail = 'Ha ocurrido un error.'
    default_code = 'error'

    def __init__(self, detail=None, code=None, status_code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        if status_code is not None:
            self.status_code = status_code

        self.detail = {
            'message': detail,
            'code': code
        }


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if getattr(response, 'data', False):
        print(response.data)
    if isinstance(exc, CustomAPIException):
        response = Response(exc.detail, status=exc.status_code)
    elif response is not None:
        response.data = {
            'message': response.data.get('detail', 'Ha ocurrido un error.'),
            'code': response.data.get('code', 'error')
        }

    return response
