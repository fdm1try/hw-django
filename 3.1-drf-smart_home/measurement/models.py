from django.db import models


class Sensor(models.Model):
    name = models.CharField(max_length=40)
    description = models.TextField()


class TemperatureSensorData(models.Model):
    sensor_id = models.ForeignKey(to=Sensor, on_delete=models.CASCADE, related_name='measurements')
    temperature = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(null=True)
