from django.contrib.auth.decorators import login_required
from _collections import OrderedDict, defaultdict
from organization.models import *
from django.shortcuts import render, redirect, render_to_response,\
    get_object_or_404
    
@login_required 
def importSeqFiles(request,pk):
    template_name = 'importFiles.html'
    excel_file = request.FILES['excel_file']
    excel_file_content=excel_file.read().decode("utf-8")
    lines = excel_file_content.split("\n")
    runDict=OrderedDict()
    context = {}
    count=1
    for line in lines:
        line=line.rstrip("\r")
        v=line.split(",")
        if(v[1]!=""):
            runName=v[1]
        if(v[0]!=""):
            expName=v[0]
        if(len(v)>3 and v[3]!=""):
            md5Sum=v[3]
            runDict[v[2]]=[expName,runName,md5Sum]
            context['md5sum']=True
        else:
            runDict[v[2]]=[expName,runName]
            context['md5sum']=False
        count+=1
    if "File Path" in runDict:
        del runDict["File Path"]
    if " " in runDict:
        del runDict[" "]
    
    runDictSorted=sorted(runDict.items())
    context['runDict'] = runDictSorted
    project=Project.objects.get(pk=pk)
    context['project']=project
    
    return (request, template_name, context)