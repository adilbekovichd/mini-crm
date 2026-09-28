from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views_api import LeadViewSet, DashboardStatsAPIView

router = DefaultRouter()
router.register(r'leads', LeadViewSet, basename='lead')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/stats/', DashboardStatsAPIView.as_view(), name='dashboard-stats'),
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
]
