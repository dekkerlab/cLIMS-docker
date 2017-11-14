'''
Created on Apr 1, 2017

@author: nanda
'''
from django.core.validators import RegexValidator

alphanumeric = RegexValidator(r'^[0-9a-zA-Z-.]*$', 'Only alphanumeric characters, dashes, dots are allowed in names.')


def compareJsonInitial(obj_json_fields,self):
    for key in obj_json_fields:
            if(obj_json_fields[key]!=self.data[key]):
                self.instance.update_dcic=True