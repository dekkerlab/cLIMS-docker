from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from wetLab.models import References
from organization.validators import alphanumeric

# Create your models here.

class JsonObjField(models.Model):
    field_name = models.CharField(max_length=50, null=False, default="", db_index=True)
    field_type = models.CharField(max_length=50, null=False, default="")
    field_set = JSONField(null=True, blank=True)
    jsonField_description = models.CharField(max_length=200, null=True, blank=True)
    def __str__(self):
        return self.field_name
    class Meta:
        ordering = ['field_name']

class Choice(models.Model):
    choice_name = models.CharField(max_length=50, null=False, default="", db_index=True)
    choice_type = models.CharField(max_length=50, null=False, default="")
    choice_description =  models.CharField(max_length=200,  null=True, blank=True,)
    
    def __str__(self):
        return self.choice_name


class ContributingLabs(models.Model):
    lab_name = models.CharField(max_length=100, null=False, default="")
    def __str__(self):
        return self.lab_name
    class Meta:
        verbose_name_plural = 'Contributing Labs'
        ordering = ['lab_name']
    
class Project(models.Model):
    project_name = models.CharField(max_length=300, null=False, default="", unique=True,  db_index=True, help_text="Name of the project", validators=[alphanumeric])
    project_owner = models.ForeignKey(User, related_name='ownerProject', on_delete=models.CASCADE,)
    project_contributor = models.ManyToManyField(User, related_name='memberProject', blank=True, help_text="Collaborating members for this project")
    contributing_labs = models.ManyToManyField(ContributingLabs, blank=True, help_text="Contributing labs for this project")
    project_notes = models.TextField( null=True, blank=True, help_text="Notes for the project.")
    project_active = models.BooleanField(default=True, help_text="Is project currently in progress?")
    dcic_alias = models.CharField(max_length=500, null=False, unique=True, db_index=True, default="", help_text="Provide an alias name for the object for DCIC submission.")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.project_name
    class Meta:
        ordering = ['-pk']

class Experiment(References):
    UNIT_CHOICES = (
        ('', ''),
        ('g', 'g'),
        ('mg', 'mg'),
        ('μg', 'μg'),
        ('ml', 'ml'),
        ('cells', 'cells'),
    )
    experiment_name = models.CharField(max_length=300, null=False, unique=True, default="", db_index=True, validators=[alphanumeric])
    project = models.ForeignKey(Project,related_name='expProject', on_delete=models.CASCADE,)
    bio_rep_no = models.IntegerField(null=True, blank=True, help_text="Biological Replicate number")
    tec_rep_no = models.IntegerField(null=True, blank=True, help_text="Technical Replicate number")
    experiment_biosample = models.ForeignKey('wetLab.Biosample',related_name='expBio', on_delete=models.CASCADE,help_text="Starting biological material.")
    biosample_quantity = models.FloatField(null=False, default="0", help_text="Quantity of your starting material, e.g. No of cells")
    biosample_quantity_units= models.CharField(
        max_length=5,
        choices=UNIT_CHOICES,
        default='',
    )
    protocol = models.ForeignKey('wetLab.Protocol',related_name='expPro', on_delete=models.CASCADE,)
    type = models.ForeignKey('organization.JsonObjField', on_delete=models.CASCADE, related_name='expType', help_text="JsonObjField")
    experiment_fields = JSONField(null=True, blank=True)
    variation = models.ForeignKey('wetLab.Protocol',related_name='expProVar', verbose_name="protocol_variations", blank=True, null=True)
    experiment_enzyme = models.ForeignKey('wetLab.Enzyme',null=True, blank=True, related_name='expEnz',help_text="The enzyme used for digestion of the DNA.")
    antibody = models.ForeignKey('wetLab.Antibody',null=True, blank=True, related_name='expAntibody', help_text="For Cut&Run experiments reference to a antibody object")
    experiment_description = models.TextField(max_length=500,  null=True, blank=True, help_text="A short description of the experiment")
    authentication_docs =  models.ManyToManyField('wetLab.Protocol',blank=True, related_name='expAddProto', 
                                                   help_text="Attach any authentication document for your biosample here. e.g. Fragment Analyzer document, Gel images."
                                                   )
    imageObjects = models.ManyToManyField( 'dryLab.ImageObjects', related_name='expImg' , blank=True, help_text="Any additional image related to this experiment.")
    dcic_alias = models.CharField(max_length=500, null=False, default="", unique=True, db_index=True, help_text="Provide an alias name for the object for DCIC submission.")
    update_dcic = models.BooleanField(default=False, help_text="This object needs to be updated at DCIC.")
    finalize_dcic_submission = models.BooleanField(default=False, help_text="This object and related entries have been submitted to DCIC")
    contributing_labs = models.ManyToManyField(ContributingLabs, blank=True, help_text="Contributing labs for this experiment.")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.experiment_name
    class Meta:
        ordering = ['-pk']
    
    

class ExperimentSet(models.Model):
    experimentSet_name = models.CharField(max_length=300, null=False, default="", unique=True, db_index=True,  validators=[alphanumeric])
    project =  models.ForeignKey('organization.Project',related_name='expSetProject', on_delete=models.CASCADE,)
    experimentSet_type = models.ForeignKey('organization.Choice', on_delete=models.CASCADE, related_name='setChoice', help_text="The categorization of the set of experiments.")
    experimentSet_exp = models.ManyToManyField(Experiment, related_name='setExp')
    document = models.ForeignKey('wetLab.Document', on_delete=models.CASCADE, related_name='setDoc',null=True, blank=True)
    description =  models.TextField(max_length=500, null=False, default="")
    dcic_alias = models.CharField(max_length=500, null=False,  default="", unique=True, db_index=True, help_text="Provide an alias name for the object for DCIC submission.")
    update_dcic = models.BooleanField(default=False, help_text="This object needs to be updated at DCIC.")
    contributing_labs = models.ManyToManyField(ContributingLabs, blank=True, help_text="Contributing labs for this set.")
    
    
    def __str__(self):
        return self.experimentSet_name
    
class Publication(models.Model):
    name = models.CharField(max_length=300, null=False, default="", unique=True, db_index=True, validators=[alphanumeric])
    publication_title = models.CharField(max_length=200, null=False, default="", help_text="Title of the publication or communication.")
    publication_id = models.CharField(max_length=200,  null=False, default="", help_text="PMID or doi for the publication.")
    attachment = models.FileField(upload_to='uploads/')
    exp_sets_prod_in_pub = models.ForeignKey(ExperimentSet,related_name='pubProdSet', null=True, blank=True, on_delete=models.SET_NULL, help_text="List of experiment sets that are produced by this publication.")
    exp_sets_used_in_pub = models.ForeignKey(ExperimentSet,related_name='pubUsedSet', null=True, blank=True, on_delete=models.SET_NULL, help_text="List of experiment sets that are used (not produced) by this publication.")
    publication_categories = models.ForeignKey('organization.Choice', null=True, on_delete=models.SET_NULL, related_name='pubCatChoice', help_text="The categorization of publications.")
    publication_published_by = models.ForeignKey('organization.Choice', null=True, on_delete=models.SET_NULL, related_name='pubByChoice', help_text="Publication publisher.")
    dcic_alias = models.CharField(max_length=500, null=False, default="", unique=True, db_index=True, help_text="Provide an alias name for the object for DCIC submission.")
    update_dcic = models.BooleanField(default=False, help_text="This object needs to be updated at DCIC.")
    contributing_labs = models.ManyToManyField(ContributingLabs, blank=True, help_text="Contributing labs for this publication.")
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']
    
    
class Award(models.Model):
    award_name = models.CharField(max_length=50, null=False, default="", db_index=True)
    award_exp = models.ManyToManyField(Experiment, related_name='awardExp')
    award_project = models.ManyToManyField(Project, related_name='awardPro')
    
    def __str__(self):
        return self.award_name

class Tag(models.Model):
    tag_name = models.CharField(max_length=100, null=False, default="", unique=True, db_index=True, validators=[alphanumeric])
    project =  models.ForeignKey('organization.Project',related_name='tagProject', on_delete=models.CASCADE,)
    tag_exp = models.ManyToManyField(Experiment, related_name='tagExp')
    tag_user = models.ForeignKey(User, related_name='tagUser', on_delete=models.CASCADE,)
    
    def __str__(self):
        return self.tag_name

 




    
     
    