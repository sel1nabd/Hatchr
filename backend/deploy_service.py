"""
Deployment Service - Render.com Integration
Handles automatic deployment of generated backends to Render
"""

import os
from typing import Dict, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

RENDER_API_KEY = os.getenv("RENDER_API_KEY", "")
RENDER_API_URL = "https://api.render.com/v1"


class RenderDeployer:
    """Handles deployment to Render.com via their API"""

    @staticmethod
    def deploy_project(
        project_id: str, project_name: str, zip_download_url: str
    ) -> Dict:
        """
        Deploy a project to Render using their tarball/zip API

        Args:
            project_id: Unique project identifier
            project_name: Human-readable project name
            zip_download_url: Public URL where Render can download the zip
                            (e.g., "https://your-app.com/download/{project_id}")

        Returns:
            {
                "service_id": str,
                "service_name": str,
                "live_url": str,
                "dashboard_url": str
            }
        """

        print("=" * 80)
        print("🚀 DEPLOYING TO RENDER.COM")
        print(f"   Project: {project_name}")
        print(f"   Project ID: {project_id}")
        print(f"   Zip URL: {zip_download_url}")
        print("=" * 80)

        if not RENDER_API_KEY:
            raise ValueError("RENDER_API_KEY not found in environment variables")

        # Generate a safe service name (Render requires lowercase alphanumeric + hyphens)
        safe_name = f"hatchr-{project_name.lower().replace(' ', '-')}-{project_id[:8]}"

        # Render API payload
        payload = {
            "type": "web_service",
            "name": safe_name,
            "runtime": "python",
            "plan": "free",
            "region": "oregon",  # Free tier region
            "branch": "main",
            "buildCommand": "pip install -r requirements.txt",
            "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
            "envVars": [{"key": "PYTHON_VERSION", "value": "3.11.0"}],
            "serviceDetails": {"tarballUrl": zip_download_url, "tarballBranch": "main"},
        }

        headers = {
            "Authorization": f"Bearer {RENDER_API_KEY}",
            "Content-Type": "application/json",
        }

        print("🔄 Sending deployment request to Render API...")
        print(f"   Service Name: {safe_name}")
        print(f"   Runtime: Python")
        print(f"   Plan: Free")

        try:
            response = requests.post(
                f"{RENDER_API_URL}/services", json=payload, headers=headers, timeout=30
            )

            response.raise_for_status()
            result = response.json()

            service_id = result["service"]["id"]
            service_url = result["service"].get("serviceDetails", {}).get("url", "")

            # If URL not in response, construct it from service name
            if not service_url:
                service_url = f"https://{safe_name}.onrender.com"

            dashboard_url = f"https://dashboard.render.com/web/{service_id}"

            print("✅ DEPLOYMENT SUCCESSFUL!")
            print(f"   Service ID: {service_id}")
            print(f"   Live URL: {service_url}")
            print(f"   Dashboard: {dashboard_url}")
            print("=" * 80)

            return {
                "service_id": service_id,
                "service_name": safe_name,
                "live_url": service_url,
                "dashboard_url": dashboard_url,
                "status": "deploying",
            }

        except requests.exceptions.HTTPError as e:
            error_detail = e.response.text if e.response else str(e)
            print(f"❌ RENDER API ERROR: {e}")
            print(f"   Status Code: {e.response.status_code if e.response else 'N/A'}")
            print(f"   Response: {error_detail}")
            print("=" * 80)

            raise Exception(f"Render deployment failed: {error_detail}")

        except Exception as e:
            print(f"❌ DEPLOYMENT FAILED: {str(e)}")
            print("=" * 80)
            raise

    @staticmethod
    def get_service_status(service_id: str) -> Optional[Dict]:
        """
        Check the deployment status of a Render service

        Args:
            service_id: The Render service ID

        Returns:
            {
                "status": "live" | "deploying" | "failed",
                "url": str,
                "last_deploy": str
            }
        """

        if not RENDER_API_KEY:
            return None

        headers = {"Authorization": f"Bearer {RENDER_API_KEY}"}

        try:
            response = requests.get(
                f"{RENDER_API_URL}/services/{service_id}", headers=headers, timeout=10
            )

            response.raise_for_status()
            result = response.json()

            service = result.get("service", {})

            return {
                "status": service.get("status", "unknown"),
                "url": service.get("serviceDetails", {}).get("url", ""),
                "last_deploy": service.get("updatedAt", ""),
            }

        except Exception as e:
            print(f"⚠️  Could not fetch service status: {str(e)}")
            return None


class DeploymentManager:
    """High-level deployment orchestration"""

    @staticmethod
    def deploy_to_render(project_id: str, project_name: str, base_url: str) -> Dict:
        """
        Deploy a generated project to Render

        Args:
            project_id: Project UUID
            project_name: Human-readable name
            base_url: Base URL of your Hatchr API (e.g., "https://hatchr.onrender.com")

        Returns:
            Deployment info with live_url
        """

        # Construct the download URL for the zip
        zip_download_url = f"{base_url}/download/{project_id}"

        print(f"\n🌐 ZIP Download URL: {zip_download_url}")
        print("   (Render will fetch the zip from this URL)\n")

        # Deploy to Render
        deployment = RenderDeployer.deploy_project(
            project_id=project_id,
            project_name=project_name,
            zip_download_url=zip_download_url,
        )

        return deployment
