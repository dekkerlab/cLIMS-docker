'''
Created on Nov 15, 2016

@author: nanda
'''
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, HttpResponseRedirect
from organization.models import *
import csv
import xlwt
from xlwt.compat import xrange
from openpyxl.reader.excel import load_workbook
from organization.excelRow import insert_rows
from openpyxl.styles import Color, Fill
from cLIMS.base import *
from dryLab.models import *
import json
from _collections import OrderedDict, defaultdict
from wetLab.models import *
import collections
from openpyxl.utils.cell import get_column_letter
from django.contrib import messages


@login_required 
def exportExperiment(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="meta_data_sample.csv"'
    projectId = request.session['projectId']
    dbdata = Experiment.objects.filter(project=projectId)
    writer = csv.writer(response)
    for a in dbdata:
        field_names = [x.name for x in a._meta.local_fields]
        break
    writer.writerow(field_names)
    for obj in dbdata:
        writer.writerow([getattr(obj, field) for field in field_names])
    return response

def orderByNumber(jsonDict):
    jsonList = jsonDict.items()
    sorted_list = sorted(jsonList, key=lambda k: (int(k[1]['order'])))
    sorted_dict= OrderedDict(sorted_list)
    return sorted_dict

    
def export(analysisType,ws, projectId):
    dbdata = Analysis.objects.filter(analysis_exp__project=projectId, analysis_type__field_name=analysisType)
    if (dbdata):
        row_num = 0
        for a in dbdata:
            field_names = [x.name for x in a._meta.local_fields]
            break
        columns = []
        for names in field_names:
            if(names == "analysis_fields"):
                jsonObj = JsonObjField.objects.get(field_name=analysisType)
                jsonFields = orderByNumber(jsonObj.field_set)
                for keys in jsonFields:
                    columns.append((keys, 4000))
            elif(names == "analysis_import"):
                pass
            elif(names == "analysis_hiGlass"):
                pass
            else:
                columns.append((names, 4000))
        
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
    
        for col_num in xrange(len(columns)):
            ws.write(row_num, col_num, columns[col_num][0], font_style)
            # set column width
            ws.col(col_num).width = columns[col_num][1]
    
        font_style = xlwt.XFStyle()
        font_style.alignment.wrap = 1
        
        
        for obj in dbdata:
            row_num += 1
            row = []
            for field in field_names:
                att = getattr(obj, field)
                if(field == "analysis_fields"):
                    json_data = json.loads(att)
                    for keys in jsonFields:
                        json_val = json_data[keys]
                        row.append(json_val)
                elif(field == "analysis_import"):
                    pass
                elif(field == "analysis_hiGlass"):
                    pass
                else:
                    if ((type(att) != int) and (type(att) != str)):
                        att = str(att)
                    row.append(att)
            for col_num in xrange(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)
    else:
        pass
    
         
@login_required 
def exportAnalysis(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=mymodel.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    
    projectId = request.session['projectId']
    ana = Analysis.objects.filter(analysis_exp__project=projectId)
    
    analysis = list(set([x.analysis_type for x in ana]))
    
    for analysisType in analysis:
        print(analysisType, analysis)
        if str(analysisType) == "Hi-C Analysis":
            ws = wb.add_sheet('Hi-C')
            export(analysisType,ws, projectId)
            
        elif str(analysisType) == "3C Analysis":
            ws = wb.add_sheet('3C')
            export(analysisType,ws, projectId)
             
        elif str(analysisType) == "5C Analysis":
            ws = wb.add_sheet('5C')
            export(analysisType,ws, projectId)
        
        elif str(analysisType) == "CaptureC Analysis":
            ws = wb.add_sheet('CaptureC')
            export(analysisType,ws, projectId)
             
        else:
            pass
        
        
    wb.save(response)
    return response


@login_required 
def exportGEO(request):
    projectId = request.session['projectId']
    prj = Project.objects.get(pk=projectId)
    runUnits = SequencingRun.objects.filter(project=projectId)
    files = SeqencingFile.objects.filter(sequencingFile_exp__project=projectId)
    experiments = Experiment.objects.filter(project=projectId)
    bioSample = Biosample.objects.filter(expBio__project=projectId)
    
    
    title = prj.project_name
    summary = prj.project_notes
    contributor1 = str(prj.project_owner)
    contributor2 = prj.project_contributor.all()
    membersList = []
    for values in contributor2:
        membersList.append(values)
    
 
     
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=GEO.xlsx'
    file_path_new = ROOTFOLDER+'/organization/static/siteWide/geo_template_new.xlsx'
 
    wb = load_workbook(file_path_new)
    ws = wb.worksheets[0]
    ws.insert_rows = insert_rows
     
    ws.cell(row=9, column=2).value = title
    ws.cell(row=10, column=2).value = summary
    ws.cell(row=12, column=2).value = contributor1
     
    memberRowNo = 13
    for members in membersList:
        insert_rows(ws, row_idx= memberRowNo, cnt = 1, above=True, copy_style=True)
        ws.cell(row=memberRowNo, column=1).value = "contributor"
        ws.cell(row=memberRowNo, column=2).value = str(members)
         
        memberRowNo +=1
     
    rowNo = ws.max_row
    for i in range (rowNo):
        if((ws.cell(row=i+1, column=1).value)=="Sample name"):
            sampleRowNo = i+2
            break
     
    count = 1
     
         
    for sample in bioSample:
        insert_rows(ws, row_idx= sampleRowNo, cnt = 1, above=False, copy_style=False)
        ws.cell(row=sampleRowNo, column=1).value = "Sample " + str(count)
        ws.cell(row=sampleRowNo, column=2).value = str(sample.biosample_name)
        ws.cell(row=sampleRowNo, column=3).value = str(sample.biosample_biosource.biosource_tissue)
        ws.cell(row=sampleRowNo, column=4).value = str(sample.biosample_individual.individual_type)
        if(sample.protocol):
            #ws.cell(row=sampleRowNo, column=5).value = str(sample.protocol.type)
            ws.cell(row=sampleRowNo, column=6).value = str(sample.protocol.enzyme) 
        ws.cell(row=sampleRowNo, column=7).value = str(sample.biosample_biosource.biosource_cell_line)  
        ws.cell(row=sampleRowNo, column=8).value = str("DNA")
        ws.cell(row=sampleRowNo, column=9).value = str(sample.biosample_biosource.biosource_description)
         
        sampleRowNo += 1
        count += 1
     
    rowNo = ws.max_row
    for i in range (rowNo):
        if((ws.cell(row=i+1, column=1).value)=="RAW FILES"):
            rawFilesRowNo = i+3
            break
     
     
    for file in files:
        insert_rows(ws, row_idx= rawFilesRowNo, cnt = 1, above=True, copy_style=False)
        ws.cell(row=rawFilesRowNo, column=1).value = str(file.sequencingFile_name)
        ws.cell(row=rawFilesRowNo, column=3).value = str(file.sequencingFile_sha256sum)
#         ws.cell(row=rawFilesRowNo, column=5).value = str(file.number_of_reads)
         
        rawFilesRowNo += 1
 
    wb.save(response)
    return response

def appendFilterdcic(dcicExcelSheet,sheetname,entry):
    if(not(entry[0].split(":")[0]=="dcic")):
        dcicExcelSheet[sheetname].append(entry)
        

def update_dcic(obj):
    obj.update_dcic = False
    obj.save()
                
def initialize(tab,sheetTab):
    file_path_new = ROOTFOLDER+'/organization/static/siteWide/Metadata_entry_form_V3.xlsx'
    wb = load_workbook(file_path_new)
    sheet = wb.get_sheet_by_name(tab)
    maxCol=get_column_letter(sheet.max_column)
    headers = []
    
    for rowOfCellObjects in sheet['B1':maxCol]:         
        for cellObj in rowOfCellObjects:
            if "*" in cellObj.value:
                headers.append(cellObj.value[1:])
            else:
                headers.append(cellObj.value)
    
    sheetTab.append(headers)
    return (sheetTab)


def appendPublication(pKey, dcicExcelSheet,finalizeOnly):
    pub = Publication.objects.get(pk=pKey)
    if(finalizeOnly):
        update_dcic(pub)
    singlePub = []
    singlePub.append(pub.dcic_alias)
    singlePub.append(str(pub.publication_title))
    singlePub.append(str(pub.publication_id))
    if(pub.attachment):
        singlePub.append(str(FILEUPLOADPATH)+str(pub.attachment))
    else:
        singlePub.append("")
    if(pub.publication_categories):
        singlePub.append(str(pub.publication_categories))
    else:
        singlePub.append("")
    if(pub.exp_sets_prod_in_pub):
        singlePub.append(str(pub.exp_sets_prod_in_pub))
    else:
        singlePub.append("")
    if(pub.exp_sets_used_in_pub):
        singlePub.append(str(pub.exp_sets_used_in_pub))
    else:
        singlePub.append("")
    if(pub.publication_published_by):
        singlePub.append(str(pub.publication_published_by))
    else:
        singlePub.append("")                   
    appendFilterdcic(dcicExcelSheet,'Publication',singlePub)

def appendDocument(pKey, dcicExcelSheet,finalizeOnly):
    doc = Document.objects.get(pk=pKey)
    if(finalizeOnly):
        update_dcic(doc)
    singleDocument = []
    singleDocument.append(doc.dcic_alias)
    singleDocument.append(doc.description)
    singleDocument.append(str(doc.type))
    if(doc.attachment):
        singleDocument.append(str(FILEUPLOADPATH)+str(doc.attachment))
    else:
        singleDocument.append("")
    singleDocument.append(str(doc.url))
    if(doc.references):
        singleDocument.append(doc.references.dcic_alias)
        appendPublication(doc.references.pk,dcicExcelSheet,finalizeOnly)
    else:
        singleDocument.append("")
    appendFilterdcic(dcicExcelSheet,'Document',singleDocument)

def appendVendor(pKey,dcicExcelSheet,finalizeOnly):
    ven = Vendor.objects.get(pk=pKey)
    if(finalizeOnly):
        update_dcic(ven)
    singleVendor = []
    singleVendor.append(ven.dcic_alias)
    singleVendor.append(str(ven.vendor_title))
    if(ven.vendor_description != None):
        singleVendor.append(str(ven.vendor_description))
    else:
        singleVendor.append("")
    singleVendor.append(str(ven.vendor_url))
    appendFilterdcic(dcicExcelSheet,'Vendor',singleVendor)

def appendEnzyme(pKey,dcicExcelSheet,finalizeOnly):
    enz = Enzyme.objects.get(pk=pKey)
    if(finalizeOnly):
        update_dcic(enz)
    singleEnzyme = []
    singleEnzyme.append(enz.dcic_alias)
    singleEnzyme.append(enz.enzyme_name)
    singleEnzyme.append(enz.enzyme_description)
    if(enz.enzyme_vendor):
        singleEnzyme.append(str(enz.enzyme_vendor.dcic_alias))
        appendVendor(enz.enzyme_vendor.pk, dcicExcelSheet,finalizeOnly)
    else:
        singleEnzyme.append("")
    if(enz.document):
        singleEnzyme.append(enz.document.dcic_alias)
        appendDocument(enz.document.pk, dcicExcelSheet,finalizeOnly)
    else:
        singleEnzyme.append("")
    singleEnzyme.append(enz.url)
    appendFilterdcic(dcicExcelSheet,'Enzyme',singleEnzyme)

def appendImageObjects(pKey,dcicExcelSheet,finalizeOnly):
    img=ImageObjects.objects.get(pk=pKey)
    if(finalizeOnly):
        update_dcic(img)
    singleItem = []
    singleItem.append(img.dcic_alias)
    singleItem.append(str(FILEUPLOADPATH)+str(img.imageObjects_images))
    singleItem.append(img.description)
    appendFilterdcic(dcicExcelSheet,'Image',singleItem)
    
def appendConstruct(pKey,dcicExcelSheet,finalizeOnly):
    construct = Construct.objects.get(pk=pKey)
    if(finalizeOnly):
        update_dcic(construct)
    singleItem = []
    singleItem.append(construct.dcic_alias)
    singleItem.append(construct.construct_name)
    if(construct.construct_description != None):
        singleItem.append(construct.construct_description)
    else:
        singleItem.append("")
    singleItem.append(str(construct.construct_type))
    if(construct.construct_vendor):
        singleItem.append(construct.construct_vendor.dcic_alias)
        appendVendor(construct.construct_vendor.pk,dcicExcelSheet,finalizeOnly)
    else:
        singleItem.append("")
    singleItem.append(construct.construct_designed_to_Target)
    singleItem.append(construct.construct_insert_sequence)
    if(construct.document):
        singleItem.append(construct.document.dcic_alias)
        appendDocument(construct.document.pk, dcicExcelSheet,finalizeOnly)
    else:
        singleItem.append("")
    singleItem.append(construct.construct_tag)
    singleItem.append(construct.construct_vector_backbone)
    singleItem.append("")
    if(construct.references):
        singleItem.append(construct.references.dcic_alias)
        appendPublication(construct.references.pk,dcicExcelSheet,finalizeOnly)
    else:
        singleItem.append("")
    singleItem.append(construct.url)
    appendFilterdcic(dcicExcelSheet,'Construct',singleItem)

def appendTarget(pKey,dcicExcelSheet,finalizeOnly):
    target=Target.objects.get(pk=pKey)
    if(finalizeOnly):
        update_dcic(target)
    singleItem = []
    singleItem.append(target.dcic_alias)
    if(target.target_description != None):
        singleItem.append(str(target.target_description))
    else:
        singleItem.append("")
    singleItem.append(str(target.targeted_genes))
    singleItem.append(str(target.targeted_region))
    singleItem.append(str(target.targeted_proteins))
    singleItem.append(str(target.targeted_rnas))
    if(target.targeted_structure!=None):
        singleItem.append(str(target.targeted_structure))
    else:
        singleItem.append("")
    if(target.references):
        singleItem.append(target.references.dcic_alias)
        appendPublication(target.references.pk,dcicExcelSheet,finalizeOnly)
    else:
        singleItem.append("")
    singleItem.append(str(target.dbxrefs))
    appendFilterdcic(dcicExcelSheet,'Target',singleItem)

def appendGenomicRegion(pKey,dcicExcelSheet,finalizeOnly):          
    genomicRegion = GenomicRegions.objects.get(pk=pKey)
    if(finalizeOnly):
        update_dcic(genomicRegion)
    singleItem = []
    singleItem.append(genomicRegion.dcic_alias)
    if(genomicRegion.genomicRegions_genome_assembly):
        singleItem.append(str(genomicRegion.genomicRegions_genome_assembly))
    else:
        singleItem.append("")
    if(genomicRegion.genomicRegions_chromosome != None):
        singleItem.append(str(genomicRegion.genomicRegions_chromosome))
    else:
        singleItem.append("")
    singleItem.append(genomicRegion.genomicRegions_start_coordinate)
    singleItem.append(genomicRegion.genomicRegions_end_coordinate)
    singleItem.append(genomicRegion.genomicRegions_location_description)
    singleItem.append(genomicRegion.genomicRegions_start_location)
    singleItem.append(genomicRegion.genomicRegions_end_location)
    appendFilterdcic(dcicExcelSheet,'GenomicRegion',singleItem)

def appendModification(pKey,dcicExcelSheet,finalizeOnly):
    modificationObj = Modification.objects.get(pk=pKey)
    if(finalizeOnly):
        update_dcic(modificationObj)
    singleMod = []
    singleMod.append(modificationObj.dcic_alias)
    singleMod.append(modificationObj.modification_description)
    if(str(modificationObj.modification_type) != None):
        singleMod.append(str(modificationObj.modification_type))
    else:
        singleMod.append("")
    if(modificationObj.constructs):
        singleMod.append(modificationObj.constructs.dcic_alias)
        appendConstruct(modificationObj.constructs.pk, dcicExcelSheet,finalizeOnly)
    else:
        singleMod.append("")
    if(modificationObj.modification_vendor):
        singleMod.append(str(modificationObj.modification_vendor.dcic_alias))
        appendVendor(modificationObj.modification_vendor.pk, dcicExcelSheet,finalizeOnly)
    else:
        singleMod.append("")
    singleMod.append(modificationObj.modification_gRNA)
    if(modificationObj.modification_genomicRegions):
        singleMod.append(modificationObj.modification_genomicRegions.dcic_alias)
        appendGenomicRegion(modificationObj.modification_genomicRegions.pk, dcicExcelSheet,finalizeOnly)
    else:
        singleMod.append("")
    if(modificationObj.target):
        singleMod.append(modificationObj.target.dcic_alias)
        appendTarget(modificationObj.target.pk, dcicExcelSheet,finalizeOnly)
    else:
        singleMod.append("")
    if(modificationObj.references):
        singleMod.append(modificationObj.references.dcic_alias)
        appendPublication(modificationObj.references.pk,dcicExcelSheet,finalizeOnly)
    else:
        singleMod.append("")
    singleMod.append(modificationObj.url)
    appendFilterdcic(dcicExcelSheet,'Modification',singleMod)
    


def appendProtocol(pKey,dcicExcelSheet,finalizeOnly):
    protocolObj = Protocol.objects.get(pk=pKey)
    if(finalizeOnly):
        update_dcic(protocolObj)
    singleProtocol = []
    singleProtocol.append(protocolObj.dcic_alias)
    singleProtocol.append(protocolObj.description)
    if(protocolObj.protocol_type != None):
        singleProtocol.append(protocolObj.protocol_type.choice_name)
    else:
        singleProtocol.append("")
    if(protocolObj.enzyme):
        appendEnzyme(protocolObj.enzyme.pk, dcicExcelSheet,finalizeOnly)
    if(protocolObj.attachment):
        singleProtocol.append(str(FILEUPLOADPATH)+str(protocolObj.attachment))
    else:
        singleProtocol.append("")
    if(protocolObj.protocol_classification != None):
        singleProtocol.append(protocolObj.protocol_classification.choice_name)
    else:
        singleProtocol.append("")
    
    appendFilterdcic(dcicExcelSheet,'Protocol',singleProtocol)


def appendFiles(pKey,dcicExcelSheet,finalizeOnly):
    f = SeqencingFile.objects.get(pk=pKey)
    singleFile = []
    if(str(f.file_format)=="fasta"):
        singleFile.append(f.dcic_alias)
        singleFile.append("") #description
        singleFile.append(str(f.file_format))
#                         if(f.file_classification != None):
#                             singleFile.append(str(f.file_classification))
#                         else:
#                             singleFile.append("")
        if(f.file_format_specifications):
            singleFile.append(str(f.file_format_specifications))
        else:
            singleFile.append("")
        singleFile.append("")
        singleFile.append("")
        singleFile.append(f.dbxrefs)
        ##FileMainPATH is exported then manually remove it so that we know the path
        singleFile.append(f.sequencingFile_mainPath)
        
        appendFilterdcic(dcicExcelSheet,'FileFasta',singleFile)
        
    elif(str(f.file_format)=="fastq"):
        singleFile.append(f.dcic_alias)
        singleFile.append("") #description
        singleFile.append(str(f.file_format))
        #singleFile.append(str(f.file_classification))
        if(f.file_format_specifications):
            singleFile.append(str(f.file_format_specifications))
        else:
            singleFile.append("")
        if(f.file_barcode):
            singleFile.append(str(f.file_barcode.barcode_index))
        else:
            singleFile.append("")
        if(f.barcode_in_read):
            singleFile.append(str(f.barcode_in_read))
        else:
            singleFile.append("")
        if(f.file_barcode):
            singleFile.append(str(f.file_barcode.barcode_position))
        else:
            singleFile.append("")
        singleFile.append(str(f.flowcell_details_chunk))
#                         if(f.sequencingFile_run):
#                             singleFile.append(str(f.sequencingFile_run))
#                         else:
        singleFile.append("")##flowcell_details.flowcell 
        singleFile.append(str(f.flowcell_details_lane))
        if(f.sequencingFile_run.run_sequencing_machine != None):
            singleFile.append(str(f.sequencingFile_run.run_sequencing_machine))
        else:
            singleFile.append("")
        if(f.sequencingFile_run.run_sequencing_instrument != None):
            singleFile.append(str(f.sequencingFile_run.run_sequencing_instrument))
        else:
            singleFile.append("")
        if(f.paired_end != None):
            singleFile.append(str(f.paired_end))
        else:
            singleFile.append("")
        #singleFile.append("") ##quality_metric
        if(f.read_length != None):
            singleFile.append(str(f.read_length))
        else:
            singleFile.append("")
        if(f.relationship_type != None):
            singleFile.append(str(f.relationship_type))
        else:
            singleFile.append("")
        if(f.related_files != None):
            singleFile.append(str(f.related_files.dcic_alias))
        else:
            singleFile.append("")   
        singleFile.append(f.dbxrefs)
        ##FileMainPATH is exported then manually remove it so that we know the path
        singleFile.append(f.sequencingFile_mainPath)
        appendFilterdcic(dcicExcelSheet,'FileFastq',singleFile)

def appendBioRep(expPk,singleExp):
    exp = Experiment.objects.get(pk=expPk)
    expSameBiosource = Experiment.objects.filter(experiment_biosample__biosample_biosource=exp.experiment_biosample.biosample_biosource,
                                                protocol=exp.protocol,experiment_enzyme=exp.experiment_enzyme, 
                                                type=exp.type,project=exp.project)

    
    biosampleFields=json.loads(exp.experiment_biosample.biosample_fields)
    bioReplicates = []
    #biosamPk = []
    fieldsToCheckBiosample=["synchronization_stage","karyotype"]
    
    for e in expSameBiosource:
        #biosamPk.append(e.experiment_biosample.pk)
        #bioReplicates=list(set(biosamPk))
        sameFieldsBiosample=json.loads(e.experiment_biosample.biosample_fields)
        #if((sorted(expSameFields.items()) == sorted(expFields.items()))):
        if(exp.type.field_name in ["Hi-C Exp Protocol","CaptureC Exp Protocol","ATAC-seq Protocol"]):
            if( all(biosampleFields[x] == sameFieldsBiosample[x] for x in fieldsToCheckBiosample) 
                and set(e.experiment_biosample.modifications.all())==set(exp.experiment_biosample.modifications.all()) 
                and e.experiment_biosample.protocol==exp.experiment_biosample.protocol
                and set(e.experiment_biosample.biosample_TreatmentRnai.all())==set(exp.experiment_biosample.biosample_TreatmentRnai.all())
                and set(e.experiment_biosample.biosample_TreatmentChemical.all())==set(exp.experiment_biosample.biosample_TreatmentChemical.all())):
                bioReplicates.append(e.experiment_biosample.pk)
        else:
            bioReplicates.append(0)

    bio_rep_no = (sorted(bioReplicates)).index(exp.experiment_biosample.pk)+1
    singleExp.append(bio_rep_no)
    
def appendTechRep(expPk,singleExp):
    exp = Experiment.objects.get(pk=expPk)
    expSameBiosample = Experiment.objects.filter(experiment_biosample=exp.experiment_biosample,project=exp.project)
    
#     expFields=json.loads(exp.experiment_fields)
    techReplicates = []
#     fieldsToCheckExpHicCaptureC=["crosslinking_time","experiment_type","average_fragment_size","digestion_temperature",
#                                  "ligation_time","digestion_time","tagging_method","ligation_volume","crosslinking_method",
#                                  "fragmentation_method","ligation_temperature","crosslinking_temperature","biotin_removed",
#                                  "fragment_size_range"]
    for e in expSameBiosample:
#         expSameFields=json.loads(e.experiment_fields)
#         if( all(expSameFields[x] == expFields[x] for x in fieldsToCheckExpHicCaptureC)):
        techReplicates.append(e.pk)
    
    tech_rep_no = (sorted(techReplicates)).index(expPk)+1
    
    singleExp.append(tech_rep_no)


    
    
def populateDict(request, experimentList):
    finalizeOnly = request.session['finalizeOnly']
    projectId = request.session['projectId']
    bioSample = Biosample.objects.filter(expBio__pk__in=experimentList)
    dcicExcelSheet=defaultdict(list)

    tabNames = ("Document","Protocol","Publication","IndividualMouse","IndividualHuman","Vendor","Enzyme","Biosource","Construct","TreatmentRnai",
                "TreatmentChemical","GenomicRegion","Target","Modification","Image","BiosampleCellCulture","Biosample","FileFastq","FileFasta",
                "ExperimentHiC","ExperimentCaptureC","ExperimentAtacseq","ExperimentSetReplicate","ExperimentSet")
    
    for tab in tabNames:
        dcicExcelSheet[tab] = initialize(tab, dcicExcelSheet[tab])
    
    
#     ##Experiment sets
#     
#     if (ExperimentSet.objects.filter(project=projectId)):
#         expSets = ExperimentSet.objects.filter(project=projectId)
#         for eSet in expSets:
#             singleItem = []
#             singleItem.append(labName +"ExperimentSet_" +str(eSet.experimentSet_name)+"_"+str(eSet.pk))
#             singleItem.append(str(eSet.experimentSet_description))
#             singleItem.append(str(eSet.experimentSet_type))
#             if(eSet.document):
#                 singleItem.append(labName +"Document_"+str(eSet.document)+"_"+str(eSet.document.pk))
#                 appendDocument(eSet.document.pk, dcicExcelSheet,finalizeOnly)
#             else:
#                 singleItem.append("")
#             dcicExcelSheet['ExperimentSet'].append(singleItem)
    
                    
    ##Biosample
    for sample in bioSample:
        if(finalizeOnly):
            update_dcic(sample)
        singleSample = []
        singleSample.append(sample.dcic_alias)
        singleSample.append(str(sample.biosample_description))
        singleSample.append(sample.biosample_biosource.dcic_alias)
        if(sample.protocol):
            singleSample.append(sample.protocol.dcic_alias)
            appendProtocol(sample.protocol.pk,dcicExcelSheet,finalizeOnly)
        else:
            singleSample.append("")
        singleSample.append("")
        singleSample.append("")    
        if(sample.biosample_type):
            ##BiosampleCellCulture is a special case for DCIC Alias since there is only one object Biosample for this
            aliasList=sample.dcic_alias.split("_")
            singleSample.append(LABNAME +"BiosampleCellCulture_"+str("_".join(aliasList[1:])))
        else:
            singleSample.append("")
        if(sample.modifications.all()):
            modList = []
            for mod in sample.modifications.all():
                if(finalizeOnly):
                    update_dcic(mod)
                modList.append(mod.dcic_alias)
                appendModification(mod.pk,dcicExcelSheet,finalizeOnly)
            singleSample.append(",".join(modList))
        else:
            singleSample.append("")
        
        rnai= []
        chemical=[]
        treatmentList=[]
        if(sample.biosample_TreatmentRnai.all()):
            for rnaiTreat in sample.biosample_TreatmentRnai.all():
                if(finalizeOnly):
                    update_dcic(rnaiTreat)
                rnai.append(rnaiTreat.dcic_alias)
            treatmentList.append(",".join(rnai))
        if(sample.biosample_TreatmentChemical.all()):
            for chemTreat in sample.biosample_TreatmentChemical.all():
                if(finalizeOnly):
                    update_dcic(chemTreat)
                chemical.append(chemTreat.dcic_alias)
            treatmentList.append(",".join(chemical))
        singleSample.append(",".join(treatmentList))
        
        if(sample.references):
            singleSample.append(sample.references.dcic_alias)
            appendPublication(sample.references.pk,dcicExcelSheet,finalizeOnly)
        else:
            singleSample.append("")
        if(sample.dbxrefs):
            singleSample.append(sample.dbxrefs)
        else:
            singleSample.append("")
            
        appendFilterdcic(dcicExcelSheet,'Biosample',singleSample)
        

        ##Biosamplecellculture
        if(sample.biosample_type):
            bcc=json.loads(sample.biosample_fields)
            singleBcc = []
            ##BiosampleCellCulture is a special case for DCIC Alias since there is only one object Biosample for this
            aliasList=sample.dcic_alias.split("_")
            
            singleBcc.append(LABNAME +"BiosampleCellCulture_"+str("_".join(aliasList[1:])))
            singleBcc.append(sample.biosample_description)
            singleBcc.append(bcc["culture_start_date"])
            
            
            ##authentication_protocols
            authDocs=[]
            if(sample.authentication_protocols.all()):
                for authDoc in sample.authentication_protocols.all():
                    if(finalizeOnly):
                        update_dcic(authDoc)
                    authDocs.append(authDoc.dcic_alias)
                    appendProtocol(authDoc.pk,dcicExcelSheet,finalizeOnly)
                singleBcc.append(",".join(authDocs))
            
            else:
                    singleBcc.append("")
            
            
            singleBcc.append(bcc["cell_line_lot_number"])
            singleBcc.append(bcc["culture_duration"])
            singleBcc.append(bcc["culture_harvest_date"])
            singleBcc.append(bcc["differentiation_state"])
            singleBcc.append(bcc["doubling_number"])
            singleBcc.append(bcc["doubling_time"])
            singleBcc.append(bcc["follows_sop"])
            singleBcc.append(bcc["karyotype"])

            if(ImageObjects.objects.filter(bioImg__pk=sample.pk)):
                image=ImageObjects.objects.filter(bioImg__pk=sample.pk)
                ig1 =[ imgs for imgs in image if imgs.imageObjects_type.choice_name=="morphology_image"]
                if(ig1):
                    singleBcc.append(ig1[0].dcic_alias)
                    appendImageObjects(ig1[0].pk,dcicExcelSheet,finalizeOnly)
                else:
                    singleBcc.append("")    
                
            else:
                singleBcc.append("")
                
            
            singleBcc.append(bcc["passage_number"])
            
#             singleBcc.append("") ##protocol_SOP_deviations
                ##protocol_additional
            if(Protocol.objects.filter(bioAddProto__pk=sample.pk)):
                proto = Protocol.objects.filter(bioAddProto__pk=sample.pk)
                if(proto.all()):
                    protoList = []
                    for p in proto.all():
                        if(finalizeOnly):
                            update_dcic(p)
                        protoList.append(p.dcic_alias)
                        appendProtocol(p.pk,dcicExcelSheet,finalizeOnly)
                    singleBcc.append(",".join(protoList))
                else:
                    singleBcc.append("")
            else:
                    singleBcc.append("")
            
            singleBcc.append(bcc["synchronization_stage"])
            
            if(sample.dbxrefs != None ):
                singleBcc.append(sample.dbxrefs)
            else:
                singleBcc.append("")
            
            
            
#             for keys in jsonFields:
#                 json_val = bcc[keys]
#                 singleBcc.append(json_val)

            appendFilterdcic(dcicExcelSheet,'BiosampleCellCulture',singleBcc)
            
        ##treatments
        if(sample.biosample_TreatmentRnai):
            treatmentRnais = TreatmentRnai.objects.filter(biosamTreatmentRnai=sample.pk)
            for treatmentRnai in treatmentRnais:
                if(finalizeOnly):
                    update_dcic(treatmentRnai)
                singleItem = []
                singleItem.append(treatmentRnai.dcic_alias)
                singleItem.append(treatmentRnai.treatmentRnai_description)
                if(treatmentRnai.treatmentRnai_type):
                    singleItem.append(str(treatmentRnai.treatmentRnai_type))
                else:
                    singleItem.append("")
                if(treatmentRnai.constructs):
                    singleItem.append(treatmentRnai.constructs.dcic_alias)
                    appendConstruct(treatmentRnai.constructs.pk, dcicExcelSheet,finalizeOnly)
                else:
                    singleItem.append("")
                if(treatmentRnai.treatmentRnai_vendor):
                    singleItem.append(str(treatmentRnai.treatmentRnai_vendor.dcic_alias))
                    appendVendor(treatmentRnai.treatmentRnai_vendor.pk, dcicExcelSheet,finalizeOnly)
                else:
                    singleItem.append("")
                if(treatmentRnai.treatmentRnai_target):
                    singleItem.append(treatmentRnai.treatmentRnai_target.dcic_alias)
                    appendTarget(treatmentRnai.treatmentRnai_target.pk, dcicExcelSheet,finalizeOnly)
                else:
                    singleItem.append("")
                if(treatmentRnai.treatmentRnai_nucleotide_seq):
                    singleItem.append(treatmentRnai.treatmentRnai_nucleotide_seq)
                else:
                    singleItem.append("")
                if(treatmentRnai.document):
                    singleItem.append(treatmentRnai.document.dcic_alias)
                    appendDocument(treatmentRnai.document.pk, dcicExcelSheet,finalizeOnly)
                else:
                    singleItem.append("")
                    
                if(treatmentRnai.references):
                    singleItem.append(treatmentRnai.references.dcic_alias)
                    appendPublication(treatmentRnai.references.pk,dcicExcelSheet,finalizeOnly)
                else:
                    singleItem.append("")
                singleItem.append(treatmentRnai.url)
                appendFilterdcic(dcicExcelSheet,'TreatmentRnai',singleItem)
                
        
        if(sample.biosample_TreatmentChemical):
            treatmentChemicals = TreatmentChemical.objects.filter(biosamTreatmentChemical=sample.pk)
            for treatmentChemical in treatmentChemicals:
                if(finalizeOnly):
                    update_dcic(treatmentChemical)
                singleItem = []
                singleItem.append(treatmentChemical.dcic_alias)
                singleItem.append(treatmentChemical.treatmentChemical_description)
                singleItem.append(treatmentChemical.treatmentChemical_chemical)
                if(treatmentChemical.treatmentChemical_concentration != 0):
                    singleItem.append(treatmentChemical.treatmentChemical_concentration)
                else:
                    singleItem.append("")
                if(treatmentChemical.treatmentChemical_concentration_units != None):
                    singleItem.append(str(treatmentChemical.treatmentChemical_concentration_units))
                else:
                    singleItem.append("")
                if(treatmentChemical.treatmentChemical_duration != None):
                    singleItem.append(str(treatmentChemical.treatmentChemical_duration))
                else:
                    singleItem.append("")
                if(treatmentChemical.treatmentChemical_duration_units != None):
                    singleItem.append(str(treatmentChemical.treatmentChemical_duration_units))
                else:
                    singleItem.append("")
                if(treatmentChemical.treatmentChemical_temperature != None):
                    singleItem.append(str(treatmentChemical.treatmentChemical_temperature))
                else:
                    singleItem.append("")
                if(treatmentChemical.document):
                    singleItem.append(treatmentChemical.document.dcic_alias)
                    appendDocument(treatmentChemical.document.pk, dcicExcelSheet,finalizeOnly)
                else:
                    singleItem.append("")
                if(treatmentChemical.references):
                    singleItem.append(treatmentChemical.references.dcic_alias)
                    appendPublication(treatmentChemical.references.pk,dcicExcelSheet,finalizeOnly)
                else:
                    singleItem.append("")
                appendFilterdcic(dcicExcelSheet,'TreatmentChemical',singleItem)
                
        if(Biosource.objects.get(bioSource__pk=sample.pk)):
            biosource = Biosource.objects.get(bioSource__pk=sample.pk)
            if(finalizeOnly):
                update_dcic(biosource)
            singleBio = []
            singleBio.append(biosource.dcic_alias)
            singleBio.append(biosource.biosource_description)
            singleBio.append(str(biosource.biosource_type))
            singleBio.append(str(biosource.biosource_cell_line))
            singleBio.append("") ##cell_line_tier calculated
#             if(biosource.biosource_cell_line_tier != None):
#                 singleBio.append(str(biosource.biosource_cell_line_tier))
#             else:
#                 singleBio.append("")
                
                
            ###Standard operation protocol 
            if(biosource.protocol):
                singleBio.append(biosource.protocol.dcic_alias)
                appendProtocol(biosource.protocol.pk, dcicExcelSheet, finalizeOnly)
            else:
                singleBio.append("")
                
            if(biosource.biosource_vendor):
                singleBio.append(str(biosource.biosource_vendor.dcic_alias))
                appendVendor(biosource.biosource_vendor.pk, dcicExcelSheet,finalizeOnly)
            else:
                singleBio.append("")
            
            #singleBio.append(biosource.cell_line_termid)
            #singleBio.append("") #cell_line_termid calculated
            
            if(biosource.biosource_individual):
                singleBio.append(biosource.biosource_individual.dcic_alias)
                indi = Individual.objects.get(pk=biosource.biosource_individual.pk)
                if(finalizeOnly):
                    update_dcic(indi)
                indiJson = json.loads(indi.individual_fields)
                singleIndi = []
                singleIndi.append(indi.dcic_alias)
                singleIndi.append(indiJson["age"])
                singleIndi.append(indiJson["age_units"])
                
                if(str(biosource.biosource_individual.individual_type)=="IndividualMouse"):
                    singleIndi.append(indiJson["mouse_life_stage"])
                    singleIndi.append(indiJson["mouse_strain"])
                    singleIndi.append(str(indi.individual_vendor.dcic_alias))
                elif(str(biosource.biosource_individual.individual_type)=="IndividualHuman"):
                    singleIndi.append(indiJson["ethnicity"])
                    singleIndi.append(indiJson["health_status"])
                    singleIndi.append(indiJson["life_stage"])
                
                else:
                    singleIndi.append("")
                    singleIndi.append("")
                    singleIndi.append("")
               
                singleIndi.append(indiJson["sex"])
                
                if(indi.document):
                    singleIndi.append(indi.document.dcic_alias)
                    appendDocument(indi.document.pk, dcicExcelSheet,finalizeOnly)
                else:
                    singleIndi.append("")
                singleIndi.append(indi.url)
                singleIndi.append(indi.dbxrefs)
                
                 
                if(str(biosource.biosource_individual.individual_type)=="IndividualMouse"):
                    appendFilterdcic(dcicExcelSheet,'IndividualMouse',singleIndi)
                    
                if(str(biosource.biosource_individual.individual_type)=="IndividualHuman"):
                    appendFilterdcic(dcicExcelSheet,'IndividualHuman',singleIndi)
                   
            else:    
                singleBio.append("")
                
            if(biosource.modifications):
                modList = []
                for mod in biosource.modifications.all():
                    if(finalizeOnly):
                        update_dcic(mod)
                    modList.append(mod.dcic_alias)
                    appendModification(mod.pk, dcicExcelSheet,finalizeOnly)
                singleBio.append(",".join(modList))
            else:
                singleBio.append("")
                
            #singleBio.append(biosource.biosource_tissue)    
            singleBio.append("")
            
            if(biosource.references):
                singleBio.append(biosource.references.dcic_alias)
                appendPublication(biosource.references.pk,dcicExcelSheet,finalizeOnly)
               
            else:
                singleBio.append("")
            singleBio.append(biosource.url)
            appendFilterdcic(dcicExcelSheet,'Biosource',singleBio)
    
    experiments = experimentList
    
    ##Experiments
    for exp in experiments:
        if(finalizeOnly):
            update_dcic(exp)
        expSet = ExperimentSet.objects.filter(experimentSet_exp=exp)
        if str(exp.type) == "Hi-C Exp Protocol":
            singleExp = []
            singleExp.append(exp.dcic_alias)
            singleExp.append(str(exp.experiment_description))
            experiment_set_join= "" 
            replicate_set_join= ""
            if(expSet):
                experiment_set = []
                replicate_set = []
                for eSet in expSet:
                    if(finalizeOnly):
                        update_dcic(eSet)
                    ExpSet = []
                    ExpSet.append(eSet.dcic_alias)
                    ExpSet.append(str(eSet.description))
                    if(eSet.document):
                        ExpSet.append(eSet.document.dcic_alias)
                        appendDocument(eSet.document.pk, dcicExcelSheet,finalizeOnly)
                    else:
                        ExpSet.append("")
                    if("replicates" in str(eSet.experimentSet_type)):
                        appendFilterdcic(dcicExcelSheet,'ExperimentSetReplicate',ExpSet)
                        experiment_set = []
                        replicate_set.append(eSet.dcic_alias)
                    else:
                        ExpSet.insert(2,str(eSet.experimentSet_type))
                        appendFilterdcic(dcicExcelSheet,'ExperimentSet',ExpSet)
                        experiment_set.append(eSet.dcic_alias)
                experiment_set_join= ",".join(experiment_set)    
                replicate_set_join= ",".join(replicate_set)
            
            singleExp.append(replicate_set_join)
            #appendBioRep(exp.pk,singleExp)
            #appendTechRep(exp.pk,singleExp)
            singleExp.append(exp.bio_rep_no) ####*bio_rep_no
            singleExp.append(exp.tec_rep_no) ####*tec_rep_no 
            singleExp.append(experiment_set_join)
            singleExp.append(exp.experiment_biosample.dcic_alias)
            
            expFields=json.loads(exp.experiment_fields)
            
            singleExp.append(expFields["experiment_type"])
            singleExp.append(str(exp.biosample_quantity))
            singleExp.append(str(exp.biosample_quantity_units))
            
            singleExp.append(str(expFields["biotin_removed"]))
            singleExp.append(str(expFields["crosslinking_method"]))
            singleExp.append(str(expFields["crosslinking_temperature"]))
            singleExp.append(str(expFields["crosslinking_time"]))
            
            if(exp.experiment_enzyme):
                singleExp.append(exp.experiment_enzyme.dcic_alias)
                appendEnzyme(exp.experiment_enzyme.pk, dcicExcelSheet,finalizeOnly)
            else:
                singleExp.append("")
                
            singleExp.append(str(expFields["digestion_temperature"]))
            singleExp.append(str(expFields["digestion_time"]))
            singleExp.append(str(expFields["enzyme_lot_number"]))
            singleExp.append(str(expFields["follows_sop"]))
            singleExp.append(str(expFields["average_fragment_size"]))
            singleExp.append(str(expFields["fragment_size_range"]))
            singleExp.append(str(expFields["fragment_size_selection_method"]))
            singleExp.append(str(expFields["fragmentation_method"]))
            singleExp.append(str(expFields["library_preparation_date"]))
            singleExp.append(str(expFields["ligation_temperature"]))
            singleExp.append(str(expFields["ligation_time"]))
            singleExp.append(str(expFields["ligation_volume"]))
            
            if(exp.protocol):
                singleExp.append(exp.protocol.dcic_alias)
                appendProtocol(exp.protocol.pk, dcicExcelSheet, finalizeOnly)
            
            
            
            if(exp.variation):
                singleExp.append(exp.variation.dcic_alias)
            else:
                singleExp.append("") ###protocol_variation
            
            singleExp.append(expFields["tagging_method"])
            
            if(SeqencingFile.objects.filter(sequencingFile_exp=exp.pk)):
                files = SeqencingFile.objects.filter(sequencingFile_exp=exp.pk)
                if(files.all()):
                    fileList = []
                    for f in files:
                        if(finalizeOnly):
                            update_dcic(f)
                        fileList.append(f.dcic_alias)
                        appendFiles(f.pk,dcicExcelSheet,finalizeOnly)
                    singleExp.append(",".join(fileList))
                else:
                    singleExp.append("")
            else:
                singleExp.append("")

            singleExp.append("")##experiment_relation.relationship_type
            singleExp.append("")##experiment_relation.experiment
            
            if(exp.document):
                singleExp.append(exp.document.dcic_alias)
                appendDocument(exp.document.pk, dcicExcelSheet,finalizeOnly)
            else:
                singleExp.append("")
            
            
            if(exp.references):
                singleExp.append(exp.references.dcic_alias)
                appendPublication(exp.references.pk, dcicExcelSheet,finalizeOnly)
            else:
                singleExp.append("")
            
            singleExp.append(exp.dbxrefs)
            appendFilterdcic(dcicExcelSheet,'ExperimentHiC',singleExp)
 #--------------
            
        if str(exp.type) == "CaptureC Exp Protocol":
            singleExp = []
            singleExp.append(exp.dcic_alias)
            singleExp.append(str(exp.experiment_description))
            experiment_set_join= "" 
            replicate_set_join= ""
            if(expSet):
                experiment_set = []
                replicate_set = []
                for eSet in expSet:
                    if(finalizeOnly):
                        update_dcic(eSet)
                    ExpSet = []
                    ExpSet.append(eSet.dcic_alias)
                    ExpSet.append(str(eSet.description))
                    if(eSet.document):
                        ExpSet.append(eSet.document.dcic_alias)
                        appendDocument(eSet.document.pk, dcicExcelSheet,finalizeOnly)
                    else:
                        ExpSet.append("")
                    if("replicates" in str(eSet.experimentSet_type)):
                        appendFilterdcic(dcicExcelSheet,'ExperimentSetReplicate',ExpSet)
                        experiment_set = []
                        replicate_set.append(eSet.dcic_alias)
                    else:
                        ExpSet.insert(2,str(eSet.experimentSet_type))
                        appendFilterdcic(dcicExcelSheet,'ExperimentSet',ExpSet)
                        experiment_set.append(eSet.dcic_alias)
                experiment_set_join= ",".join(experiment_set)    
                replicate_set_join= ",".join(replicate_set)
            
            singleExp.append(replicate_set_join)
            singleExp.append(exp.bio_rep_no) ####*bio_rep_no
            singleExp.append(exp.tec_rep_no) ####*tec_rep_no 
            singleExp.append(experiment_set_join)
            singleExp.append(exp.experiment_biosample.dcic_alias)
            
            expFields=json.loads(exp.experiment_fields)
            
            singleExp.append(expFields["experiment_type"])
            singleExp.append(str(exp.biosample_quantity))
            singleExp.append(str(exp.biosample_quantity_units))
            
            singleExp.append(str(expFields["biotin_removed"]))
            singleExp.append(str(expFields["crosslinking_method"]))
            singleExp.append(str(expFields["crosslinking_temperature"]))
            singleExp.append(str(expFields["crosslinking_time"]))
            
            if(exp.experiment_enzyme):
                singleExp.append(exp.experiment_enzyme.dcic_alias)
                appendEnzyme(exp.experiment_enzyme.pk, dcicExcelSheet,finalizeOnly)
            else:
                singleExp.append("")
                
            singleExp.append(str(expFields["digestion_temperature"]))
            singleExp.append(str(expFields["digestion_time"]))
            singleExp.append(str(expFields["enzyme_lot_number"]))
            singleExp.append(str(expFields["follows_sop"]))
            singleExp.append(str(expFields["average_fragment_size"]))
            singleExp.append(str(expFields["fragment_size_range"]))
            singleExp.append(str(expFields["fragment_size_selection_method"]))
            singleExp.append(str(expFields["fragmentation_method"]))
            singleExp.append(str(expFields["library_preparation_date"]))
            singleExp.append(str(expFields["ligation_temperature"]))
            singleExp.append(str(expFields["ligation_time"]))
            singleExp.append(str(expFields["ligation_volume"]))
            
            if(exp.protocol):
                singleExp.append(exp.protocol.dcic_alias)
                appendProtocol(exp.protocol.pk, dcicExcelSheet, finalizeOnly)
            
            if(exp.variation):
                singleExp.append(exp.variation.dcic_alias)
            else:
                singleExp.append("") ###protocol_variation
            singleExp.append(expFields["tagging_method"])
            
            if(SeqencingFile.objects.filter(sequencingFile_exp=exp.pk)):
                files = SeqencingFile.objects.filter(sequencingFile_exp=exp.pk)
                if(files.all()):
                    fileList = []
                    for f in files:
                        if(finalizeOnly):
                            update_dcic(f)
                        fileList.append(f.dcic_alias)
                        appendFiles(f.pk,dcicExcelSheet,finalizeOnly)
                    singleExp.append(",".join(fileList))
                else:
                    singleExp.append("")
            else:
                singleExp.append("")

            singleExp.append("")##experiment_relation.relationship_type
            singleExp.append("")##experiment_relation.experiment
            
            if(exp.document):
                singleExp.append(exp.document.dcic_alias)
                appendDocument(exp.document.pk, dcicExcelSheet,finalizeOnly)
            else:
                singleExp.append("")
            
            
            if(exp.references):
                singleExp.append(exp.references.dcic_alias)
                appendPublication(exp.references.pk, dcicExcelSheet,finalizeOnly)
            else:
                singleExp.append("")
            
            singleExp.append(exp.dbxrefs)
            appendFilterdcic(dcicExcelSheet,'ExperimentCaptureC',singleExp)
            
        #   ----------
        elif str(exp.type) == "ATAC-seq Protocol":
            singleExp = []
            singleExp.append(exp.dcic_alias)
            singleExp.append(str(exp.experiment_description))
            experiment_set_join= "" 
            replicate_set_join= ""
            if(expSet):
                experiment_set = []
                replicate_set = []
                for eSet in expSet:
                    if(finalizeOnly):
                        update_dcic(eSet)
                    ExpSet = []
                    ExpSet.append(eSet.dcic_alias)
                    ExpSet.append(str(eSet.description))
                    if(eSet.document):
                        ExpSet.append(eSet.document.dcic_alias)
                        appendDocument(eSet.document.pk, dcicExcelSheet,finalizeOnly)
                    else:
                        ExpSet.append("")
                    if("replicates" in str(eSet.experimentSet_type)):
                        appendFilterdcic(dcicExcelSheet,'ExperimentSetReplicate',ExpSet)
                        experiment_set = []
                        replicate_set.append(eSet.dcic_alias)
                    else:
                        ExpSet.insert(2,str(eSet.experimentSet_type))
                        appendFilterdcic(dcicExcelSheet,'ExperimentSet',ExpSet)
                        experiment_set.append(eSet.dcic_alias)
                experiment_set_join= ",".join(experiment_set)    
                replicate_set_join= ",".join(replicate_set)
            
            singleExp.append(replicate_set_join)
            singleExp.append(exp.bio_rep_no) ####*bio_rep_no
            singleExp.append(exp.tec_rep_no) ####*tec_rep_no 
#             singleExp.append("") ####*bio_rep_no
#             singleExp.append("") ####*tec_rep_no 
            singleExp.append(experiment_set_join)
            singleExp.append(exp.experiment_biosample.dcic_alias)
            
            expFields=json.loads(exp.experiment_fields)
            
            singleExp.append(expFields["experiment_type"])
            
            if(Protocol.objects.filter(protocol_type__choice_name="Authentication document", expAddProto__pk=exp.pk)):
                proto = Protocol.objects.filter(protocol_type__choice_name="Authentication document", expAddProto__pk=exp.pk)
                if(proto.all()):
                    protoList = []
                    for p in proto.all():
                        if(finalizeOnly):
                            update_dcic(p)
                        protoList.append(p.dcic_alias)
                        appendProtocol(p.pk,dcicExcelSheet,finalizeOnly)
                    singleExp.append(",".join(protoList))
                else:
                    singleExp.append("")
            else:
                    singleExp.append("")
            
            
            singleExp.append(str(exp.biosample_quantity))
            singleExp.append(str(exp.biosample_quantity_units))
            
            
            if(str(expFields["enzyme_incubation_time"]) != None):
                singleExp.append(str(expFields["enzyme_incubation_time"]))
            else:
                singleExp.append("")
                
            if(str(expFields["enzyme_lot_number"]) != None):
                singleExp.append(str(expFields["enzyme_lot_number"]))
            else:
                singleExp.append("")
            
            singleExp.append(str(expFields["follows_sop"]))
            
            if(expFields["incubation_temperature"] != None):
                singleExp.append(str(expFields["incubation_temperature"]))
            else:
                singleExp.append("")
            
            if(expFields["library_preparation_date"] != None):
                singleExp.append(str(expFields["library_preparation_date"]))
            else:
                singleExp.append("")
            
            if(expFields["pcr_cycles"] != None):
                singleExp.append(str(expFields["pcr_cycles"]))
            else:
                singleExp.append("")
            singleExp.append(str(expFields["primer_removal_method"]))
            
            if(exp.protocol):
                singleExp.append(exp.protocol.dcic_alias)
                appendProtocol(exp.protocol.pk, dcicExcelSheet, finalizeOnly)
            else:
                singleExp.append("")
            
            if(exp.variation):
                singleExp.append(exp.variation.dcic_alias)
                appendProtocol(exp.variation.pk,dcicExcelSheet,finalizeOnly)
            else:
                singleExp.append("") ###protocol_variation
            
            if(exp.experiment_enzyme):
                singleExp.append(exp.experiment_enzyme.dcic_alias)
                appendEnzyme(exp.experiment_enzyme.pk, dcicExcelSheet,finalizeOnly)
            else:
                singleExp.append("")
                
            
            if(SeqencingFile.objects.filter(sequencingFile_exp=exp.pk)):
                files = SeqencingFile.objects.filter(sequencingFile_exp=exp.pk)
                if(files.all()):
                    fileList = []
                    for f in files:
                        if(finalizeOnly):
                            update_dcic(f)
                        fileList.append(f.dcic_alias)
                        appendFiles(f.pk,dcicExcelSheet,finalizeOnly)
                    singleExp.append(",".join(fileList))
                else:
                    singleExp.append("")
            else:
                singleExp.append("")
                
                
            singleExp.append("")##experiment_relation.relationship_type
            singleExp.append("")##experiment_relation.experiment
            
            if(exp.document):
                singleExp.append(exp.document.dcic_alias)
                appendDocument(exp.document.pk, dcicExcelSheet,finalizeOnly)
            else:
                singleExp.append("")
            
            
            if(exp.references):
                singleExp.append(exp.references.dcic_alias)
                appendPublication(exp.references.pk, dcicExcelSheet,finalizeOnly)
            else:
                singleExp.append("")
            
            singleExp.append(exp.dbxrefs)
            appendFilterdcic(dcicExcelSheet,'ExperimentAtacseq',singleExp)
        # -------
        
            
#             jsonObj = JsonObjField.objects.get(field_name="Hi-C Protocol")
#             jsonFields = orderByNumber(jsonObj.field_set)
#             jsonList = jsonFields.items()
#             orders=list(map(lambda k: (int(k[1]['order'])), jsonList))
# #             
#             print(orders)
            
            
#             
#             for keys in jsonFields:
#                 json_val = expFields[keys]
#                 singleItem.append(json_val)
#             
#             print(singleItem)

#             
#             singleItem.insert(11, "")
#             singleItem.insert(20, "")
#             singleItem.insert(21, "")
#             singleItem.insert(23, "")
#             singleItem.insert(24, "")
#             singleItem.insert(25, "")
#             singleItem.insert(26, "")
#             singleItem.insert(27, "")
  
            
    
#     imageObj = ImageObjects.objects.filter(project = projectId)
#     
#     for img in imageObj:
#         singleItem = []
#         singleItem.append(labName +"Images_" +str(img.imageObjects_name)+"_"+str(img.pk))
#         singleItem.append(str(img.imageObjects_images))
#         dcicExcelSheet['Image'].append(singleItem)
#   
#   print(dcicExcelSheet)
    return(dcicExcelSheet)

def duplicates(lst, item):
    return [i for i, x in enumerate(lst) if x == item]

def removeDup(dcicExcelSheet):
    newdcicExcelSheet = defaultdict(list)
    for key, valueList in dcicExcelSheet.items():
        newValueList = []
        pk = []
        for v in valueList:
            if(v[0] not in pk):
                newValueList .append(v)
                pk.append(v[0])
            else:
                continue
#         pos = dict((x, duplicates(pk, x)) for x in set(pk) if pk.count(x) > 1)    
        newdcicExcelSheet[key] = newValueList
    return(newdcicExcelSheet)
                
                
@login_required 
def exportDCIC(request):
    expPks = request.POST.getlist('dcic')
    if(len(expPks) != 0):
        experiments = Experiment.objects.filter(pk__in=expPks)
    else:
        projectId = request.session['projectId']
        experiments = Experiment.objects.filter(project=projectId)
    if(all(ExperimentSet.objects.filter(experimentSet_exp=exp) for exp in experiments)):
        if(request.session['finalizeOnly']):
            dcicExcelSheet = populateDict(request, experiments)
            for e in experiments:
                e.finalize_dcic_submission=True
                e.save()
            messages.success(request, 'All checked experiments have been marked as DCIC submitted')
            return
        else:
            # Create the HttpResponse object with the appropriate CSV header.
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename=DCIC.xlsx'
            file_path_new = ROOTFOLDER+'/organization/static/siteWide/Metadata_entry_form_V3.xlsx'
            wb = load_workbook(file_path_new)
            
            dcicExcelSheet = populateDict(request, experiments)
            
            dcicExcelSheetOrdered = collections.OrderedDict(dcicExcelSheet)
            
            dcicExcelSheetDedup = removeDup(dcicExcelSheetOrdered)
            
            for key, valueList in dcicExcelSheetDedup.items():
                ws = wb.get_sheet_by_name(key)
                for r in reversed(list(ws.rows)):
                    values = [cell.value for cell in r]
                    if any(values):
                        maxRow=r[0].row+1
                        break
                del valueList[0]
                for v in valueList:
                    for i in range(0,len(v)):
                        ws.cell(row=maxRow, column=i+2).value = v[i]
                    maxRow +=1
            
         
            wb.save(response)
            return response
    else:
        messages.error(request, 'Please add the all experiments into biological/technical replicate experiment set!')
        return HttpResponseRedirect('/detailProject/'+request.session['projectId'])