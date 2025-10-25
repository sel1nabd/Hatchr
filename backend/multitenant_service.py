"""
Multi-Tenant Hosting Service
Hosts all generated FastAPI projects from a single Hatchr deployment
"""

import os
import sys
import io
import tempfile
import logging
from typing import Dict, Optional
from contextlib import redirect_stdout, redirect_stderr
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import importlib.util
import traceback
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("multitenant_host")


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

        logger.info(f"=" * 80)
        logger.info(f"🔄 LOADING PROJECT INTO MULTI-TENANT HOST")
        logger.info(f"   Project Name: {project_name}")
        logger.info(f"   Project ID: {project_id}")
        logger.info(f"   Code Length: {len(main_py_code)} characters")
        logger.info(f"=" * 80)

        try:
            # Create a temporary module to execute the generated code
            module_name = f"generated_project_{project_id.replace('-', '_')}"
            logger.info(f"📦 Creating module: {module_name}")

            # Create module spec
            spec = importlib.util.spec_from_loader(module_name, loader=None)
            if spec is None:
                logger.error(f"❌ Failed to create module spec for {module_name}")
                raise Exception("Failed to create module spec")

            module = importlib.util.module_from_spec(spec)
            logger.info(f"✅ Module created successfully")

            # Capture stdout/stderr during execution
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()

            logger.info(f"⚙️  Executing generated code...")

            # Execute the code in the module's namespace
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(main_py_code, module.__dict__)

            # Log any output from code execution
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()

            if stdout_output:
                logger.info(f"📝 Code execution stdout:\n{stdout_output[:500]}")
            if stderr_output:
                logger.warning(f"⚠️  Code execution stderr:\n{stderr_output[:500]}")

            # Extract the FastAPI app instance
            # Generated code should have: app = FastAPI(...)
            if not hasattr(module, 'app'):
                logger.error(f"❌ Generated code does not contain 'app' variable")
                logger.error(f"   Available attributes: {[attr for attr in dir(module) if not attr.startswith('_')]}")
                raise Exception("Generated code does not contain 'app = FastAPI()' instance")

            generated_app = module.app
            logger.info(f"✅ Found FastAPI app instance in generated code")

            # Count routes in generated app
            route_count = len(generated_app.routes)
            logger.info(f"📊 Generated app has {route_count} routes")

            # Store the app
            self.hosted_apps[project_id] = generated_app
            self.app_metadata[project_id] = {
                "project_name": project_name,
                "module": module,
                "loaded_at": datetime.utcnow().isoformat(),
                "route_count": route_count
            }

            logger.info(f"=" * 80)
            logger.info(f"✅ SUCCESSFULLY LOADED PROJECT: {project_name}")
            logger.info(f"   Total hosted projects: {len(self.hosted_apps)}")
            logger.info(f"=" * 80)

            return True

        except Exception as e:
            logger.error(f"=" * 80)
            logger.error(f"❌ FAILED TO LOAD PROJECT: {project_name}")
            logger.error(f"   Error: {str(e)}")
            logger.error(f"   Traceback:\n{traceback.format_exc()}")
            logger.error(f"=" * 80)
            return False

    def get_app(self, project_id: str) -> Optional[FastAPI]:
        """Get a hosted FastAPI app by project ID"""
        app = self.hosted_apps.get(project_id)
        if app:
            logger.debug(f"✅ Found app for project {project_id}")
        else:
            logger.warning(f"⚠️  No app found for project {project_id}")
        return app

    def list_hosted_projects(self) -> Dict[str, Dict]:
        """List all currently hosted projects"""
        logger.info(f"📋 Listing {len(self.hosted_apps)} hosted projects")
        return {
            project_id: {
                "project_name": metadata["project_name"],
                "routes": [route.path for route in app.routes],
                "loaded_at": metadata.get("loaded_at"),
                "route_count": metadata.get("route_count", 0)
            }
            for project_id, metadata in self.app_metadata.items()
            for app in [self.hosted_apps[project_id]]
        }

    def unload_project(self, project_id: str) -> bool:
        """Unload a project from memory"""
        if project_id in self.hosted_apps:
            project_name = self.app_metadata[project_id].get("project_name", "Unknown")
            del self.hosted_apps[project_id]
            del self.app_metadata[project_id]
            logger.info(f"🗑️  Unloaded project: {project_name} ({project_id})")
            logger.info(f"   Remaining projects: {len(self.hosted_apps)}")
            return True
        else:
            logger.warning(f"⚠️  Cannot unload - project not found: {project_id}")
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

    logger.info(f"=" * 80)
    logger.info(f"🔀 ROUTING REQUEST TO GENERATED PROJECT")
    logger.info(f"   Project ID: {project_id}")
    logger.info(f"   Method: {request.method}")
    logger.info(f"   Path: {request.url.path}")
    logger.info(f"   Query Params: {dict(request.query_params)}")
    logger.info(f"=" * 80)

    # Get the hosted app
    app = multitenant_host.get_app(project_id)

    if not app:
        logger.error(f"❌ Project {project_id} not found in multi-tenant host")
        logger.error(f"   Available projects: {list(multitenant_host.hosted_apps.keys())}")
        raise HTTPException(
            status_code=404,
            detail=f"Project {project_id} not found or not loaded"
        )

    logger.info(f"✅ Found app for project {project_id}")

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

    logger.info(f"🎯 Routing to generated app path: {target_path}")

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
        logger.info(f"📡 Calling generated app...")
        # Use the app's router to find and call the appropriate endpoint
        response = await app(scope, request.receive, request._send)

        logger.info(f"=" * 80)
        logger.info(f"✅ SUCCESSFULLY ROUTED TO GENERATED PROJECT")
        logger.info(f"   Project: {project_id}")
        logger.info(f"   Target Path: {target_path}")
        logger.info(f"=" * 80)

        return response

    except Exception as e:
        logger.error(f"=" * 80)
        logger.error(f"❌ ERROR ROUTING TO GENERATED PROJECT")
        logger.error(f"   Project ID: {project_id}")
        logger.error(f"   Target Path: {target_path}")
        logger.error(f"   Error: {str(e)}")
        logger.error(f"   Traceback:\n{traceback.format_exc()}")
        logger.error(f"=" * 80)
        raise HTTPException(status_code=500, detail=f"Internal error in generated project: {str(e)}")
