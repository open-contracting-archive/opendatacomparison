from django import template

register = template.Library()


@register.filter(name='addclass')
def addclass(field, addclass):
    return field.as_widget(attrs={"class": addclass})


@register.filter(name='addattrs')
def addattrs(value, arg):
    attrs = value.field.widget.attrs
    data = arg.replace(' ', '')
    kvs = data.split(',')
    for string in kvs:
        kv = string.split(':')
        attrs[kv[0]] = kv[1]
    return value.as_widget(attrs=attrs)
