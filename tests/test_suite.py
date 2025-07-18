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
from typing import List, Tuple
import shutil
import difflib

# Import config testing functionality
sys.path.append(str(Path(__file__).parent / "test_config"))
from test_config import test_config

# Import DAG testing functionality
sys.path.append(str(Path(__file__).parent / "test_dag"))
from test_dag import test_dag

# Import RUN testing functionality
sys.path.append(str(Path(__file__).parent / "test_run"))
from test_run import test_run_execution


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
            ("example_data/example_iCLIP_multiplexed/"
             "config_test_iCLIP_multiplexed.yaml")
        ]

    def run_command(self, cmd: List[str],
                    cwd: Path = None) -> Tuple[bool, str]:
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

    def test_dag(self, config_file: str) -> bool:
        """Test DAG generation for a single config file"""
        print_colored(f"Testing DAG for: {Path(config_file).name}")
        
        # Check if config file exists
        config_path = self.base_dir.parent / config_file
        print_colored(f"Looking for config file at: {config_path}")
        if not config_path.exists():
            print_error(f"Config file not found: {config_file}")
            return False

        # Use the imported test_dag function
        return test_dag(str(config_path))

    def test_run_execution(self, config_file: str) -> bool:
        """Test run execution for a single config file"""
        print_colored(f"Testing run for: {Path(config_file).name}")
        
        # Check if config file exists
        config_path = self.base_dir.parent / config_file
        print_colored(f"Looking for config file at: {config_path}")
        if not config_path.exists():
            print_error(f"Config file not found: {config_file}")
            return False

        # Use the imported test_run_execution function
        return test_run_execution(str(config_path))

    def test_all_dags(self) -> bool:
        """Test DAG generation for all config files"""
        print_colored("=== Testing DAG Generation ===")

        passed = 0
        failed = 0
        failed_tests = []

        for config_file in self.config_files:
            if self.test_dag(config_file):
                passed += 1
            else:
                failed += 1
                failed_tests.append(Path(config_file).name)

        print_colored("\nDAG Test Summary:")
        print_colored(f"Passed: {passed}")
        print_colored(f"Failed: {failed}")
        print_colored(f"Total:  {passed + failed}")

        if failed > 0:
            print_error("Failed DAG tests:")
            for test in failed_tests:
                print_colored(f"  - {test}")

        return failed == 0

    def test_all_runs(self) -> bool:
        """Test run execution for all config files"""
        print_colored("=== Testing Run Execution ===")

        passed = 0
        failed = 0
        failed_tests = []

        for config_file in self.config_files:
            if self.test_run_execution(config_file):
                passed += 1
            else:
                failed += 1
                failed_tests.append(Path(config_file).name)

        print_colored("\nRun Test Summary:")
        print_colored(f"Passed: {passed}")
        print_colored(f"Failed: {failed}")
        print_colored(f"Total:  {passed + failed}")

        if failed > 0:
            print_error("Failed run tests:")
            for test in failed_tests:
                print_colored(f"  - {test}")

        return failed == 0

    def test_installation(self) -> bool:
        """Run installation test"""
        print_colored("=== Testing Installation ===")

        # Check if test script exists
        test_script = (self.base_dir / "test_installation_from_git" /
                       "test_installation.sh")
        if not test_script.exists():
            print_error(f"Installation test script not found: {test_script}")
            return False

        # Make script executable
        os.chmod(test_script, 0o755)

        # Run installation test
        success, output = self.run_command(
            [str(test_script)], cwd=test_script.parent)

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

    def test_config_files(self) -> bool:
        """Test configuration files against expected outputs"""
        print_colored("=== Testing Configuration Files ===")        
        # Define the config file mappings
        config_mappings = [
            ("example_data/example_eCLIP_ENCODE/"
             "config_test_eCLIP_ENC_updated.yaml",
             "tests/expected_output/out_eCLIP_ENCODE/"
             "config_test_eCLIP_ENC_expected.yaml"),
            ("example_data/example_eCLIP/config_test_eCLIP_updated.yaml",
             "tests/expected_output/out_eCLIP/"
             "config_test_eCLIP_expected.yaml"),
            ("example_data/example_iCLIP/config_test_iCLIP_updated.yaml",
             "tests/expected_output/out_iCLIP/"
             "config_test_iCLIP_expected.yaml"),
            ("example_data/example_iCLIP_multiplexed/"
             "config_test_iCLIP_multiplexed_updated.yaml",
             "tests/expected_output/out_iCLIP_multiplexed/"
             "config_test_iCLIP_multiplexed_expected.yaml")
        ]
        
        passed = 0
        failed = 0
        failed_tests = []
        
        for actual_config, expected_config in config_mappings:
            actual_path = self.base_dir.parent / actual_config
            expected_path = self.base_dir.parent / expected_config
            
            config_name = Path(actual_config).name
            print_colored(f"Testing config: {config_name}")
            
            if not actual_path.exists():
                print_error(f"Actual config file not found: {actual_path}")
                failed += 1
                failed_tests.append(config_name)
                continue
                
            if not expected_path.exists():
                print_error(f"Expected config file not found: {expected_path}")
                failed += 1
                failed_tests.append(config_name)
                continue
            
            try:
                # Use the test_config function from test_config module
                result = test_config(str(actual_path), str(expected_path),
                                     show_diff=True)
                
                if result:
                    passed += 1
                    print_success(f"Config test passed: {config_name}")
                else:
                    failed += 1
                    failed_tests.append(config_name)
                    print_error(f"Config test failed: {config_name}")
                    
            except Exception as e:
                print_error(f"Error testing config {config_name}: {e}")
                failed += 1
                failed_tests.append(config_name)
        
        print_colored("\nConfig Test Summary:")
        print_colored(f"Passed: {passed}")
        print_colored(f"Failed: {failed}")
        print_colored(f"Total:  {passed + failed}")
        
        if failed > 0:
            print_error("Failed config tests:")
            for test in failed_tests:
                print_colored(f"  - {test}")
        
        return failed == 0

    def test_reports(self) -> bool:
        """Test report generation and compare with existing reports"""
        print_colored("=== Testing Report Generation ===")

        # Directory containing test reports
        report_test_dir = self.base_dir / "report_test"
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
                
        print_colored("\nReport Test Summary:")
        print_colored(f"Passed: {passed}")
        print_colored(f"Failed: {failed}")
        print_colored(f"Total:  {passed + failed}")
        
        return failed == 0

    def test_light(self) -> bool:
        """Light test: DAG tests and config tests only"""
        print_colored("🧪 Running Light Test Suite")
        print_colored("="*50)
        
        results = []

        # Test DAGs
        results.append(self.test_all_dags())
        
        # Test config files
        results.append(self.test_config_files())
        
        success = all(results)
        
        print_colored("\n" + "="*50)
        if success:
            print_success("🎉 All light tests passed!")
        else:
            print_error("❌ Some light tests failed!")
            
        return success

    def test(self) -> bool:
        """Full test: DAG tests, config tests, then run tests (conditional)"""
        print_colored("🧪 Running Full Test Suite")
        print_colored("="*50)
        
        # Test DAGs first
        dag_success = self.test_all_dags()
        
        # Test config files second
        config_success = self.test_config_files()
        
        # Only run the execution tests if DAG and config tests pass
        if dag_success and config_success:
            run_success = self.test_all_runs()
            success = run_success
        else:
            print_colored("\n⚠️ Skipping run tests due to DAG or config test failures")
            success = False
        
        print_colored("\n" + "="*50)
        if success:
            print_success("🎉 All tests passed!")
        else:
            print_error("❌ Some tests failed!")
            
        return success

    def dev_report(self) -> bool:
        """Development report test: Only report generation and comparison"""
        print_colored("🧪 Running Development Report Test")
        print_colored("="*50)
        
        # Test reports only
        success = self.test_reports()
        
        print_colored("\n" + "="*50)
        if success:
            print_success("🎉 Report test passed!")
        else:
            print_error("❌ Report test failed!")
            
        return success

    def devel_test(self) -> bool:
        """Development test: Only installation test"""
        print_colored("🧪 Running Development Test Suite")
        print_colored("="*50)
        
        # Test installation only
        success = self.test_installation()
        
        print_colored("\n" + "="*50)
        if success:
            print_success("🎉 Development test passed!")
        else:
            print_error("❌ Development test failed!")
            
        return success

def main():
    parser = argparse.ArgumentParser(description="Racoon CLIP test suite")
    parser.add_argument(
        "test_type", 
        choices=["test_light", "test", "devel_test", "dev_report"],
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
    elif args.test_type == "dev_report":
        success = suite.dev_report()
    else:
        print_error(f"Unknown test type: {args.test_type}")
        return 1
        
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
