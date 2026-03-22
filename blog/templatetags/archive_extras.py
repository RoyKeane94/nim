from django import template

register = template.Library()


@register.simple_tag
def merge_query(request, **kwargs):
    """Merge GET params: pass key='' or key=None to remove a param."""
    q = request.GET.copy()
    for k, v in kwargs.items():
        if v is None or v == '':
            q.pop(k, None)
        else:
            q[k] = str(v)
    encoded = q.urlencode()
    return '?' + encoded if encoded else '?'
