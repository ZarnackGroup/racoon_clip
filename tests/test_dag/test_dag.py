import subprocess
import sys
import os
from pathlib import Path


def generate_dag(config_file):
    """Generate current DAG from racoon_clip workflow."""
    
    # Change to parent directory before running command
    original_cwd = os.getcwd()
    os.chdir("..")
    
    cmd = ["racoon_clip", "run", "--cores", "6", "--dag",
           "--configfile", config_file]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                check=True)
        
        # Find the start of the DAG content
        dag_content = result.stdout
        dag_start = dag_content.find("digraph snakemake_dag")
        
        if dag_start != -1:
            dag_content = dag_content[dag_start:]
            # Find the first closing brace and cut there
            dag_end = dag_content.find("}")
            if dag_end != -1:
                dag_content = dag_content[:dag_end + 1]
        else:
            print("Warning: 'digraph snakemake_dag' not found in output")
        
        return dag_content
        
    except subprocess.CalledProcessError as e:
        print(f"Error generating current DAG: {e}")
        print(f"stderr: {e.stderr}")
        return None
    finally:
        # Always restore original directory
        os.chdir(original_cwd)


def test_dag(config_file):
    """Test if DAG generation runs without errors."""
    
    print(f"Testing DAG generation for {config_file}")
    
    if config_file is None:
        print("Error: config_file is required")
        return False
    
    # Generate DAG and check if it succeeds
    dag_content = generate_dag(config_file)
    
    if dag_content is None:
        print("❌ DAG test FAILED: Could not generate DAG")
        return False
    
    if "digraph snakemake_dag" in dag_content:
        print("✅ DAG test PASSED: DAG generation completed successfully")
        return True
    else:
        print("❌ DAG test FAILED: DAG content does not contain "
              "expected structure")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_dag.py <config_file>")
        sys.exit(1)
    
    config = sys.argv[1]
    
    success = test_dag(config)
    sys.exit(0 if success else 1)
