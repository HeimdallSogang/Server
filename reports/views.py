from django.shortcuts import render

# Create your views here.
from rest_framework.viewsets import ModelViewSet
from .serializers import *
from .models import *

class CurrencyViewSet(ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


class ReportViewSet(ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer


class StockViewSet(ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer


class PointViewSet(ModelViewSet):
    queryset = Point.objects.all()
    serializer_class = PointSerializer


class WritesViewSet(ModelViewSet):
    queryset = Writes.objects.all()
    serializer_class = WritesSerializer