from collections import OrderedDict
from datamap.models import Datamap, Concept
from .plotting import build_plot, get_x_label


def single_datamap_not_normalized(datamap):
    x, y, radii, fields_in_concept, concepts = \
        _build_data_for_single_datamap(datamap, [], [], [], [])
    return build_plot(x, y, radii, fields_in_concept, [datamap], concepts)


def all_datamaps_not_normalized():
    # Make the lists for the plot
    y = []
    x = []
    radii = []
    fields_in_concept = []
    datamaps = Datamap.objects.all()
    for datamap in datamaps:
        x, y, radii, fields_in_concept, concepts = \
            _build_data_for_single_datamap(datamap,
                                           x, y, radii, fields_in_concept)

    return build_plot(x, y, radii, fields_in_concept,
                      datamaps, concepts)


def _build_data_for_single_datamap(datamap, x, y, radii, fields_in_concept):
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

    return (x, y, radii, fields_in_concept, concept_dict.keys())


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
