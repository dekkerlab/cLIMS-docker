'''
Created on Oct 18, 2016

@author: nanda
'''
from django.conf.urls import url, include
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from organization.views import *
from organization.editViews import *
from organization.export import *

urlpatterns = [
    url(r'^$', views.login,{'template_name': 'registration/login.html'},name='login'),
    url(r'^logout/$', auth_views.logout,{'template_name': 'registration/logout.html'}, name='logout'),
    url(r'^error/$', ErrorView.as_view(), name='error'),
    url(r'^error_view/$', ErrorViewOnly.as_view(), name='error_view_only'),
#     url(r'^$', RedirectView.as_view(pattern_name='login',permanent=False)),
    url(r'^home/$', HomeView.as_view(), name='home'),
    
    url(r'^addProject/$', AddProject.as_view(), name='addProject'),
    url(r'^showProject/$', ShowProject.as_view(), name='showProject'),
    url(r'^detailProject/(?P<pk>[0-9]+)/$', DetailProject.as_view(), name='detailProject'),
    url(r'^detailExperiment/(?P<pk>[0-9]+)/$', DetailExperiment.as_view(), name='detailExperiment'),
    url(r'^detailSequencingRun/(?P<pk>[0-9]+)/$', DetailSequencingRun.as_view(), name='detailSequencingRun'),
    url(r'^detailAnalysis/(?P<pk>[0-9]+)/$', DetailAnalysis.as_view(), name='detailAnalysis'),
    url(r'^detailPublication/(?P<pk>[0-9]+)/$', DetailPublication.as_view(), name='detailPublication'),
    url(r'^detailProtocol/(?P<pk>[0-9]+)/$', DetailProtocol.as_view(), name='detailProtocol'),
    url(r'^detailDocument/(?P<pk>[0-9]+)/$', DetailDocument.as_view(), name='detailDocument'),
    url(r'^detailEnzyme/(?P<pk>[0-9]+)/$', DetailEnzyme.as_view(), name='detailEnzyme'),
    url(r'^detailConstruct/(?P<pk>[0-9]+)/$', DetailConstruct.as_view(), name='detailConstruct'),
    url(r'^detailGenomicRegions/(?P<pk>[0-9]+)/$', DetailGenomicRegions.as_view(), name='detailGenomicRegions'),
    url(r'^detailTarget/(?P<pk>[0-9]+)/$', DetailTarget.as_view(), name='detailTarget'),
     
    
#     url(r'^addIndividual/$', AddIndividual.as_view(), name='addIndividual'),
#     url(r'^addIndividual/constructForm/$',  views.constructForm, name='constructIndividual'), 
#     
    url(r'^addIndividual/$', AddIndividual.as_view(), name='addIndividual'),
    url(r'^constructForm/$', views.constructForm, name='constructForm'),
    
    url(r'^addBiosource/$', AddBiosource.as_view(), name='addBiosource'),
    url(r'^addBiosample/$', AddBiosample.as_view(), name='addBiosample'),
    url(r'^addModification/$', AddModification.as_view(), name='addModification'),
    url(r'^addTarget/$', AddTarget.as_view(), name='addTarget'),
    url(r'^addConstruct/$', AddConstruct.as_view(), name='addConstruct'),
    url(r'^addGenomicRegions/$', AddGenomicRegions.as_view(), name='addGenomicRegions'),
    url(r'^addProtocol/$', AddProtocol.as_view(), name='addProtocol'),
    url(r'^addDocumens/$', AddDocument.as_view(), name='addDocumens'),
    url(r'^addTreatmentRnai/$', AddTreatmentRnai.as_view(), name='addTreatmentRnai'),
    url(r'^addTreatmentChemical/$', AddTreatmentChemical.as_view(), name='addTreatmentChemical'),
    url(r'^addOther/$', AddOther.as_view(), name='addOther'),
    url(r'^addPublication/$', AddPublication.as_view(), name='addPublication'),
    url(r'^addExperiment/$', AddExperiment.as_view(), name='addExperiment'),
    url(r'^addSequencingRun/$', AddSequencingRun.as_view(), name='addSequencingRun'),   
    url(r'^addBarcode/$', AddBarcode.as_view(), name='addBarcode'),
    url(r'^addSeqencingFile/$', AddSeqencingFile.as_view(), name='addSeqencingFile'),   
    url(r'^addAnalysis/$', AddAnalysis.as_view(), name='addAnalysis'),
    url(r'^addExperimentSet/$', AddExperimentSet.as_view(), name='addExperimentSet'),
    url(r'^addFileSet/$', AddFileSet.as_view(), name='addFileSet'),
    url(r'^addTag/$', AddTag.as_view(), name='addTag'),   
    url(r'^addImageObjects/$', AddImageObjects.as_view(), name='addImageObjects'), 
    
    
    url(r'^editProject/(?P<pk>[0-9]+)/$', EditProject.as_view(), name='editProject'),
    url(r'^deleteProject/(?P<pk>[0-9]+)/$', DeleteProject.as_view(), name='deleteProject'),
    url(r'^editExperiment/(?P<pk>[0-9]+)/$', EditExperiment.as_view(), name='editExperiment'),
    url(r'^deleteExperiment/(?P<pk>[0-9]+)/$', DeleteExperiment.as_view(), name='deleteExperiment'),
    url(r'^editIndividual/(?P<pk>[0-9]+)/$', EditIndividual.as_view(), name='editIndividual'),
    url(r'^deleteIndividual/(?P<pk>[0-9]+)/$', DeleteIndividual.as_view(), name='deleteIndividual'),
    url(r'^editBiosource/(?P<pk>[0-9]+)/$', EditBiosource.as_view(), name='editBiosource'),
    url(r'^deleteBiosource/(?P<pk>[0-9]+)/$', DeleteBiosource.as_view(), name='deleteBiosource'),
    url(r'^editBiosample/(?P<pk>[0-9]+)/$', EditBiosample.as_view(), name='editBiosample'),
    url(r'^deleteBiosample/(?P<pk>[0-9]+)/$', DeleteBiosample.as_view(), name='deleteBiosample'),
    url(r'^editTreatmentRnai/(?P<pk>[0-9]+)/$', EditTreatmentRnai.as_view(), name='editTreatmentRnai'),
    url(r'^deleteTreatmentRnai/(?P<pk>[0-9]+)/$', DeleteTreatmentRnai.as_view(), name='deleteTreatmentRnai'),
    url(r'^editTreatmentChemical/(?P<pk>[0-9]+)/$', EditTreatmentChemical.as_view(), name='editTreatmentChemical'),
    url(r'^deleteTreatmentChemical/(?P<pk>[0-9]+)/$', DeleteTreatmentChemical.as_view(), name='deleteTreatmentChemical'),
    url(r'^editOther/(?P<pk>[0-9]+)/$', EditOther.as_view(), name='editOther'),
    url(r'^deleteOther/(?P<pk>[0-9]+)/$', DeleteOther.as_view(), name='deleteOther'),
    url(r'^editModification/(?P<pk>[0-9]+)/$', EditModification.as_view(), name='editModification'),
    url(r'^deleteModification/(?P<pk>[0-9]+)/$', DeleteModification.as_view(), name='deleteModification'),
    url(r'^editConstruct/(?P<pk>[0-9]+)/$', EditConstruct.as_view(), name='editConstruct'),
    url(r'^deleteConstruct/(?P<pk>[0-9]+)/$', DeleteConstruct.as_view(), name='deleteConstruct'),
    url(r'^editGenomicRegions/(?P<pk>[0-9]+)/$', EditGenomicRegions.as_view(), name='editGenomicRegions'),
    url(r'^deleteGenomicRegions/(?P<pk>[0-9]+)/$', DeleteGenomicRegions.as_view(), name='deleteGenomicRegions'),
    url(r'^editTarget/(?P<pk>[0-9]+)/$', EditTarget.as_view(), name='editTarget'),
    url(r'^deleteTarget/(?P<pk>[0-9]+)/$', DeleteTarget.as_view(), name='deleteTarget'),
    url(r'^editSequencingRun/(?P<pk>[0-9]+)/$', EditSequencingRun.as_view(), name='editSequencingRun'),
    url(r'^deleteSequencingRun/(?P<pk>[0-9]+)/$', DeleteSequencingRun.as_view(), name='deleteSequencingRun'),
    url(r'^editSequencingFile/(?P<pk>[0-9]+)/$', EditSequencingFile.as_view(), name='editSequencingFile'),
    url(r'^deleteSequencingFile/(?P<pk>[0-9]+)/$', DeleteSequencingFile.as_view(), name='deleteSequencingFile'),
    url(r'^editAnalysis/(?P<pk>[0-9]+)/$', EditAnalysis.as_view(), name='editAnalysis'),
    url(r'^deleteAnalysis/(?P<pk>[0-9]+)/$', DeleteAnalysis.as_view(), name='deleteAnalysis'),
    url(r'^editExperimentSet/(?P<pk>[0-9]+)/$', EditExperimentSet.as_view(), name='editExperimentSet'),
    url(r'^deleteExperimentSet/(?P<pk>[0-9]+)/$', DeleteExperimentSet.as_view(), name='deleteExperimentSet'),
    url(r'^editFileSet/(?P<pk>[0-9]+)/$', EditFileSet.as_view(), name='editFileSet'),
    url(r'^deleteFileSet/(?P<pk>[0-9]+)/$', DeleteFileSet.as_view(), name='deleteFileSet'),
    url(r'^editTag/(?P<pk>[0-9]+)/$', EditTag.as_view(), name='editTag'),
    url(r'^deleteTag/(?P<pk>[0-9]+)/$', DeleteTag.as_view(), name='deleteTag'),
    url(r'^editProtocol/(?P<pk>[0-9]+)/$', EditProtocol.as_view(), name='editProtocol'),
    url(r'^deleteProtocol/(?P<pk>[0-9]+)/$', DeleteProtocol.as_view(), name='deleteProtocol'),
    url(r'^editDocument/(?P<pk>[0-9]+)/$', EditDocument.as_view(), name='editDocument'),
    url(r'^deleteDocument/(?P<pk>[0-9]+)/$', DeleteDocument.as_view(), name='deleteDocument'),
    url(r'^editPublication/(?P<pk>[0-9]+)/$', EditPublication.as_view(), name='editPublication'),
    url(r'^deletePublication/(?P<pk>[0-9]+)/$', DeletePublication.as_view(), name='deletePublication'),
    url(r'^editImageObjects/(?P<pk>[0-9]+)/$', EditImageObjects.as_view(), name='editImageObjects'),
    url(r'^deleteImageObjects/(?P<pk>[0-9]+)/$', DeleteImageObjects.as_view(), name='deleteImageObjects'),
    url(r'^editBarcode/(?P<pk>[0-9]+)/$', EditBarcode.as_view(), name='editBarcode'),
    url(r'^deleteBarcode/(?P<pk>[0-9]+)/$', DeleteBarcode.as_view(), name='deleteBarcode'), 
   
    
    
    
    url(r'^submitSequencingRun/(?P<pk>[0-9]+)/$', views.submitSequencingRun, name='submitSequencingRun'),
    url(r'^approveSequencingRun/(?P<pk>[0-9]+)/$', views.approveSequencingRun, name='approveSequencingRun'),
    url(r'^sequencingRunView/$', SequencingRunView.as_view(), name='sequencingRunView'),
    url(r'^searchView/$', views.searchView, name='searchView'),
    
    url(r'^exportExperiment/$', exportExperiment, name='exportExperiment'),
    url(r'^exportAnalysis/$', exportAnalysis, name='exportAnalysis'),
    url(r'^exportGEO/$', exportGEO, name='exportGEO'),
    url(r'^exportDCIC/$', exportDCIC, name='exportDCIC'),
    url(r'^dcicView/$', DcicView.as_view(), name='dcicView'),
    url(r'^dcicFinalizeSubmission/$', DcicFinalizeSubmission.as_view(), name='dcicFinalizeSubmission'),
    url(r'^cloneExperimentList/$', CloneExperimentList.as_view(), name='cloneExperimentList'),
    url(r'^cloneExperiment/(?P<pk>[0-9]+)/$', CloneExperiment.as_view(), name='cloneExperiment'),
    url(r'^importSequencingFiles/(?P<pk>[0-9]+)/$', ImportSequencingFiles.as_view(), name='importSequencingFiles'),
    url(r'^createSequencingFiles/(?P<pk>[0-9]+)/$', CreateSequencingFiles.as_view(), name='createSequencingFiles'),
    url(r'^downloadFile/$', views.downloadFile, name='downloadFile'),
    url(r'^moveExperiments/(?P<pk>[0-9]+)/$', MoveExperiments.as_view(), name='moveExperiments'),
    url(r'^exportDistiller/(?P<pk>[0-9]+)/$', ExportDistiller.as_view(), name='exportDistiller'),
    
    ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 