from cProfile import run
from os import dup
from django.contrib.auth.decorators import login_required
from _collections import OrderedDict, defaultdict
from organization.models import *
from django.shortcuts import render, redirect, render_to_response,\
    get_object_or_404
from django.contrib import messages
from dryLab.models import *
    
@login_required 
def importNanoporeData(request,prj_pk):
    template_name = 'importNanopore.html'
    excel_file = request.FILES['excel_file']
    excel_file_content=excel_file.read().decode("utf-8")
    lines = excel_file_content.rstrip().split("\n")
    project=Project.objects.get(pk=prj_pk)
    exsisting_files=SeqencingFile.objects.filter(project=project).values_list('sequencingFile_mainPath',flat=True)
    runDict=OrderedDict()
    dupDict=OrderedDict()
    orderList=[]
    context = {}
    count=1
    for line in lines:
        line=line.rstrip("\r")
        v=line.split(",")
        print(count,v)
        if(count==1):
            exName=seqRun=filePath=md5sum=sha256=ftype=bpath=False
            runName=expName=path=""

            if("Experiment Name" in v):
                exName=True
                exNameIndx=v.index("Experiment Name")
                orderList.append("Experiment")
            if("Sequencing Run Name" in v):
                seqRun=True
                seqRunIndx=v.index("Sequencing Run Name")
                orderList.append("Run")
            if("File Path" in v):
                filePath=True
                filePathIndx=v.index("File Path")
            if("md5sum" in v):
                md5sum=True
                md5sumIndx=v.index("md5sum")
                orderList.append("md5sum")
            if("sha256sum" in v):
                sha256=True
                sha256Indx=v.index("sha256sum")
                orderList.append("sha256sum")
            if("Type" in v):
                ftype=True
                ftypeIndx=v.index("Type")
                orderList.append("Type")
            if("BackupPath" in v):
                bpath=True
                bpathIndx=v.index("BackupPath")
                orderList.append("BackupPath")
        else:
            if(seqRun==True and v[seqRunIndx]!=""):
                runName=v[seqRunIndx]
            if(exName==True and v[exNameIndx]!=""):
                expName=v[exNameIndx]
            if(filePath==True and v[filePathIndx]!=""):
                path=v[filePathIndx]
            
            if(expName!= "" and path!= ""):
                runDict[v[filePathIndx]]=[expName,runName]
            else:
                messages.error(request,"something is not correct with your input file.")
                runDict.clear()
                dupDict.clear()
                break

            if(md5sum==True and v[md5sumIndx]!=""):
                md5Sum=v[md5sumIndx]
                runDict[v[filePathIndx]].append(md5Sum)
                context['md5sum']=True
            else:
                context['md5sum']=False
                     
            if(sha256==True and v[sha256Indx]!=""):
                sha256sum=v[sha256Indx]
                runDict[v[filePathIndx]].append(sha256sum)
                context['sha256sum']=True
            else:
                context['sha256sum']=False
    
            if(ftype==True and v[ftypeIndx]!=""):
                fType=v[ftypeIndx]
                runDict[v[filePathIndx]].append(fType)
            else:
                messages.error(request,"Nanopore Data requires all entries in Type column.")
                runDict.clear()
                dupDict.clear()
                break

            if(bpath==True and v[bpathIndx]!=""):
                BackupPath=v[bpathIndx]
                runDict[v[filePathIndx]].append(BackupPath)
                context['BackupPath']=True
            else:
                context['BackupPath']=False

            
            if(path in exsisting_files):
               dupDict[path]=runDict[path]
               del runDict[path]
        count+=1
    
    if " " in runDict:
        del runDict[" "]
    print("Run:\n",runDict)
    print("Dup:\n",dupDict)
    print("Ord:\n",orderList)

    runDictSorted=sorted(runDict.items())
    dupDictSorted=sorted(dupDict.items())
    context['runDict'] = runDictSorted
    context['dupDict'] = dupDictSorted
    context['orderList'] = orderList
    context['project']=project
    
    return (request, template_name, context)