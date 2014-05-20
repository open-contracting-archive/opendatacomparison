from django.shortcuts import render
from django.views.generic.base import TemplateView

from datamap.models import Datamap
from datamap.views.maps import datamaps_normalized_sorted
from downloads.models import Link
from grid.models import Grid
from homepage.models import Dpotw, Gotw
from package.models import Category, Package
from publisher.models import Publisher


class HomePageView(TemplateView):

    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        package_count = Package.objects.count()
        publisher_count = Publisher.objects.count()
        download_count = Link.objects.count()

        try:
            potw = Dpotw.objects.latest().package
        except Dpotw.DoesNotExist:
            potw = None
        except Package.DoesNotExist:
            potw = None

        try:
            gotw = Gotw.objects.latest().grid
        except Gotw.DoesNotExist:
            gotw = None
        except Grid.DoesNotExist:
            gotw = None

        datamaps = (
            Datamap.objects
            .all()
            .prefetch_related('dataset', 'dataset__publisher', 'format',
                              'fields', 'fields__concept')
            .order_by('dataset__publisher__country')
        )

        context.update({
            'latest_packages': Package.objects.all().order_by('-created')[:5],
            'latest_publishers': Publisher.objects.all().order_by('-created')[:5],
            'potw': potw,
            'gotw': gotw,
            'categories': Category.objects.all(),
            'package_count': package_count,
            'publisher_count': publisher_count,
            'download_count': download_count,
            'all_normalized_sorted': datamaps_normalized_sorted(datamaps)})
        return context


def error_500_view(request):
    response = render(request, '500.html')
    response.status_code = 500
    return response


def error_404_view(request):
    response = render(request, '404.html')
    response.status_code = 404
    return response
