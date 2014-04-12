from django.conf.urls import patterns, url

from datamap.views.datamap_basic import (
    DatamapAddView,
    DatamapEditView,
    DatamapListView,
    DatamapView,
    DatamapJSON,
)
from datamap.views.field import (
    AddFieldView,
    EditFieldView
)

urlpatterns = patterns(
    '',
    url(r'^(?P<dm>\d+)/field/edit/(?P<pk>\d+)$', EditFieldView.as_view(), name='datamap_field_edit'),
    url(r'^(?P<dm>\d+)/field/edit/$', AddFieldView.as_view(), name='datamap_field_add'),
    url(r'^(?P<pk>\d+)/data.json$', DatamapJSON.as_view(), name='datamap_json',),  # nopep8
    url(r'^(?P<pk>\d+)/$', DatamapView.as_view(), name='datamap',),
    url(r'^edit/(?P<pk>\d+)/$', DatamapEditView.as_view(), name='datamap_edit',),  # nopep8
    url(r'^edit/$', DatamapAddView.as_view(), name='datamap_add',),
    url(r'^$', DatamapListView.as_view(), name='datamap_list',),
)
