from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='getattribute')
def getattribute(obj, attr):
    """
    Gets an attribute of an object dynamically from a string name.
    
    Usage in template:
    {{ object|getattribute:dynamic_field_name }}
    """
    if hasattr(obj, str(attr)):
        return getattr(obj, str(attr))
    elif hasattr(obj, 'get'):
        try:
            return obj.get(str(attr))
        except (TypeError, KeyError):
            return ''
    return '' 