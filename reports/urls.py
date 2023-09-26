from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

router.register(r"currency", CurrencyViewSet)
router.register(r"report", ReportViewSet)
router.register(r"stock", StockViewSet)
router.register(r"point", PointViewSet)
router.register(r"writes", WritesViewSet)


urlpatterns = [
    path("report/by_stock/<int:stock_id>/", ReportViewSet.as_view({'get': 'list'}), name='filtered-reports-by-stock'),
    path("", include(router.urls)),
]
