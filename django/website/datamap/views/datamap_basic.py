from django.views.generic import (
    ListView,
    DetailView,
)
from django.core.urlresolvers import reverse
from braces.views import LoginRequiredMixin, JSONResponseMixin
from extra_views import (
    CreateWithInlinesView,
    UpdateWithInlinesView,
    InlineFormSet
)
from datamap.models import Datamap, Field
from datamap.forms import FieldForm


class DatamapListView(ListView):
    model = Datamap


class FieldInline(InlineFormSet):
    model = Field
    form_class = FieldForm


class DatamapEntryView(LoginRequiredMixin):
    model = Datamap
    inlines = [FieldInline, ]

    def get_success_url(self):
        return reverse('datamap', kwargs={'pk': self.object.id})

    def get_context_data(self, *args, **kwargs):
        context = super(DatamapEntryView,
                        self).get_context_data(*args, **kwargs)
        context['action'] = self.action
        return context


class DatamapAddView(DatamapEntryView, CreateWithInlinesView):
    action = 'Add'

    def get_form(self, form_class):
        form_kwargs = self.get_form_kwargs()
        form_kwargs['initial'] = {'dataset': self.request.GET.get('dataset')}
        return form_class(**form_kwargs)


class DatamapEditView(DatamapEntryView, UpdateWithInlinesView):
    action = 'Edit'


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
