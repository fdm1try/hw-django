from django.urls import path
from measurement.views import SensorCreateView, SensorListView, SensorView, MeasurementCreateView, SensorUpdateView

urlpatterns = [
    # TODO: зарегистрируйте необходимые маршруты
    path('sensor/add', SensorCreateView.as_view(), name='add_sensor'),
    path('sensors', SensorListView.as_view()),
    path('sensor/<pk>', SensorView.as_view()),
    path('sensor/<pk>/change', SensorUpdateView.as_view()),
    path('measurement/add', MeasurementCreateView.as_view()),
]
