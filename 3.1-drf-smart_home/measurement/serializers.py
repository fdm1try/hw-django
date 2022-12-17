from rest_framework import serializers
from measurement.models import Sensor, TemperatureSensorData


class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemperatureSensorData
        fields = ['temperature', 'created_at', 'photo']


class MeasurementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemperatureSensorData
        fields = ['sensor_id', 'temperature', 'created_at', 'photo']


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ['id', 'name', 'description']


class SensorDetailSerializer(serializers.ModelSerializer):
    measurements = MeasurementSerializer(read_only=True, many=True)

    class Meta:
        model = Sensor
        fields = ['id', 'name', 'description', 'measurements']
