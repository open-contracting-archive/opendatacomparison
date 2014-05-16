from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.generic.base import View
from django.http import (
    Http404,
    HttpResponse,
)
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


def build_punchcard(x, y, radii, fields_in_concept,
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
        ("Datamap", "@x"),
        ("Bucket", "@y"),
        ("Fields", "@fields_in_concept"),
    ])

    return curplot().create_html_snippet(
        static_path=settings.STATIC_URL,
        embed_save_loc=settings.BOKEH_EMBED_JS_DIR,
        embed_base_url=reverse('bokeh'),
    )


def get_x_label(datamap):
    return '%s' % (datamap.dataset.publisher.name.lower())
