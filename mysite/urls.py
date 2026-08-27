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
    path("handle_specifications", views.handle_specifications, name="handle_specifications"),
    path("manual_sorting", views.manual_sorting, name="manual_sorting"),
    path("sort_manually", views.sort_manually, name="sort_manually"),
    path("calculate_route", views.calculate_route, name="calculate_route"),
    path("register", views.register, name="register"),
    path("login_view", views.login_view, name="login_view"),
    path("logout_view", views.logout_view, name="logout_view"),
    path("save_groups", views.save_groups, name="save_groups"),
    path("admin/", admin.site.urls),
]
