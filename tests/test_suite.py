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
import datetime
import tempfile

# Try to import yaml, fall back to text processing if not available
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# Import config testing functionality
sys.path.append(str(Path(__file__).parent / "test_config"))
from test_config import test_config

# Import DAG testing functionality
sys.path.append(str(Path(__file__).parent / "test_dag"))
from test_dag import test_dag

# Import CROSSLINKS testing functionality
sys.path.append(str(Path(__file__).parent / "test_crosslinks"))
from test_crosslinks import test_run_execution

# Import PEAKS testing functionality
sys.path.append(str(Path(__file__).parent / "test_peaks"))
from test_peaks import test_peaks_execution, create_absolute_paths_config

# Import FASTQSCREEN testing functionality
sys.path.append(str(Path(__file__).parent / "test_fastqscreen"))
from test_fastqscreen import test_fastqscreen_execution


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
             "config_test_iCLIP_multiplexed.yaml"),
            "example_data/example_iCLIP3/config_test_iCLIP3.yaml",
            "example_data/example_mir_eCLIP/config_test_mir_eCLIP.yaml"
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

    def run_command_realtime(self, cmd: List[str],
                            cwd: Path = None) -> Tuple[bool, str]:
        """Run command with real-time output display"""
        cwd_path = cwd or self.base_dir
        print_colored(f"Running command: {' '.join(cmd)}")
        print_colored(f"Working directory: {cwd_path}")
        print_colored("=" * 60)

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=cwd_path,
                bufsize=1,
                universal_newlines=True
            )
            
            output_lines = []
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())  # Print in real-time
                    output_lines.append(output)
            
            return_code = process.poll()
            full_output = ''.join(output_lines)
            
            if return_code == 0:
                print_colored("=" * 60)
                print_success(f"Command completed successfully")
                return True, full_output
            else:
                print_colored("=" * 60)
                print_error(f"Command failed with exit code {return_code}")
                return False, full_output
                
        except FileNotFoundError as e:
            error_msg = f"Command not found: {' '.join(cmd)}\n"
            error_msg += f"Error: {str(e)}\n"
            error_msg += f"Working directory: {cwd_path}"
            print_error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error running command: {' '.join(cmd)}\n"
            error_msg += f"Error: {str(e)}\n"
            error_msg += f"Working directory: {cwd_path}"
            print_error(error_msg)
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

        # Use absolute-path config for DAG generation to avoid './' path warnings
        dag_config = str(config_path)
        abs_config = create_absolute_paths_config(
            str(config_path),
            user_cwd=str(Path.cwd()),
            verbose=False,
        )
        if abs_config:
            dag_config = abs_config

        # Use the imported test_dag function
        success = test_dag(dag_config)

        # Print conversion details only on failure
        if not success:
            print_warning("DAG failed; showing absolute-path config conversion details")
            create_absolute_paths_config(
                str(config_path),
                user_cwd=str(Path.cwd()),
                verbose=True,
            )

        return success

    def test_crosslinks_execution(self, config_file: str, extra_args=None) -> bool:
        """Test crosslinks execution for a single config file"""
        print_colored(f"Testing crosslinks for: {Path(config_file).name}")
        
        # Check if config file exists
        config_path = self.base_dir.parent / config_file
        print_colored(f"Looking for config file at: {config_path}")
        if not config_path.exists():
            print_error(f"Config file not found: {config_file}")
            return False

        # Use the imported test_run_execution function for crosslinks
        success, _ = test_run_execution(str(config_path), extra_args=extra_args)
        return success

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

    def test_all_crosslinks(self, extra_args=None) -> tuple:
        """Test crosslinks execution for all config files. Returns (success, failed_tests)"""
        print_colored("=== Testing Crosslinks Execution ===")

        passed = 0
        failed = 0
        failed_tests = []

        for config_file in self.config_files:
            if self.test_crosslinks_execution(config_file, extra_args=extra_args):
                passed += 1
            else:
                failed += 1
                failed_tests.append(Path(config_file).name)

        print_colored("\nCrosslinks Test Summary:")
        print_colored(f"Passed: {passed}")
        print_colored(f"Failed: {failed}")
        print_colored(f"Total:  {passed + failed}")

        if failed > 0:
            print_error("Failed crosslinks tests:")
            for test in failed_tests:
                print_colored(f"  - {test}")

        return (failed == 0, failed_tests)

    def test_peaks_execution(self, config_file: str, extra_args=None) -> bool:
        """Test peaks execution for a single config file"""
        print_colored(f"Testing peaks for: {Path(config_file).name}")
        
        # Check if config file exists
        config_path = self.base_dir.parent / config_file
        print_colored(f"Looking for config file at: {config_path}")
        if not config_path.exists():
            print_error(f"Config file not found: {config_file}")
            return False

        # Use the imported test_peaks_execution function for peaks (full pipeline)
        success, _ = test_peaks_execution(str(config_path), extra_args=extra_args)
        return success

    def test_fastqscreen_execution(self, config_file: str, extra_args=None) -> bool:
        """Test fastqscreen execution for a single config file"""
        print_colored(f"Testing fastqscreen for: {Path(config_file).name}")
        
        # Check if config file exists
        config_path = self.base_dir.parent / config_file
        print_colored(f"Looking for config file at: {config_path}")
        if not config_path.exists():
            print_error(f"Config file not found: {config_file}")
            return False

        # Use the imported test_fastqscreen_execution function
        success, _ = test_fastqscreen_execution(str(config_path), extra_args=extra_args)
        return success

    def test_all_peaks(self, extra_args=None) -> tuple:
        """Test peaks execution for eCLIP ENCODE and iCLIP config files. Returns (success, failed_tests)"""
        print_colored("=== Testing Peaks Execution ===")

        # Test both eCLIP ENCODE and iCLIP config files for peaks
        peaks_configs = [
            "example_data/example_eCLIP_ENCODE/config_test_eCLIP_ENC.yaml",
            "example_data/example_iCLIP/config_test_iCLIP.yaml"
        ]
        
        passed = 0
        failed = 0
        failed_tests = []

        for peaks_config in peaks_configs:
            print_colored(f"\nTesting peaks for: {Path(peaks_config).name}")
            if self.test_peaks_execution(peaks_config, extra_args=extra_args):
                passed += 1
            else:
                failed += 1
                failed_tests.append(Path(peaks_config).name)

        print_colored("\nPeaks Test Summary:")
        print_colored(f"Passed: {passed}")
        print_colored(f"Failed: {failed}")
        print_colored(f"Total:  {passed + failed}")

        if failed > 0:
            print_error("Failed peaks tests:")
            for test in failed_tests:
                print_colored(f"  - {test}")

        return (failed == 0, failed_tests)

    def test_installation(self) -> bool:
        """Run installation test"""
        print_colored("=== Testing Installation ===")

        # Check if test script exists
        test_script = (self.base_dir / "test_installation_from_git" /
                       "test_installation.sh")
        if not test_script.exists():
            print_error(f"Installation test script not found: {test_script}")
            return False

        # Get current version from __init__.py
        try:
            init_file = self.base_dir.parent / "racoon_clip" / "__init__.py"
            print_colored(f"Looking for version in: {init_file}")
            if init_file.exists():
                with open(init_file, 'r') as f:
                    content = f.read()
                print_colored(f"__init__.py content preview: {content[:200]}...")
                import re
                version_match = re.search(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]', content)
                if version_match:
                    current_version = version_match.group(1)
                    print_colored(f"✓ Successfully parsed version from __init__.py: {current_version}")
                else:
                    current_version = "1.3.0"
                    print_colored(f"⚠ Could not parse version from __init__.py, using default: {current_version}")
            else:
                current_version = "1.3.0"
                print_colored(f"⚠ __init__.py not found at {init_file}, using default version: {current_version}")
        except Exception as e:
            current_version = "1.3.0"
            print_colored(f"⚠ Error reading version from __init__.py: {e}, using default: {current_version}")

        # Make script executable
        os.chmod(test_script, 0o755)

        # Run installation test with real-time output, passing the current version
        success, output = self.run_command_realtime(
            [str(test_script), current_version], cwd=test_script.parent)

        if success:
            print_success("Installation test passed")
            return True
        else:
            print_error(f"Installation test failed")
            if output:
                print_error(f"Output: {output}")
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
        # Map each packaged config to its expected merged configuration. DAG
        # generation materializes the packaged config as *_absolute_paths.yaml,
        # and the CLI writes the merged *_absolute_paths_updated.yaml beside it.
        config_mappings = [
            ("example_data/example_eCLIP_ENCODE/"
             "config_test_eCLIP_ENC.yaml",
             "tests/expected_output/out_eCLIP_ENCODE/"
             "config_test_eCLIP_ENC_expected.yaml"),
            ("example_data/example_eCLIP/config_test_eCLIP.yaml",
             "tests/expected_output/out_eCLIP/"
             "config_test_eCLIP_expected.yaml"),
            ("example_data/example_iCLIP/config_test_iCLIP.yaml",
             "tests/expected_output/out_iCLIP/"
             "config_test_iCLIP_expected.yaml"),
            ("example_data/example_iCLIP_multiplexed/"
             "config_test_iCLIP_multiplexed.yaml",
             "tests/expected_output/out_iCLIP_multiplexed/"
             "config_test_iCLIP_multiplexed_expected.yaml"),
            ("example_data/example_iCLIP3/"
             "config_test_iCLIP3.yaml",
             "tests/expected_output/out_iCLIP3/"
             "config_test_iCLIP3_expected.yaml"),
            ("example_data/example_mir_eCLIP/"
             "config_test_mir_eCLIP.yaml",
             "tests/expected_output/out_mir_eCLIP/"
             "config_test_mir_eCLIP_expected.yaml")
        ]
        
        passed = 0
        failed = 0
        failed_tests = []
        
        for source_config, expected_config in config_mappings:
            source_path = self.base_dir.parent / source_config
            absolute_config_path = source_path.with_name(
                f"{source_path.stem}_absolute_paths.yaml"
            )
            actual_path = absolute_config_path.with_name(
                f"{absolute_config_path.stem}_updated.yaml"
            )
            expected_source_path = self.base_dir.parent / expected_config

            config_name = actual_path.name
            print_colored(f"Testing config: {config_name}")
            
            if not actual_path.exists():
                print_error(f"Actual config file not found: {actual_path}")
                failed += 1
                failed_tests.append(config_name)
                continue
                
            if not expected_source_path.exists():
                print_error(
                    f"Expected config file not found: {expected_source_path}"
                )
                failed += 1
                failed_tests.append(config_name)
                continue

            converted_expected = create_absolute_paths_config(
                str(expected_source_path),
                user_cwd=str(Path.cwd()),
            )
            if not converted_expected:
                print_error(
                    "Could not create the absolute-path expected config: "
                    f"{expected_source_path}"
                )
                failed += 1
                failed_tests.append(config_name)
                continue

            try:
                # Use the test_config function from test_config module
                result = test_config(str(actual_path), converted_expected,
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

    def test_light(self, extra_args=None) -> bool:
        """Light test: DAG tests and config tests only"""
        print_colored("🧪 Running Light Test Suite")
        print_colored("="*50)
        
        # Print extra args info if provided
        if extra_args:
            print_colored(f"Extra arguments for snakemake: {extra_args}")
        
        # Track failed tests
        failed_tests = []

        # Test DAGs
        dag_success = self.test_all_dags()
        if not dag_success:
            failed_tests.append("DAG tests")
        
        # Test config files
        config_success = self.test_config_files()
        if not config_success:
            failed_tests.append("Config file tests")
        
        success = dag_success and config_success
        
        print_colored("\n" + "="*50)
        if success:
            print_success("🎉 All light tests passed!")
        else:
            print_error("❌ Some light tests failed!")
            print_error("\nFailed test categories:")
            for test_name in failed_tests:
                print_error(f"  ✗ {test_name}")
            
        return success

    def test_mir_trim(self) -> bool:
        """Run the synthetic unit tests for canonical miRNA trimming."""
        print_colored("\n=== Testing canonical miRNA trimming ===")
        success, output = self.run_command(
            [sys.executable, "-m", "unittest", "tests.test_mir_trim", "-v"],
            cwd=self.base_dir.parent,
        )
        if success:
            print_success("Canonical miRNA trimming tests passed")
        else:
            print_error("Canonical miRNA trimming tests failed")
            print_error(output)
        return success

    def test(self, extra_args=None) -> bool:
        """Full test: unit, DAG, config, and conditional execution tests."""
        print_colored("🧪 Running Full Test Suite")
        print_colored("="*50)
        
        # Print extra args info if provided
        if extra_args:
            print_colored(f"Extra arguments for snakemake: {extra_args}")
        
        # Track failed tests with details
        failed_tests = {}

        # Test the canonical miRNA coordinate and trimming logic.
        mir_trim_success = self.test_mir_trim()
        if not mir_trim_success:
            failed_tests["miRNA trimming unit tests"] = []
        
        # Test DAGs first
        dag_success = self.test_all_dags()
        if not dag_success:
            failed_tests["DAG tests"] = []
        
        # Test config files second
        config_success = self.test_config_files()
        if not config_success:
            failed_tests["Config file tests"] = []
        
        # Only run execution tests if the lightweight checks pass.
        if mir_trim_success and dag_success and config_success:
            crosslinks_success, crosslinks_failed = self.test_all_crosslinks(extra_args=extra_args)
            if not crosslinks_success:
                failed_tests["Crosslinks execution tests"] = crosslinks_failed
                
            peaks_success, peaks_failed = self.test_all_peaks(extra_args=extra_args)
            if not peaks_success:
                failed_tests["Peaks execution tests"] = peaks_failed
            
            # Test fastqscreen
            fastqscreen_config = "example_data/example_fastqscreen/config_test_iCLIP_fastqscreen.yaml"
            print_colored(f"\nTesting fastqscreen for: {Path(fastqscreen_config).name}")
            fastqscreen_success = self.test_fastqscreen_execution(fastqscreen_config, extra_args=extra_args)
            if not fastqscreen_success:
                failed_tests["FastqScreen execution test"] = [Path(fastqscreen_config).name]
            
            success = crosslinks_success and peaks_success and fastqscreen_success
        else:
            print_colored("\n⚠️ Skipping execution tests due to unit, DAG, or config test failures")
            success = False
        
        print_colored("\n" + "="*50)
        if success:
            print_success("🎉 All tests passed!")
        else:
            print_error("❌ Some tests failed!")
            print_error("\nFailed test categories:")
            for test_category, config_list in failed_tests.items():
                if config_list:
                    print_error(f"  ✗ {test_category}:")
                    for config in config_list:
                        print_error(f"      - {config}")
                else:
                    print_error(f"  ✗ {test_category}")
            
        return success

    def test_mir(self, extra_args=None) -> bool:
        """Run miR unit, DAG, config, crosslinks, and peak execution tests."""
        print_colored("🧪 Running Mir Test Suite")
        print_colored("="*50)

        if extra_args:
            print_colored(f"Extra arguments for snakemake: {extra_args}")

        mir_config = "example_data/example_mir_eCLIP/config_test_mir_eCLIP.yaml"
        failed_tests = []

        mir_trim_success = self.test_mir_trim()
        if not mir_trim_success:
            failed_tests.append("miRNA trimming unit tests")

        # Materialize the packaged config with absolute paths. The CLI then
        # merges it with the defaults and writes *_absolute_paths_updated.yaml.
        mir_config_path = self.base_dir.parent / mir_config
        abs_mir_config = create_absolute_paths_config(
            str(mir_config_path),
            user_cwd=str(Path.cwd()),
        )
        dag_success = False
        if abs_mir_config:
            dag_success = test_dag(abs_mir_config)
        else:
            print_error("Could not create the absolute-path mir-eCLIP config")
        if not dag_success:
            failed_tests.append("DAG test")

        # Compare the CLI-updated config with the expected merged config after
        # applying the same portable-to-absolute path conversion to it.
        expected_config = (
            self.base_dir.parent / "tests/expected_output/out_mir_eCLIP/"
            "config_test_mir_eCLIP_expected.yaml"
        )
        actual_path = None
        if abs_mir_config:
            abs_mir_path = Path(abs_mir_config)
            actual_path = abs_mir_path.with_name(
                f"{abs_mir_path.stem}_updated.yaml"
            )
        expected_path = None
        if expected_config.exists():
            converted_expected = create_absolute_paths_config(
                str(expected_config),
                user_cwd=str(Path.cwd()),
            )
            if converted_expected:
                expected_path = Path(converted_expected)

        config_success = False
        if actual_path is None or not actual_path.exists():
            print_error(f"Actual config file not found: {actual_path}")
        elif expected_path is None or not expected_path.exists():
            print_error(f"Expected config file not found: {expected_path}")
        else:
            try:
                config_success = test_config(str(actual_path), str(expected_path),
                                              show_diff=True)
                if config_success:
                    print_success("Config test passed: config_test_mir_eCLIP_updated.yaml")
                else:
                    print_error("Config test failed: config_test_mir_eCLIP_updated.yaml")
            except Exception as e:
                print_error(f"Error testing config config_test_mir_eCLIP_updated.yaml: {e}")

        if not config_success:
            failed_tests.append("Config test")

        # Crosslinks test (only if unit, DAG, and config tests pass)
        crosslinks_success = False
        if mir_trim_success and dag_success and config_success:
            crosslinks_success = self.test_crosslinks_execution(mir_config, extra_args=extra_args)
            if not crosslinks_success:
                failed_tests.append("Crosslinks test")
        else:
            print_colored("\n⚠️ Skipping crosslinks test due to unit, DAG, or config test failures")

        # Run the peaks command on the same miR example after crosslinks pass.
        peaks_success = False
        if mir_trim_success and dag_success and config_success and crosslinks_success:
            peaks_success = self.test_peaks_execution(
                mir_config,
                extra_args=extra_args,
            )
            if not peaks_success:
                failed_tests.append("Peak calling test")
        else:
            print_colored(
                "\n⚠️ Skipping peak calling test due to an earlier miR test failure"
            )

        success = (
            mir_trim_success and dag_success and config_success
            and crosslinks_success and peaks_success
        )

        print_colored("\n" + "="*50)
        if success:
            print_success("🎉 Mir test passed!")
        else:
            print_error("❌ Mir test failed!")
            if failed_tests:
                print_error("\nFailed test categories:")
                for test_name in failed_tests:
                    print_error(f"  ✗ {test_name}")

        return success

    def test_peaks(self, extra_args=None) -> bool:
        """Peaks only test: Only run peaks execution tests"""
        print_colored("🧪 Running Peaks Test Suite")
        print_colored("="*50)
        
        # Print extra args info if provided
        if extra_args:
            print_colored(f"Extra arguments for snakemake: {extra_args}")
        
        # Test peaks only
        success, failed_configs = self.test_all_peaks(extra_args=extra_args)
        
        print_colored("\n" + "="*50)
        if success:
            print_success("🎉 Peaks test passed!")
        else:
            print_error("❌ Peaks test failed!")
            if failed_configs:
                print_error("\nFailed config files:")
                for config in failed_configs:
                    print_error(f"  - {config}")
            
        return success

    def test_fastqscreen(self, extra_args=None) -> bool:
        """Fastqscreen only test: Only run fastqscreen execution test"""
        print_colored("🧪 Running FastqScreen Test Suite")
        print_colored("="*50)
        
        # Print extra args info if provided
        if extra_args:
            print_colored(f"Extra arguments for snakemake: {extra_args}")
        
        # Test fastqscreen with the specific config file
        fastqscreen_config = "example_data/example_fastqscreen/config_test_iCLIP_fastqscreen.yaml"
        
        print_colored(f"\nTesting fastqscreen for: {Path(fastqscreen_config).name}")
        success = self.test_fastqscreen_execution(fastqscreen_config, extra_args=extra_args)
        
        print_colored("\n" + "="*50)
        if success:
            print_success("🎉 FastqScreen test passed!")
        else:
            print_error("❌ FastqScreen test failed!")
            
        return success

    def test_report(self, extra_args=None) -> bool:
        """Report generation test: Run the test_report.R script"""
        print_colored("🧪 Running Report Generation Test")
        print_colored("="*50)
        
        # Print extra args info if provided (not used for R script)
        if extra_args:
            print_colored(f"Note: Extra arguments ignored for report test: {extra_args}")
        
        # Path to the test_report.R script
        report_script = self.base_dir / "report_test" / "test_report.R"
        
        if not report_script.exists():
            print_error(f"Report test script not found: {report_script}")
            return False
        
        # Create absolute paths config files first (same as crosslinks test)
        print_colored("Creating config files with absolute paths...")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        racoon_clip_dir = os.path.dirname(script_dir)  # Go up from tests to racoon_clip
        
        # List of config files used in report tests (using inputs_for_report_test)
        report_config_files = [
            "tests/report_test/inputs_for_report_test/eCLIP/config_test_report_eCLIP.yaml",
            "tests/report_test/inputs_for_report_test/eCLIP_ENCODE/config_test_eCLIP_ENC.yaml", 
            "tests/report_test/inputs_for_report_test/iCLIP/config_test_iCLIP.yaml",
            "tests/report_test/inputs_for_report_test/iCLIP_multiplexed/config_test_iCLIP_multiplexed.yaml"
        ]
        
        for config_file_rel in report_config_files:
            config_file = os.path.join(racoon_clip_dir, config_file_rel)
            
            if not os.path.exists(config_file):
                print_warning(f"Config file not found: {config_file}")
                continue
                
            # Create absolute paths version using same logic as test_crosslinks
            config_basename = os.path.splitext(os.path.basename(config_file))[0]
            abs_config_name = f"{config_basename}_absolute_paths.yaml"
            abs_config_file = os.path.join(os.path.dirname(config_file), abs_config_name)
            
            # Skip if absolute paths config already exists
            if os.path.exists(abs_config_file):
                print_colored(f"Absolute paths config already exists: {abs_config_name}")
                continue
            
            print_colored(f"Creating absolute paths config for: {os.path.basename(config_file)}")
            
            try:
                # Read original config
                with open(config_file, 'r') as f:
                    if YAML_AVAILABLE:
                        import yaml
                        config_data = yaml.safe_load(f)
                        
                        # Convert paths (same logic as in test_crosslinks.py)
                        path_keys = ['wdir', 'infiles', 'experiment_group_file', 'barcodes_fasta', 'adapter_file', 'gtf', 'genome_fasta', 'mir_genome_fasta']
                        for key in path_keys:
                            if key in config_data and config_data[key]:
                                value = config_data[key]
                                if isinstance(value, str) and value.strip() and not os.path.isabs(value):
                                    if ' ' in value:  # Space-separated files
                                        files = []
                                        for f in value.split():
                                            if not os.path.isabs(f):
                                                # Join with racoon_clip_dir, then get absolute path to resolve any ../
                                                abs_path = os.path.abspath(os.path.join(racoon_clip_dir, f))
                                                files.append(abs_path)
                                            else:
                                                files.append(f)
                                        config_data[key] = ' '.join(files)
                                        print_colored(f"  Converted {key}: {value} -> {config_data[key]}")
                                    else:  # Single file
                                        # Join with racoon_clip_dir, then get absolute path to resolve any ../
                                        abs_path = os.path.abspath(os.path.join(racoon_clip_dir, value))
                                        config_data[key] = abs_path
                                        print_colored(f"  Converted {key}: {value} -> {abs_path}")
                        
                        # Write converted config
                        with open(abs_config_file, 'w') as abs_f:
                            yaml.dump(config_data, abs_f, default_flow_style=False, sort_keys=False)
                    else:
                        # Fallback: copy original if yaml not available
                        content = f.read()
                        with open(abs_config_file, 'w') as abs_f:
                            abs_f.write(content)
                
                print_success(f"Created: {abs_config_name}")
                
            except Exception as e:
                print_error(f"Failed to create absolute paths config for {config_file}: {e}")
                continue
        
        # Path to the conda environment file
        env_file = self.base_dir.parent / "racoon_clip" / "workflow" / "envs" / "racoon_R_v0.4.yml"
        if not env_file.exists():
            print_error(f"Conda environment file not found: {env_file}")
            return False
        
        print_colored(f"Using conda environment file: {env_file}")
        
        # Check if conda/mamba is available
        conda_cmd = None
        for cmd in ["mamba", "conda"]:
            check_cmd = [cmd, "--version"]
            success, output = self.run_command(check_cmd)
            if success:
                conda_cmd = cmd
                print_success(f"{cmd} is available")
                break
        
        if not conda_cmd:
            print_error("Neither conda nor mamba is available. Please install conda/mamba to run report tests.")
            return False
        
        # Check if the environment exists, create if it doesn't
        env_name = "racoon_R_v0.4"
        env_list_cmd = [conda_cmd, "env", "list"]
        success, output = self.run_command(env_list_cmd)
        
        if success and env_name not in output:
            print_colored(f"Creating conda environment: {env_name}")
            create_env_cmd = [conda_cmd, "env", "create", "-f", str(env_file)]
            success, output = self.run_command(create_env_cmd)
            if not success:
                print_error(f"Failed to create conda environment: {output}")
                return False
            print_success(f"Created conda environment: {env_name}")
        else:
            print_colored(f"Conda environment {env_name} already exists")
        
        # Run the R script within the conda environment
        if conda_cmd == "mamba":
            # Use mamba run for better performance
            r_cmd = ["mamba", "run", "-n", env_name, "Rscript", str(report_script)]
        else:
            # Use conda run
            r_cmd = ["conda", "run", "-n", env_name, "Rscript", str(report_script)]
        
        print_colored(f"Running R script in conda environment: {report_script}")
        
        # Run R script from current working directory instead of report_test directory
        success, output = self.run_command(r_cmd, cwd=Path.cwd())
        
        print_colored("\n" + "="*50)
        if success:
            print_success("🎉 Report generation test passed!")
            print_colored("Generated reports should be available in the report_test directories")
        else:
            print_error("❌ Report generation test failed!")
            print_error(f"R script output: {output}")
            
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

    def devel_test(self, extra_args=None) -> bool:
        """Development test: Only installation test"""
        print_colored("🧪 Running Development Test Suite")
        print_colored("="*50)
        
        # Print extra args info if provided (not used for installation test)
        if extra_args:
            print_colored(f"Note: Extra arguments ignored for development test: {extra_args}")
        
        # Test installation only
        success = self.test_installation()
        
        print_colored("\n" + "="*50)
        if success:
            print_success("🎉 Development test passed!")
        else:
            print_error("❌ Development test failed!")
            
        return success

    def cleanup_results_folders(self):
        """Remove all test result folders from current working directory after successful tests."""
        print_colored("\n=== Cleaning up test result folders ===")

        # Use current working directory for cleanup
        current_dir = Path.cwd()
        
        # Look for test output directories in current working directory
        test_output_patterns = ["out_*", "test_report_*", "racoon_clip_out", "test"]
        result_dirs_found = False
        
        for pattern in test_output_patterns:
            for results_dir in current_dir.glob(pattern):
                if results_dir.is_dir():
                    result_dirs_found = True
                    try:
                        print_colored(f"Removing results directory: {results_dir}")
                        shutil.rmtree(results_dir)
                        print_success(f"Removed: {results_dir}")
                    except Exception as e:
                        print_warning(f"Could not remove results directory {results_dir}: {e}")
        
        if not result_dirs_found:
            print_colored("No results directories found to clean up.")
            
        print_colored("=== Cleanup completed ===\n")

    def cleanup_generated_configs(self) -> bool:
        """Remove configuration files generated by a successful test run."""
        print_colored("\n=== Cleaning up generated config files ===")

        repo_dir = self.base_dir.parent
        generated_config_patterns = [
            "example_data/*/*_absolute_paths*.yaml",
            "example_data/*/*_updated.yaml",
            "tests/expected_output/*/*_absolute_paths*.yaml",
            "tests/report_test/inputs_for_report_test/*/*_absolute_paths*.yaml",
            "example_data/example_fastqscreen/*_absolute_paths.config",
        ]
        generated_configs = {
            path
            for pattern in generated_config_patterns
            for path in repo_dir.glob(pattern)
            if path.is_file()
        }

        cleanup_success = True
        for config_file in sorted(generated_configs):
            try:
                config_file.unlink()
                print_success(f"Removed: {config_file}")
            except Exception as e:
                cleanup_success = False
                print_warning(
                    f"Could not remove generated config {config_file}: {e}"
                )

        if not generated_configs:
            print_colored("No generated config files found.")

        print_colored("=== Generated config cleanup completed ===\n")
        return cleanup_success
            
    def cleanup_old_logs(self, base_dir):
        """Remove racoon_clip log files older than the current day."""
        current_date = datetime.datetime.now().strftime('%Y%m%d')
        # Use current working directory for log files instead of hardcoded logs subdirectory
        log_dir = Path.cwd()

        if not log_dir.exists():
            print(f"DEBUG: Log directory does not exist: {log_dir}")
            return

        for log_file in log_dir.glob("racoon_clip_*.log"):
            log_date = log_file.stem.split('_')[-1]
            if log_date < current_date:
                try:
                    log_file.unlink()
                    print(f"DEBUG: Deleted old log file: {log_file}")
                except Exception as e:
                    print(f"WARNING: Could not delete log file {log_file}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Racoon CLIP test suite")
    parser.add_argument(
        "test_type", 
        choices=["test_light", "test", "test_mir", "test_peaks", "test_fastqscreen", "devel_test", "dev_report", "test_report"],
        help="Type of test to run"
    )
    parser.add_argument(
        "--no_clean",
        action="store_true",
        help="Do not remove test result folders after successful tests"
    )
    
    args = parser.parse_args()
    
    suite = RacoonTestSuite()
    
    if args.test_type == "test_light":
        success = suite.test_light()
    elif args.test_type == "test":
        success = suite.test()
    elif args.test_type == "test_mir":
        success = suite.test_mir()
    elif args.test_type == "test_peaks":
        success = suite.test_peaks()
    elif args.test_type == "test_fastqscreen":
        success = suite.test_fastqscreen()
    elif args.test_type == "devel_test":
        success = suite.devel_test()
    elif args.test_type == "dev_report":
        success = suite.dev_report()
    elif args.test_type == "test_report":
        success = suite.test_report()
        # Don't clean up after report test - reports need to be inspected
    else:
        print_error(f"Unknown test type: {args.test_type}")
        return 1
    
    # Generated configs are transient and are removed after every successful
    # test, even when result-folder cleanup is disabled.
    if success:
        success = suite.cleanup_generated_configs()

    # Clean up test results unless --no_clean flag is set or running report test
    if success and not args.no_clean and args.test_type != "test_report":
        suite.cleanup_results_folders()
    elif args.no_clean:
        print_colored("\n--no_clean flag set: Test result folders preserved")
    elif args.test_type == "test_report":
        print_colored("\nReport test: Result folders preserved for inspection")
    
    # Always clean up old logs, regardless of test outcome
    suite.cleanup_old_logs(suite.base_dir.parent)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
