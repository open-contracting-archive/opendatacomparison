from floppyforms import SelectMultiple


class BetterSelectMultiple(SelectMultiple):
    def __init__(self, attrs=None, choices=()):
        widget_attrs = {
            'size': 10,
            'class': 'widget-multi-select'
        }
        if attrs:
            widget_attrs.update(attrs)
        super(BetterSelectMultiple, self).__init__(widget_attrs, choices)
