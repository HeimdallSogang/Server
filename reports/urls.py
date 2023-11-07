from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

# router.register(r"stock", StockViewSet)
router.register(r"point", PointViewSet)
router.register(r"writes", WritesViewSet)


urlpatterns = [
    path("", include(router.urls)),
    # path("test/<str:stock_name>/", TestViewSet.as_view(), name="stock-page"),  ## 테스트용
]
