from django.shortcuts import render
from django.http import HttpResponse

def top3question(request):
    return HttpResponse("Hello world!")

def home(request):
    return HttpResponse("Home")