'''
Created on Oct 28, 2016

@author: nanda
'''

from django.forms.models import ModelForm
from wetLab.models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from wetLab.wrapper import add_related_field_wrapper, SelectWithPop,\
    MultipleSelectWithPop
from organization.models import Publication
from dryLab.models import ImageObjects
import json
from organization.validators import compareJsonInitial

class ModificationForm(ModelForm):
    use_required_attribute = False
    document = forms.ModelChoiceField(Document.objects.all(), widget=SelectWithPop, required=False, label_suffix='addDocumens')
    references = forms.ModelChoiceField(Publication.objects.all(), widget=SelectWithPop,required=False, label_suffix='addPublication')
    
    class Meta:
        model = Modification
        exclude = ('userOwner','constructs','modification_genomicRegions','target','dcic_alias','update_dcic',)
        fields = ['modification_name','modification_type','modification_vendor','modification_gRNA','references','document','url','dbxrefs','modification_description']
    
    def save (self, *args, **kwargs):
        if(self.changed_data != None):
            self.instance.update_dcic=True
        return super(ModificationForm, self).save(*args, **kwargs)
    
  

class ConstructForm(ModelForm):
    use_required_attribute = False
    document = forms.ModelChoiceField(Document.objects.all(), widget=SelectWithPop, required=False, label="Construct Map", help_text="Map of the construct - document", 
                                      label_suffix='addDocumens')
    class Meta:
        model = Construct
        exclude = ('dcic_alias','update_dcic',)
        
    def save (self, *args, **kwargs):
        if(self.changed_data != None):
            self.instance.update_dcic=True
        return super(ConstructForm, self).save(*args, **kwargs)
    

class GenomicRegionsForm(ModelForm):
    use_required_attribute = False
    class Meta:
        model = GenomicRegions
        exclude = ('dcic_alias','update_dcic',)
    
    def save (self, *args, **kwargs):
        if(self.changed_data != None):
            self.instance.update_dcic=True
        return super(GenomicRegionsForm, self).save(*args, **kwargs)
   

class TargetForm(ModelForm):
    use_required_attribute = False
    targeted_region = forms.ModelChoiceField(GenomicRegions.objects.all(), widget=SelectWithPop, required=False, label_suffix='addGenomicRegions')
    
    class Meta:
        model = Target
        exclude = ('dcic_alias','update_dcic',)
        fields = ['name','targeted_genes','targeted_region','targeted_proteins','targeted_rnas','targeted_structure','references','document','url','dbxrefs']
    
    def save (self, *args, **kwargs):
        if(self.changed_data != None):
            self.instance.update_dcic=True
        return super(TargetForm, self).save(*args, **kwargs)
    

class IndividualForm(ModelForm):
    use_required_attribute = False
    document = forms.ModelChoiceField(Document.objects.all(), widget=SelectWithPop, required=False, label_suffix='addDocumens')
    references = forms.ModelChoiceField(Publication.objects.all(), widget=SelectWithPop, required=False, label_suffix='addPublication')
    
#     def __init__(self, *args, **kwargs):
#         super(IndividualForm, self).__init__(*args, **kwargs)
        #add_related_field_wrapper(self, 'documents')
    class Meta:
        model = Individual
        exclude = ('individual_fields','userOwner','dcic_alias','update_dcic',)
        fields = ['individual_name','individual_vendor','individual_type','references','document','url','dbxrefs']
    
    def save (self, *args, **kwargs):
        if(self.instance.pk):
            idObj=self.instance.pk
            initialFields=Individual.objects.get(pk=idObj)
            obj_json_fields = json.loads(initialFields.individual_fields)
            compareJsonInitial(obj_json_fields,self)
        if(self.changed_data != None):
            self.instance.update_dcic=True
        return super(IndividualForm, self).save(*args, **kwargs)

class SelectForm(forms.Form):
        use_required_attribute = False
        Individual = forms.ModelChoiceField(queryset=Individual.objects.all(), empty_label=None)
        Biosource = forms.ModelChoiceField(queryset=Biosource.objects.all(), empty_label=None)
        Biosample = forms.ModelChoiceField(queryset=Biosample.objects.all(), empty_label=None)

class DocumentForm(ModelForm):
    use_required_attribute = False
    class Meta:
        model = Document
        exclude = ('dcic_alias','update_dcic',)
    
    def save (self, *args, **kwargs):
        if(self.changed_data != None):
            self.instance.update_dcic=True
        return super(DocumentForm, self).save(*args, **kwargs)


class ProtocolForm(ModelForm):
    use_required_attribute = False
    class Meta:
        model = Protocol
        exclude = ('userOwner','dcic_alias','update_dcic',)
    
    def save (self, *args, **kwargs):
        if(self.changed_data != None):
            self.instance.update_dcic=True
        return super(ProtocolForm, self).save(*args, **kwargs)
    
    

class BiosourceForm(ModelForm):
    use_required_attribute = False
    document = forms.ModelChoiceField(Document.objects.all(), widget=SelectWithPop, required=False, label_suffix='addDocumens')
    references = forms.ModelChoiceField(Publication.objects.all(), widget=SelectWithPop, required=False, label_suffix='addPublication')
    protocol = forms.ModelChoiceField(Protocol.objects.all(), widget=SelectWithPop,required=False, label="4DN SOP protocol", 
                                      help_text='Standard operation protocol for the cell line as determined by 4DN Cells Working Group', label_suffix='addProtocol')
    modifications = forms.ModelMultipleChoiceField(Modification.objects.all(), widget=MultipleSelectWithPop, required=False,
                                                   help_text='Expression or targeting vectors stably transfected to generate Crispr\'ed or other genomic modification',
                                                   label_suffix='addModification')
    
    
    class Meta:
        model = Biosource
        exclude = ('biosource_individual','dcic_alias','update_dcic',)
        fields = ['biosource_name','biosource_type','biosource_cell_line','biosource_cell_line_tier','protocol','biosource_vendor',
                  'cell_line_termid', 'modifications', 'biosource_tissue','references','document','url','dbxrefs','biosource_description']
    
    def save (self, *args, **kwargs):
        if(self.changed_data != None):
            self.instance.update_dcic=True
        return super(BiosourceForm, self).save(*args, **kwargs)
    

class BiosampleForm(ModelForm):
    use_required_attribute = False
    document = forms.ModelChoiceField(Document.objects.all(), widget=SelectWithPop, required=False, label_suffix='addDocumens')
    references = forms.ModelChoiceField(Publication.objects.all(), widget=SelectWithPop, required=False, label_suffix='addPublication')
    modifications = forms.ModelMultipleChoiceField(Modification.objects.all(), widget=MultipleSelectWithPop, required=False,
                                                   help_text="Expression or targeting vectors stably transfected to generate Crispr'ed or other genomic modification.", 
                                                   label_suffix='addModification')
    protocol= forms.ModelChoiceField(Protocol.objects.all(), widget=SelectWithPop, required=False, label="Growth protocol",
                                     help_text="Information about biosample preparation protocols.",
                                     label_suffix='addProtocol')
    biosample_TreatmentRnai = forms.ModelMultipleChoiceField(TreatmentRnai.objects.all(), widget=MultipleSelectWithPop, required=False,
                                                             help_text="Select previously created treatment", label_suffix='addTreatmentRnai')
    biosample_TreatmentChemical= forms.ModelMultipleChoiceField(TreatmentChemical.objects.all(), widget=MultipleSelectWithPop, required=False,
                                                                help_text="Select previously created treatment", label_suffix='addTreatmentChemical')
    biosample_OtherTreatment= forms.ModelMultipleChoiceField(OtherTreatment.objects.all(), widget=MultipleSelectWithPop, required=False,
                                                             help_text="Select previously created treatment", label_suffix='addOther')
    imageObjects = forms.ModelMultipleChoiceField (ImageObjects.objects.all(), widget=MultipleSelectWithPop, required=False,
                                                    help_text="Cell growth images, karyotype_image, morphology_image.", label_suffix='addImageObjects')
    protocols_additional = forms.ModelMultipleChoiceField (Protocol.objects.all(), widget=MultipleSelectWithPop, required=False,
                                                           label_suffix='addProtocol',
                                                           help_text="Protocols describing deviations from 4DN SOPs, including additional culture manipulations eg. stem cell differentiation \
                                                           or cell cycle synchronization if they do not follow recommended 4DN SOPs")
    
    class Meta:
        model = Biosample
        exclude = ('biosample_fields','userOwner','biosample_biosource', 'biosample_individual','dcic_alias','update_dcic',)
        fields = ['biosample_name','modifications','protocol','biosample_TreatmentRnai',
                  'biosample_TreatmentChemical','biosample_OtherTreatment','imageObjects','protocols_additional','biosample_type',
                  'references','document','url','dbxrefs','biosample_description']
    
    def save (self, *args, **kwargs):
        if(self.instance.pk):
            idObj=self.instance.pk
            initialFields=Biosample.objects.get(pk=idObj)
            obj_json_fields = json.loads(initialFields.biosample_fields)
            compareJsonInitial(obj_json_fields,self)
        if(self.changed_data != None):
            self.instance.update_dcic=True
        return super(BiosampleForm, self).save(*args, **kwargs)
    
 
class TreatmentRnaiForm(ModelForm):
    use_required_attribute = False
    document = forms.ModelChoiceField(Document.objects.all(), widget=SelectWithPop, required=False, label_suffix='addDocumens')
    references = forms.ModelChoiceField(Publication.objects.all(), widget=SelectWithPop, required=False, label_suffix='addPublication')
    constructs = forms.ModelChoiceField(Construct.objects.all(), widget=SelectWithPop, required=False, label_suffix='addConstruct')
    treatmentRnai_target = forms.ModelChoiceField(Target.objects.all(), widget=SelectWithPop, required=False, label_suffix='addTarget')
    
    class Meta:
        model = TreatmentRnai
        exclude = ('userOwner','dcic_alias','update_dcic',)
        fields = ['treatmentRnai_name','treatmentRnai_type','constructs','treatmentRnai_vendor','treatmentRnai_target','treatmentRnai_nucleotide_seq',
                  'references','document','url','dbxrefs','treatmentRnai_description']
    
    def save (self, *args, **kwargs):
        if(self.changed_data != None):
            self.instance.update_dcic=True
        return super(TreatmentRnaiForm, self).save(*args, **kwargs)
  

class TreatmentChemicalForm(ModelForm):
    use_required_attribute = False
    document = forms.ModelChoiceField(Document.objects.all(), widget=SelectWithPop, required=False, label_suffix='addDocumens')
    references = forms.ModelChoiceField(Publication.objects.all(), widget=SelectWithPop, required=False, label_suffix='addPublication')
    
    class Meta:
        model = TreatmentChemical
        exclude = ('userOwner','dcic_alias','update_dcic',)
        fields = ['treatmentChemical_name','treatmentChemical_chemical','treatmentChemical_concentration','treatmentChemical_concentration_units','treatmentChemical_duration','treatmentChemical_duration_units',
                  'treatmentChemical_temperature','references','document','url','dbxrefs','treatmentChemical_description']
    
    def save (self, *args, **kwargs):
        if(self.changed_data != None):
            self.instance.update_dcic=True
        return super(TreatmentChemicalForm, self).save(*args, **kwargs)


class OtherForm(ModelForm):
    use_required_attribute = False
    documents = forms.ModelChoiceField(Document.objects.all(), widget=SelectWithPop, required=False, label_suffix='addDocumens')
    references = forms.ModelChoiceField(Publication.objects.all(), widget=SelectWithPop, required=False, label_suffix='addPublication')
    
    class Meta:
        model = OtherTreatment
        exclude = ('userOwner',)
        fields = ['name','references','documents','url','dbxrefs','description']
    

class BarcodeForm(ModelForm):
    use_required_attribute = False
    class Meta:
        model = Barcode
        exclude = ('',)
#     def __init__(self, *args, **kwargs):
#         self.helper = FormHelper()
#         self.helper.form_id = 'id-exampleForm'
#         self.helper.form_class = 'blueForms'
#         self.helper.form_method = 'post'
#         self.helper.form_action = 'submit_survey'
#  
#         self.helper.add_input(Submit('submit', 'Submit'))
#         super(BarcodeForm, self).__init__(*args, **kwargs)
        
        