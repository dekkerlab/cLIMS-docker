from django.contrib import admin
from django.contrib.admin.options import ModelAdmin

from .models import *




admin.site.register(Modification)
admin.site.register(Individual)
admin.site.register(Document)
admin.site.register(Protocol)
admin.site.register(Vendor)
admin.site.register(Enzyme)
admin.site.register(Biosource)
admin.site.register(Biosample)
admin.site.register(Construct)
admin.site.register(GenomicRegions)
admin.site.register(Target)
admin.site.register(TreatmentRnai)
admin.site.register(TreatmentChemical)
admin.site.register(OtherTreatment)
admin.site.register(Barcode)
admin.site.register(Antibody)
