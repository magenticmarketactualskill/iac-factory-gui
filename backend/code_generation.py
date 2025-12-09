"""
Code generation endpoints.
"""
from fastapi import APIRouter, HTTPException
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from gui.backend.design_manager import DesignManager
except ImportError:
    from design_manager import DesignManager

router = APIRouter(prefix="/api")
design_manager = DesignManager()


def design_to_factory(design_data):
    """Convert design data to IacFactory instance."""
    # Import iac-factory components
    try:
        # Try package imports first
        from iac_factory.factory import IacFactory
        from iac_factory.components import Gateway, Container, Lambda, Cache, Rdms, Archive
    except ImportError:
        # Fallback for when running as module
        import iac_factory.factory as factory_module
        import iac_factory.components as components_module
        IacFactory = factory_module.IacFactory
        Gateway = components_module.Gateway
        Container = components_module.Container
        Lambda = components_module.Lambda
        Cache = components_module.Cache
        Rdms = components_module.Rdms
        Archive = components_module.Archive
    
    # Try to use enhanced factory if available
    try:
        from gui.backend.enhanced_factory import EnhancedIacFactory
        return EnhancedIacFactory.from_json(design_data)
    except (ImportError, Exception):
        # Fallback: create factory manually
        
        factory = IacFactory(design_data["name"])
        
        # Component type mapping
        component_classes = {
            "Gateway": Gateway,
            "Container": Container,
            "Lambda": Lambda,
            "Cache": Cache,
            "Rdms": Rdms,
            "Archive": Archive
        }
        
        # Add components
        component_map = {}
        for comp_data in design_data.get("components", []):
            comp_class = component_classes.get(comp_data["type"])
            if comp_class:
                component = comp_class(
                    name=comp_data["name"],
                    domain_type=comp_data["domain_type"],
                    technology=comp_data.get("technology", "")
                )
                factory.add_component(component)
                component_map[comp_data["name"]] = component
        
        # Add connections
        for conn_data in design_data.get("connections", []):
            source = component_map.get(conn_data["source"])
            destination = component_map.get(conn_data["destination"])
            if source and destination:
                factory.add_connection(
                    source=source,
                    destination=destination,
                    label=conn_data.get("label", ""),
                    technology=conn_data.get("technology", "")
                )
        
        return factory


@router.post("/designs/{design_id}/generate/mermaid")
async def generate_mermaid(design_id: str):
    """Generate Mermaid diagram from design."""
    try:
        design = design_manager.load_design(design_id)
        factory = design_to_factory(design)
        
        mermaid_code = factory.generate_mermaid_diagram()
        
        return {
            "code": mermaid_code,
            "format": "mermaid"
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Design {design_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/designs/{design_id}/generate/pulumi")
async def generate_pulumi(design_id: str):
    """Generate Pulumi code from design."""
    try:
        design = design_manager.load_design(design_id)
        factory = design_to_factory(design)
        
        pulumi_code = factory.generate_pulumi_code()
        
        return {
            "code": pulumi_code,
            "format": "python"
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Design {design_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/designs/{design_id}/generate/cdk")
async def generate_cdk(design_id: str):
    """Generate AWS CDK code from design."""
    try:
        design = design_manager.load_design(design_id)
        factory = design_to_factory(design)
        
        cdk_code = factory.generate_cdk_code()
        
        return {
            "code": cdk_code,
            "format": "python"
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Design {design_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
