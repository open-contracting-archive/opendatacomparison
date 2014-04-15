from django.http import Http404
from django.views.generic import (
    ListView,
    DetailView,
    CreateView, UpdateView)
from django.core.urlresolvers import reverse
from braces.views import LoginRequiredMixin, JSONResponseMixin
from extra_views import (
    CreateWithInlinesView,
    UpdateWithInlinesView,
    InlineFormSet
)
from datamap.models import Datamap, Field
from datamap.forms import FieldForm
from package.models import Package, Format


class DatamapListView(ListView):
    model = Datamap


class FieldInline(InlineFormSet):
    model = Field
    form_class = FieldForm


class DatamapAddView(CreateView):
    action = 'Add'
    model = Datamap

    def get(self, request, *args, **kwargs):
        dataset_id = self.request.GET.get('dataset')
        if not dataset_id >= 0:
            raise Http404
        self.dataset = Package.objects.get(pk=dataset_id)
        return super(DatamapAddView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        dataset_id = self.request.POST.get('dataset')
        if not dataset_id >= 0:
            raise Http404
        self.dataset = Package.objects.get(pk=dataset_id)
        return super(DatamapAddView, self).post(request, *args, **kwargs)

    def get_form(self, form_class):
        form_kwargs = self.get_form_kwargs()
        form_kwargs['initial'] = {'dataset': self.dataset.id}
        return form_class(**form_kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(DatamapAddView, self).get_context_data(*args, **kwargs)

        package = self.dataset
        context['package'] = package
        return context

    def get_success_url(self):
        return reverse('package', kwargs={'slug': self.dataset.slug})


class DatamapEditView(UpdateView):
    action = 'Edit'

    model = Datamap

    def get_success_url(self):
        return reverse('datamap', kwargs={'pk': self.object.id})

    def get_context_data(self, *args, **kwargs):
        context = super(DatamapEditView,
                        self).get_context_data(*args, **kwargs)

        context['action'] = self.action
        context['package'] = self.object.dataset
        context['datamap'] = self.object

        return context


class DatamapView(DetailView):
    model = Datamap

    def get_context_data(self, *args, **kwargs):
        context = super(DatamapView,
                        self).get_context_data(*args, **kwargs)
        context['package'] = self.object.dataset
        return context


class DatamapJSON(JSONResponseMixin, DetailView):
    model = Datamap

    def get(self, request, *args, **kwargs):
        data =\
            [{
                'conceptname': 'tender',
                'children': [
                    {
                        'conceptname': 'awarding entity',
                        'items': [
                            {'questionkey': 'procurring_entity_id'},
                            {'questionkey': 'procurring_address'}
                        ]
                    },
                    {
                        'conceptname': 'receiving entity',
                        'items': [
                            {'questionkey': 'procurring_entity_id'},
                            {'questionkey': 'procurring_address'},
                            {'questionkey': 'procurring_entity_id'}
                        ]
                    }]
            }, {
                'conceptname': 'award',
                'children': [
                    {
                        'conceptname': 'awarding entity',
                        'items': [
                            {'questionkey': 'procurring_entity_id'},
                        ]
                    },
                    {
                        'conceptname': 'receiving entity',
                        'items': [
                            {'questionkey': 'procurring_entity_id'},
                            {'questionkey': 'procurring_entity_id'}
                        ]
                    }]
            }]

        return self.render_json_response(data)
