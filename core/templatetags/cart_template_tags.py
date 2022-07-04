from django import template
from core.models import Order, OrderItem

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = OrderItem.objects.filter(user=user, ordered=False)
        if qs.exists():
            total = 0
            for i in range(len(qs)):
                total += qs[i].quantity
            return total
    return 0


@register.filter
def get_range(value):
    """
      Filter - returns a list containing range made from given value
      Usage (in template):

      <ul>{% for i in 3|get_range %}
        <li>{{ i }}. Do something</li>
      {% endfor %}</ul>

      Results with the HTML:
      <ul>
        <li>0. Do something</li>
        <li>1. Do something</li>
        <li>2. Do something</li>
      </ul>

      Instead of 3 one may use the variable set in the views
    """
    return range(value)


@register.filter(name='python_all')
def python_all(values):
    return all(values)


@register.filter
def index(indexable, i):
    return indexable[i]


@register.filter
def get_items(user, index):
    qs = Order.objects.filter(
        user=user
    )
    item_count = qs[index].items.all().count()
    if item_count > 1:
        item_list = []
        for i in range(item_count):
            item_list.append(qs[index].items.all()[i].item.name)
        return ", ".join(item_list)
    else:
        return qs[index].items.all()[0].item.name


@register.filter(name='times')
def times(number):
    return range(number)

@register.filter(name='isEmpty')
def isEmpty(products):
    if products:
        if len(products) == 0:
            return True
        else:
            return False
    else:
        return True

@register.filter
def get_rest_of_stars(stars):
    return 5 - stars



