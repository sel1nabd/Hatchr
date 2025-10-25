"""
Example usage of Livepeer AI functions for Hatchr
Demonstrates text-to-image and image-to-video generation
"""

import asyncio
from lpfuncs import (
    generate_image_from_text,
    generate_video_from_image,
    generate_video_from_image_url,
    generate_marketing_assets
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
        
    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
    
    print("\n" + "="*80)
    print("Examples completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
