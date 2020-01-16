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
    url(r'^detailProject/(?P<prj_pk>[0-9]+)/$', DetailProject.as_view(), name='detailProject'),
    url(r'^detailExperiment/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/$', DetailExperiment.as_view(), name='detailExperiment'),
    url(r'^detailSequencingRun/(?P<seqrun_pk>[0-9]+)/$', DetailSequencingRun.as_view(), name='detailSequencingRun'),
    #url(r'^detailAnalysis/(?P<pk>[0-9]+)/$', DetailAnalysis.as_view(), name='detailAnalysis'),
    url(r'^detailPublication/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<pub_pk>[0-9]+)/$', DetailPublication.as_view(), name='detailPublication'),
    url(r'^detailProtocol/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<protocol_pk>[0-9]+)/$', DetailProtocol.as_view(), name='detailProtocol'),
    url(r'^detailDocument/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<doc_pk>[0-9]+)/$', DetailDocument.as_view(), name='detailDocument'),
    url(r'^detailEnzyme/(?P<enz_pk>[0-9]+)/$', DetailEnzyme.as_view(), name='detailEnzyme'),
    url(r'^detailConstruct/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<construct_pk>[0-9]+)/$', DetailConstruct.as_view(), name='detailConstruct'),
    url(r'^detailGenomicRegions/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<genreg_pk>[0-9]+)/$', DetailGenomicRegions.as_view(), name='detailGenomicRegions'),
    url(r'^detailTarget/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<target_pk>[0-9]+)/$', DetailTarget.as_view(), name='detailTarget'),
     
    
#     url(r'^addIndividual/$', AddIndividual.as_view(), name='addIndividual'),
#     url(r'^addIndividual/constructForm/$',  views.constructForm, name='constructIndividual'), 
#     
    url(r'^addIndividual/(?P<prj_pk>[0-9]+)/$', AddIndividual.as_view(), name='addIndividual'),
    url(r'^constructForm/$', views.constructForm, name='constructForm'),
    
    url(r'^addBiosource/(?P<prj_pk>[0-9]+)/(?P<ind_pk>[0-9]+)/$', AddBiosource.as_view(), name='addBiosource'),
    url(r'^addBiosample/(?P<prj_pk>[0-9]+)/(?P<biosrc_pk>[0-9]+)/$', AddBiosample.as_view(), name='addBiosample'),
    url(r'^addModification/(?P<prj_pk>[0-9]+)/$', AddModification.as_view(), name='addModification'),
    url(r'^addTarget/(?P<prj_pk>[0-9]+)/$', AddTarget.as_view(), name='addTarget'),
    url(r'^addConstruct/(?P<prj_pk>[0-9]+)/$', AddConstruct.as_view(), name='addConstruct'),
    url(r'^addGenomicRegions/(?P<prj_pk>[0-9]+)/$', AddGenomicRegions.as_view(), name='addGenomicRegions'),
    url(r'^addProtocol/(?P<prj_pk>[0-9]+)/$', AddProtocol.as_view(), name='addProtocol'),
    url(r'^addDocumens/(?P<prj_pk>[0-9]+)/$', AddDocument.as_view(), name='addDocumens'),
    url(r'^addTreatmentRnai/(?P<prj_pk>[0-9]+)/$', AddTreatmentRnai.as_view(), name='addTreatmentRnai'),
    url(r'^addTreatmentChemical/(?P<prj_pk>[0-9]+)/$', AddTreatmentChemical.as_view(), name='addTreatmentChemical'),
    url(r'^addOther/(?P<prj_pk>[0-9]+)/$', AddOther.as_view(), name='addOther'),
    url(r'^addPublication/(?P<prj_pk>[0-9]+)/$', AddPublication.as_view(), name='addPublication'),
    url(r'^addExperiment/(?P<prj_pk>[0-9]+)/(?P<biosm_pk>[0-9]+)/$', AddExperiment.as_view(), name='addExperiment'),
    url(r'^addSequencingRun/(?P<prj_pk>[0-9]+)/$', AddSequencingRun.as_view(), name='addSequencingRun'),   
    url(r'^addBarcode/(?P<prj_pk>[0-9]+)/$', AddBarcode.as_view(), name='addBarcode'),
    url(r'^addSeqencingFile/(?P<exp_pk>[0-9]+)/$', AddSeqencingFile.as_view(), name='addSeqencingFile'),   
    url(r'^addAnalysis/$', AddAnalysis.as_view(), name='addAnalysis'),
    url(r'^addExperimentSet/(?P<prj_pk>[0-9]+)/$', AddExperimentSet.as_view(), name='addExperimentSet'),
    url(r'^addFileSet/(?P<prj_pk>[0-9]+)/$', AddFileSet.as_view(), name='addFileSet'),
    url(r'^addTag/(?P<prj_pk>[0-9]+)/$', AddTag.as_view(), name='addTag'),   
    url(r'^addImageObjects/(?P<prj_pk>[0-9]+)/$', AddImageObjects.as_view(), name='addImageObjects'), 
    
    
    url(r'^editProject/(?P<prj_pk>[0-9]+)/$', EditProject.as_view(), name='editProject'),
    url(r'^deleteProject/(?P<prj_pk>[0-9]+)/$', DeleteProject.as_view(), name='deleteProject'),
    url(r'^editExperiment/(?P<exp_pk>[0-9]+)/$', EditExperiment.as_view(), name='editExperiment'),
    url(r'^deleteExperiment/(?P<exp_pk>[0-9]+)/$', DeleteExperiment.as_view(), name='deleteExperiment'),
    url(r'^editIndividual/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<ind_pk>[0-9]+)/$', EditIndividual.as_view(), name='editIndividual'),
    url(r'^deleteIndividual/(?P<prj_pk>[0-9]+)/(?P<ind_pk>[0-9]+)/$', DeleteIndividual.as_view(), name='deleteIndividual'),
    url(r'^editBiosource/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<biosrc_pk>[0-9]+)/$', EditBiosource.as_view(), name='editBiosource'),
    url(r'^deleteBiosource/(?P<prj_pk>[0-9]+)/(?P<biosrc_pk>[0-9]+)/$', DeleteBiosource.as_view(), name='deleteBiosource'),
    url(r'^editBiosample/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<biosm_pk>[0-9]+)/$', EditBiosample.as_view(), name='editBiosample'),
    url(r'^deleteBiosample/(?P<prj_pk>[0-9]+)/(?P<biosm_pk>[0-9]+)/$', DeleteBiosample.as_view(), name='deleteBiosample'),
    url(r'^editTreatmentRnai/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<trnai_pk>[0-9]+)/$', EditTreatmentRnai.as_view(), name='editTreatmentRnai'),
    url(r'^deleteTreatmentRnai/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<trnai_pk>[0-9]+)/$', DeleteTreatmentRnai.as_view(), name='deleteTreatmentRnai'),
    url(r'^editTreatmentChemical/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<tchem_pk>[0-9]+)/$', EditTreatmentChemical.as_view(), name='editTreatmentChemical'),
    url(r'^deleteTreatmentChemical/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<tchem_pk>[0-9]+)/$', DeleteTreatmentChemical.as_view(), name='deleteTreatmentChemical'),
    url(r'^editOther/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<trt_pk>[0-9]+)/$', EditOther.as_view(), name='editOther'),
    url(r'^deleteOther/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<trt_pk>[0-9]+)/$', DeleteOther.as_view(), name='deleteOther'),
    url(r'^editModification/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<mod_pk>[0-9]+)/$', EditModification.as_view(), name='editModification'),
    url(r'^deleteModification/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<mod_pk>[0-9]+)/$', DeleteModification.as_view(), name='deleteModification'),
    url(r'^editConstruct/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<construct_pk>[0-9]+)/$', EditConstruct.as_view(), name='editConstruct'),
    url(r'^deleteConstruct/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<construct_pk>[0-9]+)/$', DeleteConstruct.as_view(), name='deleteConstruct'),
    url(r'^editGenomicRegions/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<genreg_pk>[0-9]+)/$', EditGenomicRegions.as_view(), name='editGenomicRegions'),
    url(r'^deleteGenomicRegions/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<genreg_pk>[0-9]+)/$', DeleteGenomicRegions.as_view(), name='deleteGenomicRegions'),
    url(r'^editTarget/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<target_pk>[0-9]+)/$', EditTarget.as_view(), name='editTarget'),
    url(r'^deleteTarget/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<target_pk>[0-9]+)/$', DeleteTarget.as_view(), name='deleteTarget'),
    url(r'^editSequencingRun/(?P<run_pk>[0-9]+)/$', EditSequencingRun.as_view(), name='editSequencingRun'),
    url(r'^deleteSequencingRun/(?P<run_pk>[0-9]+)/$', DeleteSequencingRun.as_view(), name='deleteSequencingRun'),
    url(r'^editSequencingFile/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<seqfile_pk>[0-9]+)/$', EditSequencingFile.as_view(), name='editSequencingFile'),
    url(r'^deleteSequencingFile/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<seqfile_pk>[0-9]+)/$', DeleteSequencingFile.as_view(), name='deleteSequencingFile'),
 #   url(r'^editAnalysis/(?P<pk>[0-9]+)/$', EditAnalysis.as_view(), name='editAnalysis'),
 #   url(r'^deleteAnalysis/(?P<pk>[0-9]+)/$', DeleteAnalysis.as_view(), name='deleteAnalysis'),
    url(r'^editExperimentSet/(?P<prj_pk>[0-9]+)/(?P<expset_pk>[0-9]+)/$', EditExperimentSet.as_view(), name='editExperimentSet'),
    url(r'^deleteExperimentSet/(?P<prj_pk>[0-9]+)/(?P<expset_pk>[0-9]+)/$', DeleteExperimentSet.as_view(), name='deleteExperimentSet'),
    url(r'^editFileSet/(?P<prj_pk>[0-9]+)/(?P<fset_pk>[0-9]+)/$', EditFileSet.as_view(), name='editFileSet'),
    url(r'^deleteFileSet/(?P<prj_pk>[0-9]+)/(?P<fset_pk>[0-9]+)/$', DeleteFileSet.as_view(), name='deleteFileSet'),
    url(r'^editTag/(?P<prj_pk>[0-9]+)/(?P<tag_pk>[0-9]+)/$', EditTag.as_view(), name='editTag'),
    url(r'^deleteTag/(?P<prj_pk>[0-9]+)/(?P<tag_pk>[0-9]+)/$', DeleteTag.as_view(), name='deleteTag'),
    url(r'^editProtocol/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<protocol_pk>[0-9]+)/$', EditProtocol.as_view(), name='editProtocol'),
    url(r'^deleteProtocol/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<protocol_pk>[0-9]+)/$', DeleteProtocol.as_view(), name='deleteProtocol'),
    url(r'^editDocument/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<doc_pk>[0-9]+)/$', EditDocument.as_view(), name='editDocument'),
    url(r'^deleteDocument/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<doc_pk>[0-9]+)/$', DeleteDocument.as_view(), name='deleteDocument'),
    url(r'^editPublication/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<pub_pk>[0-9]+)/$', EditPublication.as_view(), name='editPublication'),
    url(r'^deletePublication/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<pub_pk>[0-9]+)/$', DeletePublication.as_view(), name='deletePublication'),
    url(r'^editImageObjects/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<img_pk>[0-9]+)/$', EditImageObjects.as_view(), name='editImageObjects'),
    url(r'^deleteImageObjects/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<img_pk>[0-9]+)/$', DeleteImageObjects.as_view(), name='deleteImageObjects'),
    url(r'^editBarcode/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<barcode_pk>[0-9]+)/$', EditBarcode.as_view(), name='editBarcode'),
    url(r'^deleteBarcode/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/(?P<barcode_pk>[0-9]+)/$', DeleteBarcode.as_view(), name='deleteBarcode'), 
    
    
    
    url(r'^submitSequencingRun/(?P<seqrun_pk>[0-9]+)/$', views.submitSequencingRun, name='submitSequencingRun'),
    url(r'^approveSequencingRun/(?P<seqrun_pk>[0-9]+)/$', views.approveSequencingRun, name='approveSequencingRun'),
    url(r'^sequencingRunView/$', SequencingRunView.as_view(), name='sequencingRunView'),
    url(r'^searchView/$', views.searchView, name='searchView'),
    
    url(r'^exportExperiment/(?P<prj_pk>[0-9]+)/$', exportExperiment, name='exportExperiment'),
    url(r'^exportAnalysis/(?P<pk>[0-9]+)/$', exportAnalysis, name='exportAnalysis'),
    url(r'^exportGEO/(?P<prj_pk>[0-9]+)/$', exportGEO, name='exportGEO'),
    url(r'^exportDCIC/(?P<prj_pk>[0-9]+)/$', exportDCIC, name='exportDCIC'),
    url(r'^dcicView/(?P<prj_pk>[0-9]+)/$', DcicView.as_view(), name='dcicView'),
    url(r'^dcicFinalizeSubmission/(?P<prj_pk>[0-9]+)/$', DcicFinalizeSubmission.as_view(), name='dcicFinalizeSubmission'),
    url(r'^cloneExperimentList/(?P<prj_pk>[0-9]+)/$', CloneExperimentList.as_view(), name='cloneExperimentList'),
    url(r'^cloneExperiment/(?P<exp_pk>[0-9]+)/$', CloneExperiment.as_view(), name='cloneExperiment'),
    url(r'^importSequencingFiles/(?P<prj_pk>[0-9]+)/$', ImportSequencingFiles.as_view(), name='importSequencingFiles'),
    url(r'^createSequencingFiles/(?P<prj_pk>[0-9]+)/$', CreateSequencingFiles.as_view(), name='createSequencingFiles'),
    url(r'^downloadFile/$', views.downloadFile, name='downloadFile'),
    url(r'^moveExperiments/(?P<prj_pk>[0-9]+)/$', MoveExperiments.as_view(), name='moveExperiments'),
    url(r'^exportDistiller/(?P<prj_pk>[0-9]+)/$', ExportDistiller.as_view(), name='exportDistiller'),
    
    ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 