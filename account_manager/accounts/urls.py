from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import CredentialListView as creds
from .views import ProjectListView as project
from .views import TaskListView as task
from .views import UserViewSet, UserSignupView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('sign-up/', UserSignupView.as_view(), name='sign_up'),
    path('sign-in/', TokenObtainPairView.as_view(), name='sign_in'),
    path('token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('users/<int:user_id>/projects/', project.as_view(), name='projects'),
    path('users/<int:user_id>/projects/<slug:slug>/', project.as_view(), name='one_project'),

    path('users/<int:user_id>/projects/<slug:slug>/tasks/', task.as_view(), name='project_tasks'),
    path('users/<int:user_id>/projects/<slug:slug>/tasks/<int:id>/', task.as_view(), name='one_project_task'),

    path('users/<int:user_id>/projects/<slug:slug>/credentials/', creds.as_view(), name='project_creds'),
    path('users/<int:user_id>/projects/<slug:slug>/credentials/<int:id>/', creds.as_view(), name='one_project_cred'),
]
urlpatterns += router.urls
