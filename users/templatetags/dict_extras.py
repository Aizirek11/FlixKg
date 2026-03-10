#Это нужно чтобы в шаблоне account.html можно было получить скидку по ID билета.
from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)