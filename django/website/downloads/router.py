from rest_framework.routers import SimpleRouter
from .views import LinkViewSet, CsvLinkViewSet


router = SimpleRouter(trailing_slash=False)
router.register(r'links', LinkViewSet)
router.register(r'links/f/csv', CsvLinkViewSet)
