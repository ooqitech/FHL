from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register('users', views.UserApiViewSet)
router.register('readonly/users', views.ReadOnlyUserApiViewSet)
router.register('readonly/departments', views.ReadOnlyDepartmentApiViewSet)
router.register('departments', views.DepartmentApiViewSet)
router.register('permissions', views.PermissionApiViewSet)
router.register('group', views.GroupApiViewSet)
router.register('config/system', views.SystemConfigApiViewSet)
router.register('config/aliyun', views.AliyunConfigApiViewSet)
router.register('config/ssh', views.SSHConfigApiViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('password_reset/', views.UserPasswordResetApiView.as_view())
]
