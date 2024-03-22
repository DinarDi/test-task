from django.urls import path, include

from rest_framework import routers

from api_v1.views import ProductViewSet


router = routers.SimpleRouter()
router.register('products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls))
]
