from django.conf.urls import patterns, url

from grid.views import (
    add_feature,
    add_grid,
    add_grid_package,
    add_new_grid_package,
    ajax_grid_list,
    delete_feature,
    delete_grid_package,
    edit_element,
    edit_grid,
    edit_feature,
    grids,
    grid_detail_landscape,
)

from .views import (
    GridDetailView,
)

urlpatterns = patterns("",
    url(r'^add/$', view=add_grid, name='add_grid',),
    url(r'^(?P<slug>[-\w]+)/edit/$', view=edit_grid, name='edit_grid',),
    url(r'^element/(?P<feature_id>\d+)/(?P<package_id>\d+)/$', view=edit_element, name='edit_element',),
    url(r'^feature/add/(?P<grid_slug>[a-z0-9\-\_]+)/$', view=add_feature, name='add_feature',),
    url(r'^feature/(?P<id>\d+)/$', view=edit_feature, name='edit_feature',),
    url(r'^feature/(?P<id>\d+)/delete/$', view=delete_feature, name='delete_feature',),
    url(r'^package/(?P<id>\d+)/delete/$', view=delete_grid_package, name='delete_grid_package',),
    url(r'^(?P<grid_slug>[a-z0-9\-\_]+)/package/add/$', view=add_grid_package, name='add_grid_package',),
    url(r'^(?P<grid_slug>[a-z0-9\-\_]+)/package/add/new$', view=add_new_grid_package, name='add_new_grid_package',),
    url(r'^ajax_grid_list/$', view=ajax_grid_list, name='ajax_grid_list',),
    url(r'^$', view=grids, name='grids',),
    url(r'^g/(?P<slug>[-\w]+)/$', GridDetailView.as_view(), name='grid',),
    url(r'^g/(?P<slug>[-\w]+)/landscape/$', view=grid_detail_landscape, name='grid_landscape',),
)
