from django.urls import path

from reports.views import StockReportsView

urlpatterns = [
    path('<int:pk>/reports/', StockReportsView.as_view(), name='stock-reports'),
]