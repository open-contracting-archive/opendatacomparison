import os
import json
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DetailView,
)

from braces.views import LoginRequiredMixin, JSONResponseMixin
from .models import Datamap


class DatamapListView(ListView):
    model = Datamap


class DatamapAddView(LoginRequiredMixin, CreateView):
    model = Datamap


class DatamapEditView(LoginRequiredMixin, UpdateView):
    model = Datamap


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
