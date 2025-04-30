# Django
# Views
from django.urls import include, path
from utils.test_utils import TestRouter

router = TestRouter(trailing_slash=False)

urlpatterns = [
    path('', include(router.urls)),
]
