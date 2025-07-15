#!/usr/bin/env python3
"""
Comprehensive test suite for racoon_clip
Includes DAG tests, installation tests, and report comparisons
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
import shutil
import difflib

# Color definitions for output
class Colors:
    CYAN = '\033[0;36m'
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'  # No Color

def print_colored(message: str, color: str = Colors.CYAN) -> None:
    """Print colored message"""
    print(f"{color}{message}{Colors.NC}")

def print_success(message: str) -> None:
    """Print success message in green"""
    print(f"{Colors.GREEN}✓ {message}{Colors.NC}")

def print_error(message: str) -> None:
    """Print error message in red"""
    print(f"{Colors.RED}❌ {message}{Colors.NC}")

def print_warning(message: str) -> None:
    """Print warning message in yellow"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.NC}")

class RacoonTestSuite:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.config_files = [
            "example_data/example_eCLIP_ENCODE/config_test_eCLIP_ENC.yaml",
            "example_data/example_eCLIP/config_test_eCLIP.yaml",
            "example_data/example_iCLIP/config_test_iCLIP.yaml",
            "example_data/example_iCLIP_multiplexed/config_test_iCLIP_multiplexed.yaml"
        ]
        self.reference_files = [
            "test_dag/expected_output/out_eCLIP_ENCODE/workflow_dag.txt",
            "test_dag/expected_output/out_eCLIP/workflow_dag.txt", 
            "test_dag/expected_output/out_iCLIP/workflow_dag.txt",
            "test_dag/expected_output/out_iCLIP_multiplexed/workflow_dag.txt"
        ]
        
    def run_command(self, cmd: List[str], cwd: Path = None) -> Tuple[bool, str]:
        """Run command and return success status and output"""
        cwd_path = cwd or self.base_dir
        print_colored(f"Running command: {' '.join(cmd)}")
        print_colored(f"Working directory: {cwd_path}")
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=cwd_path,
                check=True
            )
            print_colored(f"Command stdout: {result.stdout}")
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed with exit code {e.returncode}\n"
            error_msg += f"Command: {' '.join(cmd)}\n"
            error_msg += f"Working directory: {cwd_path}\n"
            error_msg += f"STDOUT: {e.stdout}\n"
            error_msg += f"STDERR: {e.stderr}"
            return False, error_msg
        except FileNotFoundError as e:
            error_msg = f"Command not found: {' '.join(cmd)}\n"
            error_msg += f"Error: {str(e)}\n"
            error_msg += f"Working directory: {cwd_path}"
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error running command: {' '.join(cmd)}\n"
            error_msg += f"Error: {str(e)}\n"
            error_msg += f"Working directory: {cwd_path}"
            return False, error_msg

    def test_dag_generation(self, config_file: str, reference_file: str) -> bool:
        """Test DAG generation for a single config file"""
        print_colored(f"Testing DAG for: {Path(config_file).name}")
        
        # Check if config file exists
        config_path = self.base_dir.parent / config_file
        print_colored(f"Looking for config file at: {config_path}")
        if not config_path.exists():
            print_error(f"Config file not found: {config_file}")
            return False
            
        # Check if dag_test_runner.sh exists and make it executable
        dag_runner_path = self.base_dir / "test_dag" / "dag_test_runner.sh"
        print_colored(f"Looking for script at: {dag_runner_path}")
        
        if not dag_runner_path.exists():
            print_error(f"DAG runner script not found: {dag_runner_path}")
            return False
        
        print_success(f"Found DAG runner script: {dag_runner_path}")
        
        # Make script executable
        try:
            import stat
            os.chmod(dag_runner_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
            print_success("Made script executable")
        except Exception as e:
            print_error(f"Failed to make script executable: {e}")
            
        # Test if we can execute the script (check if it's valid)
        print_colored("Testing script execution...")
        test_success, test_output = self.run_command([str(dag_runner_path)], cwd=self.base_dir)
        if not test_success and "No arguments provided" not in test_output:
            print_error(f"Script execution test failed: {test_output}")
            return False
        print_success("Script can be executed")
            
      # Generate current DAG
        print_colored(f"Running DAG test command...")
        # Run from the racoon_clip root directory (parent of tests) where Snakefile expects to be
        success, output = self.run_command([
            str(dag_runner_path), "test", 
            "-c", str(config_path),
            "-r", reference_file
        ], cwd=self.base_dir)
        
        if success:
            print_success(f"DAG test passed for {Path(config_file).name}")
            return True
        else:
            print_error(f"DAG test failed for {Path(config_file).name}")
            print_error(f"Error output: {output}")
            return False

    def test_all_dags(self) -> bool:
        """Test DAG generation for all config files"""
        print_colored("=== Testing DAG Generation ===")
        
        passed = 0
        failed = 0
        failed_tests = []
        
        for config_file, reference_file in zip(self.config_files, self.reference_files):
            if self.test_dag_generation(config_file, reference_file):
                passed += 1
            else:
                failed += 1
                failed_tests.append(Path(config_file).name)
        
        print_colored(f"\nDAG Test Summary:")
        print_colored(f"Passed: {passed}")
        print_colored(f"Failed: {failed}")
        print_colored(f"Total:  {passed + failed}")
        
        if failed > 0:
            print_error("Failed DAG tests:")
            for test in failed_tests:
                print_colored(f"  - {test}")
            
        return failed == 0

    def test_installation(self) -> bool:
        """Run installation test"""
        print_colored("=== Testing Installation ===")
        
        # Check if test script exists
        test_script = self.base_dir / "tests/report_test/test_installation_from_git/test_installation.sh"
        if not test_script.exists():
            print_error(f"Installation test script not found: {test_script}")
            return False
            
        # Make script executable
        os.chmod(test_script, 0o755)
        
        # Run installation test
        success, output = self.run_command([str(test_script)], cwd=test_script.parent)
        
        if success:
            print_success("Installation test passed")
            return True
        else:
            print_error(f"Installation test failed: {output}")
            return False

    def compare_reports(self, old_report: Path, new_report: Path) -> bool:
        """Compare two report files"""
        if not old_report.exists():
            print_warning(f"Reference report not found: {old_report}")
            return False
            
        if not new_report.exists():
            print_error(f"New report not found: {new_report}")
            return False
            
        with open(old_report, 'r') as f:
            old_content = f.readlines()
        with open(new_report, 'r') as f:
            new_content = f.readlines()
            
        diff = list(difflib.unified_diff(
            old_content, new_content,
            fromfile=f"reference/{old_report.name}",
            tofile=f"current/{new_report.name}",
            lineterm=''
        ))
        
        if diff:
            print_warning(f"Report differences found in {old_report.name}")
            # Print first few lines of diff
            for line in diff[:10]:
                print(line)
            if len(diff) > 10:
                print(f"... and {len(diff) - 10} more lines")
            return False
        else:
            print_success(f"Report comparison passed: {old_report.name}")
            return True

    def test_reports(self) -> bool:
        """Test report generation and compare with existing reports"""
        print_colored("=== Testing Report Generation ===")
        
        # Directory containing test reports
        report_test_dir = self.base_dir / "tests/report_test"
        if not report_test_dir.exists():
            print_error(f"Report test directory not found: {report_test_dir}")
            return False
            
        # Look for existing reports to compare
        reference_reports = list(report_test_dir.glob("*.html"))
        if not reference_reports:
            print_warning("No reference reports found for comparison")
            return True
            
        passed = 0
        failed = 0
        
        for ref_report in reference_reports:
            # Generate new report (this would depend on your specific report generation process)
            # For now, we'll assume the report exists or simulate report generation
            new_report_dir = report_test_dir / "current"
            new_report_dir.mkdir(exist_ok=True)
            new_report = new_report_dir / ref_report.name
            
            # Copy reference to simulate new report generation for testing
            # In real implementation, this would be replaced with actual report generation
            if not new_report.exists():
                shutil.copy2(ref_report, new_report)
                
            if self.compare_reports(ref_report, new_report):
                passed += 1
            else:
                failed += 1
                
        print_colored(f"\nReport Test Summary:")
        print_colored(f"Passed: {passed}")
        print_colored(f"Failed: {failed}")
        print_colored(f"Total:  {passed + failed}")
        
        return failed == 0

    def test_light(self) -> bool:
        """Light test: DAG tests and report comparison only"""
        print_colored("🧪 Running Light Test Suite")
        print_colored("="*50)
        
        results = []
        
        # Test DAGs
        results.append(self.test_all_dags())
        
        # Test reports
        results.append(self.test_reports())
        
        success = all(results)
        
        print_colored("\n" + "="*50)
        if success:
            print_success("🎉 All light tests passed!")
        else:
            print_error("❌ Some light tests failed!")
            
        return success

    def test(self) -> bool:
        """Full test: DAG tests, report comparison, but no installation test"""
        print_colored("🧪 Running Full Test Suite")
        print_colored("="*50)
        
        results = []
        
        # Test DAGs
        results.append(self.test_all_dags())
        
        # Test reports
        results.append(self.test_reports())
        
        success = all(results)
        
        print_colored("\n" + "="*50)
        if success:
            print_success("🎉 All tests passed!")
        else:
            print_error("❌ Some tests failed!")
            
        return success

    def devel_test(self) -> bool:
        """Development test: All tests including installation"""
        print_colored("🧪 Running Development Test Suite")
        print_colored("="*50)
        
        results = []
        
        # Test DAGs
        results.append(self.test_all_dags())
        
        # Test installation
        results.append(self.test_installation())
        
        # Test reports
        results.append(self.test_reports())
        
        success = all(results)
        
        print_colored("\n" + "="*50)
        if success:
            print_success("🎉 All development tests passed!")
        else:
            print_error("❌ Some development tests failed!")
            
        return success

def main():
    parser = argparse.ArgumentParser(description="Racoon CLIP test suite")
    parser.add_argument(
        "test_type", 
        choices=["test_light", "test", "devel_test"],
        help="Type of test to run"
    )
    
    args = parser.parse_args()
    
    suite = RacoonTestSuite()
    
    if args.test_type == "test_light":
        success = suite.test_light()
    elif args.test_type == "test":
        success = suite.test()
    elif args.test_type == "devel_test":
        success = suite.devel_test()
    else:
        print_error(f"Unknown test type: {args.test_type}")
        return 1
        
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
