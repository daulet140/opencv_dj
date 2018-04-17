from django.conf.urls import url

from . import views

app_name = 'detector'
urlpatterns = [
    # url('', views.index, name='index'),
    url('', views.AnalyticsIndexView.as_view(), name='static'),
]
