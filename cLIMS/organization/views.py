from django.contrib.auth.views import login as contrib_login
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, render_to_response,\
    get_object_or_404
from django.views.generic.base import View
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from organization.models import *
from organization.forms import *
from django.forms.formsets import formset_factory
import json
from django.http.response import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError, PermissionDenied
from wetLab.forms import *
from dryLab.forms import *
from django.apps.registry import apps
from _collections import defaultdict, OrderedDict
import tarfile
import os
from cLIMS.base import *
from organization.extractAnalysis import extractHiCAnalysis, extract5CAnalysis
import itertools
import re
from django.utils.html import escape
from django.template.context import RequestContext
from organization.decorators import class_login_required, require_permission,\
    view_only
from django.dispatch.dispatcher import receiver
from django.contrib.auth.signals import user_logged_in
from django.contrib import messages
from organization.export import exportDCIC
from django.utils.decorators import method_decorator
import organization
from django.contrib.auth.models import Permission
from organization.importSeqFiles import *
import ast
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.

@receiver(user_logged_in)
def sig_user_logged_in(sender, user, request, **kwargs):
    for i in request.user.groups.all():
        if("view_only_user" in [x.codename for x in i.permissions.all()]):
            request.session['view_only_user'] = True
        else:
            request.session['view_only_user'] = False
    if('Member' in map(str, request.user.groups.all())):
        request.session['currentGroup'] = "member"
    elif('MemberWithEditAccess' in map(str, request.user.groups.all())):
        request.session['currentGroup'] = "memberWithEditAccess"
    elif ('Admin' in map(str, request.user.groups.all()) or 'Principal Investigator' in map(str, request.user.groups.all())):
        request.session['currentGroup'] = "admin"


def login(request, **kwargs):
    if request.user.is_authenticated():
        return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        return contrib_login (request, **kwargs)

##Order Json field
def orderByNumber(jsonDict):
    jsonList = jsonDict.items()
    sorted_list = sorted(jsonList, key=lambda k: (int(k[1]['order'])))
    sorted_dict= OrderedDict(sorted_list)
    return sorted_dict        
     
@class_login_required
class HomeView(View):
    template_name = 'home.html'
    error_page = 'error.html'
    
    def get(self,request):
        context = {}
        context['currentUserName']= request.user.username
        if('Member' in map(str, request.user.groups.all())):
            request.session['currentGroup'] = "member"
            prj = Project.objects.filter((Q(project_owner=request.user.id) | Q(project_contributor=request.user.id)) , project_active="True").distinct().order_by('-pk')
            context['projects']= prj
            return render(request, self.template_name, context)
        elif('MemberWithEditAccess' in map(str, request.user.groups.all())):
            request.session['currentGroup'] = "memberWithEditAccess"
            prj = Project.objects.filter((Q(project_owner=request.user.id) | Q(project_contributor=request.user.id)) , project_active="True").distinct().order_by('-pk')
            context['projects']= prj
            return render(request, self.template_name, context)
        elif ('Admin' in map(str, request.user.groups.all()) or 'Principal Investigator' in map(str, request.user.groups.all())):
            request.session['currentGroup'] = "admin"
            prj = Project.objects.filter(project_active="True").order_by('-pk')
            context['projects']= prj
            return render(request, self.template_name, context)
        else:
            return render(request, self.error_page)


@class_login_required
class ErrorView(View):
    error_page = 'accessError.html'
    def get(self,request):
        project_owner = User.objects.get(pk=request.session['project_ownerId'])
        context = {}
        context['project_owner']=project_owner
        return render(request, self.error_page, context)
    
@class_login_required
class ErrorViewOnly(View):
    error_page = 'viewOnlyError.html'
    def get(self,request):
        return render(request, self.error_page)
        

@class_login_required 
class AddProject(View): 
    template_name = 'customForm.html'
    error_page = 'error.html'
    form_class = ProjectForm
    
    def get(self,request):
        form = self.form_class()
        return render(request, self.template_name,{'form':form})
    
    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            result = form.save(commit= False)
            result.project_owner = request.user
            aliasList=["Project",result.project_name]
            result.dcic_alias = LABNAME +"_".join(aliasList)
            result.save()
            project_contributor = request.POST.getlist('project_contributor')
            if(project_contributor):
                for contributor in project_contributor:
                    user = User.objects.get(pk=contributor)
                    result.project_contributor.add(user)
            return HttpResponseRedirect('/showProject/')
        else:
            return render(request, self.template_name,{'form':form})
    
    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required
class ShowProject(View):
    template_name = 'showProject.html'
    error_page = 'error.html'
    
    def get(self,request):
        userType = request.session['currentGroup']
        userId = request.user.id
        if (userType == "member"):
            obj = Project.objects.filter(Q(project_owner=userId) |  Q(project_contributor=userId)).distinct().order_by('-pk')
        elif (userType == "memberWithEditAccess"):
            obj = Project.objects.filter(Q(project_owner=userId) |  Q(project_contributor=userId)).distinct().order_by('-pk')
        elif (userType == "admin"):
            obj = Project.objects.all().order_by('-pk')
        else:
            raise ValidationError
        context = {
            'object': obj,
        }
        
        return render(request, self.template_name, context)
    



@class_login_required
class DetailProject(View):
    template_name = 'detailProject.html'
    error_page = 'error.html'
    def get(self,request,pk):
        request.session['projectId'] = pk
        request.session['finalizeOnly'] = False
        context = {}
        prj = Project.objects.get(pk=pk)
        request.session['project_ownerId']=prj.project_owner.id
    #     units = Lane.objects.filter(project=pk)
    #     files = DeepSeqFile.objects.filter(project=pk)
        experiments = Experiment.objects.filter(project=pk).order_by('-pk')
        sequencingRuns = SequencingRun.objects.filter(project=pk).order_by('-pk')
        experimentSets = ExperimentSet.objects.filter(project=pk).order_by('-pk')
        fileSets = FileSet.objects.filter(project=pk).order_by('-pk')
        tags = Tag.objects.filter(project=pk).order_by('-pk')
        
#         for run in sequencingRuns:
#             run.run_Add_Barcode = run.get_run_Add_Barcode_display()
        context['project']= prj
        context['sequencingRuns']= sequencingRuns
    #     context['files']= files
        context['experiments']= experiments
        context['experimentSets']= experimentSets
        context['fileSets']= fileSets
        context['tags']= tags
        return render(request, self.template_name, context)
    

def addUnits(jsonValue):
    jsonValueLoad=json.loads(jsonValue)
    for keys in list(jsonValueLoad):
        values=jsonValueLoad[keys]
        if("units" in keys):
            splitKey=keys.split("_units")
            att=jsonValueLoad[splitKey[0]]
            unit=values
            jsonValueLoad[splitKey[0]]=att+" "+unit
            del jsonValueLoad[keys]
    return (jsonValueLoad)

@class_login_required
class DetailExperiment(View):
    template_name = 'detailExperiment.html'
    error_page = 'error.html'
    def get(self,request,pk):
        request.session['experimentId'] = pk
        context = {}
        experiment = Experiment.objects.get(pk=pk)
        if(experiment.experiment_fields):
            experiment.protocol_fields = json.loads(experiment.experiment_fields)
        individual = False
        biosource = False
        treatmentRnai = False
        treatmentChemical = False
        otherTreatment = False
        modification = False
        seqencingFiles = False
        analysis = False
        modificationBio = False
        
        
        if (Biosample.objects.get(expBio__pk=pk)):
            biosample = Biosample.objects.get(expBio__pk=pk)
            if(Biosource.objects.get(bioSource__pk=biosample.pk)):
                biosource = Biosource.objects.get(bioSource__pk=biosample.pk)
                if(Individual.objects.filter(sourceInd__pk=biosource.pk)):
                    individual = Individual.objects.filter(sourceInd__pk=biosource.pk)
                if(Modification.objects.filter(biosMod__pk=biosource.pk)):
                    modificationBio = Modification.objects.filter(biosMod__pk=biosource.pk)
            if(TreatmentRnai.objects.filter(biosamTreatmentRnai=biosample.pk)):
                treatmentRnai = TreatmentRnai.objects.filter(biosamTreatmentRnai=biosample.pk)
            if(TreatmentChemical.objects.filter(biosamTreatmentChemical=biosample.pk)):
                treatmentChemical = TreatmentChemical.objects.filter(biosamTreatmentChemical=biosample.pk)
            if(OtherTreatment.objects.filter(biosamOtherTreatment=biosample.pk)):
                otherTreatment = OtherTreatment.objects.filter(biosamOtherTreatment=biosample.pk)
            
        if((Modification.objects.filter(bioMod__pk=biosample.pk))):
            modification = Modification.objects.filter(bioMod__pk=biosample.pk)
           
        if((SeqencingFile.objects.filter(sequencingFile_exp=pk))):
            seqencingFiles = SeqencingFile.objects.filter(sequencingFile_exp=pk).order_by('pk')
        if((Analysis.objects.filter(analysis_exp=pk))):
            analysis = Analysis.objects.filter(analysis_exp=pk).order_by('pk')

        for i in individual:
            i.individual_fields = addUnits(i.individual_fields)
        if(biosample.biosample_fields):
            biosample.biosample_fields = addUnits(biosample.biosample_fields)   
           
        context['experiment']= experiment
        context['biosample']= biosample
        context['biosource']= biosource
        context['modificationBio']= modificationBio
        
        context['individuals']= individual
        context['treatmentRnai']= treatmentRnai
        context['treatmentChemical']= treatmentChemical
        context['otherTreatment']= otherTreatment
        context['modification']= modification
       
        context['seqencingFiles']= seqencingFiles
        context['analyses']= analysis
        return render(request, self.template_name, context)

@class_login_required
class DetailSequencingRun(View):
    template_name = 'detailRun.html'
    error_page = 'error.html'
    def get(self,request,pk):
        context = {}
        sequencingRun = SequencingRun.objects.get(pk=pk)
#         barcodes = Barcode.objects.filter(barcode_run=pk)
#         sequencingRun.run_Add_Barcode = sequencingRun.get_run_Add_Barcode_display()
        context['sequencingRun']= sequencingRun
#         context['barcodes']= barcodes
#         print(barcodes)
        return render(request, self.template_name, context)

@class_login_required
class DetailAnalysis(View):
    error_page = 'error.html'
    def get(self,request,pk):
        context = {}
        analysis = Analysis.objects.get(pk=pk)
        images = Images.objects.filter(image_analysis=pk)
        analysis.analysis_fields = json.loads(analysis.analysis_fields)
        if (str(analysis.analysis_type) == "Hi-C Analysis" ):
            context['object']= analysis
            context['images'] = images
            template_name = 'detailAnalysisHiC.html'
        elif (str(analysis.analysis_type) == "5C Analysis" ):
            context['object']= analysis
            context['images'] = images
            template_name = 'detailAnalysis5C.html'
        
        return render(request, template_name, context)

@class_login_required
class DetailPublication(View):
    template_name = 'detailPublication.html'
    error_page = 'error.html'
    def get(self,request,pk):
        context = {}
        publication = Publication.objects.get(pk=pk)
        context['publication']= publication
        return render(request, self.template_name, context)

@class_login_required
class DetailProtocol(View):
    template_name = 'detailProtocol.html'
    error_page = 'error.html'
    def get(self,request,pk):
        context = {}
        protocol = Protocol.objects.get(pk=pk)
        context['protocol']= protocol
        return render(request, self.template_name, context)


@class_login_required
class DetailDocument(View):
    template_name = 'detailDocument.html'
    error_page = 'error.html'
    def get(self,request,pk):
        context = {}
        document = Document.objects.get(pk=pk)
        context['document']= document
        return render(request, self.template_name, context)


@class_login_required
class DetailEnzyme(View):
    template_name = 'detailEnzyme.html'
    error_page = 'error.html'
    def get(self,request,pk):
        context = {}
        enzyme = Enzyme.objects.get(pk=pk)
        context['enzyme']= enzyme
        return render(request, self.template_name, context)

@class_login_required
class DetailConstruct(View):
    template_name = 'detailConstructs.html'
    error_page = 'error.html'
    def get(self,request,pk):
        context = {}
        construct = Construct.objects.get(pk=pk)
        context['construct']= construct
        return render(request, self.template_name, context)

@class_login_required
class DetailGenomicRegions(View):
    template_name = 'detailGenomicRegion.html'
    error_page = 'error.html'
    def get(self,request,pk):
        context = {}
        region = GenomicRegions.objects.get(pk=pk)
        context['region']= region
        return render(request, self.template_name, context)

@class_login_required
class DetailTarget(View):
    template_name = 'detailTarget.html'
    error_page = 'error.html'
    def get(self,request,pk):
        context = {}
        target = Target.objects.get(pk=pk)
        context['target']= target
        return render(request, self.template_name, context)


def createJSON(request, fieldTypePk):
    json_object = JsonObjField.objects.get(pk=fieldTypePk).field_set
    data = {}
    for keys in json_object:
        formVal = request.POST.get(keys)
        data[keys] = formVal
    json_data = json.dumps(data)
    return(json_data)


@class_login_required
class AddIndividual(View): 
    template_name = 'customForm.html'
    error_page = 'error.html'
    form_class = IndividualForm
    selectForm_class = SelectForm
    
    def get(self,request):
        selectForm = self.selectForm_class()
        selectForm.fields["Individual"].queryset = Individual.objects.all()
        isExisting = (selectForm.fields["Individual"].queryset.count() > 0)
        existing = selectForm['Individual']
        form = self.form_class()
        form.fields["individual_type"].queryset = JsonObjField.objects.filter(field_type="Individual")
        return render(request, self.template_name,{'form':form, 'form_class':"Individual", 'existing':existing,'isExisting':isExisting})
    
    def post(self,request):
        form = self.form_class(request.POST)
        selectForm = self.selectForm_class(request.POST)
        existingSelect = request.POST.get('selectForm')
        if existingSelect == "old":
            request.session['individualPK'] = selectForm['Individual'].value()
            return HttpResponseRedirect('/addBiosource/')
        else:   
            if form.is_valid():
                individual = form.save(commit= False)
                individual_type = request.POST.get('individual_type')
                individual.userOwner = User.objects.get(pk=request.user.pk)
                individual.individual_fields = createJSON(request, individual_type)
                aliasList=["Individual",individual.individual_name]
                individual.dcic_alias = LABNAME +"_".join(aliasList)
                individual.save()
                labs = request.POST.getlist('contributing_labs')
                for l in labs:
                    iLab = ContributingLabs.objects.get(pk=l)
                    individual.contributing_labs.add(iLab)
                request.session['individualPK'] = individual.pk
                return HttpResponseRedirect('/addBiosource/')
            else:
                existing = selectForm['Individual']
                selectForm.fields["Individual"].queryset = Individual.objects.all()
                isExisting = (selectForm.fields["Individual"].queryset.count() > 0)
                form.fields["individual_type"].queryset = JsonObjField.objects.filter(field_type="Individual")
                return render(request, self.template_name,{'form':form, 'form_class':"Individual", 'existing':existing,'isExisting':isExisting})
    
    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required
class AddBiosource(View): 
    template_name = 'customForm.html'
    error_page = 'error.html'
    form_class = BiosourceForm
    selectForm_class = SelectForm
    
    def get(self,request):
        selectForm = self.selectForm_class()
        selectForm.fields["Biosource"].queryset = Biosource.objects.filter(biosource_individual=request.session['individualPK'])
        isExisting = (selectForm.fields["Biosource"].queryset.count() > 0)
        existing = selectForm['Biosource']
        form = self.form_class()
        form.fields["biosource_type"].queryset = Choice.objects.filter(choice_type="biosource_type")
        form.fields["biosource_cell_line_tier"].queryset = Choice.objects.filter(choice_type="biosource_cell_line_tier")
        form.fields["protocol"].queryset = Protocol.objects.filter(~Q(protocol_type__choice_name="Authentication document"))
        
#         formAttr=["modifications"]
#         if(self.request.session['currentGroup'] != "admin"):
#             for f in formAttr:
#                 form.fields[f].queryset = (form.fields[f].queryset).filter(userOwner=self.request.user.pk)
        
        return render(request, self.template_name,{'form':form, 'form_class':"Biosource", 'existing':existing,'isExisting':isExisting})
    
    def post(self,request):
        form = self.form_class(request.POST)
        selectForm = self.selectForm_class(request.POST)
        existingSelect = request.POST.get('selectForm')
        if existingSelect == "old":
            request.session['biosourcePK'] =  selectForm['Biosource'].value()
            return HttpResponseRedirect('/addBiosample/')
        else:
            if form.is_valid():
                biosource = form.save(commit=False)
                individualPK = request.session['individualPK']
                biosource.biosource_individual = Individual.objects.get(pk=individualPK)
                aliasList=["Biosource",biosource.biosource_name]
                biosource.dcic_alias = LABNAME +"_".join(aliasList)
                biosource.save()
                modifications = request.POST.getlist('modifications')
                for m in modifications:
                    mod = Modification.objects.get(pk=m)
                    biosource.modifications.add(mod)
                labs = request.POST.getlist('contributing_labs')
                for l in labs:
                    iLab = ContributingLabs.objects.get(pk=l)
                    biosource.contributing_labs.add(iLab)
                request.session['biosourcePK'] = biosource.pk
                return HttpResponseRedirect('/addBiosample/')
            else:
                selectForm.fields["Biosource"].queryset = Biosource.objects.filter(biosource_individual=request.session['individualPK'])
                isExisting = (selectForm.fields["Biosource"].queryset.count() > 0)
                existing = selectForm['Biosource']
                form.fields["biosource_type"].queryset = Choice.objects.filter(choice_type="biosource_type")
                form.fields["biosource_cell_line_tier"].queryset = Choice.objects.filter(choice_type="biosource_cell_line_tier")
                form.fields["protocol"].queryset = Protocol.objects.filter(~Q(protocol_type__choice_name="Authentication document"))
#                 formAttr=["modifications"]
#                 if(self.request.session['currentGroup'] != "admin"):
#                     for f in formAttr:
#                         form.fields[f].queryset = (form.fields[f].queryset).filter(userOwner=self.request.user.pk)
                return render(request, self.template_name,{'form':form, 'form_class':"Biosource", 'existing':existing,'isExisting':isExisting})
    
    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required
class AddBiosample(View): 
    template_name = 'customForm.html'
    error_page = 'error.html'
    form_class = BiosampleForm
    selectForm_class = SelectForm
    
    def get(self,request):
        selectForm = self.selectForm_class()
        selectForm.fields["Biosample"].queryset = Biosample.objects.filter(biosample_biosource=request.session['biosourcePK'])
        isExisting = (selectForm.fields["Biosample"].queryset.count() > 0)
        existing = selectForm['Biosample']
        form = self.form_class()
        form.fields["biosample_type"].queryset = JsonObjField.objects.filter(field_type="Biosample")
        form.fields["imageObjects"].queryset = ImageObjects.objects.filter(project=request.session['projectId'])
        form.fields["authentication_protocols"].queryset = Protocol.objects.filter(protocol_type__choice_name="Authentication document")
        form.fields["protocol"].queryset = Protocol.objects.filter(~Q(protocol_type__choice_name="Authentication document"))
        form.fields["protocols_additional"].queryset = Protocol.objects.filter(~Q(protocol_type__choice_name="Authentication document"))
        
        formAttr=["authentication_protocols"]
        if(self.request.session['currentGroup'] != "admin"):
            for f in formAttr:
                form.fields[f].queryset = (form.fields[f].queryset).filter(userOwner=self.request.user.pk)

        return render(request, self.template_name,{'form':form, 'form_class':"Biosample", 'existing':existing,'isExisting':isExisting})
    
    def post(self,request):
        form = self.form_class(request.POST)
        selectForm = self.selectForm_class(request.POST)
        existingSelect = request.POST.get('selectForm')
        if existingSelect == "old":
            request.session['biosamplePK'] =  selectForm['Biosample'].value()
            return HttpResponseRedirect('/addExperiment/')
        else:
            if form.is_valid():
                biosample = form.save(commit= False)
                biosample.userOwner = User.objects.get(pk=request.user.pk)
                individualPK = request.session['individualPK']
                biosourcePK = request.session['biosourcePK']
                biosample.biosample_biosource = Biosource.objects.get(pk=biosourcePK)
                biosample.biosample_individual = Individual.objects.get(pk=individualPK)
                if(request.POST.get('biosample_type')):
                    biosample_type = request.POST.get('biosample_type')
                    biosample.biosample_fields = createJSON(request, biosample_type)
                aliasList=["Biosample",biosample.biosample_biosource.biosource_name,biosample.biosample_name]
                biosample.dcic_alias = LABNAME +"_".join(aliasList)
                biosample.save()
                modifications = request.POST.getlist('modifications')
                for m in modifications:
                    mod = Modification.objects.get(pk=m)
                    biosample.modifications.add(mod)
                biosample_TreatmentRnai = request.POST.getlist('biosample_TreatmentRnai')
                for b in biosample_TreatmentRnai:
                    trt = TreatmentRnai.objects.get(pk=b)
                    biosample.biosample_TreatmentRnai.add(trt)
                biosample_TreatmentChemical = request.POST.getlist('biosample_TreatmentChemical')
                for b in biosample_TreatmentChemical:
                    trt = TreatmentChemical.objects.get(pk=b)
                    biosample.biosample_TreatmentChemical.add(trt)
                biosample_OtherTreatment = request.POST.getlist('biosample_OtherTreatment')
                for b in biosample_OtherTreatment:
                    trt = OtherTreatment.objects.get(pk=b)
                    biosample.biosample_OtherTreatment.add(trt)
                imageObjects = request.POST.getlist('imageObjects')
                for im in imageObjects:
                    img = ImageObjects.objects.get(pk=im)
                    biosample.imageObjects.add(img)
                auPro = request.POST.getlist('authentication_protocols')
                for au in auPro:
                    a = Protocol.objects.get(pk=au)
                    biosample.authentication_protocols.add(a)
                proAdd = request.POST.getlist('protocols_additional')
                for pro in proAdd:
                    p = Protocol.objects.get(pk=pro)
                    biosample.protocols_additional.add(p)
                labs = request.POST.getlist('contributing_labs')
                for l in labs:
                    iLab = ContributingLabs.objects.get(pk=l)
                    biosample.contributing_labs.add(iLab)
                request.session['biosamplePK'] = biosample.pk
                return HttpResponseRedirect('/addExperiment/')
            else:
                selectForm.fields["Biosample"].queryset = Biosample.objects.filter(biosample_biosource=request.session['biosourcePK'])
                isExisting = (selectForm.fields["Biosample"].queryset.count() > 0)
                existing = selectForm['Biosample']
                form.fields["biosample_type"].queryset = JsonObjField.objects.filter(field_type="Biosample")
                form.fields["imageObjects"].queryset = ImageObjects.objects.filter(project=request.session['projectId'])
                form.fields["authentication_protocols"].queryset = Protocol.objects.filter(protocol_type__choice_name="Authentication document")
                form.fields["protocol"].queryset = Protocol.objects.filter(~Q(protocol_type__choice_name="Authentication document"))
                form.fields["protocols_additional"].queryset = Protocol.objects.filter(~Q(protocol_type__choice_name="Authentication document"))
                
                formAttr=["authentication_protocols"]
                if(self.request.session['currentGroup'] != "admin"):
                    for f in formAttr:
                        form.fields[f].queryset = (form.fields[f].queryset).filter(userOwner=self.request.user.pk)
                        
                return render(request, self.template_name,{'form':form, 'form_class':"Biosample", 'existing':existing,'isExisting':isExisting})
    
    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required        
class AddExperiment(View): 
    template_name = 'customForm.html'
    error_page = 'error.html'
    form_class = ExperimentForm
    
    def get(self,request):
        form = self.form_class()
        form.fields["imageObjects"].queryset = ImageObjects.objects.filter(project=request.session['projectId'])
        form.fields["type"].queryset = JsonObjField.objects.filter(field_type="Experiment")
        form.fields["authentication_docs"].queryset = Protocol.objects.filter(protocol_type__choice_name="Authentication document")
        form.fields["protocol"].queryset = Protocol.objects.filter(~Q(protocol_type__choice_name="Authentication document"))
        form.fields["variation"].queryset = Protocol.objects.filter(~Q(protocol_type__choice_name="Authentication document"))
        
        formAttr=["authentication_docs"]
        if(self.request.session['currentGroup'] != "admin"):
            for f in formAttr:
                form.fields[f].queryset = (form.fields[f].queryset).filter(userOwner=self.request.user.pk)

        return render(request, self.template_name,{'form':form, 'form_class':"Experiment"})
    
    def post(self,request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.project = Project.objects.get(pk=request.session['projectId'])
            exp.experiment_biosample = Biosample.objects.get(pk=request.session['biosamplePK'])
            
            if(request.POST.get('type')):
                exp_type = request.POST.get('type')
                exp.experiment_fields = createJSON(request, exp_type)
            aliasList=["Experiment",exp.project.project_name,exp.experiment_name]
            exp.dcic_alias = LABNAME +"_".join(aliasList)
            auth = request.POST.getlist('authentication_docs')
            exp.save()
            for a in auth:
                auDoc = Protocol.objects.get(pk=a)
                exp.authentication_docs.add(auDoc)
            img = request.POST.getlist('imageObjects')
            for i in img:
                iDoc = ImageObjects.objects.get(pk=i)
                exp.imageObjects.add(iDoc)
            labs = request.POST.getlist('contributing_labs')
            for l in labs:
                iLab = ContributingLabs.objects.get(pk=l)
                exp.contributing_labs.add(iLab)
            
            return HttpResponseRedirect('/detailProject/'+request.session['projectId'])
        else:
            form.fields["imageObjects"].queryset = ImageObjects.objects.filter(project=request.session['projectId'])
            form.fields["type"].queryset = JsonObjField.objects.filter(field_type="Experiment")
            form.fields["protocol"].queryset = Protocol.objects.filter(~Q(protocol_type__choice_name="Authentication document"))
            form.fields["variation"].queryset = Protocol.objects.filter(~Q(protocol_type__choice_name="Authentication document"))
            form.fields["authentication_docs"].queryset = Protocol.objects.filter(protocol_type__choice_name="Authentication document")
            
            formAttr=["authentication_docs"]
            if(self.request.session['currentGroup'] != "admin"):
                for f in formAttr:
                    form.fields[f].queryset = (form.fields[f].queryset).filter(userOwner=self.request.user.pk)

            
            return render(request, self.template_name,{'form':form, 'form_class':"Experiment"})
    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required
class AddModification(View):
    template_name = 'modificationForm.html'
    error_page = 'error.html'
    form_class = ModificationForm
    construct_form=ConstructForm
    regions_form= GenomicRegionsForm
    target_form = TargetForm
    
    def get(self,request):
        #messages.info(request,"Fill genomic regions if different than target.")
        form = self.form_class()
        construct_form = self.construct_form()
        regions_form = self.regions_form()
        target_form = self.target_form()
        form.fields["modification_type"].queryset = Choice.objects.filter(choice_type="modification_type")
        construct_form.fields["construct_type"].queryset = Choice.objects.filter(choice_type="construct_type")
        regions_form.fields["genomicRegions_genome_assembly"].queryset = Choice.objects.filter(choice_type="genomicRegions_genome_assembly")
        regions_form.fields["genomicRegions_chromosome"].queryset = Choice.objects.filter(choice_type="genomicRegions_chromosome")
        target_form.fields["targeted_structure"].queryset = Choice.objects.filter(choice_type="targeted_structure")
        return render(request, self.template_name,{'form':form, 'construct_form':construct_form,'regions_form':regions_form, 'target_form':target_form})
    
    def post(self,request):
        form = self.form_class(request.POST)
        construct_form =self.construct_form(request.POST)
        regions_form =self.regions_form(request.POST)
        target_form =self.target_form(request.POST)
        if all([form.is_valid(), construct_form.is_valid(),regions_form.is_valid(),target_form.is_valid()]):
            modification = form.save(commit= False)
            if(construct_form['construct_name'].value() != ""):
                construct = construct_form.save(commit= False)
                aliasList=["Construct",construct.construct_name]
                construct.dcic_alias = LABNAME +"_".join(aliasList)
                construct.save()
                labs = request.POST.getlist('contributing_labs')
                for l in labs:
                    iLab = ContributingLabs.objects.get(pk=l)
                    construct.contributing_labs.add(iLab)
                modification.constructs = construct
            if(regions_form['genomicRegions_name'].value() != ""):
                regions = regions_form.save(commit= False)
                aliasList=["GenomicRegion",regions.genomicRegions_name]
                regions.dcic_alias = LABNAME +"_".join(aliasList)
                regions.save()
                labs = request.POST.getlist('contributing_labs')
                for l in labs:
                    iLab = ContributingLabs.objects.get(pk=l)
                    regions.contributing_labs.add(iLab)
                modification.modification_genomicRegions = regions
            if(target_form['target_name'].value() != ""):
                target = target_form.save(commit= False)
                target.targeted_region = regions
                aliasList=["Target",target.target_name]
                target.dcic_alias = LABNAME +"_".join(aliasList)
                target.save()
                labs = request.POST.getlist('contributing_labs')
                for l in labs:
                    iLab = ContributingLabs.objects.get(pk=l)
                    target.contributing_labs.add(iLab)
                modification.target = target
            modification.userOwner = User.objects.get(pk=request.user.pk)
            aliasList=["Modification",modification.modification_name]
            modification.dcic_alias = LABNAME +"_".join(aliasList)
            modification.save()
            labs = request.POST.getlist('contributing_labs')
            for l in labs:
                iLab = ContributingLabs.objects.get(pk=l)
                modification.contributing_labs.add(iLab)
            return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' %(escape(modification._get_pk_val()), escape(modification)))
        else:
            form.fields["modification_type"].queryset = Choice.objects.filter(choice_type="modification_type")
            construct_form.fields["construct_type"].queryset = Choice.objects.filter(choice_type="construct_type")
            regions_form.fields["genomicRegions_genome_assembly"].queryset = Choice.objects.filter(choice_type="genomicRegions_genome_assembly")
            regions_form.fields["genomicRegions_chromosome"].queryset = Choice.objects.filter(choice_type="genomicRegions_chromosome")
            target_form.fields["targeted_structure"].queryset = Choice.objects.filter(choice_type="targeted_structure")
            return render(request, self.template_name,{'form':form, 'construct_form':construct_form,'regions_form':regions_form, 'target_form':target_form})
    
    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
@class_login_required        
class AddConstruct(View): 
    form_class = ConstructForm
    field = "Construct"
    def get(self,request):
        form = self.form_class()
        form.fields["construct_type"].queryset = Choice.objects.filter(choice_type="construct_type")
        pageContext = {'form': form, 'field':self.field}
        return render(request, "popup.html", pageContext)
    
    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            newObject = None
            try:
                newObject = form.save(commit= False)
                aliasList=["Construct",newObject.construct_name]
                newObject.dcic_alias = LABNAME +"_".join(aliasList)
                newObject.save()
                labs = request.POST.getlist('contributing_labs')
                for l in labs:
                    iLab = ContributingLabs.objects.get(pk=l)
                    newObject.contributing_labs.add(iLab)
            except(forms.ValidationError):
                newObject = None
                
            if newObject:
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' %(escape(newObject._get_pk_val()), escape(newObject)))
 
        else:
            form.fields["construct_type"].queryset = Choice.objects.filter(choice_type="construct_type")
            pageContext = {'form': form, 'field':self.field}
            return render(request, "popup.html", pageContext)
    
    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
@class_login_required        
class AddTarget(View): 
    form_class = TargetForm
    field = "Target"
    def get(self,request):
        form = self.form_class()
        pageContext = {'form': form, 'field':self.field}
        form.fields["targeted_structure"].queryset = Choice.objects.filter(choice_type="targeted_structure")
        return render(request, "popup.html", pageContext)
    
    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            newObject = None
            try:
                newObject = form.save(commit= False)
                aliasList=["Target",newObject.target_name]
                newObject.dcic_alias = LABNAME +"_".join(aliasList)
                newObject.save()
                labs = request.POST.getlist('contributing_labs')
                for l in labs:
                    iLab = ContributingLabs.objects.get(pk=l)
                    newObject.contributing_labs.add(iLab)
            except(forms.ValidationError):
                newObject = None
                
            if newObject:
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' %(escape(newObject._get_pk_val()), escape(newObject)))
        else:
            pageContext = {'form': form, 'field':self.field}
            form.fields["targeted_structure"].queryset = Choice.objects.filter(choice_type="targeted_structure")
            return render(request, "popup.html", pageContext)

    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required        
class AddGenomicRegions(View): 
    form_class = GenomicRegionsForm
    field = "GenomicRegions"
    def get(self,request):
        form = self.form_class()
        pageContext = {'form': form, 'field':self.field}
        form.fields["genomicRegions_genome_assembly"].queryset = Choice.objects.filter(choice_type="genomicRegions_genome_assembly")
        form.fields["genomicRegions_chromosome"].queryset = Choice.objects.filter(choice_type="genomicRegions_chromosome")
        return render(request, "popup.html", pageContext)
    
    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            newObject = None
            try:
                newObject = form.save(commit= False)
                aliasList=["GenomicRegion",newObject.genomicRegions_name]
                newObject.dcic_alias = LABNAME +"_".join(aliasList)
                newObject.save()
                labs = request.POST.getlist('contributing_labs')
                for l in labs:
                    iLab = ContributingLabs.objects.get(pk=l)
                    newObject.contributing_labs.add(iLab)
            except(forms.ValidationError):
                newObject = None
                
            if newObject:
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' %(escape(newObject._get_pk_val()), escape(newObject)))
        else:
            pageContext = {'form': form, 'field':self.field}
            form.fields["genomicRegions_genome_assembly"].queryset = Choice.objects.filter(choice_type="genomicRegions_genome_assembly")
            form.fields["genomicRegions_chromosome"].queryset = Choice.objects.filter(choice_type="genomicRegions_chromosome")
            return render(request, "popup.html", pageContext)
    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)        
        


@class_login_required
class AddProtocol(View): 
    form_class = ProtocolForm
    field = "Protocol"
    def get(self,request):
        form = self.form_class()
        pageContext = {'form': form, 'field':self.field}
        form.fields["protocol_type"].queryset = Choice.objects.filter(choice_type="protocol_type")
        form.fields["protocol_classification"].queryset = Choice.objects.filter(choice_type="protocol_classification")
        return render(request, "popup.html", pageContext)
    
    def post(self,request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            newObject = None
            try:
                newObject = form.save(commit= False)
                newObject.userOwner = User.objects.get(pk=request.user.pk)
                aliasList=["Protocol",newObject.name]
                newObject.dcic_alias = LABNAME +"_".join(aliasList)
                newObject.save()
                labs = request.POST.getlist('contributing_labs')
                for l in labs:
                    iLab = ContributingLabs.objects.get(pk=l)
                    newObject.contributing_labs.add(iLab)
            except(forms.ValidationError):
                newObject = None
                
            if newObject:
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' %(escape(newObject._get_pk_val()), escape(newObject)))
        else:
            pageContext = {'form': form, 'field':self.field}
            form.fields["protocol_type"].queryset = Choice.objects.filter(choice_type="protocol_type")
            form.fields["protocol_classification"].queryset = Choice.objects.filter(choice_type="protocol_classification")
            return render(request, "popup.html", pageContext)

    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required        
class AddTreatmentRnai(View): 
    form_class = TreatmentRnaiForm
    field = "TreatmentRNAi"
    def get(self,request):
        form = self.form_class()
        form.fields["treatmentRnai_type"].queryset = Choice.objects.filter(choice_type="treatmentRnai_type")
        pageContext = {'form': form, 'field':self.field}
        return render(request, "popup.html", pageContext)
    
    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            newObject = None
            try:
                newObject = form.save(commit= False)
                newObject.userOwner = User.objects.get(pk=request.user.pk)
                aliasList=["TreatmentRNAi",newObject.treatmentRnai_name]
                newObject.dcic_alias = LABNAME +"_".join(aliasList)
                newObject.save()
                #modifications = request.POST.getlist('modifications')
                labs = request.POST.getlist('contributing_labs')
                for l in labs:
                    iLab = ContributingLabs.objects.get(pk=l)
                    newObject.contributing_labs.add(iLab)
            except(forms.ValidationError):
                newObject = None
                
            if newObject:
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' %(escape(newObject._get_pk_val()), escape(newObject)))

        else:
            form.fields["treatmentRnai_type"].queryset = Choice.objects.filter(choice_type="treatmentRnai_type")
            pageContext = {'form': form, 'field':self.field}
            return render(request, "popup.html", pageContext)

    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    

@class_login_required        
class AddTreatmentChemical(View): 
    form_class = TreatmentChemicalForm
    field = "TreatmentChemical"
    def get(self,request):
        form = self.form_class()
        form.fields["treatmentChemical_concentration_units"].queryset = Choice.objects.filter(choice_type="treatmentChemical_concentration_units")
        form.fields["treatmentChemical_duration_units"].queryset = Choice.objects.filter(choice_type="treatmentChemical_duration_units")
        pageContext = {'form': form, 'field':self.field}
        return render(request, "popup.html", pageContext)
    
    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            newObject = None
            try:
                newObject = form.save(commit= False)
                newObject.userOwner = User.objects.get(pk=request.user.pk)
                aliasList=["TreatmentChemical",newObject.treatmentChemical_name]
                newObject.dcic_alias = LABNAME +"_".join(aliasList)
                newObject.save()
                labs = request.POST.getlist('contributing_labs')
                for l in labs:
                    iLab = ContributingLabs.objects.get(pk=l)
                    newObject.contributing_labs.add(iLab)
            except(forms.ValidationError):
                newObject = None
                
            if newObject:
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' %(escape(newObject._get_pk_val()), escape(newObject)))
        else:
            form.fields["treatmentChemical_concentration_units"].queryset = Choice.objects.filter(choice_type="treatmentChemical_concentration_units")
            form.fields["treatmentChemical_duration_units"].queryset = Choice.objects.filter(choice_type="treatmentChemical_duration_units")
            pageContext = {'form': form, 'field':self.field}
            return render(request, "popup.html", pageContext)
    
    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required        
class AddOther(View): 
    form_class = OtherForm
    field = "OtherTreatment"
    def get(self,request):
        form = self.form_class()
        pageContext = {'form': form, 'field':self.field}
        return render(request, "popup.html", pageContext)
    
    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            newObject = None
            try:
                newObject = form.save(commit= False)
                newObject.userOwner = User.objects.get(pk=request.user.pk)
                newObject.save()
                
            except(forms.ValidationError):
                newObject = None
                
            if newObject:
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' %(escape(newObject._get_pk_val()), escape(newObject)))
        else:
            pageContext = {'form': form, 'field':self.field}
            return render(request, "popup.html", pageContext)

    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
        

@class_login_required
class AddDocument(View): 
    form_class = DocumentForm
    field = "Document"
    def get(self,request):
        form = self.form_class()
        form.fields["type"].queryset = Choice.objects.filter(choice_type="document_type")
        pageContext = {'form': form, 'field':self.field}
        return render(request, "popup.html", pageContext)
     
    def post(self,request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            newObject = None
            try:
                newObject = form.save(commit= False)
                aliasList=["Document",newObject.name]
                newObject.dcic_alias = LABNAME +"_".join(aliasList)
                newObject.save()
                labs = request.POST.getlist('contributing_labs')
                for l in labs:
                    iLab = ContributingLabs.objects.get(pk=l)
                    newObject.contributing_labs.add(iLab)
            except(forms.ValidationError):
                newObject = None
                
            if newObject:
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' %(escape(newObject._get_pk_val()), escape(newObject)))
        else:
            form.fields["type"].queryset = Choice.objects.filter(choice_type="document_type")
            pageContext = {'form': form, 'field':self.field}
            return render(request, "popup.html", pageContext)

    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
        

@class_login_required
class AddPublication(View): 
    form_class = PublicationForm
    field = "Publication"
    def get(self,request):
        form = self.form_class()
        form.fields["publication_categories"].queryset = Choice.objects.filter(choice_type="publication_categories")
        form.fields["publication_published_by"].queryset = Choice.objects.filter(choice_type="publication_published_by")
        form.fields["exp_sets_prod_in_pub"].queryset = ExperimentSet.objects.filter(project=request.session['projectId'])
        form.fields["exp_sets_used_in_pub"].queryset = ExperimentSet.objects.filter(project=request.session['projectId'])
        pageContext = {'form': form, 'field':self.field}
        return render(request, "popup.html", pageContext)
    
    def post(self,request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            newObject = None
            try:
                newObject = form.save(commit= False)
                aliasList=["Publication",newObject.name]
                newObject.dcic_alias = LABNAME +"_".join(aliasList)
                newObject.save()
                labs = request.POST.getlist('contributing_labs')
                for l in labs:
                    iLab = ContributingLabs.objects.get(pk=l)
                    newObject.contributing_labs.add(iLab)
            except(forms.ValidationError):
                newObject = None
                
            if newObject:
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' %(escape(newObject._get_pk_val()), escape(newObject)))
        else:
            form.fields["publication_categories"].queryset = Choice.objects.filter(choice_type="publication_categories")
            form.fields["publication_published_by"].queryset = Choice.objects.filter(choice_type="publication_published_by")
            form.fields["exp_sets_prod_in_pub"].queryset = ExperimentSet.objects.filter(project=request.session['projectId'])
            form.fields["exp_sets_used_in_pub"].queryset = ExperimentSet.objects.filter(project=request.session['projectId'])
            pageContext = {'form': form, 'field':self.field}
            return render(request, "popup.html", pageContext)

    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    

@class_login_required
class AddSequencingRun(View): 
    template_name = 'customForm.html'
    error_page = 'error.html'
    form_class = SequencingRunForm
    
    def get(self,request):
       
        form = self.form_class()
        form.fields["run_Experiment"].queryset = Experiment.objects.filter(project=request.session['projectId']).order_by('-pk')
        form.fields["run_sequencing_center"].queryset = Choice.objects.filter(choice_type="run_sequencing_center")
        form.fields["run_sequencing_machine"].queryset = Choice.objects.filter(choice_type="run_sequencing_machine")
        form.fields["run_sequencing_instrument"].queryset = Choice.objects.filter(choice_type="run_sequencing_instrument")
        return render(request, self.template_name,{'form':form, 'form_class':"SequencingRun"})
    
    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.project = Project.objects.get(pk=request.session['projectId'])
            form.save()
            run_Experiment = request.POST.getlist('run_Experiment')
            for expsPk in run_Experiment:
                exp = Experiment.objects.get(pk=expsPk)
                form.run_Experiment.add(exp)
            request.session['runId'] = form.pk
            return HttpResponseRedirect('/detailProject/'+request.session['projectId'])
        else:
            form.fields["run_Experiment"].queryset = Experiment.objects.filter(project=request.session['projectId']).order_by('-pk')
            form.fields["run_sequencing_center"].queryset = Choice.objects.filter(choice_type="run_sequencing_center")
            form.fields["run_sequencing_machine"].queryset = Choice.objects.filter(choice_type="run_sequencing_machine")
            form.fields["run_sequencing_instrument"].queryset = Choice.objects.filter(choice_type="run_sequencing_instrument")
            return render(request, self.template_name,{'form':form, 'form_class':"SequencingRun"})

    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required
class AddBarcode(View):
    form_class = BarcodeForm
    field = "Barcode"
    def get(self,request):
        form = self.form_class()
        pageContext = {'form': form, 'field':self.field}
        form.fields["barcode_index"].queryset = Choice.objects.filter(choice_type="barcode")
        return render(request, "popup.html", pageContext)
    
    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            newObject = None
            try:
                newObject = form.save(commit=False)
                newObject.save()
            except(forms.ValidationError):
                newObject = None
                
            if newObject:
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' %(escape(newObject._get_pk_val()), escape(newObject)))

        else:
            pageContext = {'form': form, 'field':self.field}
            form.fields["barcode_index"].queryset = Choice.objects.filter(choice_type="barcode")
            return render(request, "popup.html", pageContext)
    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
#     
#     template_name = 'barcodeForm.html'
#     error_page = 'error.html'
#     def get(self,request):
#         countForms = Experiment.objects.filter(runExp__pk=request.session['runId']).count()
#         formset= formset_factory(BarcodeForm,extra=countForms)
#         form = formset()
#         for f in form:
#             f.fields["barcode_name_1"].queryset = Choice.objects.filter(choice_type="barcode")
#             f.fields["barcode_name_2"].queryset = Choice.objects.filter(choice_type="barcode")
#             f.fields["barcode_exp"].queryset = Experiment.objects.filter(runExp__pk=request.session['runId'])
#         return render(request, self.template_name,{'form':form, 'form_class':"Barcode"})
#     
#     def post(self,request):
#         countForms = Experiment.objects.filter(runExp__pk=request.session['runId']).count()
#         formset= formset_factory(BarcodeForm,extra=countForms)
#         form = formset(request.POST)
#         if all([form.is_valid()]):
#             for f in form: 
#                 barcode = f.save(commit=False)
#                 barcode.barcode_run = SequencingRun.objects.get(pk=request.session['runId'])
#                 barcode.save()
#             return HttpResponseRedirect('/detailProject/'+request.session['projectId'])
#         else:
#             for f in form:
#                 f.fields["barcode_name_1"].queryset = Choice.objects.filter(choice_type="barcode")
#                 f.fields["barcode_name_2"].queryset = Choice.objects.filter(choice_type="barcode")
#                 f.fields["barcode_exp"].queryset = Experiment.objects.filter(runExp__pk=request.session['runId'])
#             return render(request, self.template_name,{'form':form, 'form_class':"Barcode"})

@class_login_required
class AddSeqencingFile(View): 
    template_name = 'customForm.html'
    error_page = 'error.html'
    form_class = SeqencingFileForm
    
    def get(self,request):
        form = self.form_class()
        form.fields["sequencingFile_run"].queryset = SequencingRun.objects.filter(project=request.session['projectId'])
        form.fields["file_format"].queryset = Choice.objects.filter(choice_type="file_format")
        form.fields["relationship_type"].queryset = Choice.objects.filter(choice_type="relationship_type")
        form.fields["related_files"].queryset = SeqencingFile.objects.filter(sequencingFile_exp=self.request.session['experimentId'])
        #form.fields["file_classification"].queryset = Choice.objects.filter(choice_type="file_classification")
        return render(request, self.template_name,{'form':form, 'form_class':"SeqencingFile"})
    
    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            file = form.save(commit=False)
            file.project = Project.objects.get(pk=request.session['projectId'])
            file.sequencingFile_backupPath = ""
            file.sequencingFile_sha256sum = ""
            file.sequencingFile_md5sum = ""
            file.sequencingFile_exp = Experiment.objects.get(pk = self.request.session['experimentId'] )
            aliasList=["SeqencingFile",file.project.project_name,file.sequencingFile_exp.experiment_name,file.sequencingFile_name]
            file.dcic_alias = LABNAME +"_".join(aliasList)
            file.save()
            labs = request.POST.getlist('contributing_labs')
            for l in labs:
                iLab = ContributingLabs.objects.get(pk=l)
                file.contributing_labs.add(iLab)
            return HttpResponseRedirect('/detailExperiment/'+self.request.session['experimentId'])
        else:
            form.fields["sequencingFile_run"].queryset = SequencingRun.objects.filter(project=request.session['projectId'])
            form.fields["file_format"].queryset = Choice.objects.filter(choice_type="file_format")
            #form.fields["file_classification"].queryset = Choice.objects.filter(choice_type="file_classification")
            return render(request, self.template_name,{'form':form, 'form_class':"SeqencingFile"})

    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required        
class AddFileSet(View): 
    template_name = 'customForm.html'
    error_page = 'error.html'
    form_class = FileSetForm
    
    def get(self,request):
        form = self.form_class()
        form.fields["fileset_type"].queryset = Choice.objects.filter(choice_type="fileset_type")
        form.fields["fileSet_file"].queryset = SeqencingFile.objects.filter(project=request.session['projectId'])
        return render(request, self.template_name,{'form':form, 'form_class':"FileSet"})
    
    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            fileset = form.save(commit=False)
            fileset.project = Project.objects.get(pk=request.session['projectId'])
            fileset.save()
            fileSetFile = request.POST.getlist('fileSet_file')
            for file in fileSetFile:
                f = SeqencingFile.objects.get(pk=file)
                fileset.fileSet_file.add(f)
            labs = request.POST.getlist('contributing_labs')
            for l in labs:
                iLab = ContributingLabs.objects.get(pk=l)
                fileset.contributing_labs.add(iLab)
            return HttpResponseRedirect('/detailProject/'+request.session['projectId'])
        else:
            form.fields["fileset_type"].queryset = Choice.objects.filter(choice_type="fileset_type")
            form.fields["fileSet_file"].queryset = SeqencingFile.objects.filter(project=request.session['projectId'])
            return render(request, self.template_name,{'form':form, 'form_class':"FileSet"})

    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required        
class AddExperimentSet(View): 
    template_name = 'customForm.html'
    error_page = 'error.html'
    form_class = ExperimentSetForm
    
    def get(self,request):
        form = self.form_class()  
        form.fields["experimentSet_type"].queryset = Choice.objects.filter(choice_type="experimentSet_type")
        form.fields["experimentSet_exp"].queryset = Experiment.objects.filter(project=request.session['projectId'])
        return render(request, self.template_name,{'form':form, 'form_class':"ExperimentSet"})
    
    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            expSet = form.save(commit=False)
            expSet.project = Project.objects.get(pk=request.session['projectId'])
            aliasList=["ExperimentSet",expSet.project.project_name,expSet.experimentSet_name]
            expSet.dcic_alias = LABNAME +"_".join(aliasList)
            expSet.save()
            expSetExp = request.POST.getlist('experimentSet_exp')
            for exp in expSetExp:
                e = Experiment.objects.get(pk=exp)
                expSet.experimentSet_exp.add(e)
            labs = request.POST.getlist('contributing_labs')
            for l in labs:
                iLab = ContributingLabs.objects.get(pk=l)
                expSet.contributing_labs.add(iLab)
            return HttpResponseRedirect('/detailProject/'+request.session['projectId'])
        else:
            form.fields["experimentSet_type"].queryset = Choice.objects.filter(choice_type="experimentSet_type")
            form.fields["experimentSet_exp"].queryset = Experiment.objects.filter(project=request.session['projectId'])
            return render(request, self.template_name,{'form':form, 'form_class':"ExperimentSet"})

    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    

@class_login_required
class AddTag(View): 
    template_name = 'customForm.html'
    error_page = 'error.html'   
    form_class = TagForm
    
    def get(self,request):
        form = self.form_class()
        form.fields["tag_exp"].queryset = Experiment.objects.filter(project=request.session['projectId'])
        return render(request, self.template_name,{'form':form, 'form_class':"Tag"})
    
    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            tag = form.save(commit=False)
            tag.tag_user = User.objects.get(pk=request.user.id)
            tag.project = Project.objects.get(pk=request.session['projectId'])
            tag.save()
            tagExp = request.POST.getlist('tag_exp')
            for exp in tagExp:
                e = Experiment.objects.get(pk=exp)
                tag.tag_exp.add(e)
                
            return HttpResponseRedirect('/detailProject/'+request.session['projectId'])
        else:
            form.fields["tag_exp"].queryset = Experiment.objects.filter(project=request.session['projectId'])
            return render(request, self.template_name,{'form':form, 'form_class':"Tag"})

    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required
class AddImageObjects(View): 
    form_class = ImageObjectsForm
    field = "Images"
    def get(self,request):
        form = self.form_class()
        pageContext = {'form': form, 'field':self.field}
        form.fields["imageObjects_type"].queryset = Choice.objects.filter(choice_type="imageObjects_type")
        return render(request, "popup.html", pageContext)
    
    def post(self,request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            newObject = None
            try:
                newObject = form.save(commit=False)
                newObject.project = Project.objects.get(pk=request.session['projectId'])
                aliasList=["Image",newObject.project.project_name,newObject.imageObjects_name]
                newObject.dcic_alias = LABNAME +"_".join(aliasList)
                newObject.save()
                labs = request.POST.getlist('contributing_labs')
                for l in labs:
                    iLab = ContributingLabs.objects.get(pk=l)
                    newObject.contributing_labs.add(iLab)
            except(forms.ValidationError):
                newObject = None
                
            if newObject:
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' %(escape(newObject._get_pk_val()), escape(newObject)))

        else:
            pageContext = {'form': form, 'field':self.field}
            form.fields["imageObjects_type"].queryset = Choice.objects.filter(choice_type="imageObjects_type")
            return render(request, "popup.html", pageContext)

    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)


def log_file(members):
    for tarinfo in members:
        fileExtension = os.path.splitext(tarinfo.name)[0]
        if ((fileExtension.split('.', 1))[-1] == "end.mappingLog" ):
            return tarinfo

def png_files(members, analysisPk):
    for tarinfo in members:
        if (os.path.splitext(tarinfo.name)[1] == ".png"):
            print(WORKSPACEPATH+"media/"+ tarinfo.name)
            Images.objects.create(image_path="/media/"+ tarinfo.name,image_analysis=Analysis.objects.get(pk=analysisPk) )
            yield tarinfo

def importAnalysisGZ(analysis, analysisTypePk):
    analysisTarGz = str(analysis.analysis_import)
    analysisPk = analysis.pk
    tar = tarfile.open(WORKSPACEPATH+"media/"+analysisTarGz, "r|gz")
    logFile = tar.extractfile(log_file(tar))
    content = logFile.read()
    analysisType = JsonObjField.objects.get(pk = analysisTypePk).field_name
    if(analysisType == "Hi-C Analysis"):
        json_data = extractHiCAnalysis(content, analysisTypePk)
    elif(analysisType == "5C Analysis"):
        json_data = extract5CAnalysis(content, analysisTypePk)
    tar.extractall(path=WORKSPACEPATH+"media/", members=png_files(tar, analysisPk))
    tar.close()
    os.remove(WORKSPACEPATH+"media/"+analysisTarGz)
    return json_data

@class_login_required
class AddAnalysis(View): 
    template_name = 'customForm.html'
    error_page = 'error.html'
    form_class = AnalysisForm
    
    def get(self,request):
        form = self.form_class()
        form.fields["analysis_type"].queryset = JsonObjField.objects.filter(field_type="Analysis")
        form.fields["analysis_file"].queryset = SeqencingFile.objects.filter(sequencingFile_exp=self.request.session['experimentId'] )
        return render(request, self.template_name,{'form':form, 'form_class':"Analysis"})
    
    def post(self,request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            analysis = form.save(commit=False)
            analysis_type = request.POST.get('analysis_type')
            analysis.analysis_exp = Experiment.objects.get(pk = self.request.session['experimentId'] )
            analysis.save()
            analysis_file = request.POST.getlist('analysis_file')
            for files in analysis_file:
                file = SeqencingFile.objects.get(pk=files)
                analysis.analysis_file.add(file)
            json_data = importAnalysisGZ(analysis, analysis_type)
            analysis.analysis_import.delete()
            analysis.analysis_fields = json_data
            analysis.save()
            labs = request.POST.getlist('contributing_labs')
            for l in labs:
                iLab = ContributingLabs.objects.get(pk=l)
                analysis.contributing_labs.add(iLab)
            #analysis.analysis_fields = createJSON(request, analysis_type)
            return HttpResponseRedirect('/detailExperiment/'+self.request.session['experimentId'])
        else:
            form.fields["analysis_type"].queryset = JsonObjField.objects.filter(field_type="Analysis")
            form.fields["analysis_file"].queryset = SeqencingFile.objects.filter(sequencingFile_exp=self.request.session['experimentId'] )
            return render(request, self.template_name,{'form':form, 'form_class':"Analysis"})

    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

            
@csrf_exempt                
def constructForm(request):
    if request.method == 'POST' and request.is_ajax():
        pk = request.POST.get('pk')
        obj = JsonObjField.objects.get(pk=pk)
        orderedValues= orderByNumber(obj.field_set)
        return HttpResponse(json.dumps({'field_set': orderedValues, 'model':obj.field_type}), content_type="application/json")
    else :
        return render_to_response('error.html', locals())
 

@login_required
def submitSequencingRun(request,pk):
    check= False
    projectId = request.session['projectId']
    if('Member' in map(str, request.user.groups.all()) or 'MemberWithEditAccess' in map(str, request.user.groups.all())):
        user=User.objects.get(pk=request.user.id)
        projectObj = Project.objects.get(pk=projectId)
        prjOwner = projectObj.project_owner
        print(user)
        print(prjOwner)
        if(user ==  prjOwner):
            check = True
            print("User==Owner true")
        
    if ('Admin' in map(str, request.user.groups.all()) or 'Principal Investigator' in map(str, request.user.groups.all())):
        check = True
        print("Admin/PI")
        
    if (check== True):
        obj = SequencingRun.objects.get(pk=pk)
        obj.run_submitted=True
        obj.save()
        return HttpResponseRedirect('/detailProject/'+projectId)
    else:
        raise  PermissionDenied

@login_required
def approveSequencingRun(request,pk):
    obj = SequencingRun.objects.get(pk=pk)
    obj.run_approved=True
    obj.save()
    return redirect("/sequencingRunView")

@class_login_required
class SequencingRunView(View):
    template_name = 'sequencingRuns.html'
    
    def get(self,request):
        sequencingRuns = SequencingRun.objects.all().order_by('-run_submission_date')
        d = defaultdict(list)
        for run in sequencingRuns:
#             run.run_Add_Barcode = run.get_run_Add_Barcode_display()
            d[run.project.project_name].append(run)
        context = {
            'sequencingRuns': OrderedDict(d),
        }
        return render(request, self.template_name, context)
    
    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
      
    

@login_required
def searchView(request):
    context ={}
    if request.GET:
        for searchModelForm in [ProjectSearchForm,ExperimentSearchForm,SequencingRunSearchForm,SeqencingFileSearchForm]:
            form = searchModelForm(request.GET,request=request )
            if form.is_valid():
                results = form.get_result_queryset()
            else:
                results = []
            if ((results) and (searchModelForm == ProjectSearchForm)):
                context['projects']=results
            elif ((results) and (searchModelForm == ExperimentSearchForm)):
                context['experiments']=results
            elif ((results) and (searchModelForm == SequencingRunSearchForm)):
                context['runs']=results
            elif ((results) and (searchModelForm == SeqencingFileSearchForm)):
                context['files']=results
        if not bool(context):
            context['results']="No result"
    return render(request, 'searchResult.html', context)


@class_login_required
class DcicView(View):
    template_name = 'dcicView.html'
    error_page = 'error.html'
    def get(self,request):
        projectId = request.session['projectId']
        context = {}
        project = Project.objects.get(pk=projectId)
        experiments=Experiment.objects.filter(project=projectId).order_by('-pk')
        context['project']= project
        context['experiments']= experiments
        return render(request, self.template_name, context)
    
@class_login_required
class DcicFinalizeSubmission(View):
    template_name = 'dcicView.html'
    error_page = 'error.html'
    def post(self,request):
        request.session['finalizeOnly'] = True
        exportDCIC(request)
        request.session['finalizeOnly'] = False
        return HttpResponseRedirect('/detailProject/'+request.session['projectId'])
    
    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)


@class_login_required
class CloneExperimentList(View):
    template_name = 'cloneExperimentList.html'
    error_page = 'error.html'
    def get(self,request):
        projectId = request.session['projectId']
        context = {}
        project = Project.objects.get(pk=projectId)
        experiments=Experiment.objects.filter(project=projectId).order_by('-pk')
        context['project']= project
        context['experiments']= experiments
        return render(request, self.template_name, context)
    def post(self,request):
        selectedExpPK = request.POST.get("clone")
        return HttpResponseRedirect('/cloneExperiment/'+selectedExpPK)
    
    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required        
class CloneExperiment(View): 
    template_name = 'customForm.html'
    error_page = 'error.html'
    form_class = CloneExperimentForm
    
    def get(self,request,pk):
        form = self.form_class()
        return render(request, self.template_name,{'form':form, 'form_class':"Experiment Clone"})
    
    def post(self,request,pk):
        form = self.form_class(request.POST)
        if form.is_valid():
            experiment_name=request.POST.get("experiment_name")
            experiment_description=request.POST.get("experiment_description")
            biosample_name=request.POST.get("biosample_name")
            biosample_description=request.POST.get("biosample_description")
            
            if(biosample_name != ""):
                clonedBiosampleobj = Biosample.objects.get(expBio__pk=pk)
                clonedBiosampleobj.pk = None
                clonedBiosampleobj.biosample_name = biosample_name
                clonedBiosampleobj.biosample_description = biosample_description
                aliasList=["Biosample",clonedBiosampleobj.biosample_biosource.biosource_name,clonedBiosampleobj.biosample_name]
                clonedBiosampleobj.dcic_alias = LABNAME +"_".join(aliasList)
                clonedBiosampleobj.update_dcic = True
                clonedBiosampleobj.save()
                modifications = Biosample.objects.get(expBio__pk=pk).modifications.all()
                for m in modifications:
                    clonedBiosampleobj.modifications.add(m)
                biosample_TreatmentRnai = Biosample.objects.get(expBio__pk=pk).biosample_TreatmentRnai.all()
                for b in biosample_TreatmentRnai:
                    clonedBiosampleobj.biosample_TreatmentRnai.add(b)
                biosample_TreatmentChemical = Biosample.objects.get(expBio__pk=pk).biosample_TreatmentChemical.all()
                for b in biosample_TreatmentChemical:
                    clonedBiosampleobj.biosample_TreatmentChemical.add(b)
                biosample_OtherTreatment = Biosample.objects.get(expBio__pk=pk).biosample_OtherTreatment.all()
                for b in biosample_OtherTreatment:
                    clonedBiosampleobj.biosample_OtherTreatment.add(b)
                imageObjects = Biosample.objects.get(expBio__pk=pk).imageObjects.all()
                for im in imageObjects:
                    clonedBiosampleobj.imageObjects.add(im)
                auPro = Biosample.objects.get(expBio__pk=pk).authentication_protocols.all()
                for a in auPro:
                    clonedBiosampleobj.authentication_protocols.add(a)
                proAdd = Biosample.objects.get(expBio__pk=pk).protocols_additional.all()
                for p in proAdd:
                    clonedBiosampleobj.protocols_additional.add(p)
                contri_labs=Biosample.objects.get(expBio__pk=pk).contributing_labs.all()
                for c in contri_labs:
                    clonedBiosampleobj.contributing_labs.add(c)
                
                biosamplePk = clonedBiosampleobj.pk
            
            else:
                biosamplePk = Biosample.objects.get(expBio__pk=pk).pk
            
            clonedExpobj = Experiment.objects.get(pk=pk)
            clonedExpobj.pk = None
            clonedExpobj.experiment_name = experiment_name
            clonedExpobj.experiment_description = experiment_description
            clonedExpobj.finalize_dcic_submission = False
            clonedExpobj.update_dcic = True
            clonedExpobj.experiment_biosample = Biosample.objects.get(pk=biosamplePk)
            aliasList=["Experiment",clonedExpobj.project.project_name,clonedExpobj.experiment_name]
            clonedExpobj.dcic_alias = LABNAME +"_".join(aliasList)
            clonedExpobj.save()
            auth = Experiment.objects.get(pk=pk).authentication_docs.all()
            for a in auth:
                clonedExpobj.authentication_docs.add(a)
            img = Experiment.objects.get(pk=pk).imageObjects.all()
            for i in img:
                clonedExpobj.imageObjects.add(i)
            contri_labs=Experiment.objects.get(pk=pk).contributing_labs.all()
            for c in contri_labs:
                clonedExpobj.contributing_labs.add(c)
            
            return HttpResponseRedirect('/detailProject/'+request.session['projectId'])
        else:
            return render(request, self.template_name,{'form':form, 'form_class':"Experiment Clone"})
        
    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required        
class ImportSequencingFiles(View): 
    template_name = 'customForm.html'
    error_page = 'error.html'
    form_class = ImportSequencingFilesForm
    
    def get(self,request,pk):
        form = self.form_class()
        return render(request, self.template_name,{'form':form, 'form_class':"Import Sequencing Files"})
    
    def post(self,request,pk):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            request, template_name, context = importSeqFiles(request,pk)
            return render(request,template_name, context)
        else:
            return render(request, self.template_name,{'form':form, 'form_class':"Import Sequencing Files"})
    
    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)



@class_login_required        
class CreateSequencingFiles(View):
    def post(self,request,pk):
        runDict=request.POST.get('runDict')
        c=ast.literal_eval(runDict)
        notExist=[]
        for keys, values in c:
            exp=None
            run=None
            filePath=keys
            n=filePath.split("/")
            name=n[-1].split(".")
            fileName=name[0]
            filenameSplit=fileName.split("_")
            paired_end=filenameSplit[-2][1]
            expName=values[0]
            seqRunName=values[1]
            exp_project=None
            try:
                if (Experiment.objects.get(experiment_name=expName)):
                    exp=Experiment.objects.get(experiment_name=expName)
                    exp_project=exp.project.pk
                if (SequencingRun.objects.get(run_name=seqRunName)):
                    run=SequencingRun.objects.get(run_name=seqRunName)
                if(Experiment.objects.get(experiment_name=expName) and SequencingRun.objects.get(run_name=seqRunName) and exp_project==int(pk)):
                    f=SeqencingFile(sequencingFile_name=fileName, project = Project.objects.get(pk=pk))
                    f.file_format= Choice.objects.get(pk=126)
                    f.paired_end= paired_end
                    if(paired_end=='2'):
                        filenameSplit[-2]="R1"
                        pairedFile="_".join(filenameSplit)
                        f.relationship_type= Choice.objects.get(pk=141)
                        f.related_files=SeqencingFile.objects.get(sequencingFile_name=pairedFile)
                    f.flowcell_details_lane=filenameSplit[-3]
                    f.read_length=50
                    f.sequencingFile_mainPath=filePath
                    f.sequencingFile_run=run
                    f.sequencingFile_exp=exp
                    aliasList=["SeqencingFile",f.project.project_name,f.sequencingFile_exp.experiment_name,f.sequencingFile_name]
                    f.dcic_alias = LABNAME +"_".join(aliasList)
                    f.update_dcic = True
                    f.save()
            except ObjectDoesNotExist:
                if(exp is None):
                    notExist.append(expName)
                if(run is None):
                    notExist.append(seqRunName)
            if(exp_project!=int(pk)):
                notExist.append(expName)
        if(len(notExist)>0):
            messages.error(request,",".join(set(notExist))+' does not exists in this project. Files not added for these.')
        else:
            messages.info(request,"You have added your files successfully!")
        return HttpResponseRedirect('/detailProject/'+pk)
    
    @method_decorator(view_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    


@login_required 
def downloadFile(request):
    path= ROOTFOLDER+'/organization/static/siteWide/importSeqFiles.csv'
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404





    