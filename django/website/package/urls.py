from django.conf.urls import patterns, url
from django.views.generic.dates import ArchiveIndexView

from package.models import Package
from package.views import (
    ajax_package_list,
    usage,
    post_data,
    edit_documentation,
)

from .views import (
    CategoryDetailView,
    PackageDetailView,
    PackageListView,
    PackageCreateView,
    PackageUpdateView,
)


urlpatterns = patterns('',
    url(r'^$', PackageListView.as_view(), name='packages',),
    url(r'^p/(?P<slug>[-\w]+)/$', PackageDetailView.as_view(), name='package',),
    url(r'^c/(?P<slug>[-\w]+)/$', CategoryDetailView.as_view(), name='category'),
    url(r'^latest/$', view=ArchiveIndexView.as_view(queryset=Package.objects.filter().select_related(), paginate_by=50, date_field='created'), name='latest_packages',),
    url(r'^add/$', PackageCreateView.as_view(), name='add_package',),
    url(r'^(?P<slug>[-\w]+)/edit/$', PackageUpdateView.as_view(), name='edit_package',),
    url(r'^(?P<slug>[-\w]+)/post-data/$', view=post_data, name='post_package_data',),
    url(r'^usage/(?P<slug>[-\w]+)/(?P<action>add|remove)/$', view=usage, name='usage',),
    url(r'^(?P<slug>[-\w]+)/document/$', view=edit_documentation, name='edit_documentation',),
    url(r'^ajax_package_list/$', view=ajax_package_list, name='ajax_package_list',),
)
