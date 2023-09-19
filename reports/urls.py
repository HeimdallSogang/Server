from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

router.register(r'report', ReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]