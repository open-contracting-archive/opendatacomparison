from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DetailView,
)
from django.core.urlresolvers import reverse

from braces.views import LoginRequiredMixin, JSONResponseMixin
from .models import Datamap


class DatamapListView(ListView):
    model = Datamap


class DatamapAddView(LoginRequiredMixin, CreateView):
    model = Datamap

    def get_success_url(self):
        return reverse('datamap', kwargs={'pk': self.object.id})

    def get_form(self, form_class):
        form_kwargs = self.get_form_kwargs()
        form_kwargs['initial'] = {'dataset': self.request.GET.get('dataset')}
        return form_class(**form_kwargs)




class DatamapEditView(LoginRequiredMixin, UpdateView):
    model = Datamap

    def get_success_url(self):
        return reverse('datamap', kwargs={'pk': self.object.id})


class DatamapView(DetailView):
    model = Datamap


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
