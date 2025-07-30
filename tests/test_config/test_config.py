import sys
import os
from pathlib import Path
import difflib
import yaml
import unittest  # For unittest integration
import copy

def filter_config_data(config_data, ignore_patterns):
    """Recursively filter out keys/values containing ignore patterns from config data."""
    if not ignore_patterns:
        return config_data
    
    if isinstance(config_data, dict):
        filtered = {}
        for key, value in config_data.items():
            # Skip keys that contain any ignore pattern
            key_should_be_ignored = any(pattern.lower() in str(key).lower() for pattern in ignore_patterns)
            if not key_should_be_ignored:
                # Recursively filter the value
                filtered_value = filter_config_data(value, ignore_patterns)
                # Only add if we got a valid filtered value (not None)
                if filtered_value is not None:
                    filtered[key] = filtered_value
        return filtered
    elif isinstance(config_data, list):
        filtered = []
        for item in config_data:
            filtered_item = filter_config_data(item, ignore_patterns)
            # Only add if we got a valid filtered item (not None)
            if filtered_item is not None:
                filtered.append(filtered_item)
        return filtered
    else:
        # For primitive types, check if they contain ignore patterns
        if any(pattern.lower() in str(config_data).lower() for pattern in ignore_patterns):
            return None
        return config_data

def filter_text_lines(text, ignore_patterns):
    """Filter out lines containing any of the ignore patterns."""
    if not ignore_patterns:
        return text
    
    lines = text.splitlines(keepends=True)
    filtered_lines = []
    
    for line in lines:
        # Check if any ignore pattern is in the line (case insensitive)
        line_should_be_ignored = any(pattern.lower() in line.lower() for pattern in ignore_patterns)
        if not line_should_be_ignored:
            filtered_lines.append(line)
    
    return ''.join(filtered_lines)

def load_yaml_config(config_file):
    """Load and parse YAML configuration file."""
    
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Config file not found: {config_file}")
        return None
    except Exception as e:
        print(f"Error parsing YAML config file {config_file}: {e}")
        return None

def compare_configs(updated_config, reference_config, show_diff=True, compare_yaml=True, ignore_patterns=None):
    """Compare updated config with reference config.
    
    Args:
        ignore_patterns: List of strings to ignore in comparison (e.g., ['snakebase', 'adapter_file'])
    """
    if ignore_patterns is None:
        ignore_patterns = ['snakebase', 'adapter_file']

    if compare_yaml:
        # Compare as parsed YAML for semantic comparison
        updated_data = load_yaml_config(updated_config)
        reference_data = load_yaml_config(reference_config)
        
        if updated_data is None or reference_data is None:
            return False

        # Filter out ignored patterns from both configs
        filtered_updated = filter_config_data(updated_data, ignore_patterns)
        filtered_reference = filter_config_data(reference_data, ignore_patterns)

        if filtered_updated == filtered_reference:
            print("✅ Config test PASSED: Configuration is unchanged (ignoring specified patterns)")
            print(f"   Ignored patterns: {ignore_patterns}")
            return True
        else:
            print("❌ Config test FAILED: Configuration has changed")
            print(f"   Ignored patterns: {ignore_patterns}")

            if show_diff:
                # Show text diff for better readability - read as text files
                try:
                    with open(updated_config, 'r') as f:
                        updated_text = f.read()
                    with open(reference_config, 'r') as f:
                        reference_text = f.read()

                    # Filter lines for diff display
                    updated_filtered_text = filter_text_lines(updated_text, ignore_patterns)
                    reference_filtered_text = filter_text_lines(reference_text, ignore_patterns)

                    print("\nDifferences found (ignoring specified patterns):")
                    print("=" * 50)
                    diff = difflib.unified_diff(
                        reference_filtered_text.splitlines(keepends=True),
                        updated_filtered_text.splitlines(keepends=True),
                        fromfile='reference_config',
                        tofile='updated_config',
                        lineterm=''
                    )
                    diff_lines = list(diff)
                    if diff_lines:
                        for line in diff_lines:
                            print(line)
                    else:
                        print("No differences found after filtering - this might be a bug in the filtering logic")
                except Exception as e:
                    print(f"Error reading files for diff: {e}")

            return False
    else:
        # Compare as text files
        try:
            with open(updated_config, 'r') as f:
                updated_text = f.read()
            with open(reference_config, 'r') as f:
                reference_text = f.read()
        except Exception as e:
            print(f"Error reading files: {e}")
            return False

        # Filter lines for comparison
        updated_filtered_text = filter_text_lines(updated_text, ignore_patterns)
        reference_filtered_text = filter_text_lines(reference_text, ignore_patterns)

        if updated_filtered_text.strip() == reference_filtered_text.strip():
            print("✅ Config test PASSED: Configuration is unchanged (ignoring specified patterns)")
            return True
        else:
            print("❌ Config test FAILED: Configuration has changed")

            if show_diff:
                print("\nDifferences found (ignoring specified patterns):")
                print("=" * 50)
                diff = difflib.unified_diff(
                    reference_filtered_text.splitlines(keepends=True),
                    updated_filtered_text.splitlines(keepends=True),
                    fromfile='reference_config',
                    tofile='updated_config',
                    lineterm=''
                )
                for line in diff:
                    print(line)

            return False

def test_config(updated_config_file, reference_file=None, show_diff=True, ignore_patterns=None):
    """Test if updated config matches reference config.
    
    Args:
        ignore_patterns: List of strings to ignore in comparison (e.g., ['snakebase', 'adapter_file'])
    """
    if ignore_patterns is None:
        ignore_patterns = ['snakebase', 'adapter_file']

    if reference_file is None:
        # Generate reference filename from updated config
        if updated_config_file.endswith('_updated.yaml'):
            reference_file = updated_config_file.replace('_updated.yaml', '.yaml')
        else:
            reference_file = updated_config_file.replace('_updated.yaml', '.yaml')

    print(f"Testing config: {updated_config_file}")
    print(f"Reference file: {reference_file}")

    if not os.path.exists(updated_config_file):
        raise FileNotFoundError(f"Updated config file not found: {updated_config_file}")
    
    if not os.path.exists(reference_file):
        raise FileNotFoundError(f"Reference config file not found: {reference_file}")

    # Compare configs
    return compare_configs(updated_config_file, reference_file, show_diff, compare_yaml=True, ignore_patterns=ignore_patterns)

# Test class for unittest framework
class TestConfigFiles(unittest.TestCase):

    def test_config_unchanged(self):
        """Test that config files haven't changed unexpectedly."""
        # Define your config file pairs here
        config_pairs = [
            ("/path/to/config_updated.yaml", "/path/to/config.yaml"),
            # Add more pairs as needed
        ]

        for updated_config, reference_config in config_pairs:
            with self.subTest(config=updated_config):
                result = test_config(updated_config, reference_config, show_diff=False)
                self.assertTrue(result, f"Config test failed for {updated_config}")

# Pytest-style test functions
def test_eclip_config():
    """Test eCLIP config file."""
    updated = "/home/mek24iv/racoon_devel/racoon_clip/example_data/example_eCLIP_ENCODE_updated.yaml"
    reference = "/home/mek24iv/racoon_devel/racoon_clip/example_data/example_eCLIP_ENCODE.yaml"
    assert test_config(updated, reference), "eCLIP config test failed"

# Function to discover and test all config files automatically
def test_all_configs_in_directory(directory_path):
    """Automatically test all *_updated.yaml files against their originals."""
    directory = Path(directory_path)
    updated_files = list(directory.glob("*_updated.yaml"))

    results = []
    for updated_file in updated_files:
        reference_file = updated_file.with_name(updated_file.name.replace("_updated.yaml", ".yaml"))

        if reference_file.exists():
            try:
                result = test_config(str(updated_file), str(reference_file))
                results.append((str(updated_file), result))
            except Exception as e:
                results.append((str(updated_file), False))
                print(f"Error testing {updated_file}: {e}")
        else:
            print(f"Warning: Reference file not found for {updated_file}")
            results.append((str(updated_file), False))

    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_config.py <updated_config_file> [reference_file]")
        sys.exit(1)

    updated_config = sys.argv[1]
    reference = sys.argv[2] if len(sys.argv) > 2 else None

    success = test_config(updated_config, reference)
    sys.exit(0 if success else 1)
