from django.conf.urls import patterns, url

from .views import (
    DatamapAddView,
    DatamapEditView,
)

urlpatterns = patterns(
    '',
    url(r'edit/$', DatamapAddView.as_view(), name='datamap_add',),
    url(r'edit/(?P<pk>\d+)/$', DatamapEditView.as_view(), name='datamap_edit',),
)
