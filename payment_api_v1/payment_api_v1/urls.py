from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from payment_api_v1.views import AccountViewSet


router = DefaultRouter()
router.register(r'account', AccountViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
