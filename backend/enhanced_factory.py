"""
Enhanced IacFactory with state management for GUI.
"""
import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import from iac-factory package
from iac_factory.factory import IacFactory
from iac_factory.components import Gateway, Container, Lambda, Cache, Rdms, Archive
from iac_factory.connection import Connection


class ComponentState(Enum):
    """Deployment state of a component."""
    UNDEPLOYED = "undeployed"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    UPDATING = "updating"
    DESTROYING = "destroying"
    ERROR = "error"


@dataclass
class ComponentStateInfo:
    """Detailed state information for a component."""
    state: ComponentState
    resource_id: Optional[str] = None
    error_message: Optional[str] = None
    last_updated: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "state": self.state.value,
            "resource_id": self.resource_id,
            "error_message": self.error_message,
            "last_updated": self.last_updated or datetime.utcnow().isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComponentStateInfo':
        """Create from dictionary."""
        return cls(
            state=ComponentState(data["state"]),
            resource_id=data.get("resource_id"),
            error_message=data.get("error_message"),
            last_updated=data.get("last_updated")
        )


class EnhancedIacFactory(IacFactory):
    """
    Extended IacFactory with state management and serialization.
    """
    
    def __init__(self, name: str = "Infrastructure", design_id: Optional[str] = None):
        """
        Initialize enhanced factory.
        
        Args:
            name: Name of the infrastructure project
            design_id: Unique identifier for this design
        """
        super().__init__(name)
        self.design_id = design_id or str(uuid.uuid4())
        self.component_states: Dict[str, ComponentStateInfo] = {}
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
    
    def set_component_state(self, component_name: str, state: ComponentState, 
                           resource_id: Optional[str] = None,
                           error_message: Optional[str] = None) -> None:
        """
        Update the deployment state of a component.
        
        Args:
            component_name: Name of the component
            state: New state
            resource_id: Cloud provider resource ID
            error_message: Error message if state is ERROR
        """
        self.component_states[component_name] = ComponentStateInfo(
            state=state,
            resource_id=resource_id,
            error_message=error_message,
            last_updated=datetime.utcnow().isoformat()
        )
        self.updated_at = datetime.utcnow().isoformat()
    
    def get_component_state(self, component_name: str) -> ComponentStateInfo:
        """
        Get the current state of a component.
        
        Args:
            component_name: Name of the component
            
        Returns:
            ComponentStateInfo
        """
        if component_name not in self.component_states:
            self.component_states[component_name] = ComponentStateInfo(
                state=ComponentState.UNDEPLOYED,
                last_updated=datetime.utcnow().isoformat()
            )
        return self.component_states[component_name]
    
    def to_json(self) -> Dict[str, Any]:
        """
        Serialize factory to JSON-compatible dictionary.
        
        Returns:
            Dictionary representation
        """
        # Serialize components
        components_data = []
        for comp in self._components:
            comp_data = {
                "name": comp.name,
                "type": comp.__class__.__name__,
                "domain_type": comp.domain_type,
                "technology": comp.get_technology()
            }
            components_data.append(comp_data)
        
        # Serialize connections
        connections_data = []
        for conn in self._connections:
            conn_data = {
                "source": conn.source.name,
                "destination": conn.destination.name,
                "label": conn.label,
                "technology": conn.technology
            }
            connections_data.append(conn_data)
        
        # Serialize component states
        states_data = {
            name: state.to_dict() 
            for name, state in self.component_states.items()
        }
        
        return {
            "design_id": self.design_id,
            "name": self._name,
            "components": components_data,
            "connections": connections_data,
            "component_states": states_data,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'EnhancedIacFactory':
        """
        Deserialize factory from JSON-compatible dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            EnhancedIacFactory instance
        """
        factory = cls(
            name=data["name"],
            design_id=data.get("design_id")
        )
        
        # Restore timestamps
        factory.created_at = data.get("created_at", datetime.utcnow().isoformat())
        factory.updated_at = data.get("updated_at", datetime.utcnow().isoformat())
        
        # Component type mapping
        component_classes = {
            "Gateway": Gateway,
            "Container": Container,
            "Lambda": Lambda,
            "Cache": Cache,
            "Rdms": Rdms,
            "Archive": Archive
        }
        
        # Restore components
        component_map = {}
        for comp_data in data.get("components", []):
            comp_class = component_classes.get(comp_data["type"])
            if comp_class:
                component = comp_class(
                    name=comp_data["name"],
                    domain_type=comp_data["domain_type"],
                    technology=comp_data.get("technology", "")
                )
                factory.add_component(component)
                component_map[comp_data["name"]] = component
        
        # Restore connections
        for conn_data in data.get("connections", []):
            source = component_map.get(conn_data["source"])
            destination = component_map.get(conn_data["destination"])
            if source and destination:
                factory.add_connection(
                    source=source,
                    destination=destination,
                    label=conn_data.get("label", ""),
                    technology=conn_data.get("technology", "")
                )
        
        # Restore component states
        for name, state_data in data.get("component_states", {}).items():
            factory.component_states[name] = ComponentStateInfo.from_dict(state_data)
        
        return factory
    
    def to_json_string(self) -> str:
        """
        Serialize to JSON string.
        
        Returns:
            JSON string
        """
        return json.dumps(self.to_json(), indent=2)
    
    @classmethod
    def from_json_string(cls, json_str: str) -> 'EnhancedIacFactory':
        """
        Deserialize from JSON string.
        
        Args:
            json_str: JSON string
            
        Returns:
            EnhancedIacFactory instance
        """
        data = json.loads(json_str)
        return cls.from_json(data)
