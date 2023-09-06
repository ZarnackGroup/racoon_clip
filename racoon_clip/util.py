"""MISC FUNCTIONS
You shouldn't need to tweak these much if at all
"""

import sys
import os
import subprocess
import yaml
import click
import collections.abc
import re
from shutil import copyfile
from time import localtime, strftime


class OrderedCommands(click.Group):
    """
    This class will preserve the order of subcommands, which is useful when printing --help.
    Click's click.Group class has a list_commands method that returns a list of command names associated with the group. 
    By default, this list may not necessarily preserve the order in which the commands were added. 
    The OrderedCommands class overrides this method to ensure that the order of subcommands is preserved.
    ctx is a click.Context object representing the current context of the CLI.
    """

    def list_commands(self, ctx: click.Context):
        return list(self.commands)


""" functions """

def snake_base(rel_path):
    # returns the absolut path to the snakefile, given the current dir and a rel path
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), rel_path)


def get_version():
    with open(snake_base("racoon_clip.VERSION"), "r") as f:
        version = f.readline()
    return version


def echo_click(msg, log=None):
    # this should echo click messages to the standarderr
    click.echo(msg, nl=False, err=True)
    if log:
        with open(log, "a") as l:
            l.write(msg)


def print_citation():
    with open(snake_base("racoon_clip.CITATION"), "r") as f:
        for line in f:
            echo_click(line)


def msg(err_message, log=None):
    # adds timestamp to echo_click error message
    tstamp = strftime("[%Y:%m:%d %H:%M:%S] ", localtime())
    echo_click(tstamp + err_message + "\n", log=log)


def msg_box(splash, errmsg=None, log=None):
    # creates box around error message
    msg("-" * (len(splash) + 4), log=log)
    msg(f"| {splash} |", log=log)
    msg(("-" * (len(splash) + 4)), log=log)
    if errmsg:
        echo_click("\n" + errmsg + "\n", log=log)


# def default_to_output(ctx, param, value):
#     """Callback for --configfile; place value in output directory unless specified"""
#     if param.default == value:
#         return os.path.join(ctx.params["output"], value) # function uses ctx.params["output"] to access the value of an output option
#     return value


def read_config(file):
    with open(file, "r") as stream:
        _config = yaml.safe_load(stream)
    return _config


def recursive_merge_config(prio_config, non_prio_config):
    def _update(d, u):
        for (key, value) in u.items():
            #if isinstance(value, collections.abc.Mapping): # if the value is a dict value
            if key in d:
                    continue
            else:
                d[key] = value
                # d[key] = _update(d.get(key, {}), value)      
                #         if value is not None and value != "":
                #              # makes a new entry in d and fills the value of u
                # elif value is not None and value != "":  # Skip merging None or empty string values
                #     d[key] = value
            # elif value is not None and value != "": # check if value is empthy
            #     d[key] = value
        return d
    return _update(prio_config, non_prio_config)
    


def update_config(u_config=None, merge=None, default_config = None, output_config=None, log=None):
    """Update config with new values"""
    # Load the commandline options
    full_config = merge.copy()
    msg("commandline values", log=log)
    print(full_config)

    msg("default values", log=log)
    print(default_config)

    # Load the custom config if provided and it exists
    if u_config is not None and os.path.exists(u_config):
        # Load the custom config here and merge it with full_config using recursive_merge_config
        custom_config = read_config(u_config)  # Load your custom config from u_config
        custom_config = recursive_merge_config(prio_config=custom_config, non_prio_config=default_config)
    else:
        msg("Custom config file not found. Using default config")
        custom_config = default_config
        print(custom_config)

    # Merge the command line values to the default
    msg("Updating config file with commandline values", log=log)
    final_config = recursive_merge_config(prio_config= full_config, non_prio_config=custom_config)
    print(final_config)



    # Write the merged config to the output file
    write_config(final_config , output_config, log=log)
    # if not os.path.exists(u_config):
    #     msg("Custom config file not found. Using default config")
    #     msg("Updating config file with commandline values", log=log)
    #     full_config=recursive_merge_config(config=full_config, overwrite_config= merge)
    #     write_config(full_config, output_config, log=log)
    # else:
    #     config = read_config(u_config)
    #     msg("Updating config file with commandline values", log=log)
    #     recursive_merge_config(default_config, merge)
    #     recursive_merge_config(config, default_config)
    #     write_config(config, output_config, log=log)


def write_config(_config, file, log=None):
    msg(f"Writing config file to {file}", log=log)
    if os.path.exists(file):
        mode = "w"  # File exists, overwrite
    else:
        mode = "x"  # File doesn't exist, create new
    with open(file, mode) as stream:
        yaml.dump(_config, stream)


def copy_config(
    local_config,
    merge_config=None,
    system_config=snake_base(os.path.join("config", "config.yaml")),
    log=None,
):
    if not os.path.isfile(local_config):
        if len(os.path.dirname(local_config)) > 0:
            os.makedirs(os.path.dirname(local_config), exist_ok=True)
        msg(f"Copying system default config to {local_config}", log=log)

        if merge_config:
            update_config(
                u_config=system_config,
                merge=merge_config,
                output_config=local_config,
                log=log,
            )
        else:
            copyfile(system_config, local_config)
    else:
        msg(
            f"Config file {local_config} already exists. Using existing config file.",
            log=log,
        )


"""RUN A SNAKEFILE"""


def run_snakemake(
    user_configfile=None,
    snakefile_path=None,
    merge_config=None,
    threads=1,
    verbose=False,
    # use_conda=False,
    #conda_prefix=None,
    snake_default=None,
    snake_args=[],
    log=None,
    default_config=None,
    working_directory=None,  # Add the output parameter
):
    """Run a Snakefile"""
    # Make merged config from defaults, userconfig + commandline arguments
    
    name = os.path.splitext(user_configfile)[0]
    ending = "_updated.yaml"
    output_config =  name + ending
    update_config(u_config=user_configfile, merge=merge_config, default_config= default_config, log=log, output_config=output_config)

    snake_command = ["snakemake", "-s", snakefile_path, "--configfile", output_config, "--use-conda --conda-frontend mamba"]


   
    # if using a configfile
    # if configfile:
    #     # copy sys default config if not present
    #     copy_config(configfile, log=log)

    # if merge_config:
    


    # display the runtime configuration
    # snake_config = read_config(configfile)
    # msg_box(
    #     "Runtime config",
    #     errmsg=yaml.dump(snake_config, Dumper=yaml.Dumper),
    #     log=log,
    # )

    # add threads
    if not "--profile" in snake_args:
        snake_command += ["--jobs", threads]

    if verbose:
        snake_command += ["-p"]


    # add snakemake default args
    if snake_default:
        snake_command += snake_default

    # add any additional snakemake commands

    if snake_args:
        # filtered_snake_args = []
        # racoon_keys = [
        #     "-wdir", "--working_directory", 
        #     "-i", "--infiles", 
        #     "-s", "--samples",
        #     "--experiment-groups", 
        #     "--experiment-group-file", 
        #     "--seq-format", 
        #     "-bl" "--barcodeLength",
        #     "-q" "--minBaseQuality", 
        #     "-u1", "--umi1-len",
        #     "-eb", "--experimental-barcode-len",
        #     "--encode",
        #     "--encode-umi-length",
        #     "--experiment-type",
        #     "-b", "--barcodes-fasta",
        #     "-filt", "--quality-filter-barcodes",
        #     "-demux", "--demultiplex",
        #     "-mrl", "--min-read-length",
        #     "-af", "--adapter-file",
        #     "-ac", "--adapter-cycles",
        #     "-a", "--adapter-trimming",
        #     "-gtf", "--gtf",
        #     "-gf", "--genome-fasta",
        #     "-rl", "--read-length",
        #     "--outFilterMismatchNoverReadLmax", "outFilterMismatchNoverReadLmax",
        #     "--outFilterMismatchNmax", "outFilterMismatchNmax",
        #     "--outFilterMultimapNmax", "outFilterMultimapNmax",
        #     "--outReadsUnmapped", "outReadsUnmapped",
        #     "--outSJfilterReads", "outSJfilterReads",
        #     "--moreSTARParameters", "moreSTARParameters",
        #     "-dedup", "--deduplicate"
        # ]

        # skip_next = False  # This flag is used to skip the next element if it's a value for an option

        # for i, arg in enumerate(snake_args):
        #     if skip_next:
        #         skip_next = False
        #         continue  # Skip the value after the option
            
        #     if arg.startswith('-'):
        #         option = arg.lstrip('-')
        #         # Check if the option is not in default_options
        #         if option not in racoon_keys:
        #             filtered_snake_args.append(arg)
        #             # If it's an option, check if the next element is its value
        #             if i + 1 < len(snake_args) and not snake_args[i + 1].startswith('-'):
        #                 skip_next = True  # Skip the next element (the value)
        #     else:
        #         filtered_snake_args.append(arg)

        snake_command += snake_args

    
    # click.echo("snake args:")
    # click.echo(snake_args)

    # click.echo("default_config:")
    # click.echo(racoon_keys)

    # click.echo("Filtered snake_args:")
    # click.echo(filtered_snake_args)


    # Run Snakemake!!!
    snake_command = " ".join(str(s) for s in snake_command)
    msg_box("Snakemake command", errmsg=snake_command, log=log)
    if not subprocess.run(snake_command, shell=True).returncode == 0:
        msg("ERROR: Snakemake failed", log=log)
        sys.exit(1)
    else:
        msg("Snakemake finished successfully", log=log)
    return 0
