from random import sample

from django.db.models import Count
from django.shortcuts import render
from django.views.generic.base import TemplateView

from grid.models import Grid
from homepage.models import Dpotw, Gotw, PSA
from package.models import Category, Package


class HomePageView(TemplateView):

    template_name = 'homepage.html'

    def _get_categories(self):
        category_list = []
        categories = Category.objects.annotate(package_count=Count('package'))
        for category in categories:
            element = {
                'title': category.title,
                'description': category.description,
                'count': category.package_count,
                'slug': category.slug,
                'title_plural': category.title_plural,
            }
            category_list.append(element)
        return category_list

    def _get_random_packages(self, package_count):
        # get up to 5 random packages
        random_packages = []
        if package_count > 1:
            package_ids = set([])

            # Get 5 random keys
            package_ids = sample(
                # generate a list from 1 to package_count +1
                range(1, package_count + 1),
                # Get a sample of the smaller of 5 or the package count
                min(package_count, 5)
            )
            # Get the random packages
            random_packages = Package.objects.filter(pk__in=package_ids)[:5]
        return random_packages

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        package_count = Package.objects.count()

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

        # Public Service Announcement on homepage
        try:
            psa_body = PSA.objects.latest().body_text
        except PSA.DoesNotExist:
            psa_body = """
            <p>There are currently no announcements.
            To request a PSA, ping the Open Contracting Data Standard
            <a href="http://open-contracting.github.io/pages/community.html">
            mailing list</a>.</p>"""

        context.update({
            'latest_packages': Package.objects.all().order_by('-created')[:5],
            'random_packages': self._get_random_packages(package_count),
            'potw': potw,
            'gotw': gotw,
            'psa_body': psa_body,
            'categories': self._get_categories(),
            'package_count': package_count})
        return context

def error_500_view(request):
    response = render(request, '500.html')
    response.status_code = 500
    return response


def error_404_view(request):
    response = render(request, '404.html')
    response.status_code = 404
    return response
