from django.shortcuts import render

# Create your views here.
from rest_framework.viewsets import ModelViewSet
from .serializers import *
from .models import *
from django_filters import rest_framework as django_filters
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action

class CustomPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

class ReportFilter(django_filters.FilterSet):
    date_range = django_filters.DateFromToRangeFilter(field_name="publish_date")
    hit_rate_min = django_filters.NumberFilter(field_name="hit_rate", lookup_expr='gte')
    
    class Meta:
        model = Report
        fields = ['date_range', 'hit_rate_min']

class CurrencyViewSet(ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

class ReportViewSet(ModelViewSet):
    serializer_class = ReportSerializer
    filter_backends = (filters.OrderingFilter, django_filters.DjangoFilterBackend)
    filterset_class = ReportFilter
    ordering_fields = ['publish_date', 'hit_rate']
    ordering = ['-hit_rate', '-publish_date']
    pagination_class = CustomPagination
    queryset = Report.objects.all()
    
    def list(self, request, *args, **kwargs):
        stock_id = kwargs.get('stock_id', None)
        if stock_id:
            self.queryset = self.queryset.filter(stock_id=stock_id)
        return super().list(request)
    
    def by_stock(self, request, stock_id=None):
        reports = Report.objects.filter(stock_id=stock_id)
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data)

class StockViewSet(ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer


class PointViewSet(ModelViewSet):
    queryset = Point.objects.all()
    serializer_class = PointSerializer


class WritesViewSet(ModelViewSet):
    queryset = Writes.objects.all()
    serializer_class = WritesSerializer