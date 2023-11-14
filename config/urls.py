"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.static import serve
from django.urls import re_path
from . import settings

urlpatterns = [
    path("sellpointadministrator/", admin.site.urls),
    path("analysts/", include("analysts.urls")),
    path("reports/", include("reports.urls")),
    path("stocks/", include("stocks.urls")),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(
        r"^static/(?:.*)$",
        serve,
        {
            "document_root": settings.STATIC_ROOT,
        },
    ),
]

if settings.DEBUG is True:
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
