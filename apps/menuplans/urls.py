from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='menuplans.index'),
    url(r'^create/$', views.create, name='menuplans.create'),
    url(r'^(?P<pk>[0-9a-z-]+)/$', views.detail, name='menuplans.detail')
]
