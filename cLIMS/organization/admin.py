from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Project)
admin.site.register(Tag)
admin.site.register(ExperimentSet)
admin.site.register(Publication)
admin.site.register(Award)
admin.site.register(JsonObjField)
admin.site.register(Choice)
admin.site.register(Experiment)
admin.site.register(ContributingLabs)


