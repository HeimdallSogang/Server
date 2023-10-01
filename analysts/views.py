from rest_framework import generics, viewsets
from rest_framework import filters as drf_filters

from analysts.serializers import AnalystSerializer
from analysts.pagination import CustomPageNumberPagination
from reports.models import Analyst, Report
from reports.serializers import ReportSerializer

from django_filters import rest_framework as filters


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


class AnalystViewSet(viewsets.ModelViewSet):
    queryset = Analyst.objects.all()
    serializer_class = AnalystSerializer
