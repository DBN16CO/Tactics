from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<game_id>[0-9]+)/attack/$', views.attack, name='attack'),
]