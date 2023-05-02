from django import template

register = template.Library()

@register.filter
def extract_username(user):
    return user.username.split('@')[0]