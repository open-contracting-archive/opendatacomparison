from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.conf import settings
from django.views.generic.base import TemplateView

from homepage.views import HomePageView
from profiles.views import ProfileRedirectView

admin.autodiscover()
handler404 = 'homepage.views.error_404_view'
handler500 = 'homepage.views.error_500_view'

urlpatterns = patterns('',
    # Examples:
    # url(r'^myapp/', include('myapp.urls')),
    url(r'^$', HomePageView.as_view(), name='home'),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^datasets/', include('package.urls')),
    url(r'^grids/', include('grid.urls')),
    url(r'^profiles/', include('profiles.urls')),
    url(r'^publishers/', include('publisher.urls')),
    url(r'^datamap/', include('datamap.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^accounts/profile/$', ProfileRedirectView.as_view()),

    # static pages
    url(r'^about/$', TemplateView.as_view(template_name='pages/faq.html'), name='about'),
    url(r'^terms/$', TemplateView.as_view(template_name='pages/terms.html'), name='terms'),
    url(r'^faq/$', TemplateView.as_view(template_name='pages/faq.html'), name='faq'),
    url(r'^syndication/$', TemplateView.as_view(template_name='pages/syndication.html'), name='syndication'),
    url(r'^help/$', TemplateView.as_view(template_name='pages/help.html'), name='help'),

    # This requires that static files are served from the 'static' folder.
    # The apache conf is set up to do this for you, but you will need to do it
    # on dev
    (r'/favicon.ico', 'django.views.generic.base.RedirectView',
        {'url':  '{0}images/favicon.ico'.format(settings.STATIC_URL)}),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
