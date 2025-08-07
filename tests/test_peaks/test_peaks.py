import subprocess
import sys
import os
import tempfile
import stat
import shutil
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


def create_absolute_paths_config(config_file, log_file=None):
    """
    Create a version of the config file with absolute paths.
    Returns the path to the temporary config file or None if failed.
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        tests_dir = os.path.dirname(script_dir)  # Go up from test_peaks to tests
        racoon_clip_dir = os.path.dirname(tests_dir)  # Go up from tests to racoon_clip
        
        print(f"Script directory: {script_dir}")
        print(f"Tests directory: {tests_dir}")
        print(f"Racoon_clip directory: {racoon_clip_dir}")
        
        # Generate output filename
        config_basename = os.path.splitext(os.path.basename(config_file))[0]
        abs_config_name = f"{config_basename}_absolute_paths.yaml"
        abs_config_path = os.path.join(os.path.dirname(config_file), abs_config_name)
        
        # If absolute paths config already exists, use it
        if os.path.exists(abs_config_path):
            print(f"Absolute paths config already exists: {abs_config_path}")
            return abs_config_path
            
        print(f"Creating absolute paths config: {abs_config_path}")
        
        if YAML_AVAILABLE:
            # Read config file with PyYAML
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Convert relative paths to absolute paths
            path_keys = ['wdir', 'infiles', 'experiment_group_file', 'barcodes_fasta', 'adapter_file', 'gtf', 'genome_fasta', 'star_index']
            for key in path_keys:
                if key in config_data and config_data[key]:
                    value = config_data[key]
                    if isinstance(value, str) and value.strip() and not os.path.isabs(value):
                        # Handle space-separated file lists
                        if ' ' in value:
                            files = [os.path.join(racoon_clip_dir, f.lstrip('/')) if not os.path.isabs(f) else f for f in value.split()]
                            config_data[key] = ' '.join(files)
                            print(f"Converted {key}: {value} -> {config_data[key]}")
                        else:
                            # Single file
                            abs_path = os.path.join(racoon_clip_dir, value.lstrip('/'))
                            config_data[key] = abs_path
                            print(f"Converted {key}: {value} -> {abs_path}")
            
            # Write the modified config
            with open(abs_config_path, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        else:
            # Fallback: text-based processing
            with open(config_file, 'r') as f:
                lines = f.readlines()
            
            modified_lines = []
            for line in lines:
                modified_line = line
                # Look for common path keys
                for key in ['wdir:', 'infiles:', 'experiment_group_file:', 'barcodes_fasta:', 'adapter_file:', 'gtf:', 'genome_fasta:', 'star_index:']:
                    if line.strip().startswith(key):
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            value = parts[1].strip().strip('"').strip("'")
                            if value and not os.path.isabs(value):
                                abs_path = os.path.join(racoon_clip_dir, value.lstrip('/'))
                                modified_line = f"{parts[0]}: {abs_path}\n"
                                print(f"Converted {key} {value} -> {abs_path}")
                        break
                modified_lines.append(modified_line)
            
            with open(abs_config_path, 'w') as f:
                f.writelines(modified_lines)
        
        # Show differences for debugging
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
    
    # First, create absolute paths version of config file
    abs_config_file = create_absolute_paths_config(config_file, log_file)
    if abs_config_file is None:
        print("Failed to create absolute paths config file")
        return False
    
    # Set up working directory (same dir as the script for temp files)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    working_dir = script_dir
    
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
                    return True
                else:
                    log_and_print("=" * 50, log_f)
                    log_and_print("❌ PEAKS test FAILED: racoon_clip peaks failed", log_f)
                    log_and_print(f"Return code: {return_code}", log_f)
                    return False
        else:
            # Fallback if no log file specified
            process = subprocess.run(cmd, cwd=working_dir)
            if process.returncode == 0:
                print("✅ PEAKS test PASSED: racoon_clip peaks completed successfully")
                return True
            else:
                print("❌ PEAKS test FAILED: racoon_clip peaks failed")
                print(f"Return code: {process.returncode}")
                return False
                
    except FileNotFoundError:
        error_msg = "❌ PEAKS test FAILED: racoon_clip command not found. Make sure racoon_clip is installed and in PATH."
        print(error_msg)
        if log_file:
            with open(log_file, 'a') as log_f:
                log_f.write(error_msg + "\n")
        return False
    except Exception as e:
        error_msg = f"❌ PEAKS test FAILED: Unexpected error: {e}"
        print(error_msg)
        if log_file:
            with open(log_file, 'a') as log_f:
                log_f.write(error_msg + "\n")
        return False


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
    return test_peaks_execution(config_file, log_file)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_peaks.py <config_file> [log_file]")
        sys.exit(1)
    
    config = sys.argv[1]
    log_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = test_peaks(config, log_file)
    sys.exit(0 if success else 1)
