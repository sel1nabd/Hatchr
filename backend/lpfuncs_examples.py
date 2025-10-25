"""
Example usage of Livepeer AI functions for Hatchr
Demonstrates text-to-image and image-to-video generation
"""

import asyncio
from lpfuncs import (
    generate_image_from_text,
    generate_video_from_image,
    generate_video_from_image_url,
    generate_marketing_assets,
    generate_startup_branding
)


def example_1_text_to_image():
    """Example 1: Generate an image from text"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Text-to-Image Generation")
    print("="*80 + "\n")
    
    result = generate_image_from_text(
        prompt="A futuristic startup office with holographic displays and modern furniture",
        negative_prompt="blurry, low quality, distorted, dark",
        width=1024,
        height=576,
        guidance_scale=7.5,
        num_inference_steps=50
    )
    
    if result["success"]:
        print("✅ Image generated successfully!")
        if result["images"]:
            for i, img in enumerate(result["images"]):
                print(f"   Image {i+1}: {img.get('url', 'No URL')}")
    else:
        print(f"❌ Failed: {result['error']}")
    
    return result


def example_2_image_to_video():
    """Example 2: Generate video from a local image file"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Image-to-Video from Local File")
    print("="*80 + "\n")
    
    # Replace with your actual image path
    image_path = "path/to/your/image.png"
    
    result = generate_video_from_image(
        image_path=image_path,
        width=1024,
        height=576,
        fps=6,
        motion_bucket_id=127,
        num_inference_steps=25
    )
    
    if result["success"]:
        print("✅ Video generated successfully!")
        if result["video"]:
            print(f"   Video URL: {result['video'].get('url', 'No URL')}")
    else:
        print(f"❌ Failed: {result['error']}")
    
    return result


def example_3_complete_workflow():
    """Example 3: Complete workflow - text to image to video"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Complete Workflow (Text → Image → Video)")
    print("="*80 + "\n")
    
    result = generate_marketing_assets(
        prompt="A sleek, modern logo for a tech startup named 'Hatchr' with an egg hatching into code",
        negative_prompt="blurry, low quality, distorted, text, watermark",
        image_width=1024,
        image_height=576,
        video_fps=6,
        motion_intensity=150  # Higher motion for dynamic effect
    )
    
    if result["success"]:
        print("\n✅ Complete workflow successful!")
        print(f"   Image URL: {result.get('image_url', 'N/A')}")
        print(f"   Video URL: {result.get('video_url', 'N/A')}")
    else:
        print(f"\n❌ Workflow failed: {result['error']}")
    
    return result


def example_4_custom_parameters():
    """Example 4: Generate with custom parameters"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Custom Parameters for Specific Style")
    print("="*80 + "\n")
    
    # Generate a cinematic style image
    result = generate_image_from_text(
        prompt="Cinematic shot of a startup founder presenting to investors, dramatic lighting, 4k",
        negative_prompt="cartoon, anime, low quality, blurry, amateur",
        width=1920,  # Wider aspect ratio
        height=1080,
        guidance_scale=8.5,  # Higher guidance for more prompt adherence
        num_inference_steps=75,  # More steps for higher quality
        safety_check=True
    )
    
    if result["success"]:
        print("✅ High-quality cinematic image generated!")
        if result["images"]:
            print(f"   Image URL: {result['images'][0].get('url', 'N/A')}")
    else:
        print(f"❌ Failed: {result['error']}")
    
    return result


def example_5_startup_branding():
    """Example 5: Generate complete startup branding (FRONTEND INTEGRATION)"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Startup Branding - Logo + Promotional Video")
    print("="*80 + "\n")
    print("This is the main function for frontend integration!")
    print()
    
    # Simulate user input from frontend
    startup_idea = "AI-powered task management and scheduling assistant for busy freelancers and remote workers"
    startup_name = "FlowAI"
    
    result = generate_startup_branding(
        startup_idea=startup_idea,
        startup_name=startup_name,
        style="modern",
        color_scheme="blue and purple gradient",
        logo_width=1024,
        logo_height=1024,
        video_fps=8,
        motion_intensity=150,
        include_video=True
    )
    
    if result["success"]:
        print("\n✅ Startup branding generated successfully!")
        print(f"\n📊 Results:")
        print(f"   Startup: {result['metadata']['startup_name']}")
        print(f"   Idea: {result['metadata']['startup_idea'][:60]}...")
        print(f"   Style: {result['metadata']['style']}")
        print(f"\n🎨 Logo URL: {result['logo_url']}")
        print(f"🎬 Video URL: {result['video_url']}")
        print(f"\n💡 Prompt used: {result['logo_prompt'][:100]}...")
        
        # This is what you'd return to the frontend
        frontend_response = {
            "logo": result['logo_url'],
            "video": result['video_url'],
            "metadata": result['metadata']
        }
        print(f"\n📤 Frontend response structure:")
        print(f"   {frontend_response}")
        
    else:
        print(f"\n❌ Branding generation failed: {result['error']}")
    
    return result


def example_6_logo_only():
    """Example 6: Generate just a logo (faster, no video)"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Logo Only (No Video)")
    print("="*80 + "\n")
    
    result = generate_startup_branding(
        startup_idea="Sustainable fashion marketplace connecting eco-conscious consumers with ethical brands",
        startup_name="EcoThreads",
        style="elegant",
        color_scheme="earth tones, green and beige",
        include_video=False  # Skip video generation
    )
    
    if result["success"]:
        print(f"✅ Logo generated!")
        print(f"   Logo URL: {result['logo_url']}")
        print(f"   Video: {'Not requested' if not result['video_url'] else result['video_url']}")
    else:
        print(f"❌ Failed: {result['error']}")
    
    return result


def main():
    """Run all examples"""
    print("\n" + "🚀 " * 20)
    print("Livepeer AI Functions - Usage Examples")
    print("🚀 " * 20)
    
    # Run examples
    try:
        # Example 1: Text to Image
        example_1_text_to_image()
        
        # Example 2: Image to Video (commented out - needs actual image file)
        # example_2_image_to_video()
        
        # Example 3: Complete workflow (commented out - makes API calls)
        # example_3_complete_workflow()
        
        # Example 4: Custom parameters
        # example_4_custom_parameters()
        
        # Example 5: STARTUP BRANDING - Main frontend integration function!
        print("\n" + "🎯 " * 20)
        print("FRONTEND INTEGRATION EXAMPLE")
        print("🎯 " * 20)
        example_5_startup_branding()
        
        # Example 6: Logo only (faster)
        # example_6_logo_only()
        
    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
    
    print("\n" + "="*80)
    print("Examples completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
