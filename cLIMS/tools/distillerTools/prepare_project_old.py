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
    ("drop_sam", True),
    ("drop_readid", True), 
    ("drop_seq", True)
])

pcr_dups_max_mismatch_bp = 0
DEFAULT_BIN_SIZES = [1000000, 200000, 100000, 40000, 20000, 10000, 5000, 1000]
INTERMEDIATES_BASEDIR = "intermediates/"
OUTPUT_BASEDIR = "output/"
SEPARATOR = "__"

################################################################

def get_arguments():
    parser = argparse.ArgumentParser(description="""
    This script generates a project file in yaml format
    for the distiller pipeline.
    The user needs to specify
    i) a folder for fastq files
    ii) a yaml file containing genome indices and chrom sizes.
       See the example in the github repository

    Optional Input:
    i)   A Prefix for the output folder
    ii)  PCR Duplicate threshold
    iii) gnome assembly: hg19, mm10,...

    Fastq Directory Structure:
    libname
     -lane_1
         - file1 file2
     - lane_2
          - file1 file 2
    .......       

    File Naming Convention:
    """)
    parser.add_argument("-f" ,
                        help = """Group of the experiments.
                                  Passing as dictionary.""" ,
                        required = True ,
                        type = str)
    parser.add_argument("-o" ,
                        help = """Output yaml file""" ,
                        required = True ,
                        type = str)
    parser.add_argument("-a" ,
                        help = """Genome Assembly Name.
                                  This must match the name in the yaml file""" ,
                        required = True ,
                        type = str)
    parser.add_argument("-g" ,
                        help = "Genome File" ,
                        required = False ,
                        type = str)
    parser.add_argument("-p" ,
                        help = "Output Prefix" ,
                        required = False ,
                        default  = "",
                        type     = str)
    parser.add_argument('--no-suffix', dest='no_suffix', action='store_true',
                        help = """the genome name is not appended at the end 
                                   of library group or library names""")


    arguments = parser.parse_args()
#     error_message = check_arguments(arguments)
#     if error_message:
#         print("Error in input parameters:\n" + error_message)
#         exit(1)
    return arguments

def get_bins():
    bin_dict = OrderedDict()
    bins_string = False
    if not bins_string:
        bin_dict["resolutions"] = DEFAULT_BIN_SIZES
    else:
        pre_bins = bins_string.split(",")
        bins = [int(this_bin) for this_bin in pre_bins]
        bin_dict["resolutions"] = bins

    bin_dict["balance"] = True
    bin_dict["zoomify"] = True
    return bin_dict

def exportYML(f,o,a,g,p="",no_suffix=False):
    _setup_yaml()
    genome_dict = OrderedDict()
    genome_dict = get_genome(a, g)
    
    if no_suffix:
        print("Not appending genome to library names...")
    
    group_dict = f
    fastq_files = get_input_files(group_dict, assembly_name = a , nosuffix = no_suffix)
    bin_dict = get_bins()
    project_dict = prepare_project_dict(group_dict,fastq_files, genome_dict, bin_dict)
    
    yaml_string=prepare_project_yaml(project_dict)
    return yaml_string
    
    

def get_intermediates():
    intermediates_basedir = False
    if not intermediates_basedir:
        intermediates_basedir = INTERMEDIATES_BASEDIR

    intermediates_dict = OrderedDict()
    intermediates_dict["base_dir"] = intermediates_basedir
    intermediates_dict["dirs"] = OrderedDict( [
        ("downloaded_fastqs", "downloaded_fastqs/"),
        ("fastq_chunks", "fastq_chunks"),
        ("bam_run", "bam/run"),
        ("pairsam_chunk", "pairsam/chunk"),
        ("pairsam_run", "pairsam/run"),
        ("pairsam_library", "pairsam/library")
    ] )
    return intermediates_dict

def get_output():
    output_basedir = False
    if not output_basedir:
        output_basedir = OUTPUT_BASEDIR

    output_dict = OrderedDict()
    output_dict["base_dir"] = output_basedir
    output_dict["dirs"] = OrderedDict([
        ("fastqc", "fastqc/"),
        ("pairs_library", "pairs/library/"),
        ("stats_chunk", "stats/chunk/"),
        ("stats_run", "stats/run/"),
        ("stats_library", "stats/library/"),
        ("stats_library_group", "stats/library_group/"),
        ("coolers_library", "coolers/library/"),
        ("coolers_library_group", "coolers/library_group/"),
        ("zoom_coolers_library", "coolers/library_zoom/"),
        ("zoom_coolers_library_group", "coolers/library_group_zoom/"),
        ("bams_library", "bams/library/")
    ])
    return output_dict

# 
# def get_library_files(folder):
#     library_name = os.path.basename(folder)
#     lanes = [ lane for lane in glob.glob(folder + "/*") if os.path.isdir(lane) ]
#     lanes.sort()
#     if not lanes:
#         return tuple()
#     library_files = OrderedDict()
#     for lane in lanes:
#         lane_files = glob.glob(lane + "/*" + FILE_EXTENSION)
#         lane_files.sort()
#         if len(lane_files) > 2:
#             print("Warning, there are more than two files in the folder:" + \
#                     lane)
#         library_files[os.path.basename(lane)] = lane_files
#     return (library_name, library_files)

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

def prepare_project_dict(group_dict,fastq_files, genome, bin_dict):
    result = OrderedDict({
                "do_fastqc": False, "do_stats": True})

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
            expNameList.append(exp.experiment_name+"__"+genome["assembly"])
        result["input"]["library_groups"][groupName] = [n for n in expNameList]
    result["input"]["library_groups"]["all"] = [f for f in fastq_files]
    result["input"]["genome"] = genome
    result["map"] = MAP_DICT
    result["filter"] = OrderedDict([("pcr_dups_max_mismatch_bp",
                               pcr_dups_max_mismatch_bp)])
    result["bin"] = bin_dict
    result["intermediates"] = get_intermediates()
    result["output"] = get_output()
    return result



def get_genome(assembly_name, genomes_file):
    result = OrderedDict({"assembly": assembly_name})
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

  