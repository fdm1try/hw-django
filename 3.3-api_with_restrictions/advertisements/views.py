from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.viewsets import ModelViewSet
from advertisements.models import Advertisement, Favorite
from advertisements.permissions import CanModerate
from advertisements.serializers import AdvertisementSerializer
from django_filters import rest_framework as filters
from advertisements.models import AdvertisementStatusChoices
from django.db.models import Q
from rest_framework.exceptions import APIException, NotFound


class AdvertisementFilter(filters.FilterSet):
    created_at = filters.DateTimeFromToRangeFilter()
    is_favorite = filters.BooleanFilter(label='is_favorite', method='filter_favorites')

    class Meta:
        model = Advertisement
        fields = ['status', 'created_at']

    def filter_favorites(self, queryset, name, value):
        favorite_ids = Favorite.objects.filter(user=self.request.user).values('advertisement')
        return queryset.filter(id__in=favorite_ids) if value else queryset.exclude(id__in=favorite_ids)


class AdvertisementViewSet(ModelViewSet):
    """ViewSet для объявлений."""
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdvertisementFilter

    # TODO: настройте ViewSet, укажите атрибуты для кверисета,
    #   сериализаторов и фильтров

    def get_queryset(self):
        if self.request.user and not self.request.user.is_anonymous:
            return self.queryset.filter(Q(creator=self.request.user) | ~Q(status=AdvertisementStatusChoices.DRAFT))
        return self.queryset.exclude(status=AdvertisementStatusChoices.DRAFT)

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), CanModerate()]
        return []

    @action(methods=['get'], detail=False)
    def favorites(self, request):
        favorites = [
            self.get_serializer(item.advertisement).data
            for item in Favorite.objects.filter(user=request.user)
        ]
        return Response(favorites)

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk=None):
        advertisements = Advertisement.objects.filter(id=pk)
        if not advertisements.exists():
            raise NotFound('Advertisement not found.')
        advertisement = advertisements.first()
        if advertisement.status == AdvertisementStatusChoices.DRAFT:
            raise NotFound('Advertisement not found.')
        if request.method.lower() == 'delete':
            favorite = Favorite.objects.filter(user=request.user, advertisement=advertisement)
            if not favorite.exists():
                raise NotFound('Advertisement not found in your favorites.')
            try:
                favorite.delete()
            except Exception as e:
                raise APIException(str(e))
            return Response(1)
        if request.method.lower() == 'post':
            if advertisement.user == request.user:
                raise APIException('This is your own adv.')
            if Favorite.objects.filter(user=request.user, advertisement=advertisement).exists():
                raise APIException('This advertisement is already your favorite.')
            favorite = Favorite(user=request.user, advertisement=advertisement)
            favorite.save()
            return Response(self.get_serializer(advertisement).data)
