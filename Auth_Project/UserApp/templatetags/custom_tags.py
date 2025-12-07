from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])

@register.filter
def user_ids(queryset):
    return list(queryset.values_list('user_id', flat=True))


