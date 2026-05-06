from django import template

register = template.Library()


@register.filter(name='customer_counter_id')
def customer_transactions(value, page):
    value, page = int(value), int(page)
    adjusted_value = value + (page - 1) * 10
    return adjusted_value