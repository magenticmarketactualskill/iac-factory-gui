"""
Simple round-trip test for EnhancedIacFactory.

Feature: interactive-gui-lifecycle, Property 4: Design persistence round-trip
Validates: Requirements 1.5, 7.1, 7.3
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from gui.backend.enhanced_factory import EnhancedIacFactory, ComponentState
from iac_factory.components import Gateway, Container, Lambda, Cache, Rdms, Archive


def test_simple_round_trip():
    """
    **Feature: interactive-gui-lifecycle, Property 4: Design persistence round-trip**
    **Validates: Requirements 1.5, 7.1, 7.3**
    
    Test that saving and loading preserves all design data.
    """
    print("Testing simple round-trip serialization...")
    
    factory = EnhancedIacFactory("Test Infrastructure")
    
    # Add components
    gateway = Gateway("API Gateway", "Public", "AWS API Gateway")
    container = Container("Web App", "Web", "Docker")
    database = Rdms("User DB", "Data", "PostgreSQL")
    cache = Cache("Session Cache", "Data", "Redis")
    
    factory.add_component(gateway)
    factory.add_component(container)
    factory.add_component(database)
    factory.add_component(cache)
    
    # Add connections
    factory.add_connection(container, gateway, "Makes API calls", "HTTPS")
    factory.add_connection(gateway, database, "Queries data", "SQL")
    factory.add_connection(container, cache, "Caches sessions", "Redis Protocol")
    
    # Set some component states
    factory.set_component_state("API Gateway", ComponentState.DEPLOYED, "resource-123")
    factory.set_component_state("Web App", ComponentState.DEPLOYING)
    
    # Serialize to JSON
    json_data = factory.to_json()
    print(f"  Serialized factory with {len(json_data['components'])} components")
    
    # Deserialize from JSON
    restored = EnhancedIacFactory.from_json(json_data)
    print(f"  Restored factory with {len(restored.components)} components")
    
    # Verify factory properties
    assert restored.name == "Test Infrastructure", "Factory name mismatch"
    assert restored.design_id == factory.design_id, "Design ID mismatch"
    
    # Verify components
    assert len(restored.components) == 4, f"Expected 4 components, got {len(restored.components)}"
    
    component_names = {c.name for c in restored.components}
    expected_names = {"API Gateway", "Web App", "User DB", "Session Cache"}
    assert component_names == expected_names, f"Component names mismatch: {component_names} vs {expected_names}"
    
    # Verify component types and properties
    restored_comps = {c.name: c for c in restored.components}
    assert isinstance(restored_comps["API Gateway"], Gateway)
    assert isinstance(restored_comps["Web App"], Container)
    assert isinstance(restored_comps["User DB"], Rdms)
    assert isinstance(restored_comps["Session Cache"], Cache)
    
    assert restored_comps["API Gateway"].domain_type == "Public"
    assert restored_comps["Web App"].domain_type == "Web"
    assert restored_comps["User DB"].get_technology() == "PostgreSQL"
    
    # Verify connections
    assert len(restored.connections) == 3, f"Expected 3 connections, got {len(restored.connections)}"
    
    conn_pairs = {(c.source.name, c.destination.name) for c in restored.connections}
    expected_pairs = {
        ("Web App", "API Gateway"),
        ("API Gateway", "User DB"),
        ("Web App", "Session Cache")
    }
    assert conn_pairs == expected_pairs, f"Connection pairs mismatch"
    
    # Verify connection properties
    for conn in restored.connections:
        if conn.source.name == "Web App" and conn.destination.name == "API Gateway":
            assert conn.label == "Makes API calls"
            assert conn.technology == "HTTPS"
    
    # Verify component states
    api_state = restored.get_component_state("API Gateway")
    assert api_state.state == ComponentState.DEPLOYED
    assert api_state.resource_id == "resource-123"
    
    webapp_state = restored.get_component_state("Web App")
    assert webapp_state.state == ComponentState.DEPLOYING
    
    print("✓ All assertions passed!")
    return True


def test_empty_factory():
    """Test round-trip with empty factory."""
    print("\nTesting empty factory round-trip...")
    
    factory = EnhancedIacFactory("Empty Design")
    json_data = factory.to_json()
    restored = EnhancedIacFactory.from_json(json_data)
    
    assert restored.name == "Empty Design"
    assert len(restored.components) == 0
    assert len(restored.connections) == 0
    
    print("✓ Empty factory test passed!")
    return True


def test_json_string_serialization():
    """Test JSON string serialization."""
    print("\nTesting JSON string serialization...")
    
    factory = EnhancedIacFactory("String Test")
    lambda_fn = Lambda("Process Function", "Application", "AWS Lambda")
    factory.add_component(lambda_fn)
    
    # Serialize to string
    json_str = factory.to_json_string()
    assert isinstance(json_str, str)
    assert "String Test" in json_str
    assert "Process Function" in json_str
    
    # Deserialize from string
    restored = EnhancedIacFactory.from_json_string(json_str)
    assert restored.name == "String Test"
    assert len(restored.components) == 1
    assert restored.components[0].name == "Process Function"
    
    print("✓ JSON string serialization test passed!")
    return True


if __name__ == "__main__":
    try:
        test_simple_round_trip()
        test_empty_factory()
        test_json_string_serialization()
        print("\n" + "="*50)
        print("ALL TESTS PASSED!")
        print("="*50)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
