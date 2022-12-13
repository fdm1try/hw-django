from rest_framework import serializers
from measurement.models import Sensor, TemperatureSensorData


class TemperatureSensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemperatureSensorData
        fields = ['temperature', 'created_at', 'photo']


class SensorSerializer(serializers.ModelSerializer):
    measurements = TemperatureSensorDataSerializer(read_only=True, many=True)

    class Meta:
        model = Sensor
        fields = ['id', 'name', 'description', 'measurements']
