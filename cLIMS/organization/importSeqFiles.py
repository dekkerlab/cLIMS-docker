from django.contrib.auth.decorators import login_required
from _collections import OrderedDict, defaultdict
from organization.models import *
from django.shortcuts import render, redirect, render_to_response,\
    get_object_or_404
from django.contrib import messages
from dryLab.models import *
    
@login_required 
def importSeqFiles(request,prj_pk):
    template_name = 'importFiles.html'
    excel_file = request.FILES['excel_file']
    excel_file_content=excel_file.read().decode("utf-8")
    #Experiment Name,Sequencing Run Name,File Path,Type,md5sum,sha256sum,BackupPath
    lines = excel_file_content.rstrip().split("\n")
    project=Project.objects.get(pk=prj_pk)
    exsisting_files=SeqencingFile.objects.filter(project=project).values_list('sequencingFile_mainPath',flat=True)
    runDict=OrderedDict()
    dupDict=OrderedDict()
    orderList=["Experiment Name","Sequencing Run Name","md5sum","sha256sum","BackupPath"]
    nano=["Experiment Name","Sequencing Run Name","Type","md5sum","sha256sum","BackupPath"]
    context = {}
    rn=lines[1].split(',')[1]
    platform=SequencingRun.objects.get(run_name=rn).run_sequencing_instrument.choice_name
    print(platform)
    md5sum=sha256=ftype=bpath=False
    for line in lines[1:]:
        line=line.rstrip("\r")
        v=line.split(",")
        runName=expName=path=""
        md5Sum=sha256sum=BackupPath=""
        if(v[0]!=""):
            expName=v[0]
        if(v[1]!=""):
            runName=v[1]
        if(v[2]!=""):
            path=v[2]
        
        if(expName!= "" and path!= "" and runName!=""):
            runDict[path]=[expName,runName]
        else:
            messages.error(request,"something is not correct with your input file; check Experiment Name, Run Name and FilePath")
            runDict.clear()
            dupDict.clear()
            break
        
        if(platform=="Nanopore"):
            print("In Nanopore condition")
            ftype=True
            template_name='importNanopore.html'
            orderList=nano
            if(v[3]==""):
                messages.error(request,"Missing Entry in Type column.")
                runDict.clear()
                dupDict.clear()
                break
            else:
                filetype=v[3]
                runDict[path].append(filetype) 


        if(v[4]!=""):
            md5Sum=v[4]
            md5sum=True
        runDict[path].append(md5Sum)           
        if(v[5]!=""):
            sha256sum=v[5]
            sha256=True 
        runDict[path].append(sha256sum)  
        if(v[6]!=""):
            BackupPath=v[6]
            bpath=True
        runDict[path].append(BackupPath)
            
        if(path in exsisting_files):
           dupDict[path]=runDict[path]
           del runDict[path]
    
    if " " in runDict:
        del runDict[" "]
    
    context['md5sum']=md5sum
    context['sha256sum']=sha256
    context['BackupPath']=bpath
    context['ftype']=ftype

    runDictSorted=sorted(runDict.items())
    dupDictSorted=sorted(dupDict.items())
    context['runDict'] = runDictSorted
    context['dupDict'] = dupDictSorted
    context['orderList'] = orderList
    context['project']=project
    
    return (request, template_name, context)