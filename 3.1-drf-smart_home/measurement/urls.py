from django.urls import path
from measurement.views import SensorCreateView, SensorListView, SensorView, SensorDataView

urlpatterns = [
    # TODO: зарегистрируйте необходимые маршруты
    path('sensor/add', SensorCreateView.as_view(), name='add_sensor'),
    path('sensors', SensorListView.as_view()),
    path('sensor/<pk>', SensorView.as_view()),
    path('sensor/<int:sensor_id>/add', SensorDataView.as_view()),
]
