from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse
from datamap.forms import FieldForm, TranslatedFieldForm
from django.forms.formsets import formset_factory

from datamap.models import Datamap


class AddFieldView(CreateView):
    template_name = 'datamap/field_add.html'
    form_class = FieldForm

    def get_success_url(self):
        return reverse('datamap', kwargs={'pk': self.datamap.id})

    def get_context_data(self, *args, **kwargs):
        context = super(AddFieldView, self).get_context_data(*args, **kwargs)
        context.update({'datamap': self.datamap})
        if hasattr(self, 'formset'):
            context.update({'formset': self.formset})
        return context

    def get(self, request, *args, **kwargs):
        self.datamap = Datamap.objects.get(id=kwargs.get('pk'))
        self.form = self.form_class()
        TranslatedFieldFormSet = formset_factory(TranslatedFieldForm)
        self.formset = TranslatedFieldFormSet()
        return super(AddFieldView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.datamap = self.datamap
        self.object.save()
        return super(AddFieldView, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        self.datamap = Datamap.objects.get(id=kwargs.get('pk'))
        return super(AddFieldView, self).post(request, *args, **kwargs)
