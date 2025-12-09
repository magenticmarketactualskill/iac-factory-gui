"""
Property-based tests for EnhancedIacFactory.

Feature: interactive-gui-lifecycle, Property 4: Design persistence round-trip
"""
import pytest
from hypothesis import given, strategies as st
from hypothesis.strategies import composite
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from gui.backend.enhanced_factory import EnhancedIacFactory, ComponentState
from iac_factory.components import Gateway, Container, Lambda, Cache, Rdms, Archive


# Strategy for generating component types
@composite
def component_strategy(draw):
    """Generate random components."""
    comp_type = draw(st.sampled_from([Gateway, Container, Lambda, Cache, Rdms, Archive]))
    name = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
    domain = draw(st.sampled_from(["Public", "Web", "Application", "Data"]))
    tech = draw(st.text(min_size=1, max_size=15, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))))
    
    return comp_type(name=f"comp_{name}", domain_type=domain, technology=tech)


@composite
def factory_strategy(draw):
    """Generate random factories with components and connections."""
    name = draw(st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'))))
    factory = EnhancedIacFactory(name=name or "Test")
    
    # Add 1-5 components
    num_components = draw(st.integers(min_value=1, max_value=5))
    components = []
    for _ in range(num_components):
        try:
            comp = draw(component_strategy())
            factory.add_component(comp)
            components.append(comp)
        except ValueError:
            # Skip duplicate names
            pass
    
    # Add 0-3 connections if we have at least 2 components
    if len(components) >= 2:
        num_connections = draw(st.integers(min_value=0, max_value=min(3, len(components))))
        for _ in range(num_connections):
            source = draw(st.sampled_from(components))
            destination = draw(st.sampled_from([c for c in components if c != source]))
            label = draw(st.text(max_size=20))
            tech = draw(st.text(max_size=10))
            try:
                factory.add_connection(source, destination, label, tech)
            except ValueError:
                pass
    
    return factory


@given(factory_strategy())
def test_design_persistence_round_trip(factory):
    """
    **Feature: interactive-gui-lifecycle, Property 4: Design persistence round-trip**
    **Validates: Requirements 1.5, 7.1, 7.3**
    
    For any design state, saving and then loading should reconstruct 
    an equivalent design with all components and connections preserved.
    """
    # Serialize to JSON
    json_data = factory.to_json()
    
    # Deserialize from JSON
    restored_factory = EnhancedIacFactory.from_json(json_data)
    
    # Verify factory name
    assert restored_factory.name == factory.name
    
    # Verify design ID
    assert restored_factory.design_id == factory.design_id
    
    # Verify component count
    assert len(restored_factory.components) == len(factory.components)
    
    # Verify each component
    original_comps = {c.name: c for c in factory.components}
    restored_comps = {c.name: c for c in restored_factory.components}
    
    assert set(original_comps.keys()) == set(restored_comps.keys())
    
    for name in original_comps.keys():
        orig = original_comps[name]
        rest = restored_comps[name]
        assert type(orig) == type(rest)
        assert orig.domain_type == rest.domain_type
        assert orig.get_technology() == rest.get_technology()
    
    # Verify connection count
    assert len(restored_factory.connections) == len(factory.connections)
    
    # Verify each connection
    for orig_conn, rest_conn in zip(factory.connections, restored_factory.connections):
        assert orig_conn.source.name == rest_conn.source.name
        assert orig_conn.destination.name == rest_conn.destination.name
        assert orig_conn.label == rest_conn.label
        assert orig_conn.technology == rest_conn.technology


def test_simple_round_trip():
    """Simple test case for round-trip serialization."""
    factory = EnhancedIacFactory("Test Infrastructure")
    
    # Add components
    gateway = Gateway("API Gateway", "Public", "AWS API Gateway")
    container = Container("Web App", "Web", "Docker")
    database = Rdms("User DB", "Data", "PostgreSQL")
    
    factory.add_component(gateway)
    factory.add_component(container)
    factory.add_component(database)
    
    # Add connections
    factory.add_connection(container, gateway, "Makes API calls", "HTTPS")
    factory.add_connection(gateway, database, "Queries data", "SQL")
    
    # Set some component states
    factory.set_component_state("API Gateway", ComponentState.DEPLOYED, "resource-123")
    
    # Serialize and deserialize
    json_data = factory.to_json()
    restored = EnhancedIacFactory.from_json(json_data)
    
    # Verify
    assert restored.name == "Test Infrastructure"
    assert len(restored.components) == 3
    assert len(restored.connections) == 2
    assert restored.get_component_state("API Gateway").state == ComponentState.DEPLOYED
    assert restored.get_component_state("API Gateway").resource_id == "resource-123"


if __name__ == "__main__":
    # Run simple test
    test_simple_round_trip()
    print("Simple round-trip test passed!")
    
    # Run property-based test with fewer examples for quick check
    from hypothesis import settings
    test_design_persistence_round_trip()
    print("Property-based round-trip test passed!")
