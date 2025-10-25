"""
Railway Deployment Service
Handles automatic deployment of generated backends to Railway.app
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

RAILWAY_API_TOKEN = os.getenv("RAILWAY_API_TOKEN", "") or os.getenv("RAILWAY_TOKEN", "")
RAILWAY_PROJECT_ID = os.getenv("RAILWAY_PROJECT_ID", "")


class RailwayDeployer:
    """Handles deployment to Railway.app using CLI"""

    @staticmethod
    def deploy_project(
        project_path: Path,
        project_name: str,
        project_id: str
    ) -> Dict:
        """
        Deploy a generated project to Railway using CLI

        Args:
            project_path: Path to the project directory
            project_name: Human-readable project name
            project_id: Unique project identifier (UUID)

        Returns:
            {
                "service_id": str,
                "service_name": str,
                "live_url": str,
                "deployment_id": str
            }
        """

        print("="*80)
        print("🚀 DEPLOYING TO RAILWAY.APP")
        print(f"   Project: {project_name}")
        print(f"   Project ID: {project_id}")
        print(f"   Directory: {project_path}")
        print("="*80)

        if not RAILWAY_API_TOKEN:
            raise ValueError("RAILWAY_API_TOKEN not found in environment variables")

        if not RAILWAY_PROJECT_ID:
            raise ValueError("RAILWAY_PROJECT_ID not found in environment variables")

        # Set environment variables for Railway CLI
        env = os.environ.copy()
        env["RAILWAY_TOKEN"] = RAILWAY_API_TOKEN

        try:
            # Change to project directory
            os.chdir(project_path)

            # Check if railway CLI is installed
            print("🔍 Checking Railway CLI installation...")
            result = subprocess.run(
                ["railway", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                raise Exception("Railway CLI not installed. Run: npm i -g @railway/cli")

            print(f"   ✅ Railway CLI version: {result.stdout.strip()}")

            # Link to Railway project
            print(f"\n🔗 Linking to Railway project: {RAILWAY_PROJECT_ID}")
            result = subprocess.run(
                ["railway", "link", "--project", RAILWAY_PROJECT_ID],
                env=env,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                print(f"   ⚠️  Link output: {result.stdout}")
                print(f"   ⚠️  Link error: {result.stderr}")
                # Continue anyway - might already be linked
            else:
                print(f"   ✅ Linked to project")

            # Deploy using railway up
            print("\n📦 Deploying with 'railway up'...")
            print("   (This may take 1-3 minutes)")

            result = subprocess.run(
                ["railway", "up", "--detach"],
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )

            print(f"\n   Railway Output:")
            print(f"   {result.stdout}")

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                print(f"❌ RAILWAY DEPLOYMENT FAILED")
                print(f"   Error: {error_msg}")
                print("="*80)
                raise Exception(f"Railway deployment failed: {error_msg}")

            # Get the deployment URL
            print("\n🌐 Getting deployment URL...")
            result = subprocess.run(
                ["railway", "status", "--json"],
                env=env,
                capture_output=True,
                text=True,
                timeout=30
            )

            deployment_info = {}
            if result.returncode == 0:
                try:
                    deployment_info = json.loads(result.stdout)
                except:
                    pass

            # Generate service URL (Railway format)
            # Note: Actual URL comes from Railway after deployment
            service_name = project_name.lower().replace(" ", "-")
            live_url = deployment_info.get("url", f"https://{service_name}-production.up.railway.app")

            print("✅ DEPLOYMENT SUCCESSFUL!")
            print(f"   Live URL: {live_url}")
            print(f"   Project: https://railway.app/project/{RAILWAY_PROJECT_ID}")
            print("="*80)

            return {
                "service_id": project_id,
                "service_name": service_name,
                "live_url": live_url,
                "deployment_id": project_id,
                "project_url": f"https://railway.app/project/{RAILWAY_PROJECT_ID}",
                "status": "deployed"
            }

        except subprocess.TimeoutExpired:
            print("❌ DEPLOYMENT TIMEOUT")
            print("   Railway deployment took too long (>5 minutes)")
            print("="*80)
            raise Exception("Railway deployment timeout after 5 minutes")

        except Exception as e:
            print(f"❌ DEPLOYMENT FAILED: {str(e)}")
            print("="*80)
            raise


class DeploymentManager:
    """High-level deployment orchestration for Railway"""

    @staticmethod
    def deploy_to_railway(
        project_path: str,
        project_name: str,
        project_id: str
    ) -> Dict:
        """
        Deploy a generated project to Railway

        Args:
            project_path: Path to project directory (str)
            project_name: Human-readable name
            project_id: Project UUID

        Returns:
            Deployment info with live_url
        """

        path = Path(project_path)

        # Deploy to Railway
        deployment = RailwayDeployer.deploy_project(
            project_path=path,
            project_name=project_name,
            project_id=project_id
        )

        return deployment
