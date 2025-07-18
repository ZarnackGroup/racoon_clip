import sys
import os
from pathlib import Path
import difflib
import yaml
import unittest  # For unittest integration

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

def compare_configs(updated_config, reference_config, show_diff=True, compare_yaml=True):
    """Compare updated config with reference config."""

    if compare_yaml:
        # Compare as parsed YAML for semantic comparison
        updated_data = load_yaml_config(updated_config)
        reference_data = load_yaml_config(reference_config)
        
        if updated_data is None or reference_data is None:
            return False

        if updated_data == reference_data:
            print("✅ Config test PASSED: Configuration is unchanged")
            return True
        else:
            print("❌ Config test FAILED: Configuration has changed")

            if show_diff:
                # Show text diff for better readability
                updated_text = load_yaml_config(updated_config)
                reference_text = load_yaml_config(reference_config)

                if updated_text and reference_text:
                    print("\nDifferences found:")
                    print("=" * 50)
                    diff = difflib.unified_diff(
                        reference_text.splitlines(keepends=True),
                        updated_text.splitlines(keepends=True),
                        fromfile='reference_config',
                        tofile='updated_config',
                        lineterm=''
                    )
                    for line in diff:
                        print(line)

            return False
    else:
        # Compare as text files
        updated_text = load_yaml_config(updated_config)
        reference_text = load_yaml_config(reference_config)

        if updated_text is None or reference_text is None:
            return False

        if updated_text.strip() == reference_text.strip():
            print("✅ Config test PASSED: Configuration is unchanged")
            return True
        else:
            print("❌ Config test FAILED: Configuration has changed")

            if show_diff:
                print("\nDifferences found:")
                print("=" * 50)
                diff = difflib.unified_diff(
                    reference_text.splitlines(keepends=True),
                    updated_text.splitlines(keepends=True),
                    fromfile='reference_config',
                    tofile='updated_config',
                    lineterm=''
                )
                for line in diff:
                    print(line)

            return False

def test_config(updated_config_file, reference_file=None, show_diff=True):
    """Test if updated config matches reference config."""

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
    return compare_configs(updated_config_file, reference_file, show_diff)

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
