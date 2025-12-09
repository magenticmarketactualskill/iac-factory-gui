"""
DesignManager for persisting and managing infrastructure designs.
"""
import os
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path


class DesignManager:
    """Manages design persistence and retrieval."""
    
    def __init__(self, storage_dir: str = "designs"):
        """
        Initialize the design manager.
        
        Args:
            storage_dir: Directory to store design files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
    
    def _get_design_path(self, design_id: str) -> Path:
        """Get the file path for a design."""
        return self.storage_dir / f"{design_id}.json"
    
    def create_design(self, name: str) -> Dict[str, Any]:
        """
        Create a new infrastructure design.
        
        Args:
            name: Name of the design
            
        Returns:
            Design data dictionary
        """
        design_id = str(uuid.uuid4())
        design_data = {
            "design_id": design_id,
            "name": name,
            "components": [],
            "connections": [],
            "component_states": {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Save to file
        self.save_design(design_data)
        
        return design_data
    
    def load_design(self, design_id: str) -> Dict[str, Any]:
        """
        Load an existing design.
        
        Args:
            design_id: ID of the design to load
            
        Returns:
            Design data dictionary
            
        Raises:
            FileNotFoundError: If design doesn't exist
            ValueError: If design file is invalid
        """
        design_path = self._get_design_path(design_id)
        
        if not design_path.exists():
            raise FileNotFoundError(f"Design {design_id} not found")
        
        try:
            with open(design_path, 'r') as f:
                design_data = json.load(f)
            
            # Validate required fields
            required_fields = ["design_id", "name", "components", "connections"]
            for field in required_fields:
                if field not in design_data:
                    raise ValueError(f"Invalid design file: missing '{field}' field")
            
            return design_data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in design file: {e}")
    
    def save_design(self, design_data: Dict[str, Any]) -> None:
        """
        Persist design to storage.
        
        Args:
            design_data: Design data dictionary
        """
        design_id = design_data.get("design_id")
        if not design_id:
            raise ValueError("Design data must include 'design_id'")
        
        # Update timestamp
        design_data["updated_at"] = datetime.utcnow().isoformat()
        
        design_path = self._get_design_path(design_id)
        
        with open(design_path, 'w') as f:
            json.dump(design_data, f, indent=2)
    
    def delete_design(self, design_id: str) -> None:
        """
        Delete a design.
        
        Args:
            design_id: ID of the design to delete
            
        Raises:
            FileNotFoundError: If design doesn't exist
        """
        design_path = self._get_design_path(design_id)
        
        if not design_path.exists():
            raise FileNotFoundError(f"Design {design_id} not found")
        
        design_path.unlink()
    
    def list_designs(self) -> List[Dict[str, Any]]:
        """
        List all available designs.
        
        Returns:
            List of design summaries
        """
        designs = []
        
        for design_file in self.storage_dir.glob("*.json"):
            try:
                with open(design_file, 'r') as f:
                    design_data = json.load(f)
                
                # Create summary
                summary = {
                    "design_id": design_data.get("design_id"),
                    "name": design_data.get("name"),
                    "component_count": len(design_data.get("components", [])),
                    "connection_count": len(design_data.get("connections", [])),
                    "created_at": design_data.get("created_at"),
                    "updated_at": design_data.get("updated_at")
                }
                designs.append(summary)
                
            except (json.JSONDecodeError, KeyError):
                # Skip invalid files
                continue
        
        # Sort by updated_at descending
        designs.sort(key=lambda d: d.get("updated_at", ""), reverse=True)
        
        return designs
    
    def validate_design(self, design_data: Dict[str, Any]) -> List[str]:
        """
        Validate design data structure.
        
        Args:
            design_data: Design data to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check required fields
        required_fields = ["design_id", "name", "components", "connections"]
        for field in required_fields:
            if field not in design_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate components
        if "components" in design_data:
            if not isinstance(design_data["components"], list):
                errors.append("'components' must be a list")
            else:
                for i, comp in enumerate(design_data["components"]):
                    if not isinstance(comp, dict):
                        errors.append(f"Component {i} must be a dictionary")
                        continue
                    
                    if "name" not in comp:
                        errors.append(f"Component {i} missing 'name' field")
                    if "type" not in comp:
                        errors.append(f"Component {i} missing 'type' field")
                    if "domain_type" not in comp:
                        errors.append(f"Component {i} missing 'domain_type' field")
                    
                    # Validate domain_type
                    if comp.get("domain_type") not in ["Public", "Web", "Application", "Data"]:
                        errors.append(f"Component {i} has invalid domain_type: {comp.get('domain_type')}")
        
        # Validate connections
        if "connections" in design_data:
            if not isinstance(design_data["connections"], list):
                errors.append("'connections' must be a list")
            else:
                component_names = {c.get("name") for c in design_data.get("components", [])}
                
                for i, conn in enumerate(design_data["connections"]):
                    if not isinstance(conn, dict):
                        errors.append(f"Connection {i} must be a dictionary")
                        continue
                    
                    if "source" not in conn:
                        errors.append(f"Connection {i} missing 'source' field")
                    elif conn["source"] not in component_names:
                        errors.append(f"Connection {i} references non-existent source: {conn['source']}")
                    
                    if "destination" not in conn:
                        errors.append(f"Connection {i} missing 'destination' field")
                    elif conn["destination"] not in component_names:
                        errors.append(f"Connection {i} references non-existent destination: {conn['destination']}")
        
        return errors
