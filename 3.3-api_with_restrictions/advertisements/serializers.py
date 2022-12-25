import re
from django.contrib.auth.models import User
from rest_framework import serializers
from advertisements.models import Advertisement, AdvertisementStatusChoices
from rest_framework.exceptions import APIException, ValidationError
from api_with_restrictions.settings import API_LIMITS

RE_VALIDATE_TITLE = re.compile(r'^[A-Za-zА-Яа-я][A-Za-z А-Яа-я\[\]\d\-_()]{2,}$')


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at', )

    def create(self, validated_data):
        """Метод для создания"""

        # Простановка значения поля создатель по-умолчанию.
        # Текущий пользователь является создателем объявления
        # изменить или переопределить его через API нельзя.
        # обратите внимание на `context` – он выставляется автоматически
        # через методы ViewSet.
        # само поле при этом объявляется как `read_only=True`
        creator = self.context['request'].user
        validated_data['creator'] = creator
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""
        # TODO: добавьте требуемую валидацию
        request_method = self.context['request'].method
        creator = self.context['request'].user
        if request_method == 'POST' or (
                 request_method in ['PATCH', 'UPDATE']
                 and 'status' in data
                 and data['status'] == AdvertisementStatusChoices.OPEN
        ):
            open_adv_count = len(Advertisement.objects.filter(creator=creator, status=AdvertisementStatusChoices.OPEN))
            if open_adv_count >= API_LIMITS.get('LIMIT_USER_MAX_ADV_COUNT'):
                raise APIException('The limit on the number of open ads has been reached')
        if 'title' in data and not RE_VALIDATE_TITLE.match(data.get('title')):
            raise ValidationError('Invalid title format.')
        return data
