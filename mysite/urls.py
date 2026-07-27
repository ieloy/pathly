from django.contrib import admin
from django.urls import path
from pathly import views

urlpatterns = [
    path("", views.index, name="index"),
    path("routes", views.routes, name="routes"),
    path("mapinfo", views.mapinfo, name="mapinfo"),
    path("sorting", views.sorting, name="sorting"),
    path("adminkml", views.adminkml, name="adminkml"),
    path("about", views.about, name="about"),
    path("handle_kml", views.handle_kml, name="handle_kml"),
    path("get_places", views.get_places, name="get_places"),
    path("handle_specifications", views.handle_specifications, name="handle_specifications"),
    path("apply_specifications", views.apply_specifications, name="apply_specifications"),
    path("admin/", admin.site.urls),
]
