"""
Deployment Service - Multi-Tenant Hosting
Handles deployment of generated backends within the same Hatchr instance
No external API calls needed - all projects hosted from single deployment
"""

import os
import logging
from typing import Dict, Optional

from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("deploy_service")

# Legacy environment variables (kept for backward compatibility)
RENDER_API_KEY = os.getenv("RENDER_API_KEY", "")
RENDER_API_URL = "https://api.render.com/v1"


class MultiTenantDeployer:
    """Handles multi-tenant hosting within the same Hatchr instance"""

    @staticmethod
    def deploy_project(
        project_id: str,
        project_name: str,
        base_url: str,
        main_py_code: str
    ) -> Dict:
        """
        Deploy a project to multi-tenant hosting (same Hatchr instance)

        Args:
            project_id: Unique project identifier
            project_name: Human-readable project name
            base_url: Base URL of Hatchr deployment (e.g., "https://hatchr.onrender.com")
            main_py_code: The generated main.py code to host

        Returns:
            {
                "service_id": str (same as project_id),
                "service_name": str,
                "live_url": str,
                "api_docs_url": str,
                "status": str
            }
        """

        logger.info("=" * 80)
        logger.info("🚀 DEPLOYING TO MULTI-TENANT HOST")
        logger.info(f"   Project: {project_name}")
        logger.info(f"   Project ID: {project_id}")
        logger.info(f"   Base URL: {base_url}")
        logger.info(f"   Code Length: {len(main_py_code)} characters")
        logger.info("=" * 80)

        # Import the multi-tenant host
        from multitenant_service import multitenant_host

        logger.info(f"📦 Loading project into multi-tenant host...")

        # Load the project into the host
        success = multitenant_host.load_project_app(
            project_id=project_id,
            main_py_code=main_py_code,
            project_name=project_name
        )

        if not success:
            logger.error(f"❌ Failed to load project into multi-tenant host")
            raise Exception(f"Failed to load project {project_name} into multi-tenant host")

        logger.info(f"✅ Project loaded successfully")

        # Construct URLs
        live_url = f"{base_url}/projects/{project_id}"
        api_docs_url = f"{base_url}/projects/{project_id}/docs"

        logger.info("=" * 80)
        logger.info("✅ DEPLOYMENT SUCCESSFUL!")
        logger.info(f"   Service ID: {project_id}")
        logger.info(f"   Live URL: {live_url}")
        logger.info(f"   API Docs: {api_docs_url}")
        logger.info(f"   Hosting Type: Multi-Tenant")
        logger.info("=" * 80)

        return {
            "service_id": project_id,
            "service_name": project_name,
            "live_url": live_url,
            "api_docs_url": api_docs_url,
            "status": "live",
            "hosting_type": "multi-tenant"
        }

    @staticmethod
    def get_service_status(project_id: str) -> Optional[Dict]:
        """
        Check if a project is currently loaded in multi-tenant host

        Args:
            project_id: The project ID

        Returns:
            {
                "status": "live" | "not_loaded",
                "url": str
            }
        """

        from multitenant_service import multitenant_host

        logger.info(f"🔍 Checking status of project: {project_id}")

        app = multitenant_host.get_app(project_id)

        if app:
            base_url = os.getenv("HATCHR_PUBLIC_URL", "http://localhost:8001")
            logger.info(f"✅ Project {project_id} is LIVE")
            return {
                "status": "live",
                "url": f"{base_url}/projects/{project_id}",
            }
        else:
            logger.warning(f"⚠️  Project {project_id} is NOT LOADED")
            return {
                "status": "not_loaded",
                "url": "",
            }


# Keep RenderDeployer as alias for backward compatibility
RenderDeployer = MultiTenantDeployer


class DeploymentManager:
    """High-level deployment orchestration"""

    @staticmethod
    def deploy_to_multitenant(project_id: str, project_name: str, base_url: str, main_py_code: str) -> Dict:
        """
        Deploy a generated project to multi-tenant hosting

        Args:
            project_id: Project UUID
            project_name: Human-readable name
            base_url: Base URL of your Hatchr API (e.g., "https://hatchr.onrender.com")
            main_py_code: The generated main.py code

        Returns:
            Deployment info with live_url
        """

        logger.info(f"\n🌐 MULTI-TENANT DEPLOYMENT MANAGER")
        logger.info(f"   Base URL: {base_url}")
        logger.info(f"   Project: {project_name}\n")

        # Deploy to multi-tenant host
        deployment = MultiTenantDeployer.deploy_project(
            project_id=project_id,
            project_name=project_name,
            base_url=base_url,
            main_py_code=main_py_code
        )

        logger.info(f"✅ Deployment manager completed")
        logger.info(f"   Deployment URL: {deployment.get('live_url')}")

        return deployment
