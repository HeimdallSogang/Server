from rest_framework import serializers
from reports.models import *


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = "__all__"


class ReportSerializer(serializers.ModelSerializer):
    target_price = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = "__all__"

    def get_target_price(self, obj):
        # Define your custom logic to serialize the target_price field
        # For example, you can access the target_price from the model object (obj)
        return obj.target_price


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = "__all__"


class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = "__all__"


class WritesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Writes
        fields = "__all__"


## http://127.0.0.1:8000/reports/test/
class StockPageSerializer(serializers.ModelSerializer):
    ## point에 대한 정보
    points = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            "points",
            "target_price",
            "publish_date",
            "hit_rate",
            "days_to_first_hit",
            "days_to_first_miss",
        ]

    ## 현재 리포트에 대한 부정포인트 추출
    def get_points(self, obj):
        points = Point.objects.filter(report=obj)[
            :3
        ]  ## 더보기를 누르기 전에는 최대 3개의 부정포인트만 추출하도록 함
        point_serializer = PointSerializer(points, many=True)
        content_list = [item["content"] for item in point_serializer.data]
        return content_list
