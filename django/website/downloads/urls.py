from django.conf.urls import patterns, url

from downloads.views import (
    GetDownloadView,
)

urlpatterns = patterns(
    '',
    url(r'^(?P<pk>\d+)/$', GetDownloadView.as_view(), name='download',),
)
