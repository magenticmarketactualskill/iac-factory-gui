"""
API routes for the GUI backend.
"""
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

try:
    from gui.backend.design_manager import DesignManager
except ImportError:
    from design_manager import DesignManager

router = APIRouter(prefix="/api")
design_manager = DesignManager()


# Request/Response Models
class CreateDesignRequest(BaseModel):
    name: str


class ComponentRequest(BaseModel):
    name: str
    type: str
    domain_type: str
    technology: str = ""


class ConnectionRequest(BaseModel):
    source: str
    destination: str
    label: str = ""
    technology: str = ""


class UpdateComponentRequest(BaseModel):
    name: Optional[str] = None
    domain_type: Optional[str] = None
    technology: Optional[str] = None


class UpdateConnectionRequest(BaseModel):
    label: Optional[str] = None
    technology: Optional[str] = None


# Design Management Endpoints
@router.post("/designs")
async def create_design(request: CreateDesignRequest):
    """Create a new infrastructure design."""
    try:
        design = design_manager.create_design(request.name)
        return design
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/designs/{design_id}")
async def get_design(design_id: str):
    """Load an existing design."""
    try:
        design = design_manager.load_design(design_id)
        return design
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Design {design_id} not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/designs/{design_id}")
async def update_design(design_id: str, design_data: Dict[str, Any] = Body(...)):
    """Update an existing design."""
    try:
        # Ensure design_id matches
        design_data["design_id"] = design_id
        
        # Validate
        errors = design_manager.validate_design(design_data)
        if errors:
            raise HTTPException(status_code=400, detail={"errors": errors})
        
        # Save
        design_manager.save_design(design_data)
        return design_data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/designs/{design_id}")
async def delete_design(design_id: str):
    """Delete a design."""
    try:
        design_manager.delete_design(design_id)
        return {"message": "Design deleted successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Design {design_id} not found")


@router.get("/designs")
async def list_designs():
    """List all available designs."""
    designs = design_manager.list_designs()
    return {"designs": designs}


# Component Operations
@router.post("/designs/{design_id}/components")
async def add_component(design_id: str, component: ComponentRequest):
    """Add a component to a design."""
    try:
        design = design_manager.load_design(design_id)
        
        # Check for duplicate names
        if any(c["name"] == component.name for c in design["components"]):
            raise HTTPException(status_code=400, detail=f"Component '{component.name}' already exists")
        
        # Validate domain_type
        if component.domain_type not in ["Public", "Web", "Application", "Data"]:
            raise HTTPException(status_code=400, detail=f"Invalid domain_type: {component.domain_type}")
        
        # Add component
        design["components"].append({
            "name": component.name,
            "type": component.type,
            "domain_type": component.domain_type,
            "technology": component.technology
        })
        
        design_manager.save_design(design)
        return design
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Design {design_id} not found")


@router.put("/designs/{design_id}/components/{component_name}")
async def update_component(design_id: str, component_name: str, updates: UpdateComponentRequest):
    """Update a component in a design."""
    try:
        design = design_manager.load_design(design_id)
        
        # Find component
        component = None
        for c in design["components"]:
            if c["name"] == component_name:
                component = c
                break
        
        if not component:
            raise HTTPException(status_code=404, detail=f"Component '{component_name}' not found")
        
        # Apply updates
        if updates.name is not None:
            # Check for duplicate names
            if any(c["name"] == updates.name and c["name"] != component_name for c in design["components"]):
                raise HTTPException(status_code=400, detail=f"Component '{updates.name}' already exists")
            
            # Update connections that reference this component
            for conn in design["connections"]:
                if conn["source"] == component_name:
                    conn["source"] = updates.name
                if conn["destination"] == component_name:
                    conn["destination"] = updates.name
            
            component["name"] = updates.name
        
        if updates.domain_type is not None:
            if updates.domain_type not in ["Public", "Web", "Application", "Data"]:
                raise HTTPException(status_code=400, detail=f"Invalid domain_type: {updates.domain_type}")
            component["domain_type"] = updates.domain_type
        
        if updates.technology is not None:
            component["technology"] = updates.technology
        
        design_manager.save_design(design)
        return design
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Design {design_id} not found")


@router.delete("/designs/{design_id}/components/{component_name}")
async def delete_component(design_id: str, component_name: str):
    """Delete a component from a design."""
    try:
        design = design_manager.load_design(design_id)
        
        # Find and remove component
        original_count = len(design["components"])
        design["components"] = [c for c in design["components"] if c["name"] != component_name]
        
        if len(design["components"]) == original_count:
            raise HTTPException(status_code=404, detail=f"Component '{component_name}' not found")
        
        # Remove connections involving this component
        design["connections"] = [
            c for c in design["connections"]
            if c["source"] != component_name and c["destination"] != component_name
        ]
        
        design_manager.save_design(design)
        return design
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Design {design_id} not found")


# Connection Operations
@router.post("/designs/{design_id}/connections")
async def add_connection(design_id: str, connection: ConnectionRequest):
    """Add a connection to a design."""
    try:
        design = design_manager.load_design(design_id)
        
        # Validate source and destination exist
        component_names = {c["name"] for c in design["components"]}
        
        if connection.source not in component_names:
            raise HTTPException(status_code=400, detail=f"Source component '{connection.source}' not found")
        
        if connection.destination not in component_names:
            raise HTTPException(status_code=400, detail=f"Destination component '{connection.destination}' not found")
        
        # Add connection
        design["connections"].append({
            "source": connection.source,
            "destination": connection.destination,
            "label": connection.label,
            "technology": connection.technology
        })
        
        design_manager.save_design(design)
        return design
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Design {design_id} not found")


@router.put("/designs/{design_id}/connections/{connection_index}")
async def update_connection(design_id: str, connection_index: int, updates: UpdateConnectionRequest):
    """Update a connection in a design."""
    try:
        design = design_manager.load_design(design_id)
        
        if connection_index < 0 or connection_index >= len(design["connections"]):
            raise HTTPException(status_code=404, detail=f"Connection {connection_index} not found")
        
        connection = design["connections"][connection_index]
        
        if updates.label is not None:
            connection["label"] = updates.label
        
        if updates.technology is not None:
            connection["technology"] = updates.technology
        
        design_manager.save_design(design)
        return design
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Design {design_id} not found")


@router.delete("/designs/{design_id}/connections/{connection_index}")
async def delete_connection(design_id: str, connection_index: int):
    """Delete a connection from a design."""
    try:
        design = design_manager.load_design(design_id)
        
        if connection_index < 0 or connection_index >= len(design["connections"]):
            raise HTTPException(status_code=404, detail=f"Connection {connection_index} not found")
        
        design["connections"].pop(connection_index)
        
        design_manager.save_design(design)
        return design
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Design {design_id} not found")
