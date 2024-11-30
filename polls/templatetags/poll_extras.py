from django import template
from jalali_date import date2jalali, datetime2jalali

register = template.Library()


@register.filter(name="cut")
def cut(value, arg):
    """Removes all values of arg from the given string"""
    return value.replace(arg, "")

@register.filter(name="show_jalali_date")
def show_jalali_date(value):
    return date2jalali(value)

@register.filter(name="show_jalali_date_hover")
def show_jalali_date_hour(value):
    jalali_date = date2jalali(value)
    return f"{value.hour}:{value.minute} - {jalali_date.year}/{jalali_date.month}/{jalali_date.day}"

@register.filter(name="three_digits_currency")
def three_digits_currency(value: int):
    return "{:,}".format(value) + ' تومان'


@register.simple_tag
def multiply(quantity, price, *args, **kwargs):
    return three_digits_currency(quantity * price)


@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

@register.filter(name="get_color")
def get_color(recent_rainfall):
    if recent_rainfall < 5:
        return 'yellow'
    elif 5 <= recent_rainfall < 10:
        return 'orange'
    elif 10 <= recent_rainfall < 30:
        return 'lightgreen'
    elif 30 <= recent_rainfall < 50:
        return 'green'
    elif 50 <= recent_rainfall < 80:
        return 'blue'
    else:
        return 'red'