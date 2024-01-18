from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from .models import Question2


def setData(request):
    question_instance = Question2()
    question_instance.set_data()
    return HttpResponse("successful!")


@api_view(["POST"])
def create_if_not_exists(request):
    question_instance = Question2()
    question_instance.create_quest(request=request)
    return HttpResponse("successful!")
