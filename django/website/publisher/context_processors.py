from grid.context_processors import grouper
from .models import Publisher


def publisher_headers(request):
    publisher_headers = list(Publisher.objects.all().order_by('name'))
    publisher_headers = grouper(3, publisher_headers)
    return {'publisher_headers': publisher_headers}
