from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import CredentialViewSet, ProjectViewSet, ReminderViewSet
from .views import UserViewSet, UserSignupView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'credentials', CredentialViewSet, basename='credential')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'reminders', ReminderViewSet, basename='reminder')

urlpatterns = [
    path('users/sign-up/', UserSignupView.as_view(), name='sign_up'),
    path('users/sign-in/', TokenObtainPairView.as_view(), name='token_sign_in'),
    path('users/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
urlpatterns += router.urls