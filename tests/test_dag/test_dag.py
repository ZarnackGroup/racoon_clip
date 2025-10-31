import subprocess
import sys
import os
from pathlib import Path


def generate_dag(config_file):
    """Generate current DAG from racoon_clip workflow."""
    
    # Change to parent directory of tests folder
    original_cwd = os.getcwd()
    tests_dir = Path(__file__).parent.parent
    os.chdir(tests_dir.parent)
    
    cmd = ["racoon_clip", "peaks", "--cores", "1", "--dag",
           "--configfile", config_file]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                check=True)
        
        # Check if DAG content is present in output
        if "digraph snakemake_dag" in result.stdout:
            print("✅ DAG test PASSED: DAG generation completed successfully")
            return True
        else:
            print("❌ DAG test FAILED: DAG content does not contain "
                  "expected structure")
            print("=== Output ===")
            print(result.stdout)
            print("=== End Output ===")
            return False
        
    except subprocess.CalledProcessError as e:
        print("❌ DAG test FAILED: Command execution failed")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print("=== STDOUT ===")
            print(e.stdout)
            print("=== End STDOUT ===")
        if e.stderr:
            print("=== STDERR ===")
            print(e.stderr)
            print("=== End STDERR ===")
        return False
    finally:
        # Always restore original directory
        os.chdir(original_cwd)


def test_dag(config_file):
    """Test if DAG generation runs without errors."""
    
    print(f"Testing DAG generation for {config_file}")
    
    if config_file is None:
        print("Error: config_file is required")
        return False
    
    # Generate DAG and return the result directly
    return generate_dag(config_file)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_dag.py <config_file>")
        sys.exit(1)
    
    config = sys.argv[1]
    
    success = test_dag(config)
    sys.exit(0 if success else 1)
