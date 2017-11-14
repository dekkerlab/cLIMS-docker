from django.db import models
from django.contrib.postgres.fields import JSONField
from organization.validators import alphanumeric

 
# Create your models here.

class SequencingRun(models.Model):
    run_name = models.CharField(max_length=100, null=False, default="", unique=True, db_index=True, validators=[alphanumeric])
    project = models.ForeignKey('organization.Project', related_name='runProject', on_delete=models.CASCADE,)
    run_Experiment = models.ManyToManyField('organization.Experiment', related_name='runExp')
    run_sequencing_center = models.ForeignKey('organization.Choice', null=True, blank=True, on_delete=models.CASCADE, related_name='runCenterChoice', help_text="Where the sequencing has been done.")
    run_sequencing_machine = models.ForeignKey('organization.Choice', null=True, blank=True, on_delete=models.CASCADE, related_name='runPlatChoice', help_text="The lab specific name of the machine used.")
    run_sequencing_instrument = models.ForeignKey('organization.Choice', null=True, blank=True, on_delete=models.CASCADE, related_name='runInsChoice', help_text="Instrument used for sequencing")
    run_submission_date = models.DateField();
    run_retrieval_date = models.DateField(null=True, blank=True,);
    run_approved = models.BooleanField(default=False)
    run_submitted = models.BooleanField(default=False)
    update_dcic = models.BooleanField(default=False, help_text="This object needs to be updated at DCIC.")
    
    def __str__(self):
        return self.run_name  
 
class SeqencingFile(models.Model):
    PAIR_CHOICES = (
        ('', ''),
        ('1', '1'),
        ('2', '2'),
    )
    sequencingFile_name = models.CharField(max_length=255, null=False, default="", unique=True, db_index=True)
    project = models.ForeignKey('organization.Project', related_name='fileProject', on_delete=models.CASCADE,)
    file_format = models.ForeignKey('organization.Choice', on_delete=models.CASCADE, related_name='fileChoice', help_text="Type of file format.")
    relationship_type = models.ForeignKey('organization.Choice', on_delete=models.CASCADE, related_name='relChoice',null=True, blank=True,help_text="Type of relation with other files.")
    related_files = models.ForeignKey('SeqencingFile', null=True, blank=True,on_delete=models.SET_NULL, help_text="Related file.")
    #file_classification = models.ForeignKey('organization.Choice', null=True, blank=True, on_delete=models.CASCADE, related_name='fileclassChoice', help_text="General classification group for the File (raw, processed, ancillary (eg. index files))")
    #file_classification = models.CharField(max_length=200, null=True, blank=True, help_text="General classification group for the File (raw, processed, ancillary (eg. index files))")
    file_format_specifications = models.ForeignKey('wetLab.Document', null=True, blank=True, help_text="Text or pdf files that further explain the file format")
    file_barcode = models.ForeignKey('wetLab.Barcode', on_delete=models.SET_NULL, null=True, blank=True, help_text="Barcode attached to the file.")
    barcode_in_read = models.CharField(
        max_length=1,
        choices=PAIR_CHOICES,
        default='',
        null=True, 
        blank=True,
        help_text="The read the barcode is located on."
    )
    flowcell_details_chunk = models.CharField(max_length=500, null=True, blank=True, help_text="The file chunk label as assigned by Illumina software when splitting up a \
                                                                        fastq into specified chunk sizes, this label is used to re-assemble the chunks into the original file in the correct order.")
    flowcell_details_lane = models.CharField(max_length=200, null=True, blank=True, help_text="")
    paired_end = models.CharField(
        max_length=1,
        choices=PAIR_CHOICES,
        default='',
        null=True, 
        blank=True,
        help_text="Which pair the file belongs to (if paired end library)"
    )
    read_length = models.IntegerField(null=True, blank=True, help_text="The length of the enzyme recognition sequence.")
    sequencingFile_mainPath = models.CharField(max_length=500, null=False, default="")
    sequencingFile_backupPath = models.CharField(max_length=500, null=False, default="")
    sequencingFile_sha256sum = models.CharField(max_length=64, null=False, default="")
    sequencingFile_md5sum = models.CharField(max_length=32, null=False, default="")
    sequencingFile_run = models.ForeignKey(SequencingRun, related_name='fileRun', on_delete=models.CASCADE,)
    sequencingFile_exp = models.ForeignKey('organization.Experiment', related_name='fileExp', on_delete=models.CASCADE,)
    dbxrefs = models.CharField(max_length=500, null=True, blank=True, help_text="Unique identifiers from external resources, enter as a database name:identifier eg. HGNC:PARK2")
    dcic_alias = models.CharField(max_length=500, null=False, default="", unique=True, db_index=True, help_text="Provide an alias name for the object for DCIC submission.")
    update_dcic = models.BooleanField(default=False, help_text="This object needs to be updated at DCIC.")
    def __str__(self):
        return self.sequencingFile_name

class FileSet(models.Model):
    fileSet_name = models.CharField(max_length=50, null=False, default="", unique=True, db_index=True, validators=[alphanumeric])
    project = models.ForeignKey('organization.Project', related_name='filesetProject', on_delete=models.CASCADE,)
    fileset_type = models.ForeignKey('organization.Choice', on_delete=models.CASCADE, related_name='fileSetChoice', help_text="The categorization of the set of files.")
    fileSet_file = models.ManyToManyField(SeqencingFile, related_name='fileSetFile')
    fileset_description = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return self.fileSet_name


class Analysis(models.Model):
    analysis_name = models.CharField(max_length=50, null=False, default="", unique=True, db_index=True, validators=[alphanumeric])
    analysis_type = models.ForeignKey('organization.JsonObjField', related_name='analysisType', on_delete=models.CASCADE, help_text="AnalysisField")
    analysis_fields = JSONField(null=True, blank=True)
    analysis_file = models.ManyToManyField(SeqencingFile, related_name='analysisFile')
    analysis_exp = models.ForeignKey('organization.Experiment', related_name='analysisExp', on_delete=models.CASCADE,)
    analysis_import = models.FileField(upload_to='uploads/', null=True, blank=True, help_text="Import .gz file")
    analysis_hiGlass = models.FileField(null="True", blank="True", upload_to='uploads/', help_text="Import HiGlass file")
    def __str__(self):
        return self.analysis_name
    
    class Meta:
        verbose_name_plural = 'Analysis'

class Images(models.Model): 
    image_path = models.FilePathField(max_length=500)
    image_analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE)
    def __str__(self):
        return self.image_path
    class Meta:
        verbose_name_plural = 'Images'

class ImageObjects(models.Model):
    imageObjects_name = models.CharField(max_length=50, null=False, default="", unique=True, db_index=True, validators=[alphanumeric])
    imageObjects_images = models.FileField(upload_to='uploads/', help_text="Import image file", max_length=200)
    imageObjects_type = models.ForeignKey('organization.Choice', null=False, on_delete=models.CASCADE, related_name='imgChoice', help_text="The categorization of the images.")
    description = models.CharField(max_length=200, null=True, blank=True)
    project = models.ForeignKey('organization.Project', related_name='imgProject', on_delete=models.CASCADE,)
    dcic_alias = models.CharField(max_length=500, null=False, default="", unique=True, db_index=True, help_text="Provide an alias name for the object for DCIC submission.")
    update_dcic = models.BooleanField(default=False, help_text="This object needs to be updated at DCIC.")
    
    def __str__(self):
        return self.imageObjects_name
    class Meta:
        verbose_name_plural = 'ImageObjects'
        
        
