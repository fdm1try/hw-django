from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.viewsets import ModelViewSet
from advertisements.filters import AdvertisementFilter
from advertisements.models import Advertisement, Favorite
from advertisements.permissions import CanModerate
from advertisements.serializers import AdvertisementSerializer
from advertisements.models import AdvertisementStatusChoices
from django.db.models import Q


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
            return Response(data={'details': 'Advertisement not found.'}, status=404)
        advertisement = advertisements.first()
        if advertisement.status == AdvertisementStatusChoices.DRAFT:
            return Response(data={'details': 'Advertisement not found.'}, status=404)

        if request.method.lower() == 'delete':
            favorite = Favorite.objects.filter(user=request.user, advertisement=advertisement)
            if not favorite.exists():
                return Response(data={'details': 'Advertisement not found.'}, status=404)
            try:
                favorite.delete()
            except Exception:
                return Response(data={'details': 'Internal server error.'}, status=500)
            return Response(1)

        if request.method.lower() == 'post':
            if advertisement.creator == request.user:
                return Response(data={'details': 'It is forbidden to add your own advertisement to favorites.'},
                                status=400)
            if Favorite.objects.filter(user=request.user, advertisement=advertisement).exists():
                return Response(self.get_serializer(advertisement).data)
            favorite = Favorite(user=request.user, advertisement=advertisement)
            favorite.save()
            return Response(self.get_serializer(advertisement).data)
