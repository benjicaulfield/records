from django.urls import path
from .views import ScraperDataReceiveView

urlpatterns = [
    path("data/receive/", ScraperDataReceiveView.as_view(), name="data-receive"),
]
