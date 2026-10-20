from django import template

register = template.Library()


@register.filter
def img_url(file_field, default='/static/default-image.jpg'):
    """Safely resolve an ImageField's URL.

    ``{{ x.img.url|default:'...' }}`` looks safe but isn't: FieldFile.url
    raises a plain ValueError when no file is attached, and Django's
    template engine only silently swallows exceptions marked
    silent_variable_failure (like DoesNotExist), so ValueError crashes the
    whole page before the `default` filter ever runs.
    """
    if not file_field:
        return default
    try:
        return file_field.url
    except ValueError:
        return default
