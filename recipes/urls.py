from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='recipes.index'),
    url(r'^create/$', views.create, name='recipes.create'),
    url(r'^(?P<pk>[0-9a-z-]+)/$', views.detail, name='recipes.detail')
]
