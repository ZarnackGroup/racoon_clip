import subprocess
import sys
import os
from pathlib import Path

def generate_dag(config_file, output_file="/home/mek24iv/racoon_devel/racoon_clip/tests/test_dag/expected_output/out_eCLIP_ENCODE/workflow_dag.txt"):
    """Generate DAG from Snakemake workflow and save to file."""
    
    
    cmd = ["racoon_clip", "run", "--cores", "1", "–-dryrun", "--configfile", config_file]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Find the start of the DAG content
        dag_content = result.stdout
        dag_start = dag_content.find("digraph snakemake_dag")
        
        if dag_start != -1:
            dag_content = dag_content[dag_start:]
            dag_end = dag_content.find("}")
            if dag_end != -1:
                dag_content = dag_content[:dag_end + 1]
        else:
            print("Warning: 'digraph snakemake_dag' not found in output")
            
            
        
        # Save DAG to file
        with open(output_file, 'w') as f:
            f.write(dag_content)
        
        print(f"DAG saved to {output_file}")
        return dag_content
        
    except subprocess.CalledProcessError as e:
        print(f"Error generating DAG: {e}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_dag.py <config_file> [output_file]")
        sys.exit(1)
    
    config = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "workflow_dag.txt"
    
    generate_dag(config, output)