from django.conf.urls import patterns, url

from .views import (
    DatamapAddView,
    DatamapEditView,
    DatamapListView,
    DatamapView,
    DatamapJSON,
)

urlpatterns = patterns(
    '',
    url(r'^(?P<pk>\d+)/data.json$', DatamapJSON.as_view(), name='datamap_json',),  # nopep8
    url(r'^(?P<pk>\d+)/$', DatamapView.as_view(), name='datamap',),
    url(r'^edit/(?P<pk>\d+)/$', DatamapEditView.as_view(), name='datamap_edit',),  # nopep8
    url(r'^edit/$', DatamapAddView.as_view(), name='datamap_add',),
    url(r'^$', DatamapListView.as_view(), name='datamap_list',),
)
