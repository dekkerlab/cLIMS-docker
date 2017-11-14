'''
Created on Dec 16, 2016

@author: nanda
'''
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib import admin
from django.template.loader import render_to_string
import django.forms as forms


def add_related_field_wrapper(form, col_name):
    rel_model = form.Meta.model
    rel = rel_model._meta.get_field(col_name).rel
    form.fields[col_name].widget = RelatedFieldWidgetWrapper(form.fields[col_name].widget, rel, 
    admin.site, can_add_related=True, can_change_related=True)


class SelectWithPop(forms.Select):
    def render(self, name, *args, **kwargs):
        html = super(SelectWithPop, self).render(name, *args, **kwargs)
        popupplus = render_to_string("popplus.html", {'field': name})
        return html+popupplus
    
class MultipleSelectWithPop(forms.SelectMultiple):
    def render(self, name, *args, **kwargs):
        html = super(MultipleSelectWithPop, self).render(name, *args, **kwargs)
        popupplus = render_to_string("popplus.html", {'field': name})
        return html+popupplus
    

