"""
Multi-Tenant Hosting Service
Hosts all generated FastAPI projects from a single Hatchr deployment
"""

import os
import sys
import io
import tempfile
from typing import Dict, Optional
from contextlib import redirect_stdout, redirect_stderr
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import importlib.util
import traceback


class MultiTenantHost:
    """
    Manages multiple generated FastAPI apps within a single process
    Each generated project gets its own FastAPI sub-application
    """

    def __init__(self):
        self.hosted_apps: Dict[str, FastAPI] = {}
        self.app_metadata: Dict[str, Dict] = {}

    def load_project_app(self, project_id: str, main_py_code: str, project_name: str) -> bool:
        """
        Load a generated project's FastAPI app into memory

        Args:
            project_id: Unique project identifier
            main_py_code: The generated main.py code
            project_name: Human-readable project name

        Returns:
            True if successfully loaded, False otherwise
        """

        try:
            print(f"🔄 Loading project: {project_name} ({project_id})")

            # Create a temporary module to execute the generated code
            module_name = f"generated_project_{project_id.replace('-', '_')}"

            # Create module spec
            spec = importlib.util.spec_from_loader(module_name, loader=None)
            if spec is None:
                raise Exception("Failed to create module spec")

            module = importlib.util.module_from_spec(spec)

            # Capture stdout/stderr during execution
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()

            # Execute the code in the module's namespace
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(main_py_code, module.__dict__)

            # Extract the FastAPI app instance
            # Generated code should have: app = FastAPI(...)
            if not hasattr(module, 'app'):
                raise Exception("Generated code does not contain 'app = FastAPI()' instance")

            generated_app = module.app

            # Store the app
            self.hosted_apps[project_id] = generated_app
            self.app_metadata[project_id] = {
                "project_name": project_name,
                "module": module,
                "loaded_at": None  # You can add timestamp if needed
            }

            print(f"✅ Successfully loaded: {project_name}")
            return True

        except Exception as e:
            print(f"❌ Failed to load {project_name}: {str(e)}")
            traceback.print_exc()
            return False

    def get_app(self, project_id: str) -> Optional[FastAPI]:
        """Get a hosted FastAPI app by project ID"""
        return self.hosted_apps.get(project_id)

    def list_hosted_projects(self) -> Dict[str, Dict]:
        """List all currently hosted projects"""
        return {
            project_id: {
                "project_name": metadata["project_name"],
                "routes": [route.path for route in app.routes]
            }
            for project_id, metadata in self.app_metadata.items()
            for app in [self.hosted_apps[project_id]]
        }

    def unload_project(self, project_id: str) -> bool:
        """Unload a project from memory"""
        if project_id in self.hosted_apps:
            del self.hosted_apps[project_id]
            del self.app_metadata[project_id]
            print(f"🗑️  Unloaded project: {project_id}")
            return True
        return False


# Global instance
multitenant_host = MultiTenantHost()


async def route_to_generated_project(
    project_id: str,
    request: Request
) -> Response:
    """
    Route incoming requests to the appropriate generated project

    Args:
        project_id: The project identifier
        request: The incoming FastAPI request

    Returns:
        Response from the generated app
    """

    # Get the hosted app
    app = multitenant_host.get_app(project_id)

    if not app:
        raise HTTPException(
            status_code=404,
            detail=f"Project {project_id} not found or not loaded"
        )

    # Extract path without the /projects/{project_id} prefix
    # Request path will be like: /projects/{project_id}/items
    # We want to route to: /items in the generated app
    original_path = request.url.path
    project_prefix = f"/projects/{project_id}"

    if original_path.startswith(project_prefix):
        # Remove the prefix
        target_path = original_path[len(project_prefix):]
        if not target_path:
            target_path = "/"
    else:
        target_path = original_path

    # Create a new request scope for the generated app
    scope = dict(request.scope)
    scope["path"] = target_path
    scope["root_path"] = project_prefix

    # Import ASGI utilities
    from starlette.requests import Request as StarletteRequest
    from starlette.datastructures import Headers

    # Create a new request for the generated app
    generated_request = StarletteRequest(scope, request.receive)

    # Call the generated app and get the response
    try:
        # Use the app's router to find and call the appropriate endpoint
        response = await app(scope, request.receive, request._send)
        return response

    except Exception as e:
        print(f"❌ Error routing to generated project {project_id}: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error in generated project: {str(e)}")
