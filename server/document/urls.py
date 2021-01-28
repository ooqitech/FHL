from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register('rsync', views.RsyncApiViewSet)
router.register('', views.DocumentApiViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
