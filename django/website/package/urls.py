from django.conf.urls import patterns, url
from django.views.generic.dates import ArchiveIndexView

from package.models import Package
from package.views import (
    add_package,
    edit_package,
    update_package,
    usage,
    package_list,
    post_data,
    edit_documentation,
)

from .views import (
    PackageDetailView,
)


urlpatterns = patterns('',
    url(r'^$', package_list, name='packages',),
    url(r'^latest/$', view=ArchiveIndexView.as_view(queryset=Package.objects.filter().select_related(), paginate_by=50, date_field='created'), name='latest_packages',),
    url(r'^add/$', view=add_package, name='add_package',),
    url(r'^(?P<slug>[-\w]+)/edit/$', view=edit_package, name='edit_package',),
    url(r'^(?P<slug>[-\w]+)/fetch-data/$', view=update_package, name='fetch_package_data',),
    url(r'^(?P<slug>[-\w]+)/post-data/$', view=post_data, name='post_package_data',),
    url(r'^p/(?P<slug>[-\w]+)/$', PackageDetailView.as_view(), name='package',),
    url(r'^usage/(?P<slug>[-\w]+)/(?P<action>add|remove)/$', view=usage, name='usage',),
    url(r'^(?P<slug>[-\w]+)/document/$', view=edit_documentation, name='edit_documentation',),
)
