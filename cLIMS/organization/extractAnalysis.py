'''
Created on Nov 16, 2016

@author: nanda
'''
import re
from organization.models import JsonObjField
import json


def extractHiCAnalysis(fileContent, analysisTypePk):
    searchObj = fileContent.decode("utf-8")
    general = re.search(r'General(.*)Dataset', searchObj, re.I|re.S)
    dataset = re.search(r'Dataset(.*)Alignment Options', searchObj, re.I|re.S)
    alignment = re.search(r'Alignment Options(.*)Iterative Mapping Options', searchObj, re.I|re.S)
    iterative = re.search(r'Iterative Mapping Options(.*)Mapping Statistics', searchObj, re.I|re.S)
    statistics = re.search(r'Mapping Statistics(.*)Hi-C Library Quality Metrics', searchObj, re.I|re.S)
    quality = re.search(r'Hi-C Library Quality Metrics(.*)Hi-C Library Redundancy Metrics', searchObj, re.I|re.S)
    redundancy = re.search(r'Hi-C Library Redundancy Metrics(.*)', searchObj, re.I|re.S)
    
    
    
    time = re.search(r'time\s+(.*?)\n', general.group(1),re.I).group(1)
    cType = re.search(r'cType\s+(.*?)\s', general.group(1),re.I).group(1)
    logDirectory = re.search(r'logDirectory\s+(.*?)\s', general.group(1),re.I).group(1)
    UUID = re.search(r'UUID\s+(.*?)\s', general.group(1),re.I).group(1)
    cMapping = re.search(r'cMapping\s+(.*?)\s', general.group(1),re.I).group(1)
    computeResource = re.search(r'computeResource\s+(.*?)\s', general.group(1),re.I).group(1)
    reduceResources = re.search(r'reduceResources\s+(.*?)\s', general.group(1),re.I).group(1)
    mapResources = re.search(r'mapResources\s+(.*?)\s', general.group(1),re.I).group(1)
    reduceScratchDir = re.search(r'reduceScratchDir\s+(.*?)\s', general.group(1),re.I).group(1)
    mapScratchDir = re.search(r'mapScratchDir\s+(.*?)\s', general.group(1),re.I).group(1)
    mapScratchSize = re.search(r'mapScratchSize\s+(.*?)\s', general.group(1),re.I).group(1)
    nCPU = int(re.search(r'nCPU\s+(.*?)\s', general.group(1),re.I).group(1))
    reduceMemoryNeeded = re.search(r'reduceMemoryNeeded\s+(.*?)\s', general.group(1),re.I).group(1)
    mapMemoryNeeded = re.search(r'mapMemoryNeeded\s+(.*?)\s', general.group(1),re.I).group(1)
    
    jobName = re.search(r'jobName\s+(.*?)\s', dataset.group(1),re.I).group(1)
    flowCell = re.search(r'flowCell\s+(.*?)\s', dataset.group(1),re.I).group(1)
    laneName = re.search(r'laneName\s+(.*?)\s', dataset.group(1),re.I).group(1)
    laneNum = int(re.search(r'laneNum\s+(.*?)\s', dataset.group(1),re.I).group(1))
    side1File = re.search(r'side1File\s+(.*?)\s', dataset.group(1),re.I).group(1)
    side2File = re.search(r'side2File\s+(.*?)\s', dataset.group(1),re.I).group(1)
    readLength = int(re.search(r'readLength\s+(.*?)\s', dataset.group(1),re.I).group(1))
    qvEncoding = re.search(r'qvEncoding\s+(.*?)\s', dataset.group(1),re.I).group(1)
    numReads = int(re.search(r'numReads\s+(.*?)\s', dataset.group(1),re.I).group(1).replace(",", ""))
    
    
    splitSize = int(re.search(r'splitSize\s+(.*?)\s', alignment.group(1),re.I).group(1).replace(",", ""))
    splitSizeMegabyte = re.search(r'splitSizeMegabyte\s+(.*?)\s', alignment.group(1),re.I).group(1)
    aligner = re.search(r'aligner\s+(.*?)\s', alignment.group(1),re.I).group(1)
    alignmentSoftwarePath = re.search(r'alignmentSoftwarePath\s+(.*?)\s', alignment.group(1),re.I).group(1)
    alignmentOptions = re.search(r'alignmentOptions\s+(.*?)\n', alignment.group(1),re.I).group(1)
    side1AlignmentOptions = re.search(r'side1AlignmentOptions\s+(.*?)\s', alignment.group(1),re.I).group(1)
    side2AlignmentOptions = re.search(r'side2AlignmentOptions\s+(.*?)\s', alignment.group(1),re.I).group(1)
    enzyme = re.search(r'enzyme\s+(.*?)\s', alignment.group(1),re.I).group(1)
    restrictionSite = re.search(r'restrictionSite\s+(.*?)\s', alignment.group(1),re.I).group(1)
    restrictionFragmentFile = re.search(r'restrictionFragmentFile\s+(.*?)\s', alignment.group(1),re.I).group(1)
    genome = re.search(r'genome\s+(.*?)\s', alignment.group(1),re.I).group(1)
    genomePath = re.search(r'genomePath\s+(.*?)\s', alignment.group(1),re.I).group(1)
    genomeSize = re.search(r'genomeSize\s+(.*?)\s', alignment.group(1),re.I).group(1)
    
    iterativeMapping = re.search(r'iterativeMapping\s+(.*?)\s', iterative.group(1),re.I).group(1)
    iterativeMappingStart = int(re.search(r'iterativeMappingStart\s+(.*?)\s', iterative.group(1),re.I).group(1).replace(",", ""))
    iterativeMappingEnd = int(re.search(r'iterativeMappingEnd\s+(.*?)\s', iterative.group(1),re.I).group(1).replace(",", ""))
    iterativeMappingStep = int(re.search(r'iterativeMappingStep\s+(.*?)\s', iterative.group(1),re.I).group(1).replace(",", ""))
    
    side1TotalReads = int(re.search(r'side1TotalReads\s+(.*?)\s', statistics.group(1),re.I).group(1).replace(",", ""))
    side1NoMap = int(re.search(r'side1NoMap\s+(.*?)\s', statistics.group(1),re.I).group(1).replace(",", ""))
    side1NoMapPer = float(re.search(r'side1NoMap\s+.*?\t(.*?)\n', statistics.group(1),re.I|re.S).group(1))
    side1MultiMap = int(re.search(r'side1MultiMap\s+(.*?)\s', statistics.group(1),re.I).group(1).replace(",", ""))
    side1MultiMapPer = float(re.search(r'side1MultiMap\s+.*?\t(.*?)\n', statistics.group(1),re.I|re.S).group(1))
    side1UniqueMap = int(re.search(r'side1UniqueMap\s+(.*?)\s', statistics.group(1),re.I).group(1).replace(",", ""))
    side1UniqueMapPer = float(re.search(r'side1UniqueMap\s+.*?\t(.*?)\n', statistics.group(1),re.I|re.S).group(1))
    side2TotalReads = int(re.search(r'side2TotalReads\s+(.*?)\s', statistics.group(1),re.I).group(1).replace(",", ""))
    side2NoMap = int(re.search(r'side2NoMap\s+(.*?)\s', statistics.group(1),re.I).group(1).replace(",", ""))
    side2NoMapPer = float(re.search(r'side2NoMap\s+.*?\t(.*?)\n', statistics.group(1),re.I|re.S).group(1))
    side2MultiMap = int(re.search(r'side2MultiMap\s+(.*?)\s', statistics.group(1),re.I).group(1).replace(",", ""))
    side2MultiMapPer = float(re.search(r'side2MultiMap\s+.*?\t(.*?)\n', statistics.group(1),re.I|re.S).group(1))
    side2UniqueMap = int(re.search(r'side2UniqueMap\s+(.*?)\s', statistics.group(1),re.I).group(1).replace(",", ""))
    side2UniqueMapPer = float(re.search(r'side2UniqueMap\s+.*?\t(.*?)\n', statistics.group(1),re.I|re.S).group(1))
    
    
    totalReads = int(re.search(r'totalReads\s+(.*?)\s', quality.group(1),re.I).group(1).replace(",", ""))
    unMapped = int(re.search(r'unMapped\s+(.*?)\s', quality.group(1),re.I).group(1).replace(",", ""))
    unMappedPer = float(re.search(r'unMapped\s+.*?\t(.*?)\n', quality.group(1),re.I|re.S).group(1))
    singleSided = int(re.search(r'singleSided\s+(.*?)\s', quality.group(1),re.I).group(1).replace(",", ""))
    singleSidedPer = float(re.search(r'singleSided\s+.*?\t(.*?)\n', quality.group(1),re.I|re.S).group(1))
    bothSideMapped = int(re.search(r'bothSideMapped\s+(.*?)\s', quality.group(1),re.I).group(1).replace(",", ""))
    bothSideMappedPer = float(re.search(r'bothSideMapped\s+.*?\t(.*?)\n', quality.group(1),re.I|re.S).group(1).replace(",", ""))
    sameFragment = int(re.search(r'sameFragment\s+(.*?)\s', quality.group(1),re.I).group(1).replace(",", ""))
    sameFragmentPer = float(re.search(r'sameFragment\s+.*?\t(.*?)\n', quality.group(1),re.I|re.S).group(1))
    selfCircle = int(re.search(r'selfCircle\s+(.*?)\s', quality.group(1),re.I).group(1).replace(",", ""))
    selfCirclePer = float(re.search(r'selfCircle\s+.*?\t(.*?)\n', quality.group(1),re.I|re.S).group(1))
    danglingEnd = int(re.search(r'danglingEnd\s+(.*?)\s', quality.group(1),re.I).group(1).replace(",", ""))
    danglingEndPer = float(re.search(r'danglingEnd\s+.*?\t(.*?)\n', quality.group(1),re.I|re.S).group(1))
    bounded = int(re.search(r'bounded\s+(.*?)\s', quality.group(1),re.I).group(1).replace(",", ""))
    boundedPer = float(re.search(r'bounded\s+.*?\t(.*?)\n', quality.group(1),re.I|re.S).group(1))
    internal = int(re.search(r'internal\s+(.*?)\s', quality.group(1),re.I).group(1).replace(",", ""))
    internalPer = float(re.search(r'internal\s+.*?\t(.*?)\n', quality.group(1),re.I|re.S).group(1))
    error = int(re.search(r'error\s+(.*?)\s', quality.group(1),re.I).group(1).replace(",", ""))
    errorPer = float(re.search(r'error\s+.*?\t(.*?)\n', quality.group(1),re.I|re.S).group(1))
    validPair = int(re.search(r'validPair\s+(.*?)\s', quality.group(1),re.I).group(1).replace(",", ""))
    validPairPer = float(re.search(r'validPair\s+.*?\t(.*?)\n', quality.group(1),re.I|re.S).group(1))
    cis = int(re.search(r'cis\s+(.*?)\s', quality.group(1),re.I).group(1).replace(",", ""))
    cisPer = float(re.search(r'cis\s+.*?\t(.*?)\n', quality.group(1),re.I|re.S).group(1))
    trans = int(re.search(r'trans\s+(.*?)\s', quality.group(1),re.I).group(1).replace(",", ""))
    transPer = float(re.search(r'trans\s+.*?\t(.*?)\n', quality.group(1),re.I|re.S).group(1))
    
    
    validPairRed = int(re.search(r'validPair\s+(.*?)\s', redundancy.group(1),re.I).group(1).replace(",", ""))
    validPairRedPer = float(re.search(r'validPair\s+.*?\t(.*?)\n', redundancy.group(1),re.I|re.S).group(1))
    totalMolecules = int(re.search(r'totalMolecules\s+(.*?)\s', redundancy.group(1),re.I).group(1).replace(",", ""))
    totalMoleculesPer = float(re.search(r'totalMolecules\s+.*?\t(.*?)\n', redundancy.group(1),re.I|re.S).group(1))
    redundantInteractions = int(re.search(r'redundantInteractions\s+(.*?)\s', redundancy.group(1),re.I).group(1).replace(",", ""))
    redundantInteractionsPer = float(re.search(r'redundantInteractions\s+.*?\t(.*?)\n', redundancy.group(1),re.I|re.S).group(1))
    nonRedundantInteractions = int(re.search(r'nonRedundantInteractions\s+(.*?)\s', redundancy.group(1),re.I).group(1).replace(",", ""))
    nonRedundantInteractionsPer = float(re.search(r'nonRedundantInteractions\s+.*?\t(.*?)\n', redundancy.group(1),re.I|re.S).group(1))
    percentRedundant = float(re.search(r'percentRedundant\s+(.*?)%', redundancy.group(1),re.I|re.S).group(1))
    
    json_object = JsonObjField.objects.get(pk=analysisTypePk).field_set
    data = {}
    for keys in json_object:
        formVal = eval(keys)
        data[keys] = formVal
    json_data = json.dumps(data)
    return json_data



def extract5CAnalysis(fileContent, analysisTypePk):
    searchObj = fileContent.decode("utf-8")
    general = re.search(r'General(.*)Dataset', searchObj, re.I|re.S)
    dataset = re.search(r'Dataset(.*)Alignment Options', searchObj, re.I|re.S)
    alignment = re.search(r'Alignment Options(.*)Mapping Statistics', searchObj, re.I|re.S)
    statistics = re.search(r'Mapping Statistics(.*)Mapping Artifacts', searchObj, re.I|re.S)
    artifacts = re.search(r'Mapping Artifacts(.*)Advanced', searchObj, re.I|re.S)
    advanced = re.search(r'Advanced(.*)', searchObj, re.I|re.S)
    
    
    time = re.search(r'time\s+(.*?)\n', general.group(1),re.I).group(1)
    cType = re.search(r'cType\s+(.*?)\s', general.group(1),re.I).group(1)
    logDirectory = re.search(r'logDirectory\s+(.*?)\s', general.group(1),re.I).group(1)
    UUID = re.search(r'UUID\s+(.*?)\s', general.group(1),re.I).group(1)
    cMapping = re.search(r'cMapping\s+(.*?)\s', general.group(1),re.I).group(1)
    computeResource = re.search(r'computeResource\s+(.*?)\s', general.group(1),re.I).group(1)
    reduceResources = re.search(r'reduceResources\s+(.*?)\s', general.group(1),re.I).group(1)
    mapResources = re.search(r'mapResources\s+(.*?)\s', general.group(1),re.I).group(1)
    reduceScratchDir = re.search(r'reduceScratchDir\s+(.*?)\s', general.group(1),re.I).group(1)
    mapScratchDir = re.search(r'mapScratchDir\s+(.*?)\s', general.group(1),re.I).group(1)
    mapScratchSize = re.search(r'mapScratchSize\s+(.*?)\s', general.group(1),re.I).group(1)
    nCPU = int(re.search(r'nCPU\s+(.*?)\s', general.group(1),re.I).group(1))
    reduceMemoryNeeded = re.search(r'reduceMemoryNeeded\s+(.*?)\s', general.group(1),re.I).group(1)
    mapMemoryNeeded = re.search(r'mapMemoryNeeded\s+(.*?)\s', general.group(1),re.I).group(1)
    
    jobName = re.search(r'jobName\s+(.*?)\s', dataset.group(1),re.I).group(1)
    flowCell = re.search(r'flowCell\s+(.*?)\s', dataset.group(1),re.I).group(1)
    laneName = re.search(r'laneName\s+(.*?)\s', dataset.group(1),re.I).group(1)
    laneNum = int(re.search(r'laneNum\s+(.*?)\s', dataset.group(1),re.I).group(1))
    side1File = re.search(r'side1File\s+(.*?)\s', dataset.group(1),re.I).group(1)
    side2File = re.search(r'side2File\s+(.*?)\s', dataset.group(1),re.I).group(1)
    readLength = int(re.search(r'readLength\s+(.*?)\s', dataset.group(1),re.I).group(1))
    qvEncoding = re.search(r'qvEncoding\s+(.*?)\s', dataset.group(1),re.I).group(1)
    numReads = int(re.search(r'numReads\s+(.*?)\s', dataset.group(1),re.I).group(1).replace(",", ""))
    
    
    splitSize = int(re.search(r'splitSize\s+(.*?)\s', alignment.group(1),re.I).group(1).replace(",", ""))
    splitSizeMegabyte = re.search(r'splitSizeMegabyte\s+(.*?)\s', alignment.group(1),re.I).group(1)
    aligner = re.search(r'aligner\s+(.*?)\s', alignment.group(1),re.I).group(1)
    alignmentSoftwarePath = re.search(r'alignmentSoftwarePath\s+(.*?)\s', alignment.group(1),re.I).group(1)
    alignmentOptions = re.search(r'alignmentOptions\s+(.*?)\n', alignment.group(1),re.I).group(1)
    side1AlignmentOptions = re.search(r'side1AlignmentOptions\s+(.*?)\s', alignment.group(1),re.I).group(1)
    side2AlignmentOptions = re.search(r'side2AlignmentOptions\s+(.*?)\s', alignment.group(1),re.I).group(1)
    enzyme = re.search(r'enzyme\s+(.*?)\s', alignment.group(1),re.I).group(1)
    restrictionSite = re.search(r'restrictionSite\s+(.*?)\s', alignment.group(1),re.I).group(1)
    restrictionFragmentFile = re.search(r'restrictionFragmentFile\s+(.*?)\s', alignment.group(1),re.I).group(1)
    genome = re.search(r'genome\s+(.*?)\s', alignment.group(1),re.I).group(1)
    genomePath = re.search(r'genomePath\s+(.*?)\s', alignment.group(1),re.I).group(1)
    genomeSize = re.search(r'genomeSize\s+(.*?)\s', alignment.group(1),re.I).group(1)
    
    
    numRawReads = int(re.search(r'numRawReads\s+(.*?)\s', statistics.group(1),re.I).group(1).replace(",", ""))
    side1Mapped = int(re.search(r'side1Mapped\s+(.*?)\s', statistics.group(1),re.I).group(1).replace(",", ""))
    side1MappedPer = float(re.search(r'side1Mapped\s+.*?\t(.*?)\n', statistics.group(1),re.I|re.S).group(1))
    side2Mapped = int(re.search(r'side2Mapped\s+(.*?)\s', statistics.group(1),re.I).group(1).replace(",", ""))
    side2MappedPer = float(re.search(r'side2Mapped\s+.*?\t(.*?)\n', statistics.group(1),re.I|re.S).group(1))
    noSideMapped = int(re.search(r'noSideMapped\s+(.*?)\s', statistics.group(1),re.I).group(1).replace(",", ""))
    noSideMappedPer = float(re.search(r'noSideMapped\s+.*?\t(.*?)\n', statistics.group(1),re.I|re.S).group(1))
    oneSideMapped = int(re.search(r'oneSideMapped\s+(.*?)\s', statistics.group(1),re.I).group(1).replace(",", ""))
    oneSideMappedPer = float(re.search(r'oneSideMapped\s+.*?\t(.*?)\n', statistics.group(1),re.I|re.S).group(1))
    bothSideMapped = int(re.search(r'bothSideMapped\s+(.*?)\s', statistics.group(1),re.I).group(1).replace(",", ""))
    bothSideMappedPer = float(re.search(r'bothSideMapped\s+.*?\t(.*?)\n', statistics.group(1),re.I|re.S).group(1))
    errorPairs = int(re.search(r'errorPairs\s+(.*?)\s', statistics.group(1),re.I).group(1).replace(",", ""))
    errorPairsPer = float(re.search(r'errorPairs\s+.*?\t(.*?)\n', statistics.group(1),re.I|re.S).group(1))
    invalidPairs = int(re.search(r'invalidPairs\s+(.*?)\s', statistics.group(1),re.I).group(1).replace(",", ""))
    invalidPairsPer = float(re.search(r'invalidPairs\s+.*?\t(.*?)\n', statistics.group(1),re.I|re.S).group(1))
    validPairs = int(re.search(r'validPairs\s+(.*?)\s', statistics.group(1),re.I).group(1).replace(",", ""))
    validPairsPer = float(re.search(r'validPairs\s+.*?\t(.*?)\n', statistics.group(1),re.I|re.S).group(1))
    
    
    fHomo = int(re.search(r'fHomo\s+(.*?)\s', artifacts.group(1),re.I).group(1).replace(",", ""))
    fHomoPer = float(re.search(r'fHomo\s+.*?\t(.*?)\n', artifacts.group(1),re.I|re.S).group(1))
    rHomo = int(re.search(r'rHomo\s+(.*?)\s', artifacts.group(1),re.I).group(1).replace(",", ""))
    rHomoPer = float(re.search(r'rHomo\s+.*?\t(.*?)\n', artifacts.group(1),re.I|re.S).group(1))
    
    
    same1 = int(re.search(r'same\|\-\>\.\-\>\s+(.*?)\s', advanced.group(1),re.I).group(1).replace(",", ""))
    same2 = int(re.search(r'same\|\-\>\.\<\-\s+(.*?)\s', advanced.group(1),re.I).group(1).replace(",", ""))
    same3 = int(re.search(r'same\|\<\-\.\-\>\s+(.*?)\s', advanced.group(1),re.I).group(1).replace(",", ""))
    same4 = int(re.search(r'same\|\<\-\.\<\-\s+(.*?)\s', advanced.group(1),re.I).group(1).replace(",", ""))
    
    different1 = int(re.search(r'different\|\-\>\.\-\>\s+(.*?)\s', advanced.group(1),re.I).group(1).replace(",", ""))
    different2 = int(re.search(r'different\|\-\>\.\<\-\s+(.*?)\s', advanced.group(1),re.I).group(1).replace(",", ""))
    different3 = int(re.search(r'different\|\<\-\.\-\>\s+(.*?)\s', advanced.group(1),re.I).group(1).replace(",", ""))
    different4 = int(re.search(r'different\|\<\-\.\<\-\s+(.*?)\s', advanced.group(1),re.I).group(1).replace(",", ""))
    
    
    json_object = JsonObjField.objects.get(pk=analysisTypePk).field_set
    data = {}
    for keys in json_object:
        formVal = eval(keys)
        data[keys] = formVal
    json_data = json.dumps(data)
    return json_data
    