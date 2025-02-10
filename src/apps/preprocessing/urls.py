from django.urls import path

from . import views

urlpatterns = [
    path("preprocess_data/", views.preprocess_data, name="preprocess_data"),
]
