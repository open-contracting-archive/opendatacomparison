from django.conf.urls import patterns, url
from django.views.generic.base import View

from datamap.views.datamap_basic import (
    DatamapAddView,
    DatamapEditView,
    DatamapListView,
    DatamapView,
)
from datamap.views.plotting import (
    BokehJS,
)
from datamap.views.field import (
    FieldView,
    FieldListView,
    FieldByConceptListView,
    AddFieldView,
    EditFieldView
)

urlpatterns = patterns(
    '',
    url(r'^(?P<dm>\d+)/field/(?P<pk>\d+)/$', FieldView.as_view(), name='datamap_field'),
    url(r'^(?P<dm>\d+)/field/edit/(?P<pk>\d+)/$', EditFieldView.as_view(), name='datamap_field_edit'),
    url(r'^(?P<dm>\d+)/field/edit/$', AddFieldView.as_view(), name='datamap_field_add'),
    url(r'^(?P<pk>\d+)/$', DatamapView.as_view(), name='datamap',),
    url(r'^edit/(?P<pk>\d+)/$', DatamapEditView.as_view(), name='datamap_edit',),  # nopep8
    url(r'^edit/$', DatamapAddView.as_view(), name='datamap_add',),
    url(r'^bokeh/$', View.as_view(), name='bokeh',),
    url(r'^bokeh/(?P<uuid>.+).embed.js', BokehJS.as_view(), name='bokehjs',),
    url(r'^field/$', FieldListView.as_view(), name='field_list',),
    url(r'^field/(?P<pk>\d+)/$', FieldByConceptListView.as_view(), name='field_by_concept',),
    url(r'^$', DatamapListView.as_view(), name='datamap_list',),
)
