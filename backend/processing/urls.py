from django.urls import path
from .views import ProcessDataView

urlpatterns = [
    path("data/receive/", ProcessDataView.as_view(), name="process_data"),
]
