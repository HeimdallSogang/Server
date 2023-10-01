from django.db.models import Min
from rest_framework import viewsets, generics
from rest_framework import filters as drf_filters

from reports.serializers import (
    PointSerializer,
    ReportSerializer,
    StockSerializer,
    WritesSerializer,
)
from reports.models import Point, Report, Stock, Writes
from analysts.pagination import CustomPageNumberPagination

from django_filters import rest_framework as filters


class StockReportFilter(filters.FilterSet):
    publish_date = filters.DateFromToRangeFilter()
    min_hit_rate = filters.NumberFilter(field_name="hit_rate", lookup_expr="gte")
    min_analyst_hit_rate = filters.NumberFilter(
        method="filter_by_min_hit_rate", label="Minimum hit rate of analyst"
    )

    class Meta:
        model = Report
        fields = ["publish_date", "min_hit_rate", "min_analyst_hit_rate"]

    def filter_by_min_hit_rate(self, queryset, name, value):
        # Annotate each report with the minimum analyst hit rate
        queryset = queryset.annotate(min_hit_rate=Min("writes__analyst__hit_rate"))

        # Filter by the annotated field
        return queryset.filter(min_hit_rate__gte=value)


class StockReportsView(generics.ListAPIView):
    serializer_class = ReportSerializer
    filter_backends = [filters.DjangoFilterBackend, drf_filters.OrderingFilter]
    filterset_class = StockReportFilter
    ordering_fields = ["publish_date", "hit_rate"]
    ordering = ["-hit_rate", "-publish_date"]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        stock_id = self.kwargs["pk"]
        return Report.objects.filter(stock_id=stock_id)


class AnalystReportFilter(filters.FilterSet):
    publish_date = filters.DateFromToRangeFilter()
    sentiment = filters.ChoiceFilter(
        field_name="written_sentiment", choices=Report.SENTIMENT_CHOICES
    )
    stock_id = filters.NumberFilter()

    class Meta:
        model = Report
        fields = ["publish_date", "sentiment", "stock_id"]


class AnalystReportsView(generics.ListAPIView):
    serializer_class = ReportSerializer
    filter_backends = [filters.DjangoFilterBackend, drf_filters.OrderingFilter]
    filterset_class = AnalystReportFilter
    ordering_fields = ["publish_date", "hit_rate"]
    ordering = ["-hit_rate", "-publish_date"]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        analyst_id = self.kwargs["pk"]
        return Report.objects.filter(writes__analyst_id=analyst_id)


class StockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer


class PointViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Point.objects.all()
    serializer_class = PointSerializer


class WritesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Writes.objects.all()
    serializer_class = WritesSerializer
