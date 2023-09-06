"""
Entrypoint for racoon_clip

Check out the wiki for a detailed look at customising this file:
https://github.com/beardymcjohnface/Snaketool/wiki/Customising-your-Snaketool
"""

import os
import click

from .util import (
    snake_base,
    get_version,
    #default_to_output,
    copy_config,
    run_snakemake,
    OrderedCommands,
    print_citation,
)


def common_options(func):
    """Common command line args
    Define common command line args here, and include them with the @common_options decorator below.
    """
    options = [
        ##########################
        # options for snakemake
        ##########################
        click.option(
            "-cf", "--configfile", "_configfile", 
            default="",
            #required=True,
            show_default=False,
            #callback=default_to_output,
            help="A config file specifing all needed parameters. You can obtain a configfile with all default settings with the example-config option. See Manual for specific iCLIP and eCLIP examples. Commandline options will overwrite the corresponding option in the config file. Empthy options will use the default. default: (outputDir)/config.yaml", 
            type=str, 
        ),
        click.option(
            "--threads", help="Number of threads to use", default=1, show_default=True
        ),
        click.option(
            "--verbose", '-v', is_flag = True, help="Print all commands of the process to console."
        ),
        # click.option(
        #     "--conda-prefix",
        #     default=snake_base(os.path.join("workflow", "conda")),
        #     help="Custom conda env directory",
        #     type=click.Path(),
        #     show_default=False,
        # ),
        click.option(
            "--snake-default",
            multiple=True,
            default=[
                "--rerun-incomplete",
                "--printshellcmds",
                "--nolock",
                "--show-failed-logs",
            ],
            help="Customise Snakemake runtime args",
            show_default=True,
        ),
        click.option(
            "--log",
            default="racoon_clip.log",
            #callback=default_to_output,
            hidden=True,
        ),
        click.argument("snake_args", nargs=-1),

        ##########################
        # all options from config file
        ##########################
        click.option(
            "-wdir", "--working_directory",
            help="Output directory",
            type=click.Path(dir_okay=True, writable=True, readable=True),
            default="./racoon_clip_out",
            show_default=True,
        ),
        click.option(
            "-i", "--infiles",
            help="Input fastq files. Multiple files should be provided in one string separated by a space.",
            default="",
            show_default=False,
            #type = click.STRING()
        ),
        click.option(
            "-s", "--samples",
            help="Names of all samples. Should be provided in one string separated by a space. The sample names should be consistant wit the input file names (without the ending), with the experiment groups file and with the barcode file ",
            default="",
            show_default=False,
            #type = click.STRING()
        ),
        click.option(
            "--experiment-groups",
            help= "Names of sample groups that should be merged. Should be provided in one string separated by a space. Names should correspont to the names in the experiment-group-file. If no experiment groups are specified all samples are merged and respective files are called all.bam and all.bw",          
            default=""
        ),
        click.option(
            "--experiment-group-file",
            help= "A txt file notating the corresponding group for each sample. The format is group space sample per row. Should correspond to --experiment_groups. See user manual for example.",          
            default=""
        ),
        click.option(
            "--seq-format",
            help= "Sequence encoding. Usually -Q33 (default) for Illumnia sequencers and -Q64 for Sanger sequencers.",
            default="-Q33",
            show_default=True,             
        ),
        click.option(
            "-bl", "--barcodeLength", "barcodeLength",
            help= "Total length of barcode (experimental barcode + UMI)",     
            default=0     
        ),
        click.option(
            "-q", "--minBaseQuality", "minBaseQuality",
            help= "Minimum sequencing quality of each base in the barcode or UMI region. Used with quality-filter-barcodes or demultiplex.",
            default=10,
            show_default=True,          
        ),
        click.option(
            "-u1", "--umi1-len",
            help= "Length of the 5' half of the UMI (for split UMIs like used for iCLIP) or total length of UMI (for unsplit UMI like eCLIP).",             
            default=0        
        ),
        click.option(
            "-u2", "--umi2-len",
            help= "Length of the 3' half of the UMI. Only used for split UMIs.",    
            default=0,
            show_default=True,            
        ),
        click.option(
            "-eb", "--experimental-barcode-len",
            help= "Length of the experimental barcode. Defaults to 0 if barcodes were already removed.",     
            default=0,
            show_default=True,        
        ),
        click.option(
            "--encode",
            help= "Wheter data was preprocessed by ENCODE.",   
            type=click.Choice(['False', 'True'], case_sensitive=False),
            default="False",
            show_default=True,        
        ),
        click.option(
            "--encode-umi-length",
            help= "Length of the UMI from ENCODE. Usually 10, or for older data 5.",     
            default=10,
            show_default=True,        
        ),
        click.option(
            "--experiment-type",
            help= "Different experimental approaches (iCLIP, iCLIP2, eCLIP) will use different lengths and positions for barcodes, UMIs, and adaptors. If your experiment used one of the setups, you can use the expereriment_type parameter instead of defining barcoedLength, umi1_len, umi2_len and exp_barcode_len, manually. ",   
            type=click.Choice(['iCLIP', 'iCLIP2', 'eCLIP', 'eCLIP_ENCODE', 'other'], case_sensitive=False),
            default='other',
            show_default=True,  
        ),
        click.option(
            "-b", "--barcodes-fasta",
            help= "Path to a fasta file specifing the barcodes containing both the experimental barcode and the UMI. The UMI nucleotides of the barcode should be specified as N. In the fasta barcodes have to be named after > corresponding to the sample names. Keep in mind that the barcodes in the reads are antisense to the barcodes used in the experiment. See also examples in User Manual.",   
            type=click.Path(dir_okay=True, writable=True, readable=True),
        ),
        click.option(
            "-filt", "--quality-filter-barcodes",
            help= "If no demultiplexing is done, should reads still be filtered for barcode / umi quality.",   
            type=click.Choice(["False", "True"]),
            default="True",
            show_default=True,   
        ),
        click.option(
            "-demux", "--demultiplex",
            help= "Wheter demultiplexing should be done. Remember to provide the barcode_fasta for demultiplexing as well.",   
            type=click.Choice(['False', 'True'], case_sensitive=False),
            default="False",
            show_default=True,   
        ),
        click.option(
            "-mrl", "--min-read-length",
            help= "Minimum read length after barcode and adapter trimming. Shorter reads are discarded.",   
            default= 15,
            show_default=True,   
        ),
        click.option(
            "-af", "--adapter-file",
            help= "Path to a fasta file specifing the used adapters. Defaults to a collection of typically used adpaters.",   
            type=click.Path(dir_okay=True, writable=True, readable=True),
        ),
        click.option(
            "-ac", "--adapter-cycles",
            help= "Number of adapter trimming cycles. For eCLIP data it is sometimes recommend to perform 2 cycles of adapter trimming.",   
            default=1,
            show_default=True,   
        ),
        click.option(
            "-a", "--adapter-trimming",
            help= "Wheter adapters need to be trimmed. Adapter trimming will be performed automatically if demultiplexing of barcode filtering are used.",   
            type=click.Choice(['False', 'True'], case_sensitive=False),
            default="True",
            show_default=True, 
        ), 
        click.option(
            "-gtf", "--gtf",
            help= "Genome annotation as unzipped gtf file.",   
            type=click.Path(dir_okay=True, writable=True, readable=True),
        ),
        click.option(
            "-gf", "--genome-fasta",
            help= "Genome assably as unzipped or bgzipped fasta file.",   
            type=click.Path(dir_okay=True, writable=True, readable=True),
        ),
        click.option(
            "-rl", "--read-length",
            help= "Length of reads.",   
            default=150,
            show_default=True, 
        ),
        click.option(
            "--outFilterMismatchNoverReadLmax", "outFilterMismatchNoverReadLmax",
            help= "Percentage of allowed mismaches during alignment. This parameter is directly passed to STAR (see also STAR documentation.",   
            default=0.04,
            show_default=True, 
        ),
        click.option(
            "--outFilterMismatchNmax", "outFilterMismatchNmax",
            help= "Number of allowed mismaches during alignment. By default the number is very high, so alignemnt relies on outFilterMismatchNoverReadLmax. This parameter is directly passed to STAR (see also STAR documentation.",   
            default=999,
            show_default=True, 
        ),
        click.option(
            "--outFilterMultimapNmax", "outFilterMultimapNmax",
            help= "Number of allowed multimapping during alignment. This parameter is directly passed to STAR (see also STAR documentation.",   
            default=1,
            show_default=True, 
        ),
        click.option(
            "--outReadsUnmapped", "outReadsUnmapped",
            help= "This parameter is directly passed to STAR (see also STAR documentation).",   
            default="Fastx",
            show_default=True, 
        ),
        click.option(
            "--outSJfilterReads", "outSJfilterReads",
            help= "This parameter is directly passed to STAR (see also STAR documentation).",   
            default="Unique",
            show_default=True, 
        ),
        click.option(
            "--moreSTARParameters", "moreSTARParameters",
            help= "Additional parameters, that can be directly  passed to STAR (see also STAR documentation).",   
            default="",
            show_default=True, 
        ),
        click.option(
            "-dedup", "--deduplicate",
            help= "Wheter crosslinks should be deduplicated by UMI. Turn of if reads do not contain UMIs.",   
            type=click.Choice(['False', 'True'], case_sensitive=False),
            default="True",
            show_default=True, 
        ), 


    ]
    for option in reversed(options):
        func = option(func)
    return func


@click.group(
    cls=OrderedCommands, context_settings=dict(help_option_names=["-h", "--help"])
)
@click.version_option(get_version(), "-v", "--version", is_flag=True)
def cli():
    """Snakemake-powered commandline tool to obtain single-nucleotide crosslinks from i/eCLIP data.
    \b
    For more options, run:
    racoon_clip command --help"""
    pass


help_msg_extra = """
\b
CLUSTER EXECUTION:
racoon_clip run ... --profile [profile]
For information on Snakemake profiles see:
https://snakemake.readthedocs.io/en/stable/executing/cli.html#profiles
\b
RUN EXAMPLES:
Required:           racoon_clip run --configfile [file]
Specify threads:    racoon_clip run ... --threads [threads]
Change defaults:    racoon_clip run ... --snake-default="-k --nolock"
Add Snakemake args: racoon_clip run ... --dry-run --keep-going --touch
Specify targets:    racoon_clip run ... all print_targets
Available targets:
    all             Run everything (default)
    print_targets   List available targets
"""

#################
# run command
#################
# runs snakemake 

@click.command(
    epilog=help_msg_extra, # the epilog argument is used to provide additional text that will be displayed after the command's help message. The epilog argument allows you to include any extra information or examples that you want to provide to the user.
    context_settings=dict(
        help_option_names=["-h", "--help"], ignore_unknown_options=True
    ), # The context_settings argument accepts a dictionary with specific keys to define the desired settings.
)

@common_options
def run( _configfile, 
        log, 
        working_directory, 
        infiles,
        samples,
        experiment_groups,
        experiment_group_file,
        seq_format,
        barcodeLength,
        minBaseQuality,
        umi1_len,
        umi2_len,
        experimental_barcode_len,
        encode,
        encode_umi_length,
        experiment_type,
        barcodes_fasta,
        quality_filter_barcodes,
        demultiplex,
        min_read_length,
        adapter_file,
        adapter_cycles,
        adapter_trimming,
        gtf,
        genome_fasta,
        read_length,
        outFilterMismatchNoverReadLmax,
        outFilterMismatchNmax,
        outFilterMultimapNmax,
        outReadsUnmapped,
        outSJfilterReads,
        moreSTARParameters,
        deduplicate,
        **kwargs): 
    
    """Run racoon_clip"""
    # Config to add or update in configfile
    merge_config = {"wdir": working_directory, 
                    "log": log,
                    "snakebase": snake_base("workflow"),
                    "infiles": infiles,
                    "samples": samples,
                    "experiment_groups": experiment_groups,
                    "experiment_group_file": experiment_group_file,
                    "seq_format": seq_format,
                    "barcodeLength": barcodeLength,
                    "minBaseQuality": minBaseQuality,
                    "umi1_len": umi1_len,
                    "umi2_len": umi2_len,
                    "experimental_barcode_len": experimental_barcode_len,
                    "encode": encode,
                    "encode_umi_length": encode_umi_length,
                    "experiment_type": experiment_type,
                    "barcodes_fasta": barcodes_fasta,
                    "quality_filter_barcodes": quality_filter_barcodes,
                    "demultiplex": demultiplex,
                    "min_read_length": min_read_length,
                    "adapter_file": adapter_file,
                    "adapter_cycles": adapter_cycles,
                    "adapter_trimming": adapter_trimming,
                    "gtf": gtf,
                    "genome_fasta": genome_fasta,
                    "read_length": read_length,
                    "outFilterMismatchNoverReadLmax": outFilterMismatchNoverReadLmax,
                    "outFilterMismatchNmax": outFilterMismatchNmax,
                    "outFilterMultimapNmax": outFilterMultimapNmax,
                    "outReadsUnmapped": outReadsUnmapped,
                    "outSJfilterReads": outSJfilterReads,
                    "moreSTARParameters": moreSTARParameters,
                    "deduplicate": deduplicate,
                    }
    default_config = {"wdir": "./racoon_clip_out", 
                    "infiles": "",
                    "experiment_groups": "",
                    "experiment_group_file":"",
                    "seq_format": "-Q33",
                    "barcodeLength": "",
                    "minBaseQuality": 10,
                    "umi1_len": "",
                    "umi2_len": "",
                    "experimental_barcode_len": "",
                    "encode": "False",
                    "encode_umi_length": 10,
                    "experiment_type": "other",
                    "barcodes_fasta": "",
                    "quality_filter_barcodes": True,
                    "demultiplex": False,
                    "adapter_file": snake_base("workflow/params.dir/adapter.fa"),
                    "min_read_length": 15,
                    "adapter_cycles": 1,
                    "adapter_trimming": True,
                    "gtf":"",
                    "genome_fasta": "",
                    "read_length": 150,
                    "outFilterMismatchNoverReadLmax": 0.04,
                    "outFilterMismatchNmax": 999,
                    "outFilterMultimapNmax": 1,
                    "outReadsUnmapped": "Fastx",
                    "outSJfilterReads": "Unique",
                    "moreSTARParameters": "",
                    "deduplicate": True,
                    }
    # Create a new dictionary containing non-default values given by the user
    non_default_config = {key: value for key, value in merge_config.items() if value != default_config.get(key)}


    # run!
    run_snakemake(
        # Full path to Snakefile
        snakefile_path=snake_base(os.path.join("workflow", "Snakefile")),
        user_configfile=_configfile,
        log=log,
        **kwargs,
        merge_config=non_default_config,
        default_config=default_config,
        working_directory=working_directory
    )


@click.command()
@common_options
def example_config(configfile, **kwargs):
    """Copy the system default config file"""
    copy_config(configfile)


@click.command()
def citation(**kwargs):
    """Print the citation(s) for this tool"""
    print_citation()


cli.add_command(run)
cli.add_command(example_config)
cli.add_command(citation)


def main():
    cli()

# refering name of tool to main function
if __name__ == "__main__":
    main()
