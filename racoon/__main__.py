"""
Entrypoint for racoon

Check out the wiki for a detailed look at customising this file:
https://github.com/beardymcjohnface/Snaketool/wiki/Customising-your-Snaketool
"""

import os
import click

from .util import (
    snake_base,
    get_version,
    default_to_output,
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
        click.option(
            "--output",
            help="Output directory",
            type=click.Path(dir_okay=True, writable=True, readable=True),
            default="racoon.out",
            show_default=True,
        ),
        click.option(
            "-cf", "--configfile", "_configfile", 
            default="config.yaml",
            required=True,
            show_default=False,
            callback=default_to_output,
            help="A config file specifiing all needed parameters. You can obtain a configfile with all default settings with the example-config option. See Manual for specific iCLIP and eCLIP examples. Commandline options will overwrite the corresponding option in the config file. Empthy options will use the default. default: (outputDir)/config.yaml", 
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
            default="racoon.log",
            callback=default_to_output,
            hidden=True,
        ),
        click.argument("snake_args", nargs=-1),
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
    racoon command --help"""
    pass


help_msg_extra = """
\b
CLUSTER EXECUTION:
racoon run ... --profile [profile]
For information on Snakemake profiles see:
https://snakemake.readthedocs.io/en/stable/executing/cli.html#profiles
\b
RUN EXAMPLES:
Required:           racoon run --configfile [file]
Specify threads:    racoon run ... --threads [threads]
Change defaults:    racoon run ... --snake-default="-k --nolock"
Add Snakemake args: racoon run ... --dry-run --keep-going --touch
Specify targets:    racoon run ... all print_targets
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
def run( _configfile, log, output, **kwargs): # _input, output
    """Run racoon"""
    # Config to add or update in configfile
    merge_config = {"output": output, "log": log}

    # run!
    run_snakemake(
        # Full path to Snakefile
        snakefile_path=snake_base(os.path.join("workflow", "Snakefile")),
        configfile=_configfile,
        log=log,
        **kwargs,
        merge_config=merge_config
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


if __name__ == "__main__":
    main()
