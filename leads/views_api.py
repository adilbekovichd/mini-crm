from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .models import Lead, LeadActivity
from .serializers import LeadSerializer, LeadActivitySerializer
from .filters import LeadFilter
from .pagination import StandardResultsSetPagination


class LeadViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows leads to be created, viewed, edited, filtered and deleted.
    """
    queryset = Lead.objects.all().select_related('assigned_to')
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = LeadFilter
    search_fields = ['name', 'phone', 'email', 'source', 'note']
    ordering_fields = ['created_at', 'updated_at', 'name', 'status']
    ordering = ['-created_at']

    @extend_schema(
        summary="Retrieve activity history for a specific lead",
        responses={200: LeadActivitySerializer(many=True)}
    )
    @action(detail=True, methods=['get'], url_path='activities')
    def activities(self, request, pk=None):
        lead = self.get_object()
        activities = lead.activities.all().select_related('user').order_by('-created_at')
        serializer = LeadActivitySerializer(activities, many=True)
        return Response(serializer.data)


class DashboardStatsAPIView(APIView):
    """
    API endpoint that returns aggregate statistics for the CRM dashboard.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get CRM dashboard summary metrics",
        responses={200: OpenApiTypes.OBJECT}
    )
    def get(self, request, *args, **kwargs):
        qs = Lead.objects.all()
        total = qs.count()
        new_count = qs.filter(status=Lead.StatusChoices.NEW).count()
        contacted_count = qs.filter(status=Lead.StatusChoices.CONTACTED).count()
        qualified_count = qs.filter(status=Lead.StatusChoices.QUALIFIED).count()
        won_count = qs.filter(status=Lead.StatusChoices.WON).count()
        lost_count = qs.filter(status=Lead.StatusChoices.LOST).count()

        return Response({
            "total": total,
            "new": new_count,
            "contacted": contacted_count,
            "qualified": qualified_count,
            "won": won_count,
            "lost": lost_count
        })
