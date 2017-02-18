from django.conf.urls import url

from portfolios import views

urlpatterns = [
  url(r'^$', views.index, name='index'),
]
