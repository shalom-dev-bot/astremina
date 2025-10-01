from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from properties.models import Property, Favorite, Alert
from partners.models import Partner, Contract
from scraping.models import ScrapingSource
from scraping.tasks import scrape_source

from .serializers import (
    UserSerializer, PropertySerializer, PropertyListSerializer,
    FavoriteSerializer, AlertSerializer, PartnerSerializer, ContractSerializer
)
from .filters import PropertyFilter
from .permissions import IsOwnerOrReadOnly, IsPartnerOrAdmin

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get', 'put'])
    def me(self, request):
        """Profil de l'utilisateur connecté"""
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.filter(status='published').select_related('owner').prefetch_related('images')
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = PropertyFilter
    search_fields = ['title', 'description', 'city', 'neighborhood']
    ordering_fields = ['created_at', 'price', 'title']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PropertyListSerializer
        return PropertySerializer
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=False, methods=['get'])
    def search_by_bbox(self, request):
        """Recherche par bounding box pour la carte"""
        min_lat = request.query_params.get('min_lat')
        min_lng = request.query_params.get('min_lng')
        max_lat = request.query_params.get('max_lat')
        max_lng = request.query_params.get('max_lng')
        
        if not all([min_lat, min_lng, max_lat, max_lng]):
            return Response(
                {'error': 'Missing bbox parameters'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        properties = self.get_queryset().filter(
            latitude__gte=min_lat,
            latitude__lte=max_lat,
            longitude__gte=min_lng,
            longitude__lte=max_lng,
            latitude__isnull=False,
            longitude__isnull=False
        )
        
        serializer = PropertyListSerializer(properties, many=True)
        return Response(serializer.data)

class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('property')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AlertViewSet(viewsets.ModelViewSet):
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Alert.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    permission_classes = [IsPartnerOrAdmin]
    
    @action(detail=True, methods=['get'])
    def properties(self, request, pk=None):
        """Propriétés d'un partenaire"""
        partner = self.get_object()
        properties = Property.objects.filter(owner=partner.user)
        serializer = PropertyListSerializer(properties, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def contracts(self, request, pk=None):
        """Contrats d'un partenaire"""
        partner = self.get_object()
        contracts = Contract.objects.filter(partner=partner)
        serializer = ContractSerializer(contracts, many=True)
        return Response(serializer.data)

class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [IsPartnerOrAdmin]

class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        """Statistiques pour le dashboard admin"""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        stats = {
            'total_users': User.objects.count(),
            'active_users_30d': User.objects.filter(last_login__gte=thirty_days_ago).count(),
            'total_properties': Property.objects.count(),
            'published_properties': Property.objects.filter(status='published').count(),
            'total_partners': Partner.objects.count(),
            'active_contracts': Contract.objects.filter(status='active').count(),
        }
        
        return Response(stats)

class ScrapingControlView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        """Déclencher un job de scraping"""
        source_id = request.data.get('source_id')
        
        if not source_id:
            return Response(
                {'error': 'source_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            source = ScrapingSource.objects.get(id=source_id, active=True)
        except ScrapingSource.DoesNotExist:
            return Response(
                {'error': 'Source not found or inactive'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Déclencher la tâche Celery
        scrape_source.delay(source_id)
        
        return Response({
            'message': f'Scraping job started for {source.name}',
            'source_id': source_id
        })