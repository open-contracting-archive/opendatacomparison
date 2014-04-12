from django.views.generic.edit import CreateView, UpdateView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from datamap.forms import FieldForm, TranslatedFieldForm
from django.forms.models import inlineformset_factory

from datamap.models import Datamap, TranslatedField, Field


class AddFieldView(CreateView):
    model = Field
    template_name = 'datamap/field_add.html'
    form_class = FieldForm
    formset_class = inlineformset_factory(Field,
                                          TranslatedField,
                                          form=TranslatedFieldForm,
                                          can_delete=False)

    def get_success_url(self):
        return reverse('datamap', kwargs={'pk': self.datamap.id})

    def get_context_data(self, *args, **kwargs):
        context = super(AddFieldView, self).get_context_data(*args, **kwargs)
        context.update({'datamap': self.datamap})
        if hasattr(self, 'formset'):
            context.update({'formset': self.formset})
        return context

    def dispatch(self, request, *args, **kwargs):
        field_id = kwargs.get('pk')
        if field_id:
            self.object = Field.objects.get(id=field_id)
        else:
            self.object = None
        self.datamap = Datamap.objects.get(id=kwargs.get('dm'))
        return super(AddFieldView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.form = self.form_class()
        if self.object:
            self.formset = self.formset_class(instance=self.object)
        else:
            self.formset = self.formset_class()
        return super(AddFieldView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.datamap = self.datamap
        self.object.save()
        return self.object

    def invalid(self, form, formset):
        context = self.get_context_data(form=form, formset=formset)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            field = self.form_valid(form)
        else:
            formset = self.formset_class(request.POST)
            return self.invalid(form, formset=formset)

        formset = self.formset_class(request.POST, instance=field)
        if formset.is_valid():
            formset.save()
        else:
            return self.invalid(form, formset=formset)

        return HttpResponseRedirect(self.get_success_url())


class EditFieldView(AddFieldView, UpdateView):
    model = Field
