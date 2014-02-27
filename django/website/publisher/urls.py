from django.conf.urls import patterns, url

from .views import (
    PublisherListView,
    PublisherDetailView,
)

urlpatterns = patterns("",
    url(r'^$', PublisherListView.as_view(), name='publishers',),
    url(r'^g/(?P<slug>[-\w]+)/$', PublisherDetailView.as_view(), name='publisher',),
)
