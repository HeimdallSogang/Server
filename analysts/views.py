from django.shortcuts import render

# Create your views here.
from rest_framework.viewsets import ModelViewSet
from .serializers import *

class AnalystViewSet(ModelViewSet):
    queryset = Analyst.objects.all()
    serializer_class = AnalystSerializer