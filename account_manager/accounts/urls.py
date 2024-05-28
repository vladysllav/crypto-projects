from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from .views import UserViewSet,UserSignupView
from django.urls import path
router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('users/signup/', UserSignupView.as_view(), name='signup'),
    path('users/signin/', TokenObtainPairView.as_view(), name='token_signin'),
    path('users/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
urlpatterns += router.urls