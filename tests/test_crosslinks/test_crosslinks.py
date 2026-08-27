import subprocess
import sys
import os
import tempfile
import stat
import shutil
from datetime import datetime
from pathlib import Path

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
        error_msg = f"Error comparing config files: {e}\n"
        print(error_msg)
        if log_file:
            with open(log_file, 'a') as log_f:
                log_f.write(error_msg)


def test_run_execution(config_file, log_file=None, extra_args=None):
    """Test if racoon_clip crosslinks executes without errors."""
    
    # Change to racoon_clip directory (2 levels up from where script is located)
    current_dir = os.getcwd()
    # Ensure we're starting from the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # From script location, go up 2 levels: tests/test_crosslinks -> tests -> racoon_clip
    racoon_clip_dir = os.path.dirname(os.path.dirname(script_dir))
    
    # Convert config file paths to absolute paths FIRST
    print(f"DEBUG: Original config file: {config_file}")
    print(f"DEBUG: Converting paths to absolute...")
    
    # Create config file with absolute paths
    config_basename = os.path.splitext(os.path.basename(config_file))[0]
    abs_config_name = f"{config_basename}_absolute_paths.yaml"
    abs_config_file = os.path.join(os.path.dirname(config_file), abs_config_name)
    
    try:
        # Read original config
        with open(config_file, 'r') as f:
            if YAML_AVAILABLE:
                config_data = yaml.safe_load(f)
                print("DEBUG: Using YAML mode for conversion")
                
                # Convert paths
                path_keys = ['wdir', 'infiles', 'experiment_group_file', 'barcodes_fasta', 'adapter_file', 'gtf', 'genome_fasta', 'mir_genome_fasta']
                for key in path_keys:
                    if key in config_data and config_data[key]:
                        value = config_data[key]
                        if isinstance(value, str) and value.strip() and not os.path.isabs(value):
                            if key == 'wdir':
                                # For wdir, use user's current directory instead of racoon_clip_dir
                                config_data[key] = os.path.join(current_dir, value.lstrip('./'))
                                print(f"DEBUG: Converted {key}: {value} -> {config_data[key]}")
                            elif ' ' in value:  # Space-separated files
                                files = [os.path.join(racoon_clip_dir, f.lstrip('/')) if not os.path.isabs(f) else f for f in value.split()]
                                config_data[key] = ' '.join(files)
                                print(f"DEBUG: Converted {key}: {value} -> {config_data[key]}")
                            else:  # Single file / pattern
                                # Resolve relative paths against repo root and normalize
                                # so glob patterns like *.fastq still work.
                                abs_path = os.path.abspath(os.path.join(racoon_clip_dir, value))
                                config_data[key] = abs_path
                                print(f"DEBUG: Converted {key}: {value} -> {abs_path}")
                
                # Write converted config
                with open(abs_config_file, 'w') as abs_f:
                    yaml.dump(config_data, abs_f, default_flow_style=False, sort_keys=False)
            else:
                print("DEBUG: Using text mode for conversion")
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
                ]

                converted_lines = []
                for line in lines:
                    new_line = line
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

                            if key == 'wdir:' and not os.path.isabs(path_value):
                                converted_path_value = os.path.abspath(
                                    os.path.join(current_dir, path_value.lstrip('./'))
                                )
                            else:
                                tokens = path_value.split()
                                converted_tokens = []
                                for token in tokens:
                                    if os.path.isabs(token):
                                        converted_tokens.append(token)
                                    else:
                                        converted_tokens.append(
                                            os.path.abspath(
                                                os.path.join(racoon_clip_dir, token)
                                            )
                                        )
                                converted_path_value = ' '.join(converted_tokens)

                            if quote_char:
                                converted_value_str = (
                                    f"{quote_char}{converted_path_value}{quote_char}"
                                )
                            else:
                                converted_value_str = converted_path_value

                            comment_suffix = ''
                            if comment_sep:
                                comment_suffix = f" {comment_sep}{comment_part}"

                            new_line = f"{parts[0]}: {converted_value_str}{comment_suffix}\n"
                            break

                    converted_lines.append(new_line)

                with open(abs_config_file, 'w') as abs_f:
                    abs_f.writelines(converted_lines)
        
        print(f"DEBUG: Created absolute paths config: {abs_config_file}")
        config_file = abs_config_file  # Use the converted config file
        
    except Exception as e:
        print(f"WARNING: Could not convert config paths: {e}")
        print("DEBUG: Using original config file")
    
    # Use current working directory instead of project root
    working_dir = current_dir
    try:
        # Test if we can write to current directory
        test_file = os.path.join(current_dir, "test_write_permission.tmp")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print(f"Using current working directory: {current_dir}")
    except (PermissionError, OSError) as e:
        # Use current directory if we can't write here
        working_dir = current_dir
        print(f"Using current working directory: {current_dir}")
    
    # Create racoon_clip log file in current directory (where we have write access)
    racoon_log_name = f"racoon_clip_{os.path.basename(config_file).replace('.yaml', '').replace('.yml', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Try current directory first, fall back to temp directory if permission denied
    try:
        racoon_log_path = os.path.join(current_dir, racoon_log_name)
        # Test if we can write to current directory
        test_file = os.path.join(current_dir, "test_write_permission.tmp")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
    except (PermissionError, OSError):
        # Use temp directory if current directory is not writable
        temp_dir = tempfile.gettempdir()
        racoon_log_path = os.path.join(temp_dir, racoon_log_name)
        print(f"Warning: Using temp directory for logs: {temp_dir}")
    
    cmd = ["racoon_clip", "crosslinks", "--cores", "4",
           "--configfile", config_file, 
           "--log", racoon_log_path]
    
    # Add extra arguments if provided
    if extra_args:
        if isinstance(extra_args, str):
            # Split string into list of arguments
            extra_args = extra_args.split()
        cmd.extend(extra_args)
        print(f"DEBUG: Added extra arguments: {extra_args}")
    
    print(f"DEBUG: Using config file for racoon_clip: {config_file}")
    
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
                    log_and_print("✅ CROSSLINKS test PASSED: racoon_clip crosslinks completed successfully", log_f)
                    return True, abs_config_file
                else:
                    log_and_print("=" * 50, log_f)
                    log_and_print("❌ CROSSLINKS test FAILED: racoon_clip crosslinks failed", log_f)
                    log_and_print(f"Return code: {return_code}", log_f)
                    return False, abs_config_file
        else:
            # Fallback if no log file specified
            print(log_msg)
            print(log_msg_dir)
            print("=" * 50)
            
            process = subprocess.Popen(cmd, text=True, bufsize=1, universal_newlines=True,
                                     cwd=working_dir)
            return_code = process.wait()
            
            # Try to make the racoon_clip log file readable/writable
            try:
                if os.path.exists(racoon_log_path):
                    os.chmod(racoon_log_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
            except (PermissionError, OSError):
                pass  # Ignore if we can't change permissions
            
            print("=" * 50)
            if return_code == 0:
                print("✅ CROSSLINKS test PASSED: racoon_clip crosslinks completed successfully")
                return True, abs_config_file
            else:
                print("❌ CROSSLINKS test FAILED: racoon_clip crosslinks failed")
                print(f"Return code: {return_code}")
                return False, abs_config_file
        
    except (FileNotFoundError, OSError) as e:
        error_msg = f"❌ CROSSLINKS test FAILED: System error: {e}"
        if log_file:
            with open(log_file, 'a') as log_f:
                log_f.write(error_msg + "\n")
        print(error_msg)
        return False, abs_config_file



def read_config_value(config_path, key):
    with open(config_path) as config_file:
        for line in config_file:
            if line.strip().startswith(f"{key}:"):
                value = line.split(":", 1)[1].partition("#")[0].strip()
                return value.strip("'\"")
    raise ValueError(f"Missing {key!r} in {config_path}")


def run_eclip_no_gtf_crosslink_case(config_file, extra_args=None):
    """Run eCLIP crosslink calling without a GTF and verify STAR outputs."""
    repo_dir = Path(__file__).resolve().parents[2]
    config_path = Path(config_file)
    if not config_path.is_absolute():
        config_path = repo_dir / config_path

    if read_config_value(config_path, "gtf"):
        return False, "The no-GTF test config contains a GTF path"

    success, _ = test_run_execution(str(config_path), extra_args=extra_args)
    if not success:
        return False, "racoon_clip crosslinks failed without a GTF"

    output_dir = Path(read_config_value(config_path, "wdir"))
    if not output_dir.is_absolute():
        output_dir = Path.cwd() / str(output_dir).removeprefix("./")

    missing_alignments = [
        sample
        for sample in read_config_value(config_path, "samples").split()
        if not (
            output_dir
            / "results"
            / "aligned"
            / f"{sample}.Aligned.sortedByCoord.out.bam"
        ).is_file()
    ]
    if missing_alignments:
        return False, f"Missing STAR alignment output for: {', '.join(missing_alignments)}"

    return True, str(output_dir)


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


def test_run(config_file, log_file=None):
    """Test if racoon_clip crosslinks executes without errors."""
    
    # Generate log file name if not provided
    if log_file is None:
        log_file = "test_racoon_clip_crosslinks.log"
    
    # Initialize log file
    with open(log_file, 'w') as log_f:
        log_f.write(f"Crosslinks test run started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_f.write(f"Config file: {config_file}\n")
        log_f.write("=" * 80 + "\n\n")
    
    test_msg = f"Testing racoon_clip crosslinks for {config_file}"
    with open(log_file, 'a') as log_f:
        log_f.write(test_msg + "\n")
        log_f.write(f"Log file: {log_file}\n\n")
    
    print(test_msg)
    print(f"Log file: {log_file}")
    
    # Test crosslinks execution (conversion happens inside test_run_execution now)
    success, abs_config_file = test_run_execution(config_file, log_file)
    
    # Cleanup results folder if test was successful
    if success and abs_config_file:
        cleanup_results_folder(abs_config_file)
    
    return success


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_crosslinks.py <config_file> [log_file]")
        sys.exit(1)
    
    config = sys.argv[1]
    log_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = test_run(config, log_file)
    sys.exit(0 if success else 1)
