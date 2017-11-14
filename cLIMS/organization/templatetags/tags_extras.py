'''
Created on Dec 15, 2016

@author: nanda
'''
from django import template  


register = template.Library()

@register.filter  
def contains(value, arg):
    """ 
  Usage: 
  {% if text|contains:"http://" %} 
  This is a link. 
  {% else %} 
  Not a link. 
  {% endif %} 
  """
    return arg in value   