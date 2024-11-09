from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import RecordAPIView, TopRecordsBySellerAPIView, TopRecordsByBudgetAPIView
from .views import RecommenderAPIView
urlpatterns = [
    path("records/", RecordAPIView.as_view(), name="record-list"),
    path("records/top-sellers/", TopRecordsBySellerAPIView.as_view(), name="top-sellers"),
    path("records/by-budget/", TopRecordsByBudgetAPIView.as_view(), name="records-by-budget"),
    path("records/recommender/", RecommenderAPIView.as_view(), name="recommender"),
]
