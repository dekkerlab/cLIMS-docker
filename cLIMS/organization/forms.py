'''
Created on Oct 25, 2016

@author: nanda
'''
from django.forms.models import ModelForm
from organization.models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from organization.simple_search import BaseSearchForm
from django import forms
from wetLab.models import Protocol, Document
from wetLab.wrapper import SelectWithPop, MultipleSelectWithPop
from dryLab.models import ImageObjects
import json
from organization.validators import *

class ProjectForm(ModelForm):
    use_required_attribute = False
    class Meta:
        model = Project
        exclude = ('project_owner','dcic_alias','update_dcic',)
    
    

class ProjectSearchForm(BaseSearchForm):
    formName = 'ProjectSearchForm'
    use_required_attribute = False
    class Meta:
        base_qs = Project.objects
        search_fields = ('project_name', 'project_notes',) 

        # assumes a fulltext index has been defined on the fields
        # 'name,description,specifications,id'
        fulltext_indexes = (
            ('experiment_name', 2), # name matches are weighted higher
            ('experiment_name,experiment_description', 1),
        )
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(ProjectSearchForm, self).__init__(*args, **kwargs)

        
class ExperimentForm(ModelForm):
    use_required_attribute = False
    document = forms.ModelChoiceField(Document.objects.all(), widget=SelectWithPop, required=False, label_suffix='addDocumens')
    references = forms.ModelChoiceField(Publication.objects.all(), widget=SelectWithPop,required=False, label_suffix='addPublication')
    protocol = forms.ModelChoiceField(Protocol.objects.all(), widget=SelectWithPop, label_suffix='addProtocol', label="Experiment protocol")
    imageObjects = forms.ModelMultipleChoiceField (ImageObjects.objects.all(), widget=MultipleSelectWithPop, required=False, label_suffix='addImageObjects',
                                                   help_text="Any additional image related to this experiment.")
    authentication_docs = forms.ModelMultipleChoiceField (Protocol.objects.all(), widget=MultipleSelectWithPop, required=False,
                                                           label_suffix='addProtocol',
                                                           help_text="Images or Documents that authenticate the experiment e.g. Fragment Analyzer document, Gel images.")
    variation = forms.ModelChoiceField(Protocol.objects.all(), widget=SelectWithPop, label_suffix='addProtocol', required=False, label="Protocol Variations")
    
    class Meta:
        model = Experiment
        exclude = ('project','experiment_biosample','experiment_fields','dcic_alias','update_dcic','finalize_dcic_submission',)
        fields = ['experiment_name','bio_rep_no','tec_rep_no','biosample_quantity','biosample_quantity_units','protocol','type','variation','experiment_enzyme',
                  'antibody','authentication_docs','imageObjects','references','document','contributing_labs','url','dbxrefs','experiment_description']
         
       
        
    def save (self, *args, **kwargs):
        if(self.instance.pk):
            idObj=self.instance.pk
            initialFields=Experiment.objects.get(pk=idObj)
            obj_json_fields = json.loads(initialFields.experiment_fields)
            compareJsonInitial(obj_json_fields,self)
        if(self.changed_data != None):
            self.instance.update_dcic=True
        return super(ExperimentForm, self).save(*args, **kwargs)
      
#     def clean(self):
#         if(self.changed_data != None):
#             print(self.changed_data)
#             self.data["update_dcic"]=True

   

class ExperimentSearchForm(BaseSearchForm):
    use_required_attribute = False
    formName = 'ExperimentSearchForm'
    class Meta:
        base_qs = Experiment.objects
        search_fields = ('experiment_name', 'experiment_description',) 

        # assumes a fulltext index has been defined on the fields
        # 'name,description,specifications,id'
        fulltext_indexes = (
            ('experiment_name', 2), # name matches are weighted higher
            ('experiment_name,experiment_description', 1),
        )
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(ExperimentSearchForm, self).__init__(*args, **kwargs)
    

class ExperimentSetForm(ModelForm):
    use_required_attribute = False
    document = forms.ModelChoiceField(Document.objects.all(), widget=SelectWithPop, required=False, label_suffix='addDocumens')
    class Meta:
        model = ExperimentSet
        exclude = ('project','update_dcic','dcic_alias',)
    
    def save (self, *args, **kwargs):
        if(self.changed_data != None):
            self.instance.update_dcic=True
        return super(ExperimentSetForm, self).save(*args, **kwargs)
    
class PublicationForm(ModelForm):
    use_required_attribute = False
    class Meta:
        model = Publication
        exclude = ('dcic_alias','update_dcic',)
    def save (self, *args, **kwargs):
        if(self.changed_data != None):
            self.instance.update_dcic=True
        return super(PublicationForm, self).save(*args, **kwargs)
    

class AwardForm(ModelForm):
    use_required_attribute = False
    class Meta:
        model = Award
        exclude = ('',)
   

class TagForm(ModelForm):
    use_required_attribute = False
    class Meta:
        model = Tag
        exclude = ('tag_user','project',)

class CloneExperimentForm(forms.Form):
    use_required_attribute = False
    experiment_name = forms.CharField(max_length=100, validators=[alphanumeric], help_text="Name of the experiment")
    experiment_description = forms.CharField(max_length=200, widget=forms.Textarea(), help_text="A short description of the experiment")
    biosample_name = forms.CharField(max_length=100, validators=[alphanumeric],required=False, help_text="Name of the Biosample")
    biosample_description = forms.CharField(max_length=200, widget=forms.Textarea(), required=False, help_text="A plain text for catalog description.")

class ImportSequencingFilesForm(forms.Form):
    use_required_attribute = False
    excel_file=forms.FileField(help_text="Upload the excel sheet in correct format here")
    
    
    
    
    
     
    
    
    
    
    



