# TODO: опишите необходимые обработчики, рекомендуется использовать generics APIView классы:
# TODO: ListCreateAPIView, RetrieveUpdateAPIView, CreateAPIView
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from measurement.models import Sensor, TemperatureSensorData
from measurement.serializers import SensorSerializer, TemperatureSensorDataSerializer
from django.http import Http404


class SensorListView(ListAPIView):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer


class SensorCreateView(CreateAPIView):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer


class SensorView(RetrieveUpdateAPIView):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer


class SensorDataView(CreateAPIView):
    queryset = TemperatureSensorData.objects.filter()
    serializer_class = TemperatureSensorDataSerializer

    def post(self, request, *args, **kwargs):
        sensor = Sensor.objects.filter(id=kwargs.get('sensor_id')).first()
        if not sensor:
            raise Http404
        temperature = request.data.get('temperature')
        try:
            sensor.measurements.add(TemperatureSensorData(temperature=temperature), bulk=False)
        except Exception as e:
            return Response(status=HTTP_400_BAD_REQUEST, data={'details': str(e)})
        return Response()
