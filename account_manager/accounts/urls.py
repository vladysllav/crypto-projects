from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CredentialViewSet, ProjectViewSet, ReminderViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'credentials', CredentialViewSet, basename='credential')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'reminders', ReminderViewSet, basename='reminder')

urlpatterns = router.urls
