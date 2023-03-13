from rest_framework.routers import DefaultRouter

from user.views import UserViewSet, UserFieldViewSet, DynamicFieldViewSet

app_name = 'user'

router = DefaultRouter()

router.register('dynamic-fields', DynamicFieldViewSet, basename='dynamic-fields')
router.register('fields', UserFieldViewSet, basename='user-fields')
router.register('', UserViewSet, basename='user')

urlpatterns = router.urls
