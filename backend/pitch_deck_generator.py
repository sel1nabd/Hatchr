"""
Pitch Deck Generator
Generates a professional 5-slide pitch deck for startups using Livepeer AI
"""

import os
from typing import Dict, Any, List
import time
from dotenv import load_dotenv
from lpfuncs import generate_image_from_text

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
Professional corporate presentation title slide in English language,
large bold text displaying "{startup_name}" as company name centered on slide,
subtitle text "Investor Pitch Deck" below the company name,
clean minimalist layout, modern sans-serif font, high contrast black text on light background,
simple geometric logo icon, business presentation aesthetic, crisp clear typography,
all text must be in English, graphic design style, no photos or realistic imagery
"""
    
    slide_1 = generate_image_from_text(
        prompt=slide_1_prompt.strip(),
        negative_prompt="blurry text, unreadable font, non-English text, foreign language, small text, messy typography, low quality, photo, people, cluttered, distorted letters",
        width=1024,
        height=576,
        guidance_scale=8.0,
        num_inference_steps=60,
        safety_check=True
    )
    
    if slide_1["success"] and slide_1["images"]:
        slides.append({
            "slide_number": 1,
            "title": "Title Slide",
            "image_url": slide_1["images"][0]["url"],
            "prompt": slide_1_prompt.strip()
        })
        print(f"✅ Slide 1 generated: {slide_1['images'][0]['url']}")
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
Corporate investor presentation slide in English with bold title "THE PROBLEM" at top,
clean infographic layout showing bullet points: "Market Inefficiency", "Customer Pain Points", "Unmet Needs",
modern business icons illustrating each problem, high contrast black text on white background,
professional minimalist design, clear sans-serif typography with good spacing,
typical venture capital pitch deck style, all text in English language,
business diagram aesthetic, vector graphics, no photos or people
"""
    
    slide_2 = generate_image_from_text(
        prompt=slide_2_prompt.strip(),
        negative_prompt="blurry text, small font, unreadable, non-English text, foreign characters, messy, low quality, photo, people, cluttered layout, distorted text",
        width=1024,
        height=576,
        guidance_scale=8.0,
        num_inference_steps=60,
        safety_check=True
    )
    
    if slide_2["success"] and slide_2["images"]:
        slides.append({
            "slide_number": 2,
            "title": "The Problem",
            "image_url": slide_2["images"][0]["url"],
            "prompt": slide_2_prompt.strip()
        })
        print(f"✅ Slide 2 generated: {slide_2['images'][0]['url']}")
        time.sleep(2)  # Small delay between requests
    else:
        print(f"⚠️  Slide 2 failed, continuing...")
        time.sleep(1)
    
    # SLIDE 3: SOLUTION SLIDE
    print("\n📊 Generating Slide 3/5: Solution Slide...")
    solution_features = f"{startup_name} platform" if startup_name else "our innovative platform"
    
    slide_3_prompt = f"""
Business investor presentation slide in English with large title "OUR SOLUTION",
product feature diagram showing: "Technology Platform", "User Experience", "Key Features",
modern UI/UX visualization boxes with labeled components, clean arrow connections,
high contrast readable English text labels, professional tech company presentation design,
flow chart or system architecture style, minimalist blue and white color palette,
crisp sans-serif typography, all text must be in English, no realistic photos, vector graphics only
"""
    
    slide_3 = generate_image_from_text(
        prompt=slide_3_prompt.strip(),
        negative_prompt="blurry text, illegible font, non-English text, foreign language, small text, messy, low quality, photo, people, cluttered",
        width=1024,
        height=576,
        guidance_scale=8.0,
        num_inference_steps=60,
        safety_check=True
    )
    
    if slide_3["success"] and slide_3["images"]:
        slides.append({
            "slide_number": 3,
            "title": "Our Solution",
            "image_url": slide_3["images"][0]["url"],
            "prompt": slide_3_prompt.strip()
        })
        print(f"✅ Slide 3 generated: {slide_3['images'][0]['url']}")
        time.sleep(2)  # Small delay between requests
    else:
        print(f"⚠️  Slide 3 failed, continuing...")
        time.sleep(1)
    
    # SLIDE 4: MARKET OPPORTUNITY
    print("\n📊 Generating Slide 4/5: Market Opportunity...")
    market_info = target_market if target_market else "B2B SaaS market"
    
    slide_4_prompt = f"""
Corporate VC pitch deck slide in English with bold headline "MARKET OPPORTUNITY",
data visualization showing: "TAM: $10B", "SAM: $2B", "SOM: $500M" as large numbers,
bar charts showing market growth with "45% CAGR" label, upward trend green arrows,
professional infographic style with readable English labels and legends,
text: "Target Market", "Growth Rate", "Market Size", high contrast black text on light background,
clean modern business analytics layout, vector graphics, all text in English language,
no photos or people, clear typography throughout
"""
    
    slide_4 = generate_image_from_text(
        prompt=slide_4_prompt.strip(),
        negative_prompt="blurry text, tiny numbers, illegible labels, non-English text, foreign characters, messy, low quality, photo, people, cluttered data",
        width=1024,
        height=576,
        guidance_scale=8.0,
        num_inference_steps=60,
        safety_check=True
    )
    
    if slide_4["success"] and slide_4["images"]:
        slides.append({
            "slide_number": 4,
            "title": "Market Opportunity",
            "image_url": slide_4["images"][0]["url"],
            "prompt": slide_4_prompt.strip()
        })
        print(f"✅ Slide 4 generated: {slide_4['images'][0]['url']}")
        time.sleep(2)  # Small delay between requests
    else:
        print(f"⚠️  Slide 4 failed, continuing...")
        time.sleep(1)
    
    # SLIDE 5: BUSINESS MODEL
    print("\n📊 Generating Slide 5/5: Business Model...")
    biz_model = business_model if business_model else "SaaS subscription model"
    
    slide_5_prompt = f"""
Professional investor presentation slide in English with prominent title "BUSINESS MODEL",
revenue stream diagram showing boxes labeled: "Subscription Revenue", "Enterprise Sales", "Platform Fees",
pricing tier table with: "Free Tier: $0/month", "Pro: $29/month", "Enterprise: Custom",
customer journey funnel with arrows showing conversion flow, dollar signs and revenue icons,
clean infographic design with high contrast black text on white background,
modern sans-serif typography, vector graphics style, all text must be in English language,
typical VC pitch deck financial slide, no photos or realistic imagery, organized layout
"""
    
    slide_5 = generate_image_from_text(
        prompt=slide_5_prompt.strip(),
        negative_prompt="blurry text, small font, illegible, non-English text, foreign language, messy layout, low quality, photo, people, cluttered, distorted",
        width=1024,
        height=576,
        guidance_scale=8.0,
        num_inference_steps=60,
        safety_check=True
    )
    
    if slide_5["success"] and slide_5["images"]:
        slides.append({
            "slide_number": 5,
            "title": "Business Model",
            "image_url": slide_5["images"][0]["url"],
            "prompt": slide_5_prompt.strip()
        })
        print(f"✅ Slide 5 generated: {slide_5['images'][0]['url']}")
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
