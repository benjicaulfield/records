from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import RecordAPIView, TopRecordsBySellerAPIView, TopRecordsByBudgetAPIView
from .views import RecommenderAPIView, DashboardRecordsAPIView
from .views import LoginView, LogoutView, UserView, RegisterView

urlpatterns = [
    path("records/", RecordAPIView.as_view(), name="record-list"),
    path("records/top-sellers/", TopRecordsBySellerAPIView.as_view(), name="top-sellers"),
    path("records/by-budget/", TopRecordsByBudgetAPIView.as_view(), name="records-by-budget"),
    path("records/recommender/", RecommenderAPIView.as_view(), name="recommender"),
    path("records/dashboard/", DashboardRecordsAPIView.as_view(), name="dashboard"),
    path("api/login/", LoginView.as_view(), name="login"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("api/user/", UserView.as_view(), name="user"),
    path("api/register/", RegisterView.as_view(), name="register"),
]
