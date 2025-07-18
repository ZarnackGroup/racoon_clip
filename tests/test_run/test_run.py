import subprocess
import sys


def test_run_execution(config_file):
    """Test if racoon_clip run executes without errors."""
    
    cmd = ["racoon_clip", "run", "--cores", "4",
           "--configfile", config_file]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                check=True)
        
        # Check if run completed successfully
        if result.returncode == 0:
            print("✅ RUN test PASSED: racoon_clip run completed successfully")
            return True
        else:
            print("❌ RUN test FAILED: racoon_clip run failed")
            print("\nSTDOUT:")
            print("=" * 50)
            print(result.stdout)
            if result.stderr:
                print("\nSTDERR:")
                print("=" * 50)
                print(result.stderr)
            return False
        
    except subprocess.CalledProcessError as e:
        print("❌ RUN test FAILED: Command execution failed")
        print(f"Return code: {e.returncode}")
        print("\nSTDOUT:")
        print("=" * 50)
        print(e.stdout if e.stdout else "(empty)")
        print("\nSTDERR:")
        print("=" * 50)
        print(e.stderr if e.stderr else "(empty)")
        return False
    except (FileNotFoundError, OSError) as e:
        print(f"❌ RUN test FAILED: System error: {e}")
        return False


def test_run(config_file):
    """Test if racoon_clip run executes without errors."""
    
    print(f"Testing racoon_clip run for {config_file}")
    
    if config_file is None:
        print("Error: config_file is required")
        return False
    
    # Test run execution
    return test_run_execution(config_file)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_run.py <config_file>")
        sys.exit(1)
    
    config = sys.argv[1]
    
    success = test_run(config)
    sys.exit(0 if success else 1)
