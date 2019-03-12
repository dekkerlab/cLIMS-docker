import yaml
import os
import argparse
import datetime
from collections import OrderedDict
import glob
import json
from django.http.response import HttpResponse
from organization.models import Experiment
from dryLab.models import SeqencingFile




###############################################################
FILE_EXTENSION = "gz"

MAP_DICT = OrderedDict([
    ("chunksize", 28000000),
    ("mapping_options", '')
])

fILTERS_DICT = OrderedDict([
    ("no_filter", ''),
    ("mapq_30", '(mapq1>=30) and (mapq2>=30)')
])

max_mismatch_bp = 1
DEFAULT_BIN_SIZES = [1000000,500000,250000,100000,50000,25000,10000,5000,2000,1000]
SEPARATOR = "__"

################################################################


def get_bins():
    bin_dict = OrderedDict()
    
    bins_string = False
    if not bins_string:
        bin_dict["resolutions"] = DEFAULT_BIN_SIZES
    

    bin_dict["balance"] = True
    bin_dict["filters"] = fILTERS_DICT
    return bin_dict

def get_parse():
    parse_dict = OrderedDict()
    parse_dict["make_pairsam"] = False
    parse_dict["drop_seq"] = False
    
    parse_dict["drop_readid"] = True
    parse_dict["keep_unparsed_bams"] = False
    parse_dict["parsing_options"] = "--add-columns mapq"
    return parse_dict
    

def exportYML(f,o,a,g,p="",no_suffix=False):
    _setup_yaml()
    genome_dict = OrderedDict()
    genome_dict = OrderedDict(get_genome(a, g))
    
    if no_suffix:
        print("Not appending genome to library names...")
    
    group_dict = f
    fastq_files = get_input_files(group_dict, assembly_name = a , nosuffix = no_suffix)
    bin_dict = get_bins()
    parse_dict = get_parse()
    project_dict = prepare_project_dict(group_dict,fastq_files, genome_dict, parse_dict, bin_dict)
    
    yaml_string=prepare_project_yaml(project_dict)
    return yaml_string
    
def get_output():
    output_dict = OrderedDict()
    
    output_dict["dirs"] = OrderedDict([
        ("processed_fastqs", "results/processed_fastqs/"),
        ("mapped_parsed_sorted_chunks", "results/mapped_parsed_sorted_chunks"),
        ("fastqc", "results/fastqc/"),
        ("pairs_library", "results/pairs_library"),
        ("coolers_library", "results/coolers_library/"),
        ("coolers_library_group", "results/coolers_library_group/"),
        ("stats_library_group", "results/stats_library_group/")
    ])
    return output_dict

def get_input_files(input_exp_group, assembly_name, nosuffix = False):
    libraries = OrderedDict()
    for groupName, experiments in input_exp_group.items():
        for ePk in experiments:
            exp=Experiment.objects.get(pk=ePk)
            fastqFiles=SeqencingFile.objects.filter(sequencingFile_exp=exp.pk)
            fileList=[]
            for fl in fastqFiles:
                fileList.append(fl.sequencingFile_mainPath)
            libraries[exp.experiment_name]=sorted(fileList)
    
    if nosuffix:
        return libraries
    libraries_appended = OrderedDict()
    for lib_name, value in libraries.items():
       libraries_appended[lib_name + SEPARATOR + assembly_name] = value 
    return libraries_appended

def _setup_yaml():
    """ http://stackoverflow.com/a/8661021
       also
       https://pastebin.com/raw/NpcT6Yc4 """
    represent_dict_order = lambda self, data:\
                              self.represent_mapping('tag:yaml.org,2002:map',
                                 data.items())
    yaml.add_representer(OrderedDict, represent_dict_order)



def prepare_project_yaml(project_dict):
    yaml_string = yaml.dump( project_dict, default_flow_style=False,
                             indent=4, line_break=5)
    return yaml_string

def prepare_project_dict(group_dict,fastq_files, genome, parse_dict, bin_dict):
    result = OrderedDict({})
    
    result["input"] = OrderedDict()
    
    lane_fastq_files = OrderedDict()
    f=[]
    
    for key,vals in fastq_files.items():
        count=1
        lane_fastq_files[key]=OrderedDict()
        for v in vals:
            f.append(v)
            if(len(f)==2):
                lane_fastq_files[key]["lane"+str(count)]=f
                count+=1
                f=[]
            
    result["input"]["raw_reads_paths"] = lane_fastq_files
    result["input"]["library_groups"] = OrderedDict()
    for groupName, experiments in group_dict.items():
        expNameList=[]
        for ePk in experiments:
            exp=Experiment.objects.get(pk=ePk)
            expNameList.append(exp.experiment_name+"__"+genome["assembly_name"])
        result["input"]["library_groups"][groupName] = [n for n in expNameList]
    result["input"]["library_groups"]["all"] = [f for f in fastq_files]
    result["input"]["genome"] = genome
    
    result["do_fastqc"]=False
    
    
    result["map"] = MAP_DICT
    result["parse"] = parse_dict
    result["dedup"] = OrderedDict([("max_mismatch_bp",
                               max_mismatch_bp)])
    
    result["bin"]=bin_dict

    result["output"] = get_output()
    return result



def get_genome(assembly_name, genomes_file):
    result = OrderedDict({"assembly_name": assembly_name})
    genomes = _get_genomes(genomes_file)
    if assembly_name not in genomes.keys():
        print("Error! No assembly with the name ", assembly_name,
              " exists in the genomes file", genomes_file)
        exit(1)
    return OrderedDict({**result, **genomes[assembly_name]})

def _get_genomes(genome_yaml_file):
    if not os.path.isfile(genome_yaml_file):
        exit("Error: Could not find the genome file " + genome_yaml_file)
    with open(genome_yaml_file, 'r') as input_stream:
        try:
            genomes = yaml.load(input_stream)
        except yaml.YAMLError as exc:
            print("There was an error in the yaml file:")
            print(exc)
            exit(1)

    return genomes

  