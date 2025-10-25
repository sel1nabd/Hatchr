"""
Generation Service - GPT-4o Enrichment + Sonnet 4.5 Code Generation
Flow: User idea → GPT-4o enriches → Sonnet generates FastAPI + SQLite → Deploy
"""

import os
import json
import uuid
import zipfile
from pathlib import Path
from typing import Dict, Callable
from openai import AsyncOpenAI
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize clients
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

def get_openai_client():
    """Lazy initialization of OpenAI client"""
    return AsyncOpenAI(api_key=OPENAI_API_KEY if OPENAI_API_KEY else None)

def get_anthropic_client():
    """Lazy initialization of Anthropic client"""
    return Anthropic(api_key=ANTHROPIC_API_KEY if ANTHROPIC_API_KEY else None)


class PromptEnricher:
    """GPT-4o for enriching user prompts with examples, context, and specifications"""

    @staticmethod
    async def enrich_prompt(user_idea: str) -> Dict:
        """
        Use GPT-4o to research and enrich the user's startup idea

        Returns:
            {
                "enriched_prompt": "Detailed prompt for code generation",
                "project_name": "Short project name",
                "description": "Brief description",
                "example_companies": ["Company1", "Company2", ...],
                "key_features": ["Feature1", "Feature2", ...]
            }
        """

        print("="*80)
        print("🔵 GPT-4O PROMPT ENRICHMENT STARTING")
        print(f"📥 USER IDEA: {user_idea}")
        print("="*80)

        system_prompt = """You are an expert product analyst and technical architect.

Your job is to take a raw startup idea and research it thoroughly to create a detailed technical specification.

Output JSON format:
{
  "project_name": "Short, catchy project name (2-3 words max)",
  "description": "One sentence description",
  "example_companies": ["Real competitor 1", "Real competitor 2", "Real competitor 3"],
  "market_context": "Brief market analysis (2-3 sentences)",
  "key_features": ["Core feature 1", "Core feature 2", "Core feature 3", "Core feature 4", "Core feature 5"],
  "database_schema": "Simple description of what tables/models are needed",
  "api_endpoints": ["GET /items", "POST /items", "GET /items/{id}", "PUT /items/{id}", "DELETE /items/{id}"],
  "enriched_prompt": "A MEGA DETAILED prompt that includes: the idea, market context, example companies, typical features from those companies, database schema, API endpoints, and tech requirements. This will be fed to an AI code generator."
}

Research the space, find real competitors, identify common patterns, and create a rich, detailed specification."""

        user_prompt = f"""Research and enrich this startup idea:

"{user_idea}"

Steps:
1. Identify what market/space this is in
2. Find 3-5 real competitor companies in this space
3. Analyze what features those competitors typically have
4. Design a simple database schema (3-5 tables max)
5. List essential API endpoints (CRUD operations)
6. Create a DETAILED enriched prompt that includes ALL of this context

IMPORTANT: Keep the backend SIMPLE and FOCUSED. This is an MVP/demo.
- SQLite database (file-based)
- FastAPI backend
- 5-10 REST API endpoints max
- No authentication (for simplicity)
- Focus on core functionality only

Return as JSON."""

        client = get_openai_client()

        print("🔄 Calling OpenAI GPT-4o...")

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )

        result = json.loads(response.choices[0].message.content)

        print("✅ GPT-4o ENRICHMENT COMPLETE")
        print(f"   Project: {result.get('project_name', 'N/A')}")
        print(f"   Examples: {', '.join(result.get('example_companies', []))}")
        print(f"   Features: {len(result.get('key_features', []))} identified")
        print(f"   Enriched Prompt Length: {len(result.get('enriched_prompt', ''))} chars")
        print("="*80)

        return result


class CodeGenerator:
    """Sonnet 4.5 for generating complete FastAPI + SQLite codebases"""

    @staticmethod
    def generate_code(enriched_spec: Dict) -> Dict[str, str]:
        """
        Use Sonnet 4.5 to generate a complete FastAPI + SQLite backend

        Args:
            enriched_spec: Output from PromptEnricher

        Returns:
            Dict of filename -> file contents
            {
                "main.py": "...",
                "requirements.txt": "...",
                "README.md": "..."
            }
        """

        print("="*80)
        print("🟣 SONNET 4.5 CODE GENERATION STARTING")
        print(f"📥 Project: {enriched_spec.get('project_name', 'N/A')}")
        print("="*80)

        prompt = f"""You are an expert Python backend developer. Generate a complete, production-ready FastAPI + SQLite backend.

## Project Specification:
{enriched_spec['enriched_prompt']}

## Technical Requirements:
- **Framework**: FastAPI (latest version)
- **Database**: SQLite (file-based, no external DB)
- **File Structure**: Single file (main.py) for simplicity
- **CORS**: Enabled for all origins
- **Port**: Must use PORT environment variable: `port = int(os.getenv("PORT", 8000))`
- **Auto-docs**: FastAPI will auto-generate /docs
- **Deployment**: Must work on Render.com free tier

## Database Schema:
{enriched_spec.get('database_schema', 'Design appropriate tables')}

## API Endpoints:
{chr(10).join(f"- {endpoint}" for endpoint in enriched_spec.get('api_endpoints', []))}

## Key Features to Implement:
{chr(10).join(f"- {feature}" for feature in enriched_spec.get('key_features', []))}

## CRITICAL OUTPUT FORMAT:
You MUST output files in this EXACT format:

FILE: main.py
```python
# Your FastAPI code here
# Must include:
# - from fastapi import FastAPI
# - SQLite database setup with SQLAlchemy
# - All CRUD endpoints
# - CORS middleware
# - Port from environment variable
```

FILE: requirements.txt
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
```

FILE: README.md
```markdown
# {enriched_spec.get('project_name', 'Project')}

{enriched_spec.get('description', 'Description')}

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run the server: `uvicorn main:app --reload`
3. Visit API docs: http://localhost:8000/docs

## API Endpoints
{chr(10).join(f"- {endpoint}" for endpoint in enriched_spec.get('api_endpoints', []))}
```

Generate complete, working, immediately deployable code. No placeholders. No TODOs. Production-ready."""

        client = get_anthropic_client()

        print("🔄 Calling Anthropic Sonnet 4.5...")
        print(f"   Model: claude-sonnet-4-5-20250929")

        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8000,
            temperature=0.3,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = message.content[0].text

        print("✅ SONNET 4.5 GENERATION COMPLETE")
        print(f"   Response Length: {len(response_text)} chars")
        print(f"   Input Tokens: {message.usage.input_tokens}")
        print(f"   Output Tokens: {message.usage.output_tokens}")
        print("="*80)

        # Parse the response to extract files
        files = CodeGenerator._parse_files_from_response(response_text)

        print(f"📁 Extracted {len(files)} files:")
        for filename in files.keys():
            print(f"   - {filename} ({len(files[filename])} chars)")
        print("="*80)

        return files

    @staticmethod
    def _parse_files_from_response(response: str) -> Dict[str, str]:
        """
        Parse Sonnet's response to extract file contents

        Expected format:
        FILE: main.py
        ```python
        code here
        ```

        FILE: requirements.txt
        ```
        content here
        ```
        """
        files = {}
        lines = response.split('\n')

        current_file = None
        current_content = []
        in_code_block = False

        for line in lines:
            # Check for file markers
            if line.startswith('FILE:'):
                # Save previous file
                if current_file and current_content:
                    files[current_file] = '\n'.join(current_content).strip()

                # Start new file
                current_file = line.replace('FILE:', '').strip()
                current_content = []
                in_code_block = False

            elif current_file:
                # Check for code block markers
                if line.strip().startswith('```'):
                    in_code_block = not in_code_block
                    continue

                # Add content if inside code block
                if in_code_block:
                    current_content.append(line)

        # Save last file
        if current_file and current_content:
            files[current_file] = '\n'.join(current_content).strip()

        return files


class ProjectManager:
    """Manages local project folders and zip files"""

    @staticmethod
    def save_project(project_id: str, files: Dict[str, str]) -> tuple[Path, Path]:
        """
        Save generated files to local folder and create zip

        Args:
            project_id: Unique project identifier
            files: Dict of filename -> content

        Returns:
            (project_path, zip_path)
        """

        print("="*80)
        print("💾 SAVING PROJECT TO DISK")
        print(f"   Project ID: {project_id}")
        print("="*80)

        # Create directories if they don't exist
        projects_dir = Path("projects")
        projects_dir.mkdir(exist_ok=True)

        tmp_dir = Path("tmp")
        tmp_dir.mkdir(exist_ok=True)

        # Create project folder
        project_path = projects_dir / project_id
        project_path.mkdir(parents=True, exist_ok=True)

        # Write all files
        for filename, content in files.items():
            file_path = project_path / filename
            file_path.write_text(content, encoding="utf-8")
            print(f"   ✅ Wrote {filename} ({len(content)} chars)")

        # Create zip file
        zip_path = tmp_dir / f"{project_id}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in project_path.rglob("*"):
                if file.is_file():
                    zipf.write(file, arcname=file.relative_to(project_path))

        print(f"   📦 Created zip: {zip_path} ({zip_path.stat().st_size / 1024:.1f} KB)")
        print("="*80)

        return project_path, zip_path


# Main orchestration function
async def generate_startup_backend(
    user_idea: str,
    job_id: str,
    log_callback: Callable
) -> Dict:
    """
    Complete pipeline: Enrich → Generate → Save → Deploy

    Args:
        user_idea: User's raw startup idea
        job_id: Job ID for tracking
        log_callback: Function(job_id, message, type) for progress updates

    Returns:
        {
            "project_id": str,
            "project_name": str,
            "project_path": str,
            "zip_path": str,
            "files": Dict[str, str],
            "spec": Dict
        }
    """

    print("\n" + "="*80)
    print("🚀 STARTING COMPLETE STARTUP BACKEND GENERATION")
    print(f"   Job ID: {job_id}")
    print(f"   User Idea: {user_idea}")
    print("="*80 + "\n")

    # Step 1: Enrich prompt with GPT-4o (0-25%)
    log_callback(job_id, "🔍 Researching your idea and finding competitors...", "info")

    try:
        enriched_spec = await PromptEnricher.enrich_prompt(user_idea)
        log_callback(job_id, f"✅ Found {len(enriched_spec.get('example_companies', []))} competitors and identified key features", "success")
    except Exception as e:
        log_callback(job_id, f"❌ Enrichment failed: {str(e)}", "error")
        raise

    # Step 2: Generate code with Sonnet 4.5 (25-50%)
    log_callback(job_id, "⚙️ Generating complete FastAPI backend with SQLite...", "info")

    try:
        files = CodeGenerator.generate_code(enriched_spec)
        log_callback(job_id, f"✅ Generated {len(files)} files with production-ready code", "success")
    except Exception as e:
        log_callback(job_id, f"❌ Code generation failed: {str(e)}", "error")
        raise

    # Step 3: Save to disk and create zip (50-60%)
    log_callback(job_id, "💾 Saving project files and creating deployment package...", "info")

    project_id = str(uuid.uuid4())

    try:
        project_path, zip_path = ProjectManager.save_project(project_id, files)
        log_callback(job_id, "✅ Project saved and zipped successfully", "success")
    except Exception as e:
        log_callback(job_id, f"❌ File save failed: {str(e)}", "error")
        raise

    print("\n" + "="*80)
    print("✅ GENERATION COMPLETE - READY FOR DEPLOYMENT")
    print(f"   Project ID: {project_id}")
    print(f"   Project Name: {enriched_spec.get('project_name', 'N/A')}")
    print(f"   Project Path: {project_path}")
    print(f"   Zip Path: {zip_path}")
    print(f"   Files: {', '.join(files.keys())}")
    print("="*80 + "\n")

    return {
        "project_id": project_id,
        "project_name": enriched_spec.get("project_name", "Generated Project"),
        "description": enriched_spec.get("description", ""),
        "project_path": str(project_path),
        "zip_path": str(zip_path),
        "files": files,
        "spec": enriched_spec
    }
