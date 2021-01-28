from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register('database', views.DatabaseViewSet)
router.register('ecs', views.EcsViewSet)
router.register('ecs_list', views.ReadOnlyEcsViewSet)
router.register('staff', views.StaffApiViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
