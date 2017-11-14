from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(SequencingRun)
admin.site.register(FileSet)
admin.site.register(SeqencingFile)
admin.site.register(Analysis)  
admin.site.register(Images)  
admin.site.register(ImageObjects) 