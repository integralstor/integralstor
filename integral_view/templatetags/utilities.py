from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def split(value,split_string):
  import unicodedata
  value = unicodedata.normalize('NFKD', value).encode('ascii','ignore')
  return value.split(split_string)[-1]

#Given a string with a seperator, it will replace the seperator with a space. Eg: hello_world will result hello world
@register.filter
def human_readable_title(value,split_string):
  return value.replace(split_string," ")

#Given a dict with a key, it will fetch the value of the key. Can be used recursively incase of nested dict. Eg : view_volume_info.html
@register.filter
def get_item(dictionary,key):
  return dictionary.get(key)
