from django.conf.urls import (
    patterns,
    include,
    url
)
from downloads.router import (
    router,
)

# URLs
urlpatterns = patterns('',
    url(r'^', include(router.urls)),
)
