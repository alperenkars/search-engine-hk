from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("clear-history/", views.clear_history, name="clear_history"),
]