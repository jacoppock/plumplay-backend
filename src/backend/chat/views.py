# chat/views.py
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "chat/index.html")


def chat_view(request: HttpRequest) -> HttpResponse:
    return render(request, "chat/chat.html")
