from django.core.urlresolvers import reverse
from django.db.models import Count
from datamap.forms import FieldForm, TranslatedFieldForm
from django.forms.models import inlineformset_factory
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView

from braces.views import LoginRequiredMixin

from datamap.models import Datamap, TranslatedField, Field, Concept


class FieldListView(ListView):
    model = Field

    def get_queryset(self):
        return Field.objects.all().prefetch_related('datamap', 'concept')

    def get_context_data(self):
        context = super(FieldListView, self).get_context_data()
        context['concepts'] = \
            Concept.objects.all()\
            .order_by('name').annotate(num_fields=Count('field'))
        return context


class FieldByConceptListView(FieldListView):
    def get(self, request, *args, **kwargs):
        self.concept = kwargs.get('pk')
        return super(FieldByConceptListView,
                     self).get(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(FieldByConceptListView, self).get_queryset()
        return qs.filter(concept=self.concept)


class AddFieldView(LoginRequiredMixin, CreateView):
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
        user = self.request.user
        if user.is_authenticated() and not user.profile.can_edit_datamap:
            return HttpResponseForbidden("permission denied")
        else:
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


class FieldView(EditFieldView):
    template_name = 'datamap/field.html'

    def post(self, request, *args, **kwargs):
        # We don't want post doing anything, so send it to get
        return super(FieldView, self).get(request, *args, **kwargs)
