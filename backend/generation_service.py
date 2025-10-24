"""
Generation Service - Perplexity Sonar + OpenAI Pipeline
Clean, efficient competitor research and code generation
"""

import os
import json
import zipfile
from typing import Dict, List
from pathlib import Path
import httpx
from openai import AsyncOpenAI

# Initialize clients lazily
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")

def get_openai_client():
    """Lazy initialization of OpenAI client"""
    return AsyncOpenAI(api_key=OPENAI_API_KEY if OPENAI_API_KEY else None)


class PerplexityService:
    """Perplexity Sonar API for competitor research"""

    @staticmethod
    async def research_competitors(prompt: str) -> Dict:
        """Use Perplexity Sonar to research competitors and features"""

        # Craft search query
        search_query = f"""Find the top 3-5 most popular web applications or services that are similar to: {prompt}

For each competitor, provide:
1. Name and URL
2. Key features (list 5-7 main features)
3. Technology stack if known
4. Target audience
5. Unique selling points

Format the response as structured data."""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a product research analyst. Provide detailed, structured information about web applications and their features."
                        },
                        {
                            "role": "user",
                            "content": search_query
                        }
                    ]
                },
                timeout=60.0
            )

            result = response.json()

            return {
                "competitors_analysis": result["choices"][0]["message"]["content"],
                "citations": result.get("citations", []),
                "search_results": result.get("search_results", [])
            }


class CodeGeneratorService:
    """OpenAI GPT-4 for code generation"""

    @staticmethod
    async def generate_nextjs_app(prompt: str, competitor_analysis: str) -> Dict:
        """Generate complete Next.js application code"""

        system_prompt = """You are an expert full-stack developer specializing in Next.js 14, TypeScript, Tailwind CSS, and Supabase.

Generate COMPLETE, PRODUCTION-READY code for a full-stack web application.

IMPORTANT INSTRUCTIONS:
1. Generate ALL files needed for a working Next.js 14 app
2. Use App Router (not Pages Router)
3. Include TypeScript throughout
4. Use Tailwind CSS for styling
5. Include Supabase setup for backend
6. Make it modern, beautiful, and functional
7. Return files in a structured JSON format

Required files to generate:
- package.json (with all dependencies)
- next.config.js
- tailwind.config.ts
- tsconfig.json
- app/layout.tsx
- app/page.tsx (landing page with hero, features, CTA)
- app/dashboard/page.tsx (main app functionality)
- app/auth/login/page.tsx
- app/auth/signup/page.tsx
- app/api/*/route.ts (at least 2-3 API routes)
- components/* (at least 5 reusable components)
- lib/supabase.ts (Supabase client setup)
- .env.example
- README.md (with setup instructions)

Return your response as a JSON object with this structure:
{
  "project_name": "string",
  "description": "string",
  "files": {
    "package.json": "file content here",
    "app/page.tsx": "file content here",
    ...
  }
}

Make the code:
- Clean and well-commented
- Following best practices
- Fully functional (no placeholders)
- Beautiful UI with Tailwind
- Responsive design"""

        user_prompt = f"""Create a complete Next.js 14 application for: {prompt}

Based on this competitor analysis:
{competitor_analysis}

Generate a modern, production-ready application that combines the best features from the competitors while adding unique value.

The app should be visually stunning, user-friendly, and include:
- Beautiful landing page
- User authentication
- Main dashboard/functionality
- Settings page
- Responsive design
- Dark mode support
- Loading states
- Error handling

Remember to return the response as a JSON object with all the files."""

        client = get_openai_client()
        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=16000
        )

        generated_content = response.choices[0].message.content

        try:
            return json.loads(generated_content)
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', generated_content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError("Failed to parse generated code as JSON")


class ProjectPackager:
    """Package generated code into downloadable project"""

    @staticmethod
    def create_project_files(project_data: Dict, project_id: str) -> str:
        """Write all generated files to disk and create ZIP"""

        # Create project directory
        project_dir = Path(f"generated_projects/{project_id}")
        project_dir.mkdir(parents=True, exist_ok=True)

        files = project_data.get("files", {})

        # Write each file
        for file_path, content in files.items():
            full_path = project_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write the file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

        # Create ZIP archive
        zip_path = f"generated_projects/{project_id}.zip"

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in project_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(project_dir)
                    zipf.write(file_path, arcname)

        return zip_path

    @staticmethod
    def get_project_metadata(project_data: Dict) -> Dict:
        """Extract metadata from generated project"""

        files = project_data.get("files", {})

        return {
            "project_name": project_data.get("project_name", "Generated App"),
            "description": project_data.get("description", ""),
            "file_count": len(files),
            "has_auth": any("auth" in path for path in files.keys()),
            "has_api": any("api" in path for path in files.keys()),
            "has_dashboard": any("dashboard" in path for path in files.keys()),
            "tech_stack": ["Next.js 14", "TypeScript", "Tailwind CSS", "Supabase"]
        }


# Main orchestration function
async def generate_full_stack_app(prompt: str, job_id: str, log_callback) -> Dict:
    """
    Main pipeline: Perplexity research → OpenAI generation → Package

    Args:
        prompt: User's startup idea
        job_id: Job ID for logging
        log_callback: Function to call for progress updates

    Returns:
        Dict with project_id, files, metadata
    """

    # Step 1: Research competitors with Perplexity
    log_callback(job_id, "Researching competitors with Perplexity Sonar...", "info")
    competitor_data = await PerplexityService.research_competitors(prompt)

    log_callback(job_id, f"Found competitors with {len(competitor_data.get('citations', []))} sources", "success")

    # Step 2: Generate code with OpenAI
    log_callback(job_id, "Generating Next.js application with GPT-4...", "info")
    project_data = await CodeGeneratorService.generate_nextjs_app(
        prompt,
        competitor_data["competitors_analysis"]
    )

    log_callback(job_id, f"Generated {len(project_data.get('files', {}))} files", "success")

    # Step 3: Package everything
    log_callback(job_id, "Creating project files and ZIP archive...", "info")

    # Generate unique project ID (passed from caller)
    import uuid
    project_id = str(uuid.uuid4())

    zip_path = ProjectPackager.create_project_files(project_data, project_id)
    metadata = ProjectPackager.get_project_metadata(project_data)

    log_callback(job_id, "Project packaged successfully!", "success")

    return {
        "project_id": project_id,
        "zip_path": zip_path,
        "metadata": metadata,
        "competitor_citations": competitor_data.get("citations", []),
        "files_generated": len(project_data.get("files", {}))
    }
