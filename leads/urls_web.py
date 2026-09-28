from django.urls import path
from .views_web import (
    login_view,
    logout_view,
    dashboard_view,
    leads_list_view,
    lead_create_view,
    lead_detail_view,
    lead_edit_view
)

urlpatterns = [
    path('', dashboard_view, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('leads/', leads_list_view, name='leads_list'),
    path('leads/create/', lead_create_view, name='lead_create'),
    path('leads/<int:pk>/', lead_detail_view, name='lead_detail'),
    path('leads/<int:pk>/edit/', lead_edit_view, name='lead_edit'),
]
