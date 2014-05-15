from __future__ import division
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import (
    Http404,
    HttpResponseForbidden,
    HttpResponse,
    HttpResponseNotFound,
)
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
)
from django.views.generic.base import View

from bokeh.plotting import (
    figure,
    circle,
    rect,
    curplot,
    output_file,
    grid,
    hold,
    ColumnDataSource,
)
from bokeh.objects import HoverTool
from collections import OrderedDict
from braces.views import LoginRequiredMixin
from extra_views import (
    InlineFormSet
)
from datamap.models import Datamap, Field, Concept
from datamap.forms import FieldForm
from package.models import Package


class DatamapListView(ListView):
    model = Datamap

    def get_context_data(self, *args, **kwargs):
        context = super(DatamapListView,
                        self).get_context_data(*args, **kwargs)
        context['visual'] = self.build_visual_map()
        return context

    def build_visual_map(self):
        # Make the lists for the plot
        y = []
        x = []
        radii = []
        fields_in_concept = []
        datamaps = Datamap.objects.all()
        for datamap in datamaps:
            concept_dict = get_empty_concept_dict()
            fields = datamap.fields.all()
            for field in fields:
                concept = field.concept
                concept_dict[concept.name].append(field.fieldname)

            for concept, fields in concept_dict.iteritems():
                y.append(concept)
                x.append(get_x_label(datamap))
                radii.append(len(fields) * 5)
                fields_in_concept.append(', '.join(fields))
        return build_plot(x, y, radii, fields_in_concept,
                          datamaps, concept_dict.keys())


class FieldInline(InlineFormSet):
    model = Field
    form_class = FieldForm


class DatamapAddView(LoginRequiredMixin, CreateView):
    action = 'Add'
    model = Datamap

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated() and not user.profile.can_edit_package:
            return HttpResponseForbidden("permission denied")
        else:
            return super(DatamapAddView,
                         self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        dataset_id = request.GET.get('dataset')
        if not dataset_id >= 0:
            raise Http404
        self.dataset = Package.objects.get(pk=dataset_id)
        return super(DatamapAddView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        dataset_id = request.POST.get('dataset')
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


class DatamapEditView(LoginRequiredMixin, UpdateView):
    action = 'Edit'
    model = Datamap

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated() and not user.profile.can_edit_datamap:
            return HttpResponseForbidden("permission denied")
        else:
            return super(DatamapEditView,
                         self).dispatch(request, *args, **kwargs)

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
        context['visual'] = self.build_visual_map()
        return context

    def build_visual_map(self):
        concept_dict = get_empty_concept_dict()
        fields = self.object.fields.all()
        for field in fields:
            concept = field.concept
            concept_dict[concept.name].append(field.fieldname)

        # Make the lists for the plot
        y = []
        x = []
        radii = []
        fields_in_concept = []
        for concept, fields in concept_dict.iteritems():
            y.append(concept)
            x.append(get_x_label(self.object))
            radii.append(len(fields) * 5)
            fields_in_concept.append(', '.join(fields))
        return build_plot(x, y, radii, fields_in_concept,
                          [self.object], concept_dict.keys())


class BokehJS(View):
    def get(self, request, **kwargs):
        try:
            file_object = open('%s/%s.embed.js' % (settings.BOKEH_EMBED_JS_DIR,
                                                   kwargs.get('uuid')), 'rb')
        except (ValueError, IOError):
            return HttpResponseNotFound()
        return HttpResponse(file_object)


def build_plot(x, y, radii, fields_in_concept,
               datamaps, concepts,
               plot_width=1200, plot_height=800):
    source = ColumnDataSource(
        data=dict(
            x=x,
            y=y,
            radii=radii,
            fields_in_concept=fields_in_concept,
        )
    )
    output_file('')
    hold()
    figure()
    plot_properties = {
        'title': None,
        'tools': "hover",
        'x_range': [get_x_label(datamap) for datamap in datamaps],
        'y_range': concepts,
        'plot_width': plot_width,
        'plot_height': plot_height,
    }

    rect(x, y, 1, 1,
         source=source,
         color='white',  # put in background
         **plot_properties)

    circle('x', 'y',
           source=source,
           size='radii',
           color='black',
           **plot_properties)

    grid().grid_line_color = None

    hover = [t for t in curplot().tools if isinstance(t, HoverTool)][0]

    hover.tooltips = OrderedDict([
        ("Bucket", "@y"),
        ("Fields", "@fields_in_concept"),
    ])

    return curplot().create_html_snippet(
        static_path=settings.STATIC_URL,
        embed_save_loc=settings.BOKEH_EMBED_JS_DIR,
        embed_base_url=reverse('bokeh'),
    )


def get_empty_concept_dict():
    """
    Returns a list of concepts (not yet in the order we want)
        concepts = [
                "SYSTEM",
                "DOCUMENT",
                "TENDER TRACKING",
                "TENDER FEATURES",
                "GOODS / SERVICES",
                "AMOUNT",
                "BUYER",
                "SUPPLIER",
                "AWARD TRACKING",
                "AWARD FEATURES",
                "CONTRACT TRACKING",
                "CONTRACT FEATURES",
                "ADD ON"
        ]
    """
    concepts = \
        Concept.objects.all().values_list('name', flat=True).order_by('name')
    empty_list = ([] for concept in concepts)
    concept_dict = OrderedDict(zip(concepts, empty_list))
    return concept_dict


def get_x_label(datamap):
    return '%s - %s' % (datamap.dataset.publisher.country,
                        datamap.dataset.publisher.name)
