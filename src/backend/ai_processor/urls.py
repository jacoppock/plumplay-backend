from django.urls import path

from . import views

urlpatterns = [
    path("", views.some_view, name="ai_processor_home"),  # New view for ai_processor home
    path("process_voice_memo/", views.process_voice_memo, name="process_voice_memo"),
]
