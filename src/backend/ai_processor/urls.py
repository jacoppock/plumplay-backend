from django.urls import path

from . import views

urlpatterns = [
    path("process_voice_memo/", views.process_voice_memo, name="process_voice_memo"),
]
