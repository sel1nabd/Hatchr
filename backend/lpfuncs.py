"""
Livepeer AI Functions
Handles text-to-image and image-to-video generation using Livepeer AI SDK
"""

import os
from typing import Optional, Dict, Any
from livepeer_ai import Livepeer


def get_livepeer_client() -> Livepeer:
    """
    Get Livepeer client with API key from environment
    
    Returns:
        Livepeer: Configured Livepeer client
    """
    api_key = os.getenv("LIVEPEER_API_KEY")
    if not api_key:
        raise ValueError("LIVEPEER_API_KEY not found in environment variables")
    
    return Livepeer(http_bearer=api_key)


def generate_image_from_text(
    prompt: str,
    negative_prompt: str = "",
    width: int = 1024,
    height: int = 576,
    guidance_scale: float = 7.5,
    num_inference_steps: int = 50,
    safety_check: bool = True
) -> Dict[str, Any]:
    """
    Generate an image from a text prompt using Livepeer AI.
    Uses SG161222/RealVisXL_V4.0_Lightning model.
    
    Args:
        prompt: The text description of the image to generate
        negative_prompt: What to avoid in the generated image
        width: Image width in pixels (default: 1024)
        height: Image height in pixels (default: 576)
        guidance_scale: How closely to follow the prompt (default: 7.5)
        num_inference_steps: Number of denoising steps (default: 50)
        safety_check: Enable safety filtering (default: True)
        
    Returns:
        Dict containing the image response with URL and other metadata
        
    Example:
        >>> result = generate_image_from_text("A futuristic startup office")
        >>> image_url = result['images'][0]['url']
    """
    with get_livepeer_client() as livepeer:
        try:
            res = livepeer.generate.text_to_image(request={
                "model_id": "SG161222/RealVisXL_V4.0_Lightning",
                "loras": "",
                "prompt": prompt,
                "height": height,
                "width": width,
                "guidance_scale": guidance_scale,
                "negative_prompt": negative_prompt,
                "safety_check": safety_check,
                "num_inference_steps": num_inference_steps,
                "num_images_per_prompt": 1,
            })
            
            if res.image_response is None:
                raise Exception("No image response received from Livepeer")
            
            # Convert response to dict for easier handling
            return {
                "success": True,
                "images": res.image_response.images if hasattr(res.image_response, 'images') else [],
                "raw_response": res.image_response
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "images": []
            }


def generate_video_from_image(
    image_path: str,
    width: int = 1024,
    height: int = 576,
    fps: int = 6,
    motion_bucket_id: int = 127,
    noise_aug_strength: float = 0.02,
    num_inference_steps: int = 25,
    safety_check: bool = True
) -> Dict[str, Any]:
    """
    Generate a video from an input image using Livepeer AI.
    Uses tencent/HunyuanVideo model.
    
    Args:
        image_path: Path to the input image file
        width: Video width in pixels (default: 1024)
        height: Video height in pixels (default: 576)
        fps: Frames per second (default: 6)
        motion_bucket_id: Motion intensity (default: 127, range: 1-255)
        noise_aug_strength: Noise augmentation strength (default: 0.02)
        num_inference_steps: Number of denoising steps (default: 25)
        safety_check: Enable safety filtering (default: True)
        
    Returns:
        Dict containing the video response with URL and other metadata
        
    Example:
        >>> result = generate_video_from_image("startup_logo.png")
        >>> video_url = result['video']['url']
    """
    with get_livepeer_client() as livepeer:
        try:
            # Read the image file
            with open(image_path, "rb") as image_file:
                res = livepeer.generate.image_to_video(request={
                    "image": {
                        "file_name": os.path.basename(image_path),
                        "content": image_file.read(),
                    },
                    "model_id": "tencent/HunyuanVideo",
                    "height": height,
                    "width": width,
                    "fps": fps,
                    "motion_bucket_id": motion_bucket_id,
                    "noise_aug_strength": noise_aug_strength,
                    "safety_check": safety_check,
                    "num_inference_steps": num_inference_steps,
                })
                
                if res.video_response is None:
                    raise Exception("No video response received from Livepeer")
                
                # Convert response to dict for easier handling
                return {
                    "success": True,
                    "video": res.video_response.video if hasattr(res.video_response, 'video') else None,
                    "raw_response": res.video_response
                }
                
        except FileNotFoundError:
            return {
                "success": False,
                "error": f"Image file not found: {image_path}",
                "video": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "video": None
            }


def generate_video_from_image_url(
    image_url: str,
    width: int = 1024,
    height: int = 576,
    fps: int = 6,
    motion_bucket_id: int = 127,
    noise_aug_strength: float = 0.02,
    num_inference_steps: int = 25,
    safety_check: bool = True
) -> Dict[str, Any]:
    """
    Generate a video from an image URL using Livepeer AI.
    Downloads the image first, then generates the video.
    Uses tencent/HunyuanVideo model.
    
    Args:
        image_url: URL of the input image
        width: Video width in pixels (default: 1024)
        height: Video height in pixels (default: 576)
        fps: Frames per second (default: 6)
        motion_bucket_id: Motion intensity (default: 127, range: 1-255)
        noise_aug_strength: Noise augmentation strength (default: 0.02)
        num_inference_steps: Number of denoising steps (default: 25)
        safety_check: Enable safety filtering (default: True)
        
    Returns:
        Dict containing the video response with URL and other metadata
        
    Example:
        >>> result = generate_video_from_image_url("https://example.com/image.png")
        >>> video_url = result['video']['url']
    """
    import requests
    import tempfile
    
    try:
        # Download the image
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_file.write(response.content)
            tmp_path = tmp_file.name
        
        # Generate video from the temporary file
        result = generate_video_from_image(
            image_path=tmp_path,
            width=width,
            height=height,
            fps=fps,
            motion_bucket_id=motion_bucket_id,
            noise_aug_strength=noise_aug_strength,
            num_inference_steps=num_inference_steps,
            safety_check=safety_check
        )
        
        # Clean up temporary file
        os.unlink(tmp_path)
        
        return result
        
    except requests.RequestException as e:
        return {
            "success": False,
            "error": f"Failed to download image: {str(e)}",
            "video": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "video": None
        }


# Convenience function for the complete workflow
def generate_marketing_assets(
    prompt: str,
    negative_prompt: str = "blurry, low quality, distorted",
    image_width: int = 1024,
    image_height: int = 576,
    video_fps: int = 6,
    motion_intensity: int = 127
) -> Dict[str, Any]:
    """
    Complete workflow: Generate an image from text, then create a video from that image.
    
    Args:
        prompt: Text description for image generation
        negative_prompt: What to avoid in the image
        image_width: Width for both image and video
        image_height: Height for both image and video
        video_fps: Video frame rate
        motion_intensity: How much motion in the video (1-255)
        
    Returns:
        Dict containing both image and video results
        
    Example:
        >>> result = generate_marketing_assets("Modern tech startup logo")
        >>> image_url = result['image']['url']
        >>> video_url = result['video']['url']
    """
    print(f"🎨 Generating image from prompt: {prompt[:50]}...")
    
    # Step 1: Generate image
    image_result = generate_image_from_text(
        prompt=prompt,
        negative_prompt=negative_prompt,
        width=image_width,
        height=image_height
    )
    
    if not image_result["success"]:
        return {
            "success": False,
            "error": f"Image generation failed: {image_result['error']}",
            "image": None,
            "video": None
        }
    
    # Get the image URL from the response
    image_url = None
    if image_result["images"]:
        image_url = image_result["images"][0].get("url")
    
    if not image_url:
        return {
            "success": False,
            "error": "No image URL in response",
            "image": image_result,
            "video": None
        }
    
    print(f"✅ Image generated: {image_url}")
    print(f"🎬 Generating video from image...")
    
    # Step 2: Generate video from image
    video_result = generate_video_from_image_url(
        image_url=image_url,
        width=image_width,
        height=image_height,
        fps=video_fps,
        motion_bucket_id=motion_intensity
    )
    
    if not video_result["success"]:
        return {
            "success": False,
            "error": f"Video generation failed: {video_result['error']}",
            "image": image_result,
            "video": None
        }
    
    print(f"✅ Video generated successfully!")
    
    return {
        "success": True,
        "image": image_result,
        "video": video_result,
        "image_url": image_url,
        "video_url": video_result.get("video", {}).get("url") if video_result.get("video") else None
    }


if __name__ == "__main__":
    # Example usage
    print("Testing Livepeer AI functions...")
    
    # Test text-to-image
    result = generate_image_from_text(
        prompt="A modern tech startup office with glass walls and natural lighting",
        negative_prompt="blurry, low quality"
    )
    
    if result["success"]:
        print(f"✅ Image generated successfully!")
        print(f"   Images: {len(result['images'])}")
    else:
        print(f"❌ Image generation failed: {result['error']}")
