from django_filters import rest_framework as filters
from advertisements.models import Advertisement, Favorite


class AdvertisementFilter(filters.FilterSet):
    created_at = filters.DateTimeFromToRangeFilter()
    is_favorite = filters.BooleanFilter(label='is_favorite', method='filter_favorites')

    class Meta:
        model = Advertisement
        fields = ['status', 'created_at']

    def filter_favorites(self, queryset, name, value):
        favorite_ids = Favorite.objects.filter(user=self.request.user).values('advertisement')
        return queryset.filter(id__in=favorite_ids) if value else queryset.exclude(id__in=favorite_ids)
