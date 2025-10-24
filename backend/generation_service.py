"""
Generation Service - GPT-5 Analysis + Lovable Integration
Simple, focused workflow: Analyze idea → Create Lovable URL
"""

import os
import json
from typing import Dict
from urllib.parse import quote
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

def get_openai_client():
    """Lazy initialization of OpenAI client"""
    return AsyncOpenAI(api_key=OPENAI_API_KEY if OPENAI_API_KEY else None)


class IdeaAnalyzer:
    """GPT-5 for analyzing startup ideas and market research"""

    @staticmethod
    async def analyze_idea(prompt: str) -> Dict:
        """
        Use GPT-5 to analyze the startup idea and generate structured information

        Returns:
            {
                "information": "Description of space, competitors, insights",
                "structure": "Typical website structure for this type"
            }
        """

        system_prompt = """You are a product analyst and UX expert specializing in web applications.

Analyze startup ideas and output structured information to help build better websites.

Output JSON format:
{
  "information": "Detailed description including: the core idea, what market space this is in, the main competitors in this space (name 3-5 real companies), what makes this idea unique, and the target audience",
  "structure": "Typical website structure for this type of application, including: main pages needed (landing, dashboard, etc.), key features to implement, essential user flows, and important UI components"
}

Be thorough, specific, and actionable. Reference real competitors and proven patterns."""

        user_prompt = f"""Analyze this startup idea and provide strategic insights:

"{prompt}"

Provide:
1. **Information**: What space is this in? Who are the main competitors (real companies)? What patterns do successful apps in this space follow? What makes this idea valuable?

2. **Structure**: What should the website include? What pages are essential? What features must it have? What's the typical user journey?

Return as JSON with 'information' and 'structure' keys."""

        client = get_openai_client()

        response = await client.chat.completions.create(
            model="gpt-5",  # Using GPT-5
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
            # Note: GPT-5 doesn't support temperature parameter (default is 1)
            # Can use reasoning_effort: "low" | "medium" | "high" instead
        )

        result = json.loads(response.choices[0].message.content)

        return result


class LovableService:
    """Create Lovable Build URLs from analyzed ideas"""

    @staticmethod
    def create_lovable_url(user_prompt: str, analysis: Dict) -> str:
        """
        Create a Lovable Build URL from the GPT-5 analysis

        Args:
            user_prompt: Original user input
            analysis: GPT-5 analysis with {information, structure}

        Returns:
            Lovable URL: https://lovable.dev/?autosubmit=true#prompt=...
        """

        # Craft enhanced prompt from GPT-5 analysis
        enhanced_prompt = f"""Build a modern web application: {user_prompt}

## Market Context
{analysis['information']}

## Website Structure
{analysis['structure']}

## Requirements
Create a beautiful, professional web application with:
- Modern, clean UI using Tailwind CSS
- Fully responsive design (mobile, tablet, desktop)
- User authentication (login/signup pages)
- Main dashboard with core functionality
- Landing page with hero section and features
- Settings/profile page
- Dark mode support
- Loading states and error handling
- Smooth animations and transitions
- Professional color scheme and typography

Make it production-ready, visually stunning, and better than the competitors mentioned above.
Use Next.js, TypeScript, and Supabase for the backend."""

        # URL encode the prompt (max 50k characters)
        encoded_prompt = quote(enhanced_prompt, safe='')

        # Construct Lovable URL
        lovable_url = f"https://lovable.dev/?autosubmit=true#prompt={encoded_prompt}"

        # Log URL length (warn if too long)
        if len(lovable_url) > 8000:
            print(f"WARNING: Lovable URL is {len(lovable_url)} chars - might be too long for some browsers")

        return lovable_url


# Main orchestration function
async def generate_full_stack_app(prompt: str, job_id: str, log_callback) -> Dict:
    """
    Main pipeline: GPT-5 analysis → Lovable URL generation

    Args:
        prompt: User's startup idea
        job_id: Job ID for logging
        log_callback: Function to call for progress updates

    Returns:
        Dict with lovable_url and analysis
    """

    # Step 1: Analyze idea with GPT-5
    log_callback(job_id, "Analyzing your startup idea with GPT-5...", "info")

    analysis = await IdeaAnalyzer.analyze_idea(prompt)

    log_callback(job_id, "Analysis complete - identified market space and competitors", "success")

    # Step 2: Create enhanced Lovable prompt
    log_callback(job_id, "Crafting optimized Lovable prompt...", "info")

    lovable_url = LovableService.create_lovable_url(prompt, analysis)

    log_callback(job_id, "Lovable URL generated successfully!", "success")

    # Generate metadata
    import uuid
    project_id = str(uuid.uuid4())

    # Extract project name from prompt (simple heuristic)
    words = prompt.split()[:3]
    project_name = " ".join(w.capitalize() for w in words)

    return {
        "project_id": project_id,
        "project_name": project_name,
        "lovable_url": lovable_url,
        "analysis": analysis,
        "prompt_length": len(lovable_url)
    }
