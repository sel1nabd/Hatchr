"""
Test script to generate promotional content (logo + video)
Outputs links to the generated assets
"""

import os
from dotenv import load_dotenv
from lpfuncs import generate_startup_branding

# Load environment variables from .env file
load_dotenv()

def test_branding_generation():
    """Test the complete branding generation workflow"""
    
    print("=" * 80)
    print("STARTUP BRANDING GENERATION TEST")
    print("=" * 80)
    print()
    
    # Check if API key is set
    api_key = os.getenv("LIVEPEER_API_KEY")
    if not api_key:
        print("❌ ERROR: LIVEPEER_API_KEY not set!")
        print("Please set it with: export LIVEPEER_API_KEY='your_key_here'")
        return
    
    print(f"✅ API Key found (length: {len(api_key)})")
    print()
    
    # Test case: Generate branding for a sample startup
    print("🚀 Generating branding for test startup...")
    print()
    
    test_startup = {
        "idea": "AI-powered task management and scheduling assistant for busy freelancers and remote workers",
        "name": "FlowMaster",
        "style": "modern",
        "colors": "blue and purple gradient"
    }
    
    print(f"📝 Startup Name: {test_startup['name']}")
    print(f"💡 Startup Idea: {test_startup['idea']}")
    print(f"🎨 Style: {test_startup['style']}")
    print(f"🌈 Colors: {test_startup['colors']}")
    print()
    print("-" * 80)
    print()
    
    # Generate branding
    try:
        result = generate_startup_branding(
            startup_idea=test_startup["idea"],
            startup_name=test_startup["name"],
            style=test_startup["style"],
            color_scheme=test_startup["colors"],
            logo_width=1024,
            logo_height=1024,
            video_fps=8,
            motion_intensity=150,
            include_video=True
        )
        
        print()
        print("=" * 80)
        
        if result["success"]:
            print("✅ BRANDING GENERATION SUCCESSFUL!")
            print("=" * 80)
            print()
            
            # Display logo information
            print("📊 LOGO:")
            print("-" * 80)
            if result["logo_url"]:
                print(f"URL: {result['logo_url']}")
                print(f"Dimensions: {result['metadata'].get('logo_dimensions', 'N/A')}")
            else:
                print("⚠️  No logo URL available")
            print()
            
            # Display video information
            print("🎬 PROMOTIONAL VIDEO:")
            print("-" * 80)
            if result["video_url"]:
                print(f"URL: {result['video_url']}")
                print(f"FPS: {result['metadata'].get('video_fps', 'N/A')}")
                print(f"Motion Intensity: {result['metadata'].get('motion_intensity', 'N/A')}")
            else:
                print("⚠️  No video URL available")
                if "video_error" in result.get("metadata", {}):
                    print(f"Error: {result['metadata']['video_error']}")
            print()
            
            # Display prompt used
            print("💭 PROMPT USED:")
            print("-" * 80)
            print(result.get("logo_prompt", "N/A"))
            print()
            
            # Display metadata
            print("📋 METADATA:")
            print("-" * 80)
            for key, value in result["metadata"].items():
                print(f"  {key}: {value}")
            print()
            
            # Summary with copyable links
            print("=" * 80)
            print("📎 COPYABLE LINKS:")
            print("=" * 80)
            print()
            if result["logo_url"]:
                print(f"Logo:\n{result['logo_url']}")
                print()
            if result["video_url"]:
                print(f"Video:\n{result['video_url']}")
                print()
            
            print("=" * 80)
            print("✅ Test completed successfully!")
            print("=" * 80)
            
            return result
            
        else:
            print("❌ BRANDING GENERATION FAILED")
            print("=" * 80)
            print()
            print(f"Error: {result.get('error', 'Unknown error')}")
            print()
            return None
            
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ EXCEPTION OCCURRED")
        print("=" * 80)
        print()
        print(f"Error: {str(e)}")
        print()
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = test_branding_generation()
    
    if result and result["success"]:
        print()
        print("🎉 You can now use these URLs in your application!")
        print()
        
        # Optionally save to a file
        save_choice = input("Do you want to save the URLs to a file? (y/n): ").lower()
        if save_choice == 'y':
            filename = "generated_assets.txt"
            with open(filename, 'w') as f:
                f.write("GENERATED STARTUP BRANDING ASSETS\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Startup Name: {result['metadata']['startup_name']}\n")
                f.write(f"Startup Idea: {result['metadata']['startup_idea']}\n\n")
                f.write("LOGO:\n")
                f.write(f"{result['logo_url']}\n\n")
                if result['video_url']:
                    f.write("VIDEO:\n")
                    f.write(f"{result['video_url']}\n\n")
                f.write(f"\nGenerated at: {result['metadata']}\n")
            
            print(f"✅ URLs saved to: {filename}")
