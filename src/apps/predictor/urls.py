from django.urls import path
from . import views

urlpatterns = [
    path("predictor/", views.predictor, name="predictor"),
    path("next_event/", views.show_next_event, name="next_event"),
]
