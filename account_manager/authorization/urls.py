from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from user.views import UserSignupView

router = DefaultRouter()

urlpatterns = [
    path("sign-up/", UserSignupView.as_view(), name="sign_up"),
    path("sign-in/", TokenObtainPairView.as_view(), name="sign_in"),
    path("token-refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
urlpatterns += router.urls
