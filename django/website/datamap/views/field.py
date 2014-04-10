from django.forms import ModelForm
from django.forms.formsets import formset_factory
from django.shortcuts import render_to_response
from django.views.generic.base import TemplateView


from datamap.models import Datamap


class AddFieldView(TemplateView):
    template_name = 'datamap/field_add.html'

    def get_context_data(self, *args, **kwargs):
        context = super(AddFieldView, self).get_context_data(*args, **kwargs)
        context.update({
            'datamap': self.datamap
        })
        return context

    def get(self, request, *args, **kwargs):
        self.datamap = Datamap.objects.get(id=kwargs.get('pk'))
        return super(AddFieldView, self).get(request, *args, **kwargs)
