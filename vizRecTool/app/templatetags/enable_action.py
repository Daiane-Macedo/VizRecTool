from django import template

register = template.Library()


@register.simple_tag
def button_disabled(list_1, list_2):
    if not list_1 or not list_2:
        return True
    return False
