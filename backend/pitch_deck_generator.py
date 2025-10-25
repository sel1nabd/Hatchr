"""
Pitch Deck Generator
Generates a professional 5-slide pitch deck for startups using Livepeer AI
"""

import os
from typing import Dict, Any, List
import time
from dotenv import load_dotenv
from lpfuncs import generate_image_from_text, download_image_to_temp, refine_image_text_readability

# Load environment variables
load_dotenv()


def generate_pitch_deck(
    startup_idea: str,
    startup_name: str = "",
    industry: str = "",
    target_market: str = "",
    business_model: str = "",
    style: str = "professional minimalist"
) -> Dict[str, Any]:
    """
    Generate a complete 5-slide pitch deck for a startup idea.
    
    Creates professional investor-ready slides:
    1. Title Slide - Company name, tagline, and logo
    2. Problem Slide - The problem being solved
    3. Solution Slide - How the startup solves it
    4. Market Slide - Target market and opportunity
    5. Business Model Slide - How the company makes money
    
    Args:
        startup_idea: Core startup concept/description
        startup_name: Company name (auto-generated if empty)
        industry: Industry/sector (e.g., "FinTech", "HealthTech")
        target_market: Description of target customers
        business_model: How the company generates revenue
        style: Visual style ("professional minimalist", "modern tech", "bold colorful")
        
    Returns:
        Dict containing:
        - success: bool
        - slides: List of dicts with slide_number, title, image_url
        - error: str (if failed)
        
    Example:
        >>> result = generate_pitch_deck(
        ...     startup_idea="AI-powered task management for freelancers",
        ...     startup_name="FlowMaster",
        ...     industry="SaaS",
        ...     target_market="Freelancers and solopreneurs",
        ...     business_model="Freemium subscription model"
        ... )
        >>> for slide in result["slides"]:
        ...     print(f"Slide {slide['slide_number']}: {slide['image_url']}")
    """
    
    print("=" * 80)
    print("🎯 GENERATING INVESTOR PITCH DECK")
    print("=" * 80)
    print(f"Startup: {startup_name or 'Auto-naming based on idea'}")
    print(f"Idea: {startup_idea}")
    print(f"Style: {style}")
    print("=" * 80)
    
    # Auto-generate startup name if not provided
    if not startup_name:
        # Extract key words from idea for name
        words = startup_idea.split()[:3]
        startup_name = "".join([w.capitalize() for w in words])
    
    # Base prompt styling
    base_style = f"{style} pitch deck slide, clean layout, investor presentation, high contrast, readable text, professional design"
    
    # Define the 5 slides
    slides = []
    
    # SLIDE 1: TITLE SLIDE
    print("\n📊 Generating Slide 1/5: Title Slide...")
    slide_1_prompt = f"""
Minimalist corporate presentation title slide in English,
only large bold text: "{startup_name}" centered as main headline,
simple geometric icon logo above the text,
solid light background, ultra-clean layout, no small text, no subtitles,
modern sans-serif typography, high contrast, professional aesthetic,
graphic design poster style, vector art, no photos
"""
    
    slide_1 = generate_image_from_text(
        prompt=slide_1_prompt.strip(),
        negative_prompt="small text, tiny font, descriptive text, paragraphs, unreadable text, blurry, non-English, foreign language, messy, photo, people, cluttered, complex details",
        width=1024,
        height=576,
        guidance_scale=14.0,
        num_inference_steps=60,
        safety_check=True
    )
    
    if slide_1["success"] and slide_1["images"]:
        image_url = slide_1["images"][0]["url"]
        slide_entry = {
            "slide_number": 1,
            "title": "Title Slide",
            "image_url": image_url,
            "prompt": slide_1_prompt.strip()
        }

        # Attempt to download and refine the slide to improve text readability
        try:
            local_path = download_image_to_temp(image_url)
            refine_prompt = (
                "Enhance and render all visible text in English; make text bold, high contrast, "
                "large, and readable at presentation size. Preserve layout and icons."
            )
            refined = refine_image_text_readability(local_path, refine_prompt)
            if refined.get("success"):
                # Prefer local refined path if available, otherwise use returned URL
                if refined.get("image_path"):
                    slide_entry["refined_image_path"] = refined.get("image_path")
                else:
                    slide_entry["refined_image_url"] = refined.get("image_url")
            else:
                slide_entry["refine_error"] = refined.get("error")
        except Exception as e:
            slide_entry["refine_error"] = str(e)

        slides.append(slide_entry)
        print(f"✅ Slide 1 generated: {image_url}")
        time.sleep(2)  # Small delay between requests
    else:
        return {
            "success": False,
            "error": f"Failed to generate Slide 1: {slide_1.get('error', 'Unknown error')}",
            "slides": []
        }
    
    # SLIDE 2: PROBLEM SLIDE
    print("\n📊 Generating Slide 2/5: Problem Slide...")
    # Use actual problem or generic VC pitch deck problems
    problem_context = f"addressing issues in {industry if industry else 'the market'}" if startup_idea else "solving key market inefficiencies"
    
    slide_2_prompt = f"""
Simple business slide in English with large bold title "THE PROBLEM" at top,
three large icons with single-word labels only: "INEFFICIENCY", "COST", "TIME",
minimalist icon-based layout, no paragraphs, no small text, no descriptions,
high contrast bold text on clean white background, professional minimalist style,
only show title and 3 large icons with one-word labels, vector graphics,
no detailed text, no complex explanations
"""
    
    slide_2 = generate_image_from_text(
        prompt=slide_2_prompt.strip(),
        negative_prompt="small text, tiny font, paragraphs, detailed descriptions, unreadable text, blurry, non-English, messy, photo, people, cluttered, long sentences",
        width=1024,
        height=576,
        guidance_scale=14.0,
        num_inference_steps=60,
        safety_check=True
    )
    
    if slide_2["success"] and slide_2["images"]:
        image_url = slide_2["images"][0]["url"]
        slide_entry = {
            "slide_number": 2,
            "title": "The Problem",
            "image_url": image_url,
            "prompt": slide_2_prompt.strip()
        }
        try:
            local_path = download_image_to_temp(image_url)
            refine_prompt = (
                "Enhance and render all visible text in English; make text bold, high contrast, "
                "large, and readable at presentation size. Preserve layout and icons."
            )
            refined = refine_image_text_readability(local_path, refine_prompt)
            if refined.get("success"):
                if refined.get("image_path"):
                    slide_entry["refined_image_path"] = refined.get("image_path")
                else:
                    slide_entry["refined_image_url"] = refined.get("image_url")
            else:
                slide_entry["refine_error"] = refined.get("error")
        except Exception as e:
            slide_entry["refine_error"] = str(e)

        slides.append(slide_entry)
        print(f"✅ Slide 2 generated: {image_url}")
        time.sleep(2)  # Small delay between requests
    else:
        print(f"⚠️  Slide 2 failed, continuing...")
        time.sleep(1)
    
    # SLIDE 3: SOLUTION SLIDE
    print("\n📊 Generating Slide 3/5: Solution Slide...")
    solution_features = f"{startup_name} platform" if startup_name else "our innovative platform"
    
    slide_3_prompt = f"""
Minimalist business slide in English with large title "OUR SOLUTION",
simple diagram showing 3 boxes connected by arrows,
each box contains only single-word labels: "PLATFORM", "AUTOMATION", "INSIGHTS",
clean geometric shapes, no detailed text, no small descriptions,
high contrast bold text on light background, professional tech style,
only large readable words, vector graphics, ultra-simple layout
"""
    
    slide_3 = generate_image_from_text(
        prompt=slide_3_prompt.strip(),
        negative_prompt="small text, tiny font, paragraphs, detailed descriptions, long sentences, unreadable, blurry, non-English, photo, people, complex diagrams, cluttered",
        width=1024,
        height=576,
        guidance_scale=14.0,
        num_inference_steps=60,
        safety_check=True
    )
    
    if slide_3["success"] and slide_3["images"]:
        image_url = slide_3["images"][0]["url"]
        slide_entry = {
            "slide_number": 3,
            "title": "Our Solution",
            "image_url": image_url,
            "prompt": slide_3_prompt.strip()
        }
        try:
            local_path = download_image_to_temp(image_url)
            refine_prompt = (
                "Enhance and render all visible text in English; make text bold, high contrast, "
                "large, and readable at presentation size. Preserve layout and icons."
            )
            refined = refine_image_text_readability(local_path, refine_prompt)
            if refined.get("success"):
                if refined.get("image_path"):
                    slide_entry["refined_image_path"] = refined.get("image_path")
                else:
                    slide_entry["refined_image_url"] = refined.get("image_url")
            else:
                slide_entry["refine_error"] = refined.get("error")
        except Exception as e:
            slide_entry["refine_error"] = str(e)

        slides.append(slide_entry)
        print(f"✅ Slide 3 generated: {image_url}")
        time.sleep(2)  # Small delay between requests
    else:
        print(f"⚠️  Slide 3 failed, continuing...")
        time.sleep(1)
    
    # SLIDE 4: MARKET OPPORTUNITY
    print("\n📊 Generating Slide 4/5: Market Opportunity...")
    market_info = target_market if target_market else "B2B SaaS market"
    
    slide_4_prompt = f"""
Clean business slide in English with large title "MARKET OPPORTUNITY",
show only 3 large numbers: "$10B", "$2B", "$500M" displayed prominently,
simple labels above numbers: "TAM", "SAM", "SOM",
one large upward arrow with "45%" text,
no paragraphs, no small text, no detailed descriptions,
minimalist infographic with only big bold numbers and single-word labels,
high contrast, clean white background, vector graphics style
"""
    
    slide_4 = generate_image_from_text(
        prompt=slide_4_prompt.strip(),
        negative_prompt="small text, tiny font, detailed descriptions, paragraphs, long sentences, unreadable numbers, blurry, non-English, photo, people, cluttered, complex charts",
        width=1024,
        height=576,
        guidance_scale=14.0,
        num_inference_steps=60,
        safety_check=True
    )
    
    if slide_4["success"] and slide_4["images"]:
        image_url = slide_4["images"][0]["url"]
        slide_entry = {
            "slide_number": 4,
            "title": "Market Opportunity",
            "image_url": image_url,
            "prompt": slide_4_prompt.strip()
        }
        try:
            local_path = download_image_to_temp(image_url)
            refine_prompt = (
                "Enhance and render all visible text in English; make text bold, high contrast, "
                "large, and readable at presentation size. Preserve layout and icons."
            )
            refined = refine_image_text_readability(local_path, refine_prompt)
            if refined.get("success"):
                if refined.get("image_path"):
                    slide_entry["refined_image_path"] = refined.get("image_path")
                else:
                    slide_entry["refined_image_url"] = refined.get("image_url")
            else:
                slide_entry["refine_error"] = refined.get("error")
        except Exception as e:
            slide_entry["refine_error"] = str(e)

        slides.append(slide_entry)
        print(f"✅ Slide 4 generated: {image_url}")
        time.sleep(2)  # Small delay between requests
    else:
        print(f"⚠️  Slide 4 failed, continuing...")
        time.sleep(1)
    
    # SLIDE 5: BUSINESS MODEL
    print("\n📊 Generating Slide 5/5: Business Model...")
    biz_model = business_model if business_model else "SaaS subscription model"
    
    slide_5_prompt = f"""
Simple business slide in English with large title "BUSINESS MODEL",
show 3 pricing boxes side by side with only large text:
"FREE", "$29", "CUSTOM",
simple dollar sign icon, clean boxes layout, no detailed features list,
no small text, no descriptions, no bullet points,
minimalist pricing tier visualization, high contrast bold text,
white background, professional vector graphics, ultra-clean design
"""
    
    slide_5 = generate_image_from_text(
        prompt=slide_5_prompt.strip(),
        negative_prompt="small text, tiny font, detailed descriptions, feature lists, paragraphs, long text, unreadable, blurry, non-English, photo, people, cluttered, complex diagrams",
        width=1024,
        height=576,
        guidance_scale=14.0,
        num_inference_steps=60,
        safety_check=True
    )
    
    if slide_5["success"] and slide_5["images"]:
        image_url = slide_5["images"][0]["url"]
        slide_entry = {
            "slide_number": 5,
            "title": "Business Model",
            "image_url": image_url,
            "prompt": slide_5_prompt.strip()
        }
        try:
            local_path = download_image_to_temp(image_url)
            refine_prompt = (
                "Enhance and render all visible text in English; make text bold, high contrast, "
                "large, and readable at presentation size. Preserve layout and icons."
            )
            refined = refine_image_text_readability(local_path, refine_prompt)
            if refined.get("success"):
                if refined.get("image_path"):
                    slide_entry["refined_image_path"] = refined.get("image_path")
                else:
                    slide_entry["refined_image_url"] = refined.get("image_url")
            else:
                slide_entry["refine_error"] = refined.get("error")
        except Exception as e:
            slide_entry["refine_error"] = str(e)

        slides.append(slide_entry)
        print(f"✅ Slide 5 generated: {image_url}")
    else:
        print(f"⚠️  Slide 5 failed, continuing...")
    
    # Summary
    print("\n" + "=" * 80)
    print(f"✅ PITCH DECK GENERATION COMPLETE")
    print(f"   Successfully generated {len(slides)}/5 slides")
    print("=" * 80)
    
    return {
        "success": len(slides) > 0,
        "slides": slides,
        "startup_name": startup_name,
        "total_slides": len(slides),
        "message": f"Generated {len(slides)}/5 pitch deck slides"
    }


def save_pitch_deck_urls(result: Dict[str, Any], filename: str = "pitch_deck_urls.txt") -> None:
    """
    Save pitch deck slide URLs to a text file.
    
    Args:
        result: Result dict from generate_pitch_deck()
        filename: Output filename
    """
    if not result["success"] or not result["slides"]:
        print("❌ No slides to save")
        return
    
    with open(filename, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write(f"PITCH DECK: {result['startup_name']}\n")
        f.write("=" * 80 + "\n\n")
        
        for slide in result["slides"]:
            f.write(f"Slide {slide['slide_number']}: {slide['title']}\n")
            f.write(f"URL: {slide['image_url']}\n")
            f.write(f"Prompt: {slide['prompt'][:100]}...\n")
            f.write("\n" + "-" * 80 + "\n\n")
    
    print(f"💾 Pitch deck URLs saved to: {filename}")


# Test function
if __name__ == "__main__":
    print("🚀 Testing Pitch Deck Generator\n")
    
    # Example startup
    result = generate_pitch_deck(
        startup_idea="AI-powered task management platform that helps freelancers and solopreneurs organize their work, track time, and automate repetitive tasks using machine learning",
        startup_name="FlowMaster",
        industry="SaaS / Productivity",
        target_market="Freelancers, solopreneurs, and small business owners managing multiple clients",
        business_model="Freemium with premium tiers ($0/month free, $15/month pro, $30/month enterprise)",
        style="modern tech"
    )
    
    if result["success"]:
        print(f"\n🎉 SUCCESS! Generated {len(result['slides'])} slides\n")
        
        for slide in result["slides"]:
            print(f"📊 Slide {slide['slide_number']}: {slide['title']}")
            print(f"   URL: {slide['image_url']}\n")
        
        # Save to file
        save_pitch_deck_urls(result)
        
        # Ask user if they want to save
        try:
            save_choice = input("\n💾 Save pitch deck URLs? (y/n): ").strip().lower()
            if save_choice == 'y':
                save_pitch_deck_urls(result, "pitch_deck_urls.txt")
        except:
            pass
    else:
        print(f"\n❌ FAILED: {result.get('error', 'Unknown error')}")
