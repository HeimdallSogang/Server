from django.shortcuts import render

# Create your views here.
from rest_framework.viewsets import ModelViewSet
from .serializers import *
from .models import *
from django_filters import rest_framework as django_filters
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from reports.models import *

class CustomPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

class AnalystFilter(django_filters.FilterSet):
    date_range = django_filters.DateFromToRangeFilter(field_name="report__publish_date")
    sentiment = django_filters.ChoiceFilter(field_name="report__written_sentiment", choices=Report.SENTIMENT_CHOICES)
    stock = django_filters.ModelChoiceFilter(field_name="report__stock", queryset=Stock.objects.all())

    class Meta:
        model = Analyst
        fields = ['date_range', 'sentiment', 'stock']

class AnalystViewSet(ModelViewSet):
    queryset = Analyst.objects.all()
    serializer_class = AnalystSerializer
    filter_backends = (filters.OrderingFilter, django_filters.DjangoFilterBackend)
    filterset_class = AnalystFilter
    ordering_fields = ['name', 'report__publish_date']