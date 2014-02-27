from django.conf.urls import patterns, url

from profiles.views import (
    ProfileUpdateView,
    ProfileListView,
    ProfileDetailView,
)

urlpatterns = patterns('',
    url(r'^edit/(?P<slug>[-\w]+)/$', ProfileUpdateView.as_view(), name='profile_edit'),
    url(r'^$', ProfileListView.as_view(), name='profile_list'),
    url(r'^(?P<slug>[-\w]+)/$', ProfileDetailView.as_view(), name='profile_detail'),
)
