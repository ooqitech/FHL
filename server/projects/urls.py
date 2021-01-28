from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register('index', views.ProjectApiViewSet)
router.register('full', views.PublicProjectApiViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
