from math import pi
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.generic.base import View
from django.http import (
    Http404,
    HttpResponse,
)
from bokeh.plotting import (
    circle,
    ColumnDataSource,
    curplot,
    figure,
    grid,
    hold,
    output_file,
    rect,
    xaxis,
)
from bokeh.objects import HoverTool
from collections import OrderedDict


class BokehJS(View):
    """
    Bokeh writes the js snippet to a file, this view, retrieves the js
    from the file system when the embedded html calls it.
    """
    def get(self, request, **kwargs):
        try:
            file_object = open('%s/%s.embed.js' % (settings.BOKEH_EMBED_JS_DIR,
                                                   kwargs.get('uuid')), 'rb')
        except (ValueError, IOError):
            raise Http404
        return HttpResponse(file_object)


def build_punchcard(datamap_list, concept_list,
                    radii_list, fields_in_concept_list,
                    datamaps, concepts,
                    plot_width=1200, plot_height=800):

    source = ColumnDataSource(
        data=dict(
            datamap=datamap_list,  # x
            concept=concept_list,  # y
            radii=radii_list,
            fields_in_concept=fields_in_concept_list,
        )
    )
    output_file('')
    hold()
    figure()
    plot_properties = {
        'title': None,
        'tools': "hover,resize,previewsave",
        'y_range': [get_datamap_label(datamap) for datamap in datamaps],
        'x_range': concepts,
        'plot_width': plot_width,
        'plot_height': plot_height,
    }

    rect('concept', 'datamap',  # x, y
         1, 1,  # height, width
         source=source,
         color='white',  # put in background
         **plot_properties)

    circle('concept', 'datamap',  # x, y
           size='radii',
           source=source,
           color='black',
           **plot_properties)

    grid().grid_line_color = None
    x = xaxis()
    x.major_label_orientation = pi / 4
    hover = [t for t in curplot().tools if isinstance(t, HoverTool)][0]

    hover.tooltips = OrderedDict([
        ("Datamap", "@datamap"),
        ("Concept", "@concept"),
        ("Fields", "@fields_in_concept"),
    ])

    return curplot().create_html_snippet(
        static_path=settings.STATIC_URL,
        embed_save_loc=settings.BOKEH_EMBED_JS_DIR,
        embed_base_url=reverse('bokeh'),
    )


def get_datamap_label(datamap):
    if datamap.dataset.publisher.country:
        prefix = datamap.dataset.publisher.country
    else:
        prefix = datamap.dataset.publisher.name
    return '%s - %s' % (prefix, datamap.dataset.title)
