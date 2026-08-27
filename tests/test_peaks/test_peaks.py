import subprocess
import sys
import os
import tempfile
import stat
import shutil
from pathlib import Path
from datetime import datetime

# Try to import yaml, fall back to text processing if not available
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("Warning: PyYAML not available, using text-based config processing")


def show_config_differences(original_config, temp_config, log_file=None):
    """
    Show differences between original and converted config files for debugging.
    """
    try:
        with open(original_config, 'r') as f:
            original_content = f.read()
        with open(temp_config, 'r') as f:
            temp_content = f.read()
        
        diff_msg = "\n=== CONFIG FILE CONVERSION ===\n"
        diff_msg += f"Original config: {original_config}\n"
        diff_msg += f"Temp config: {temp_config}\n\n"
        
        if original_content != temp_content:
            diff_msg += "Changes made:\n"
            original_lines = original_content.split('\n')
            temp_lines = temp_content.split('\n')
            
            for i, (orig_line, temp_line) in enumerate(zip(original_lines, temp_lines)):
                if orig_line != temp_line:
                    diff_msg += f"Line {i+1}:\n"
                    diff_msg += f"  Original: {orig_line}\n"
                    diff_msg += f"  Modified: {temp_line}\n"
        else:
            diff_msg += "No changes needed - all paths were already absolute.\n"
        
        diff_msg += "\n" + "=" * 50 + "\n"
        
        print(diff_msg)
        if log_file:
            with open(log_file, 'a') as log_f:
                log_f.write(diff_msg)
    except Exception as e:
        error_msg = f"Error showing config differences: {e}"
        print(error_msg)
        if log_file:
            with open(log_file, 'a') as log_f:
                log_f.write(error_msg + "\n")


def create_absolute_paths_config(config_file, log_file=None, user_cwd=None, verbose=False):
    """
    Create a version of the config file with absolute paths.
    Returns the path to the temporary config file or None if failed.
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        tests_dir = os.path.dirname(script_dir)  # Go up from test_peaks to tests
        racoon_clip_dir = os.path.dirname(tests_dir)  # Go up from tests to racoon_clip
        
        if verbose:
            print(f"Script directory: {script_dir}")
            print(f"Tests directory: {tests_dir}")
            print(f"Racoon_clip directory: {racoon_clip_dir}")
        
        # Generate output filename
        config_basename = os.path.splitext(os.path.basename(config_file))[0]
        abs_config_name = f"{config_basename}_absolute_paths.yaml"
        abs_config_path = os.path.join(os.path.dirname(config_file), abs_config_name)
        
        # Always (re)create the absolute-paths config to avoid using stale files
        # from older runs (e.g. wrong root path typos).
        if verbose:
            print(f"Creating absolute paths config: {abs_config_path}")
        
        if YAML_AVAILABLE:
            # Read config file with PyYAML
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Convert relative paths to absolute paths
            path_keys = ['wdir', 'infiles', 'experiment_group_file', 'barcodes_fasta', 'adapter_file', 'gtf', 'genome_fasta', 'mir_genome_fasta', 'star_index']
            for key in path_keys:
                if key in config_data and config_data[key]:
                    value = config_data[key]
                    if isinstance(value, str) and value.strip() and not os.path.isabs(value):
                        if key == 'wdir' and user_cwd:
                            # For wdir, use user's current directory instead of racoon_clip_dir
                            config_data[key] = os.path.join(user_cwd, value.lstrip('./'))
                            if verbose:
                                print(f"Converted {key}: {value} -> {config_data[key]}")
                        # Handle space-separated file lists
                        elif ' ' in value:
                            files = [os.path.join(racoon_clip_dir, f.lstrip('/')) if not os.path.isabs(f) else f for f in value.split()]
                            config_data[key] = ' '.join(files)
                            if verbose:
                                print(f"Converted {key}: {value} -> {config_data[key]}")
                        else:
                            # Single file / pattern
                            abs_path = os.path.abspath(os.path.join(racoon_clip_dir, value))
                            config_data[key] = abs_path
                            if verbose:
                                print(f"Converted {key}: {value} -> {abs_path}")
            
            # Write the modified config
            with open(abs_config_path, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        else:
            # Fallback: text-based processing
            with open(config_file, 'r') as f:
                lines = f.readlines()

            path_keys = [
                'wdir:',
                'infiles:',
                'experiment_group_file:',
                'barcodes_fasta:',
                'adapter_file:',
                'gtf:',
                'genome_fasta:',
                'mir_genome_fasta:',
                'star_index:',
            ]

            modified_lines = []
            for line in lines:
                modified_line = line
                for key in path_keys:
                    if line.strip().startswith(key):
                        parts = line.split(':', 1)
                        if len(parts) != 2:
                            break

                        value_and_comment = parts[1].rstrip('\n')
                        value_part, comment_sep, comment_part = value_and_comment.partition('#')
                        value_str = value_part.strip()

                        if not value_str:
                            break

                        quote_char = ''
                        if (
                            len(value_str) >= 2
                            and value_str[0] in ('"', "'")
                            and value_str[-1] == value_str[0]
                        ):
                            quote_char = value_str[0]
                            path_value = value_str[1:-1]
                        else:
                            path_value = value_str

                        if key == 'wdir:' and user_cwd and not os.path.isabs(path_value):
                            converted_path_value = os.path.abspath(
                                os.path.join(user_cwd, path_value.lstrip('./'))
                            )
                        else:
                            tokens = path_value.split()
                            converted_tokens = []
                            for token in tokens:
                                if os.path.isabs(token):
                                    converted_tokens.append(token)
                                else:
                                    converted_tokens.append(
                                        os.path.abspath(os.path.join(racoon_clip_dir, token))
                                    )
                            converted_path_value = ' '.join(converted_tokens)

                        if quote_char:
                            converted_value_str = f"{quote_char}{converted_path_value}{quote_char}"
                        else:
                            converted_value_str = converted_path_value

                        comment_suffix = ''
                        if comment_sep:
                            comment_suffix = f" {comment_sep}{comment_part}"

                        modified_line = f"{parts[0]}: {converted_value_str}{comment_suffix}\n"
                        if verbose:
                            print(
                                f"Converted {key} {path_value} -> {converted_path_value}"
                            )
                        break

                modified_lines.append(modified_line)

            with open(abs_config_path, 'w') as f:
                f.writelines(modified_lines)
        
        # Show differences for debugging only when requested
        if verbose:
            show_config_differences(config_file, abs_config_path, log_file)
        
        return abs_config_path
        
    except Exception as e:
        error_msg = f"Error creating absolute paths config: {e}"
        print(error_msg)
        if log_file:
            with open(log_file, 'a') as log_f:
                log_f.write(error_msg + "\n")
        return None


def test_peaks_execution(config_file, log_file=None, extra_args=None):
    """Test if racoon_clip peaks executes without errors."""
    
    # Capture user's current working directory first
    user_cwd = os.getcwd()
    
    # First, create absolute paths version of config file
    abs_config_file = create_absolute_paths_config(config_file, log_file, user_cwd)
    if abs_config_file is None:
        print("Failed to create absolute paths config file")
        return False, None
    
    # Set up working directory (use current working directory for output files)
    working_dir = os.getcwd()
    
    # Create a unique log name for racoon_clip
    racoon_log_name = f"racoon_clip_peaks_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    racoon_log_path = os.path.join(working_dir, racoon_log_name)
    
    # Check if working directory is writable, use temp if not
    if not os.access(working_dir, os.W_OK):
        temp_dir = tempfile.mkdtemp()
        racoon_log_path = os.path.join(temp_dir, racoon_log_name)
        print(f"Warning: Using temp directory for logs: {temp_dir}")
    
    cmd = ["racoon_clip", "peaks", "--cores", "4",
           "--configfile", abs_config_file, 
           "--log", racoon_log_path]
    
    # Add extra arguments if provided
    if extra_args:
        if isinstance(extra_args, str):
            # Split string into list of arguments
            extra_args = extra_args.split()
        cmd.extend(extra_args)
        print(f"DEBUG: Added extra arguments: {extra_args}")
    
    print(f"DEBUG: Using config file for racoon_clip: {abs_config_file}")
    
    def log_and_print(message, log_file_handle=None):
        """Helper function to print and log messages."""
        print(message)
        if log_file_handle:
            log_file_handle.write(message + "\n")
            log_file_handle.flush()
    
    try:
        log_msg = f"Running command: {' '.join(cmd)}"
        log_msg_dir = f"Working directory: {working_dir}"
        if log_file:
            with open(log_file, 'a') as log_f:
                log_and_print(log_msg, log_f)
                log_and_print(log_msg_dir, log_f)
                log_and_print("=" * 50, log_f)
                
                # Run with direct output to terminal, but log test info
                process = subprocess.Popen(cmd, text=True, bufsize=1, universal_newlines=True, 
                                         cwd=working_dir)
                
                # Wait for process to complete
                return_code = process.wait()
                
                # Try to make the racoon_clip log file readable/writable
                try:
                    if os.path.exists(racoon_log_path):
                        os.chmod(racoon_log_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
                except (PermissionError, OSError):
                    pass  # Ignore if we can't change permissions
                
                # Check if run completed successfully
                if return_code == 0:
                    log_and_print("=" * 50, log_f)
                    log_and_print("✅ PEAKS test PASSED: racoon_clip peaks completed successfully", log_f)
                    return True, abs_config_file
                else:
                    log_and_print("=" * 50, log_f)
                    log_and_print("❌ PEAKS test FAILED: racoon_clip peaks failed", log_f)
                    log_and_print(f"Return code: {return_code}", log_f)
                    return False, abs_config_file
        else:
            # Fallback if no log file specified
            process = subprocess.run(cmd, cwd=working_dir)
            if process.returncode == 0:
                print("✅ PEAKS test PASSED: racoon_clip peaks completed successfully")
                return True, abs_config_file
            else:
                print("❌ PEAKS test FAILED: racoon_clip peaks failed")
                print(f"Return code: {process.returncode}")
                return False, abs_config_file
                
    except FileNotFoundError:
        error_msg = "❌ PEAKS test FAILED: racoon_clip command not found. Make sure racoon_clip is installed and in PATH."
        print(error_msg)
        if log_file:
            with open(log_file, 'a') as log_f:
                log_f.write(error_msg + "\n")
        return False, abs_config_file
    except Exception as e:
        error_msg = f"❌ PEAKS test FAILED: Unexpected error: {e}"
        print(error_msg)
        if log_file:
            with open(log_file, 'a') as log_f:
                log_f.write(error_msg + "\n")
        return False, abs_config_file


def write_genome_variant(source_path, output_path, symbol):
    """Copy a FASTA and replace one sequence base with the requested symbol."""
    replaced = False
    with open(source_path) as source, open(output_path, "w") as output:
        for line in source:
            if not replaced and line and not line.startswith(">"):
                for index, base in enumerate(line):
                    if base in "ACGTNacgtn":
                        line = line[:index] + symbol + line[index + 1:]
                        replaced = True
                        break
            output.write(line)

    if not replaced:
        raise ValueError(f"No sequence base was found in {source_path}")


def first_sequence_base(fasta_path):
    with open(fasta_path) as fasta:
        for line in fasta:
            if not line.startswith(">"):
                sequence = line.strip()
                if sequence:
                    return sequence[0]
    raise ValueError(f"No sequence base was found in {fasta_path}")


def read_compatibility_status(status_path):
    status = {}
    with open(status_path) as status_file:
        for line in status_file:
            key, value = line.rstrip("\n").split("\t", 1)
            status[key] = value
    return status


def read_config_value(config_path, key):
    with open(config_path) as config_file:
        for line in config_file:
            if line.strip().startswith(f"{key}:"):
                value = line.split(":", 1)[1].partition("#")[0].strip()
                return value.strip("'\"")
    raise ValueError(f"Missing {key!r} in {config_path}")


def write_case_config(base_config, case_config, replacements):
    with open(base_config) as source, open(case_config, "w") as output:
        for line in source:
            key = line.split(":", 1)[0].strip()
            if key in replacements:
                output.write(f'{key}: "{replacements[key]}"\n')
            else:
                output.write(line)


def run_eclip_iupac_peak_case(base_config, symbol, extra_args=None):
    """Run eCLIP peaks with a U- or Y-containing genome and validate its status."""
    repo_dir = Path(__file__).resolve().parents[2]
    base_config = Path(base_config)
    if not base_config.is_absolute():
        base_config = repo_dir / base_config

    output_names = {
        "U": "out_eCLIP_ENCODE_anno_u",
        "Y": "out_eCLIP_ENCODE_anno_extended",
    }
    output_dir = Path.cwd() / "test" / output_names[symbol]
    output_dir.mkdir(parents=True, exist_ok=True)

    source_genome = repo_dir / read_config_value(base_config, "genome_fasta")
    variant_genome = output_dir / f"test_annotation_chr21_{symbol.lower()}.fa"
    write_genome_variant(source_genome, variant_genome, symbol)
    if first_sequence_base(variant_genome) != symbol:
        return False, f"The generated genome does not contain {symbol}"

    infiles = " ".join(
        str(repo_dir / path) if not os.path.isabs(path) else path
        for path in read_config_value(base_config, "infiles").split()
    )
    replacements = {
        "wdir": output_dir,
        "infiles": infiles,
        "genome_fasta": variant_genome,
    }
    for key in ("gtf", "experiment_group_file"):
        config_path = read_config_value(base_config, key)
        replacements[key] = (
            config_path if os.path.isabs(config_path) else repo_dir / config_path
        )

    case_name = "u" if symbol == "U" else "extended"
    case_config = output_dir / f"config_test_eCLIP_ENCODE_anno_{case_name}.yaml"
    write_case_config(base_config, case_config, replacements)

    success, _ = test_peaks_execution(
        str(case_config),
        extra_args=extra_args,
    )
    if not success:
        return False, f"racoon_clip peaks failed for the {symbol} genome"

    status_path = output_dir / "results/peaks/pureclip_genome_compatibility.txt"
    if not status_path.is_file():
        return False, f"Missing compatibility status for the {symbol} genome"

    status = read_compatibility_status(status_path)
    expected_genome = variant_genome.with_name(
        f"{variant_genome.stem}_no_extended_iupac_u_to_t{variant_genome.suffix}"
    ).resolve()
    if status.get("GenomePath") != str(expected_genome):
        return (
            False,
            f"Expected GenomePath {expected_genome}, got {status.get('GenomePath')}",
        )
    expected_flags = {
        "U": ("false", "true"),
        "Y": ("true", "false"),
    }
    expected_extended, expected_uracil = expected_flags[symbol]
    if status.get("ExtendedIupacToN") != expected_extended:
        return False, f"Incorrect ExtendedIupacToN status for {symbol}"
    if status.get("UracilToT") != expected_uracil:
        return False, f"Incorrect UracilToT status for {symbol}"
    if not expected_genome.is_file():
        return False, f"Listed compatible FASTA does not exist: {expected_genome}"
    expected_first_base = {"U": "T", "Y": "N"}[symbol]
    if first_sequence_base(expected_genome) != expected_first_base:
        return False, f"Incorrect compatible FASTA sequence for {symbol}"

    peak_statuses = list(
        (output_dir / "results/peaks").glob("pureclip_status_*.txt")
    )
    if not peak_statuses:
        return False, f"No PureCLIP peak status was produced for {symbol}"

    return True, str(status_path)

def run_eclip_iupac_peak_cases(base_config, extra_args=None):
    """Run and return the U and Y eCLIP peak-calling integration results."""
    return {
        symbol: run_eclip_iupac_peak_case(base_config, symbol, extra_args)
        for symbol in ("U", "Y")
    }

def cleanup_results_folder(config_file):
    """Delete the results folder specified in the wdir of the absolute config file."""
    try:
        with open(config_file, 'r') as f:
            if YAML_AVAILABLE:
                config_data = yaml.safe_load(f)
                wdir = config_data.get('wdir')
                if wdir and os.path.exists(wdir):
                    shutil.rmtree(wdir)
                    print(f"DEBUG: Deleted results folder: {wdir}")
            else:
                print("DEBUG: YAML not available, skipping cleanup.")
    except Exception as e:
        print(f"WARNING: Could not delete results folder: {e}")


def test_peaks(config_file, log_file=None):
    """Test if racoon_clip peaks executes without errors."""
    
    # Generate log file name if not provided
    if log_file is None:
        log_file = "test_racoon_clip_peaks.log"
    
    # Initialize log file
    with open(log_file, 'w') as log_f:
        log_f.write(f"Peaks test run started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_f.write(f"Config file: {config_file}\n")
        log_f.write("=" * 80 + "\n\n")
    
    test_msg = f"Testing racoon_clip peaks for {config_file}"
    with open(log_file, 'a') as log_f:
        log_f.write(test_msg + "\n")
        log_f.write(f"Log file: {log_file}\n\n")
    
    print(test_msg)
    print(f"Log file: {log_file}")
    
    # Test peaks execution (conversion happens inside test_peaks_execution now)
    success, abs_config_file = test_peaks_execution(config_file, log_file)
    
    # Clean up results folder if success
    if success and abs_config_file:
        cleanup_results_folder(abs_config_file)
    
    return success


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_peaks.py <config_file> [log_file]")
        sys.exit(1)
    
    config = sys.argv[1]
    log_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = test_peaks(config, log_file)
    sys.exit(0 if success else 1)
