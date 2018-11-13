'''
Created on Oct 31, 2016

@author: nanda
'''
from django.forms.models import ModelForm
from dryLab.models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.admin import widgets
from django import forms
from organization.simple_search import BaseSearchForm
from wetLab.models import Barcode
from wetLab.wrapper import SelectWithPop

class SequencingRunForm(ModelForm):
    use_required_attribute = False
    class Meta:
        model = SequencingRun
        exclude = ('project','run_approved','run_submitted','update_dcic',)
    
    def save (self, *args, **kwargs):
        if(self.changed_data != None):
            self.instance.update_dcic=True
        return super(SequencingRunForm, self).save(*args, **kwargs)
    
class SequencingRunSearchForm(BaseSearchForm):
    use_required_attribute = False
    formName = 'SequencingRunSearchForm'
    class Meta:
        base_qs = SequencingRun.objects
        search_fields = ('run_name',) 

        # assumes a fulltext index has been defined on the fields
        # 'name,description,specifications,id'
        fulltext_indexes = (
            ('run_name', 1), # name matches are weighted higher
            #('run_name,run_sequencing_platform', 1),
        )
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(SequencingRunSearchForm, self).__init__(*args, **kwargs)

class SeqencingFileForm(ModelForm):
    use_required_attribute = False
    file_barcode = forms.ModelChoiceField(Barcode.objects.all(), widget=SelectWithPop, required=False, label_suffix='addBarcode')
    
    class Meta:
        model = SeqencingFile
        exclude = ('sequencingFile_backupPath','sequencingFile_sha256sum','sequencingFile_exp','project','dcic_alias','update_dcic',)
    
    def save (self, *args, **kwargs):
        if(self.changed_data != None):
            self.instance.update_dcic=True
        return super(SeqencingFileForm, self).save(*args, **kwargs)
    

class SeqencingFileSearchForm(BaseSearchForm):
    use_required_attribute = False
    formName = 'SeqencingFileSearchForm'
    class Meta:
        base_qs = SeqencingFile.objects
        search_fields = ('sequencingFile_name',) 

        # assumes a fulltext index has been defined on the fields
        # 'name,description,specifications,id'
        fulltext_indexes = (
            ('sequencingFile_name', 1), # name matches are weighted higher
        )
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(SeqencingFileSearchForm, self).__init__(*args, **kwargs)

class FileSetForm(ModelForm):
    use_required_attribute = False
    class Meta:
        model = FileSet
        exclude = ('project',)
   
class AnalysisForm(ModelForm):
    use_required_attribute = False
    class Meta:
        model = Analysis
        exclude = ('analysis_exp','analysis_fields')
    

class ImageObjectsForm(ModelForm):
    use_required_attribute = False
    class Meta:
        model = ImageObjects
        exclude = ('project','dcic_alias','update_dcic',)
    def save (self, *args, **kwargs):
        if(self.changed_data != None):
            self.instance.update_dcic=True
        return super(ImageObjectsForm, self).save(*args, **kwargs)
   
        

