from __future__ import division
import copy
from collections import OrderedDict
from django.db.models import Count
from datamap.models import Datamap, Concept
from .plotting import build_punchcard, get_datamap_label


def single_datamap_not_normalized(datamap):
    x, y, radii, fields_in_concept, concepts = \
        _build_data_for_single_datamap(datamap, [], [], [], [])
    return build_punchcard(x, y, radii, fields_in_concept,
                           [datamap], concepts,
                           plot_height=300)


def datamaps_not_normalized(datamaps):
    # Make the lists for the plot
    y = []
    x = []
    radii = []
    fields_in_concept = []
    empty_concept_dict = get_empty_concept_dict()
    for datamap in datamaps:
        x, y, radii, fields_in_concept, concepts = \
            _build_data_for_single_datamap(
                datamap, x, y, radii, fields_in_concept,
                normalized=False,
                concept_dict=copy.deepcopy(empty_concept_dict)
            )

    plot_height = datamaps.count() * 80
    return build_punchcard(x, y, radii, fields_in_concept,
                           datamaps, concepts,
                           plot_height=plot_height)


def datamaps_normalized(datamaps):
    y = []
    x = []
    radii = []
    fields_in_concept = []
    empty_concept_dict = get_empty_concept_dict()
    for datamap in datamaps:
        x, y, radii, fields_in_concept, concepts = \
            _build_data_for_single_datamap(
                datamap, x, y, radii, fields_in_concept,
                normalized=True,
                concept_dict=copy.deepcopy(empty_concept_dict)
            )

    plot_height = datamaps.count() * 80
    return build_punchcard(x, y, radii, fields_in_concept,
                           datamaps, concepts,
                           plot_height=plot_height)


def datamaps_normalized_sorted(datamaps):
    # Make a concept_dict that's ordered by normalized field counts per bucket
    concept_dict = get_empty_concept_dict()
    concepts = None
    total_concepts = 0
    for datamap in datamaps:
        concepts = Concept.objects.filter(field__datamap=datamap)
        total_concepts = concepts.count()
        field_counts = (
            concepts.distinct()
            .annotate(num_fields=Count('field'))
            .values_list('name', 'num_fields')
        )
        normalized_field_counts = [(x[0], x[1] / total_concepts)
                                   for x in field_counts]
        for nfc in normalized_field_counts:
            concept_dict[nfc[0]].append(nfc[1])

    sorted_concept_dict = OrderedDict(sorted(concept_dict.iteritems(),
                                             key=lambda x: sum(x[1]),
                                             reverse=True))
    empty_sorted_concept_dict = OrderedDict(
        zip(sorted_concept_dict.keys(),
            ([] for i in xrange(0, total_concepts)))
    )
    # now build the plot
    y = []
    x = []
    radii = []
    fields_in_concept = []
    for datamap in datamaps:
        x, y, radii, fields_in_concept, concepts = \
            _build_data_for_single_datamap(
                datamap, x, y, radii, fields_in_concept,
                normalized=True,
                concept_dict=copy.deepcopy(empty_sorted_concept_dict))
    plot_height = datamaps.count() * 80
    return build_punchcard(x, y, radii, fields_in_concept,
                           datamaps, concepts,
                           plot_height=plot_height)


def _build_data_for_single_datamap(datamap, x, y, radii, fields_in_concept,
                                   normalized=False, concept_dict=None):
    if not concept_dict:
        concept_dict = get_empty_concept_dict()
    fields = datamap.fields.all()
    total_fields = len(fields)
    for field in fields:
        concept = field.concept
        concept_dict[concept.name].append(field.fieldname)

    for concept, fields in concept_dict.iteritems():
        y.append(concept)
        x.append(get_datamap_label(datamap))
        if normalized:
            radius = (len(fields) / total_fields) * 100
        else:
            radius = len(fields) * 5
        radii.append(radius)
        fields_in_concept.append(', '.join(fields))

    return (x, y, radii, fields_in_concept, concept_dict.keys())


def get_empty_concept_dict():
    """
    returns a list of concepts (not yet in the order we want)
        concepts = [
                "system",
                "document",
                "tender tracking",
                "tender features",
                "goods / services",
                "amount",
                "buyer",
                "supplier",
                "award tracking",
                "award features",
                "contract tracking",
                "contract features",
                "add on"
        ]
    """
    concepts = \
        Concept.objects.all().values_list('name', flat=True).order_by('name')
    empty_list = ([] for concept in concepts)
    concept_dict = OrderedDict(zip(concepts, empty_list))
    return concept_dict
