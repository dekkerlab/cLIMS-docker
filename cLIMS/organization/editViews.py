'''
Created on Nov 10, 2016

@author: nanda
'''
from django.views.generic.edit import UpdateView, DeleteView
from django.core.urlresolvers import reverse
from organization.models import *
from wetLab.forms import *
from dryLab.forms import *
from organization.forms import *
import json
from organization.decorators import *
from django.utils.decorators import method_decorator
from cLIMS.base import *

def createJSON(request, fieldTypePk):
    json_object = JsonObjField.objects.get(pk=fieldTypePk).field_set
    data = {}
    for keys in json_object:
        formVal = request.POST.get(keys)
        data[keys] = formVal
    json_data = json.dumps(data)
    return(json_data)


@class_login_required 
class EditProject(UpdateView):
    form_class = ProjectForm
    model = Project
    template_name = 'customForm.html/'
    
    def get_success_url(self):
        projectId = self.kwargs.get(self.pk_url_kwarg, None)
        prj=Project.objects.get(pk=projectId)
        aliasList=["Project",prj.project_name]
        prj.dcic_alias = LABNAME +"_".join(aliasList)
        prj.save()
        return reverse('detailProject', kwargs={'pk': projectId})
    
    def get_context_data(self, **kwargs):
        context = super(EditProject , self).get_context_data(**kwargs)
        context['action'] = reverse('editProject',
                                kwargs={'pk': self.get_object().id})
        return context
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required     
class DeleteProject(DeleteView):
    model = Project
    template_name = 'delete.html'
    def get_success_url(self):
        return reverse('showProject')
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)


@class_login_required 
class EditExperiment(UpdateView):
    form_class = ExperimentForm
    model = Experiment
    template_name = 'editForm.html/'
    
    def get_success_url(self):
        projectId = self.request.session['projectId']
        expe = Experiment.objects.get(pk=self.get_object().id)
        aliasList=["Experiment",expe.project.project_name,expe.experiment_name]
        expe.dcic_alias = LABNAME +"_".join(aliasList)
        expe.save()
        if(self.request.POST.get('type')):
            exp_type = self.request.POST.get('type')
            expe.experiment_fields = createJSON(self.request, exp_type)
            expe.save()
        return reverse('detailProject', kwargs={'pk': projectId})
    
    def get_context_data(self, **kwargs):
        context = super(EditExperiment , self).get_context_data(**kwargs)
        obj = Experiment.objects.get(pk=self.get_object().id)
        if(obj.experiment_fields):
            context['jsonObj']= json.loads(obj.experiment_fields)
        context['form'].fields["type"].queryset = JsonObjField.objects.filter(field_type="Experiment")
        context['form'].fields["authentication_docs"].queryset = Protocol.objects.filter(protocol_type__choice_name="Authentication document")
        context['action'] = reverse('editProject',
                                kwargs={'pk': self.get_object().id})
        return context
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required 
class DeleteExperiment(DeleteView):
    model = Experiment
    template_name = 'deleteExperiment.html'
    def get_success_url(self):
        projectId = self.request.session['projectId']
        return reverse('detailProject', kwargs={'pk': projectId})
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)


@class_login_required 
class EditIndividual(UpdateView):
    form_class = IndividualForm
    model = Individual
    template_name = 'editForm.html/'
    
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        individual = Individual.objects.get(pk=self.get_object().id)
        individual_type = self.request.POST.get('individual_type')
        individual.individual_fields = createJSON(self.request, individual_type)
        aliasList=["Individual",individual.individual_name]
        individual.dcic_alias = LABNAME +"_".join(aliasList)
        individual.save()
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    def get_context_data(self, **kwargs):
        context = super(EditIndividual , self).get_context_data(**kwargs)
        context['form'].fields["individual_type"].queryset = JsonObjField.objects.filter(field_type="Individual")
        obj = Individual.objects.get(pk=self.get_object().id)
        if (obj.individual_fields):
            context['jsonObj']= json.loads(obj.individual_fields)
        context['action'] = reverse('detailExperiment',
                                kwargs={'pk': self.get_object().id})
        return context
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required 
class DeleteIndividual(DeleteView):
    model = Individual
    template_name = 'deleteExperiment.html'
    def get_success_url(self):
        projectId = self.request.session['projectId']
        return reverse('detailProject', kwargs={'pk': projectId})
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required 
class EditBiosource(UpdateView):
    form_class = BiosourceForm
    model = Biosource
    template_name = 'customForm.html/'
    
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        biosource = Biosource.objects.get(pk=self.get_object().id)
        aliasList=["Biosource",biosource.biosource_name]
        biosource.dcic_alias = LABNAME +"_".join(aliasList)
        biosource.save()
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    def get_context_data(self, **kwargs):
        context = super(EditBiosource , self).get_context_data(**kwargs)
        context['form'].fields["biosource_type"].queryset = Choice.objects.filter(choice_type="biosource_type")
        context['form'].fields["biosource_cell_line_tier"].queryset = Choice.objects.filter(choice_type="biosource_cell_line_tier")
        context['form'].fields["modifications"].queryset = Modification.objects.filter(userOwner=self.request.user.pk)
        context['action'] = reverse('detailExperiment',
                                kwargs={'pk': self.get_object().id})
        return context
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
@class_login_required 
class DeleteBiosource(DeleteView):
    model = Biosource
    template_name = 'deleteExperiment.html'
    def get_success_url(self):
        projectId = self.request.session['projectId']
        return reverse('detailProject', kwargs={'pk': projectId})
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
@class_login_required 
class EditBiosample(UpdateView):
    form_class = BiosampleForm
    model = Biosample
    template_name = 'editForm.html/'
    
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        biosample = Biosample.objects.get(pk=self.get_object().id)
        aliasList=["Biosample",biosample.biosample_biosource.biosource_name,biosample.biosample_name]
        biosample.dcic_alias = LABNAME +"_".join(aliasList)
        biosample.save()
        if(self.request.POST.get('biosample_type')):
            biosample_type = self.request.POST.get('biosample_type')
            biosample.biosample_fields = createJSON(self.request, biosample_type)
            biosample.save()
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    
    def get_context_data(self, **kwargs):
        context = super(EditBiosample , self).get_context_data(**kwargs)
        obj = Biosample.objects.get(pk=self.get_object().id)
        if(obj.biosample_fields):
            context['jsonObj']= json.loads(obj.biosample_fields)
            
        context['form'].fields["biosample_TreatmentRnai"].queryset = TreatmentRnai.objects.filter(userOwner=self.request.user.pk)
        context['form'].fields["biosample_TreatmentChemical"].queryset = TreatmentChemical.objects.filter(userOwner=self.request.user.pk)
        context['form'].fields["biosample_OtherTreatment"].queryset = OtherTreatment.objects.filter(userOwner=self.request.user.pk)
        context['form'].fields["biosample_type"].queryset = JsonObjField.objects.filter(field_type="Biosample")
        context['form'].fields["imageObjects"].queryset = ImageObjects.objects.filter(project=self.request.session['projectId'])
        context['form'].fields["modifications"].queryset = Modification.objects.filter(userOwner=self.request.user.pk)
        context['action'] = reverse('detailExperiment',
                                kwargs={'pk': self.get_object().id})
        return context
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
    
@class_login_required 
class DeleteBiosample(DeleteView):
    model = Biosample
    template_name = 'deleteExperiment.html'
    def get_success_url(self):
        projectId = self.request.session['projectId']
        return reverse('detailProject', kwargs={'pk': projectId})
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
@class_login_required 
class EditTreatmentRnai(UpdateView):
    form_class = TreatmentRnaiForm
    model = TreatmentRnai
    template_name = 'customForm.html/'
    
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        trt=TreatmentRnai.objects.get(pk=self.get_object().id)
        aliasList=["TreatmentRNAi",trt.treatmentRnai_name]
        trt.dcic_alias = LABNAME +"_".join(aliasList)
        trt.save()
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    def get_context_data(self, **kwargs):
        context = super(EditTreatmentRnai , self).get_context_data(**kwargs)
        context['form'].fields["treatmentRnai_type"].queryset = Choice.objects.filter(choice_type="treatmentRnai_type")
        context['action'] = reverse('detailExperiment',
                                kwargs={'pk': self.get_object().id})
        return context
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
@class_login_required 
class DeleteTreatmentRnai(DeleteView):
    model = TreatmentRnai
    template_name = 'deleteExperiment.html'
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required 
class EditTreatmentChemical(UpdateView):
    form_class = TreatmentChemicalForm
    model = TreatmentChemical
    template_name = 'customForm.html/'
    
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        trt=TreatmentChemical.objects.get(pk=self.get_object().id)
        aliasList=["TreatmentChemical",trt.treatmentChemical_name]
        trt.dcic_alias = LABNAME +"_".join(aliasList)
        trt.save()
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    def get_context_data(self, **kwargs):
        context = super(EditTreatmentChemical , self).get_context_data(**kwargs)
        context['form'].fields["treatmentChemical_concentration_units"].queryset = Choice.objects.filter(choice_type="treatmentChemical_concentration_units")
        context['form'].fields["treatmentChemical_duration_units"].queryset = Choice.objects.filter(choice_type="treatmentChemical_duration_units")
        context['action'] = reverse('detailExperiment',
                                kwargs={'pk': self.get_object().id})
        return context
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required 
class DeleteTreatmentChemical(DeleteView):
    model = TreatmentChemical
    template_name = 'deleteExperiment.html'
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
@class_login_required     
class EditOther(UpdateView):
    form_class = OtherForm
    model = OtherTreatment
    template_name = 'customForm.html/'
    
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    def get_context_data(self, **kwargs):
        context = super(EditOther , self).get_context_data(**kwargs)
        context['action'] = reverse('detailExperiment',
                                kwargs={'pk': self.get_object().id})
        return context
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
     
@class_login_required 
class DeleteOther(DeleteView):
    model = OtherTreatment
    template_name = 'deleteExperiment.html'
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
@class_login_required 
class EditModification(UpdateView):
    form_class = ModificationForm
    model = Modification
    template_name = 'customForm.html/'
    
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        modification = Modification.objects.get(pk=self.get_object().id)
        aliasList=["Modification",modification.modification_name]
        modification.dcic_alias = LABNAME +"_".join(aliasList)
        modification.save()
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    def get_context_data(self, **kwargs):
        context = super(EditModification , self).get_context_data(**kwargs)
        context['form'].fields["modification_type"].queryset = Choice.objects.filter(choice_type="modification_type")
        context['action'] = reverse('detailExperiment',
                                kwargs={'pk': self.get_object().id})
        return context
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
@class_login_required 
class DeleteModification(DeleteView):
    model = Modification
    template_name = 'deleteExperiment.html'
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)      

@class_login_required 
class EditConstruct(UpdateView):
    form_class = ConstructForm
    model = Construct
    template_name = 'customForm.html/'
    
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        con = Construct.objects.get(pk=self.get_object().id)
        aliasList=["Construct",con.construct_name]
        con.dcic_alias = LABNAME +"_".join(aliasList)
        con.save()
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    def get_context_data(self, **kwargs):
        context = super(EditConstruct , self).get_context_data(**kwargs)
        context['form'].fields["construct_type"].queryset = Choice.objects.filter(choice_type="construct_type")
        context['action'] = reverse('detailExperiment',
                                kwargs={'pk': self.get_object().id})
        return context
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)  

@class_login_required 
class DeleteConstruct(DeleteView):
    model = Construct
    template_name = 'deleteExperiment.html'
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required 
class EditGenomicRegions(UpdateView):
    form_class = GenomicRegionsForm
    model = GenomicRegions
    template_name = 'customForm.html/'
    
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        gen=GenomicRegions.objects.get(pk=self.get_object().id)
        aliasList=["GenomicRegion",gen.name]
        gen.dcic_alias = LABNAME +"_".join(aliasList)
        gen.save()
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    def get_context_data(self, **kwargs):
        context = super(EditGenomicRegions , self).get_context_data(**kwargs)
        context['form'].fields["genomicRegions_genome_assembly"].queryset = Choice.objects.filter(choice_type="genomicRegions_genome_assembly")
        context['form'].fields["genomicRegions_chromosome"].queryset = Choice.objects.filter(choice_type="genomicRegions_chromosome")
        context['action'] = reverse('detailExperiment',
                                kwargs={'pk': self.get_object().id})
        return context
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)    

@class_login_required 
class DeleteGenomicRegions(DeleteView):
    model = GenomicRegions
    template_name = 'deleteExperiment.html'
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required 
class EditTarget(UpdateView):
    form_class = TargetForm
    model = Target
    template_name = 'customForm.html/'
    
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        tar=Target.objects.get(pk=self.get_object().id)
        aliasList=["Target",tar.name]
        tar.dcic_alias = LABNAME +"_".join(aliasList)
        tar.save()
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    def get_context_data(self, **kwargs):
        context = super(EditTarget , self).get_context_data(**kwargs)
        context['form'].fields["targeted_structure"].queryset = Choice.objects.filter(choice_type="targeted_structure")
        context['action'] = reverse('detailExperiment',
                                kwargs={'pk': self.get_object().id})
        return context    
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required 
class DeleteTarget(DeleteView):
    model = Target
    template_name = 'deleteExperiment.html'
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required 
class EditSequencingRun(UpdateView):
    form_class = SequencingRunForm
    model = SequencingRun
    template_name = 'customForm.html/'
    
    def get_success_url(self):
        projectId = self.request.session['projectId']
        return reverse('detailProject', kwargs={'pk': projectId})
    
    def get_context_data(self, **kwargs):
        context = super(EditSequencingRun , self).get_context_data(**kwargs)
        context['form'].fields["run_Experiment"].queryset = Experiment.objects.filter(project=self.request.session['projectId'])
        context['form'].fields["run_sequencing_center"].queryset = Choice.objects.filter(choice_type="run_sequencing_center")
        context['form'].fields["run_sequencing_machine"].queryset = Choice.objects.filter(choice_type="run_sequencing_machine")
        context['form'].fields["run_sequencing_instrument"].queryset = Choice.objects.filter(choice_type="run_sequencing_instrument")
        context['action'] = reverse('detailProject',
                                kwargs={'pk': self.get_object().id})
        return context
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
@class_login_required 
class DeleteSequencingRun(DeleteView):
    model = SequencingRun
    template_name = 'delete.html'
    def get_success_url(self):
        projectId = self.request.session['projectId']
        return reverse('detailProject', kwargs={'pk': projectId})
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required 
class EditSequencingFile(UpdateView):
    form_class = SeqencingFileForm
    model = SeqencingFile
    template_name = 'customForm.html/'
    
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        file=SeqencingFile.objects.get(pk=self.get_object().id)
        aliasList=["SeqencingFile",file.project.project_name,file.sequencingFile_exp.experiment_name,file.sequencingFile_name]
        file.dcic_alias = LABNAME +"_".join(aliasList)
        file.save()
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    def get_context_data(self, **kwargs):
        context = super(EditSequencingFile , self).get_context_data(**kwargs)
        context['form'].fields["sequencingFile_run"].queryset = SequencingRun.objects.filter(project=self.request.session['projectId'])
        context['form'].fields["file_format"].queryset = Choice.objects.filter(choice_type="file_format")
        context['form'].fields["relationship_type"].queryset = Choice.objects.filter(choice_type="relationship_type")
        context['form'].fields["related_files"].queryset = SeqencingFile.objects.filter(sequencingFile_exp=self.request.session['experimentId'])
        #context['form'].fields["file_classification"].queryset = Choice.objects.filter(choice_type="file_classification")
        context['action'] = reverse('detailExperiment',
                                kwargs={'pk': self.get_object().id})
        return context
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
@class_login_required 
class DeleteSequencingFile(DeleteView):
    model = SeqencingFile
    template_name = 'delete.html'
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    

@class_login_required 
class EditAnalysis(UpdateView):
    form_class = AnalysisForm
    model = Analysis
    template_name = 'editForm.html/'
    
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        analysis = Analysis.objects.get(pk=self.get_object().id)
        analysis_type = self.request.POST.get('analysis_type')
        analysis.analysis_fields = createJSON(self.request, analysis_type)
        analysis.save()
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    def get_context_data(self, **kwargs):
        context = super(EditAnalysis , self).get_context_data(**kwargs)
        context['form'].fields["analysis_type"].queryset = JsonObjField.objects.filter(field_type="Analysis")
        context['form'].fields["analysis_file"].queryset = SeqencingFile.objects.filter(sequencingFile_exp=self.request.session['experimentId'] )
        obj = Analysis.objects.get(pk=self.get_object().id)
        if(obj.analysis_fields):
            context['jsonObj']= json.loads(obj.analysis_fields)
        context['action'] = reverse('detailExperiment',
                                kwargs={'pk': self.get_object().id})
        return context
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
    
@class_login_required 
class DeleteAnalysis(DeleteView):
    model = Analysis
    template_name = 'deleteExperiment.html'
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required 
class EditTag(UpdateView):
    form_class = TagForm
    model = Tag
    template_name = 'customForm.html/'
    
    def get_success_url(self):
        projectId = self.request.session['projectId']
        return reverse('detailProject', kwargs={'pk': projectId})
    
    def get_context_data(self, **kwargs):
        context = super(EditTag , self).get_context_data(**kwargs)
        context['form'].fields["tag_exp"].queryset = Experiment.objects.filter(project=self.request.session['projectId'])
        context['action'] = reverse('detailProject',
                                kwargs={'pk': self.get_object().id})
        return context
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required 
class DeleteTag(DeleteView):
    model = Tag
    template_name = 'delete.html'
    def get_success_url(self):
        projectId = self.request.session['projectId']
        return reverse('detailProject', kwargs={'pk': projectId})
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
@class_login_required 
class EditExperimentSet(UpdateView):
    form_class = ExperimentSetForm
    model = ExperimentSet
    template_name = 'customForm.html/'
    
    def get_success_url(self):
        projectId = self.request.session['projectId']
        expSet=ExperimentSet.objects.get(pk=self.get_object().id)
        aliasList=["ExperimentSet",expSet.project.project_name,expSet.experimentSet_name]
        expSet.dcic_alias = LABNAME +"_".join(aliasList)
        expSet.save()
        return reverse('detailProject', kwargs={'pk': projectId})
    
    def get_context_data(self, **kwargs):
        context = super(EditExperimentSet , self).get_context_data(**kwargs)
        context['form'].fields["experimentSet_type"].queryset = Choice.objects.filter(choice_type="experimentSet_type")
        context['form'].fields["experimentSet_exp"].queryset = Experiment.objects.filter(project=self.request.session['projectId'])
        context['action'] = reverse('detailProject',
                                kwargs={'pk': self.get_object().id})
        return context
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
      

@class_login_required 
class DeleteExperimentSet(DeleteView):
    model = ExperimentSet
    template_name = 'delete.html'
    def get_success_url(self):
        projectId = self.request.session['projectId']
        return reverse('detailProject', kwargs={'pk': projectId})

@class_login_required 
class EditFileSet(UpdateView):
    form_class = FileSetForm
    model = FileSet
    template_name = 'customForm.html/'
    
    def get_success_url(self):
        projectId = self.request.session['projectId']
        return reverse('detailProject', kwargs={'pk': projectId})
    
    def get_context_data(self, **kwargs):
        context = super(EditFileSet , self).get_context_data(**kwargs)
        context['form'].fields["fileset_type"].queryset = Choice.objects.filter(choice_type="fileset_type")
        context['form'].fields["fileSet_file"].queryset = SeqencingFile.objects.filter(project=self.request.session['projectId'])
        context['action'] = reverse('detailProject',
                                kwargs={'pk': self.get_object().id})
        return context  
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)  

@class_login_required 
class DeleteFileSet(DeleteView):
    model = FileSet
    template_name = 'delete.html'
    def get_success_url(self):
        projectId = self.request.session['projectId']
        return reverse('detailProject', kwargs={'pk': projectId})
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)


@class_login_required 
class EditProtocol(UpdateView):
    form_class = ProtocolForm
    model = Protocol
    template_name = 'editForm.html/'
    
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        prot=Protocol.objects.get(pk=self.get_object().id)
        aliasList=["Protocol",prot.name]
        prot.dcic_alias = LABNAME +"_".join(aliasList)
        prot.save()
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    def get_context_data(self, **kwargs):
        context = super(EditProtocol , self).get_context_data(**kwargs)
        context['form'].fields["protocol_type"].queryset = Choice.objects.filter(choice_type="protocol_type")
        context['form'].fields["protocol_classification"].queryset = Choice.objects.filter(choice_type="protocol_classification")
        context['action'] = reverse('detailExperiment',
                                kwargs={'pk': self.get_object().id})
        return context  
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
   
      
@class_login_required 
class DeleteProtocol(DeleteView):
    model = Protocol
    template_name = 'deleteExperiment.html'
    def get_success_url(self):
        projectId = self.request.session['projectId']
        return reverse('detailProject', kwargs={'pk': projectId})
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    

@class_login_required 
class EditDocument(UpdateView):
    form_class = DocumentForm
    model = Document
    template_name = 'editForm.html/'
    
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        doc=Document.objects.get(pk=self.get_object().id)
        aliasList=["Document",doc.name]
        doc.dcic_alias = LABNAME +"_".join(aliasList)
        doc.save()
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    def get_context_data(self, **kwargs):
        context = super(EditDocument , self).get_context_data(**kwargs)
        context['form'].fields["type"].queryset = Choice.objects.filter(choice_type="document_type")
        context['action'] = reverse('detailExperiment',
                                kwargs={'pk': self.get_object().id})
        return context    
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required 
class DeleteDocument(DeleteView):
    model = Document
    template_name = 'deleteExperiment.html'
    def get_success_url(self):
        projectId = self.request.session['projectId']
        return reverse('detailProject', kwargs={'pk': projectId})
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required 
class EditPublication(UpdateView):
    form_class = PublicationForm
    model = Publication
    template_name = 'editForm.html/'
    
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        pub=Publication.objects.get(pk=self.get_object().id)
        aliasList=["Publication",pub.name]
        pub.dcic_alias = LABNAME +"_".join(aliasList)
        pub.save()
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    def get_context_data(self, **kwargs):
        context = super(EditPublication , self).get_context_data(**kwargs)
        context['form'].fields["publication_categories"].queryset = Choice.objects.filter(choice_type="publication_categories")
        context['form'].fields["publication_published_by"].queryset = Choice.objects.filter(choice_type="publication_published_by")
        context['form'].fields["exp_sets_prod_in_pub"].queryset = ExperimentSet.objects.filter(project=self.request.session['projectId'])
        context['form'].fields["exp_sets_used_in_pub"].queryset = ExperimentSet.objects.filter(project=self.request.session['projectId'])
        context['action'] = reverse('detailExperiment',
                                kwargs={'pk': self.get_object().id})
        return context    
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
@class_login_required 
class DeletePublication(DeleteView):
    model = Publication
    template_name = 'deleteExperiment.html'
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        return reverse('detailExperiment', kwargs={'pk': experimentId})


@class_login_required 
class EditImageObjects(UpdateView):
    form_class = ImageObjectsForm
    model = ImageObjects
    template_name = 'editForm.html/'
    
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        img=ImageObjects.objects.get(pk=self.get_object().id)
        aliasList=["Image",img.project.project_name,img.imageObjects_name]
        img.dcic_alias = LABNAME +"_".join(aliasList)
        img.save()
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    def get_context_data(self, **kwargs):
        context = super(EditImageObjects , self).get_context_data(**kwargs)
        context['form'].fields["imageObjects_type"].queryset = Choice.objects.filter(choice_type="imageObjects_type")
        context['action'] = reverse('detailExperiment',
                                kwargs={'pk': self.get_object().id})
        return context
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
@class_login_required 
class DeleteImageObjects(DeleteView):
    model = ImageObjects
    template_name = 'deleteExperiment.html'
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)

@class_login_required 
class EditBarcode(UpdateView):
    form_class = BarcodeForm
    model = Barcode
    template_name = 'barcodeForm.html'
    
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    def get_context_data(self, **kwargs):
        context = super(EditBarcode , self).get_context_data(**kwargs)
        context['form'].fields["barcode_index"].queryset = Choice.objects.filter(choice_type="barcode")
#         context['form'].fields["barcode_name_1"].queryset = Choice.objects.filter(choice_type="barcode")
#         context['form'].fields["barcode_name_2"].queryset = Choice.objects.filter(choice_type="barcode")
#         context['form'].fields["barcode_exp"].queryset = Experiment.objects.filter(runExp__pk=self.request.session['runId'])
        context['action'] = reverse('detailExperiment',
                                kwargs={'pk': self.get_object().id})
        return context  
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    

@class_login_required 
class DeleteBarcode(DeleteView):
    model = Barcode
    template_name = 'deleteExperiment.html'
    def get_success_url(self):
        experimentId = self.request.session['experimentId']
        return reverse('detailExperiment', kwargs={'pk': experimentId})
    
    @method_decorator(require_permission)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,  *args, **kwargs)
    
    
    
    













    