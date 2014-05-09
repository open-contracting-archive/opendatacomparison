from django.views.generic import DetailView, ListView
from django.db.models import Count

from package.models import Package
from .models import Publisher


class PublisherListView(ListView):
    def get_queryset(self):
        queryset = Publisher.objects.all().order_by('country', 'name')
        queryset = queryset.annotate(datasetscount=Count('datasets'))
        return queryset


class PublisherDetailView(DetailView):
    model = Publisher

    def get_context_data(self, *args, **kwargs):
        datasets = Package.objects.filter(publisher=self.object)
        datasets = datasets.annotate(downloadcount=Count('downloads'))
        context = super(PublisherDetailView, self).get_context_data()
        context.update({'datasets': datasets})
        return context
