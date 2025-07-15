import subprocess
import sys
import os
from pathlib import Path
import difflib

def generate_current_dag(config_file):
    print("Generate current DAG from racoon_clip workflow.")
    
    if config_file and os.path.exists(config_file):
        cmd = ["racoon_clip", "run", "--cores", "1", "--configfile", config_file, "–dry-run –quiet"]
        print(f"Running command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Find the start of the DAG content
            dag_content = result.stdout
            print(dag_content)
            dag_start = dag_content.find("digraph snakemake_dag")
            
            if dag_start != -1:
                dag_content = dag_content[dag_start:]
                # Find the first closing brace and cut there
                dag_end = dag_content.find("}")
                if dag_end != -1:
                    dag_content = dag_content[:dag_end + 1]
                    print("DAG content generated successfully")
                    return dag_content
                else:
                    print("Warning: Closing brace not found in DAG content")
                    return dag_content  # Return what we have
            else:
                print("Warning: 'digraph snakemake_dag' not found in output")
                return None
            
        except subprocess.CalledProcessError as e:
            print(f"Error generating current DAG: {e}")
            print(f"stderr: {e.stderr}")
            return None
    else:
        print("Error: config_file (", config_file, ") is empty or does not exist")
        return None

def load_reference_dag(reference_file):
    """Load reference DAG from file."""
    try:
        with open(reference_file, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Reference DAG file {reference_file} not found!")
        return None

def compare_dags(current_dag, reference_dag, show_diff=True):
    """Compare current DAG with reference DAG."""
    
    current_lines = current_dag.splitlines(keepends=True)
    reference_lines = reference_dag.splitlines(keepends=True)
    
    if current_dag.strip() == reference_dag.strip():
        print("✅ DAG test PASSED: DAG structure is unchanged")
        return True
    else:
        print("❌ DAG test FAILED: DAG structure has changed")
        
        if show_diff:
            print("\nDifferences found:")
            print("=" * 50)
            diff = difflib.unified_diff(
                reference_lines, 
                current_lines,
                fromfile='reference_dag',
                tofile='current_dag',
                lineterm=''
            )
            for line in diff:
                print(line)
        
        return False

def test_dag(config_file, reference_file, show_diff=True):
    """Test if current DAG matches reference DAG."""
    
    print(f"Testing DAG for {config_file}")
    print(f"Reference file: {reference_file}")
    
    if config_file is None:
        print("Error: config_file is required")
        return False
    
    # Generate current DAG
    current_dag = generate_current_dag(config_file)
    if current_dag is None:
        print("Error: could not generate new DAG")
        return False
    
    # Load reference DAG
    reference_dag = load_reference_dag(reference_file)
    if reference_dag is None:
        print("Error: could not find reference DAG")
        return False
    
    # Compare DAGs
    return compare_dags(current_dag, reference_dag, show_diff)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_dag.py <config_file> [reference_file]")
        sys.exit(1)
    
    config_file = sys.argv[1]
    reference_file = sys.argv[2] 

    
    success = test_dag(config_file, reference_file)
    sys.exit(0 if success else 1)
