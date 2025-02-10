from django.urls import path

from . import views

urlpatterns = [
    path("scrape_past_events/", views.scrape_past_events, name="scrape_past_events"),
    path("scrape_next_event/", views.scrape_next_event, name="scrape_next_event"),
]
