from rest_framework import serializers
from reports.models import Analyst

class AnalystSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analyst
        fields = '__all__'