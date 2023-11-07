from rest_framework import serializers
from reports.models import *
from analysts.serializers import *


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = "__all__"


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = "__all__"


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


class StockReportSerializer(serializers.ModelSerializer):
    points = serializers.SerializerMethodField()
    analyst_data = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            "id",
            "points",
            "target_price",
            "publish_date",
            "hit_rate",
            "days_to_first_hit",
            "days_to_first_miss",
            "analyst_data",
        ]

    ## 현재 리포트에 대한 부정포인트 추출
    def get_points(self, obj):
        points = Point.objects.filter(report=obj)[
            :3
        ]  ## 더보기를 누르기 전에는 최대 3개의 부정포인트만 추출하도록 함
        point_serializer = PointSerializer(points, many=True)
        content_list = [item["content"] for item in point_serializer.data]
        return content_list

    ## 애널리스트 정보 추출
    def get_analyst_data(self, obj):
        writes = Writes.objects.filter(report=obj)
        analyst_id = writes.values_list("analyst_id", flat=True).first()

        if analyst_id is not None:
            analyst = Analyst.objects.get(id=analyst_id)
            analyst_serializer = AnalystSerializer(
                analyst
            )  # AnalystSerializer를 사용하여 시리얼라이즈

            name = analyst_serializer.data["name"]
            avg_days_hit = analyst_serializer.data["avg_days_hit"]
            avg_days_to_first_hit = analyst_serializer.data["avg_days_to_first_hit"]
            avg_days_to_first_miss = analyst_serializer.data["avg_days_to_first_miss"]

            analyst_data = {
                "name": name,
                "analyst_history": {
                    "avg_days_hit": avg_days_hit,
                    "avg_days_to_first_hit": avg_days_to_first_hit,
                    "avg_days_to_first_miss": avg_days_to_first_miss,
                },
            }
            return analyst_data
        else:
            return None  # 해당하는 analyst_id가 없을 경우 None 반환


class AnalystReportSerializer(serializers.ModelSerializer):
    points = serializers.SerializerMethodField()
    stock_name = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            "id",
            "points",
            "target_price",
            "publish_date",
            "stock_name",
            "hidden_sentiment",
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

    ## 애널리스트 정보 추출
    def get_stock_name(self, obj):
        return obj.stock.name
