from rest_framework import viewsets

from analysts.serializers import AnalystSerializer
from reports.models import Analyst


class AnalystViewSet(viewsets.ModelViewSet):
    queryset = Analyst.objects.all()
    serializer_class = AnalystSerializer
