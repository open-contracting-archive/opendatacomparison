from django.views.generic import DetailView, ListView

from .models import Publisher


class PublisherListView(ListView):
    queryset = Publisher.objects.all().order_by('country', 'name')


class PublisherDetailView(DetailView):
    model = Publisher
