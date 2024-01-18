from django.urls import path
from . import views

urlpatterns = [
    path("questions2/", views.setData, name="questions"),
    path("questions2/create", views.create_if_not_exists, name="questions"),
]
