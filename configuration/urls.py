from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404
from .views import custom_404_view

handler404 = custom_404_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("authentication.urls")),
    path("api/librarian/", include("librarian.urls")),
    path("api/libraryusers/", include("libraryusers.urls")),
]
