"""
Test runner that sets up the environment properly.
"""
import sys
import os

# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

# Now run the test
if __name__ == "__main__":
    from gui.backend.tests.test_simple_round_trip import (
        test_simple_round_trip,
        test_empty_factory,
        test_json_string_serialization
    )
    
    try:
        test_simple_round_trip()
        test_empty_factory()
        test_json_string_serialization()
        print("\n" + "="*50)
        print("ALL TESTS PASSED!")
        print("="*50)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
