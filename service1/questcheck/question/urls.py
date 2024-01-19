from django.urls import path
from . import views

urlpatterns = [
    path('questions/', views.top3question, name='questions'),
    path('home/', views.home, name='home')
]