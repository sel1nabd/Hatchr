"""
Livepeer AI Functions
Handles text-to-image and image-to-video generation using Livepeer AI SDK
"""

import os
from typing import Optional, Dict, Any
from livepeer_ai import Livepeer
from livepeer_ai.models import components
import requests
import tempfile
import time
import shutil


def get_livepeer_client() -> Livepeer:
    """
    Get Livepeer client with API key from environment
    
    Returns:
        Livepeer: Configured Livepeer client
    """
    api_key = os.getenv("LIVEPEER_API_KEY")
    if not api_key:
        raise ValueError("LIVEPEER_API_KEY not found in environment variables")
    
    # Use Security object for proper authentication
    return Livepeer(
        security=components.Security(
            http_bearer=api_key
        )
    )


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
                "model_id": "black-forest-labs/FLUX.1-dev",
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
            
            # Extract images from response (Livepeer returns Pydantic objects)
            images = []
            if hasattr(res.image_response, 'images') and res.image_response.images:
                for img in res.image_response.images:
                    # Access URL attribute directly, not via .get()
                    images.append({
                        "url": img.url if hasattr(img, 'url') else None,
                        "seed": img.seed if hasattr(img, 'seed') else None,
                        "nsfw": img.nsfw if hasattr(img, 'nsfw') else None
                    })
            
            # Convert response to dict for easier handling
            return {
                "success": True,
                "images": images,
                "raw_response": res.image_response
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "images": []
            }


def download_image_to_temp(image_url: str) -> str:
    """Download an image URL to a temporary file and return the local path."""
    try:
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        temp_dir = tempfile.gettempdir()
        fname = f"lp_image_{os.urandom(8).hex()}.png"
        path = os.path.join(temp_dir, fname)
        with open(path, 'wb') as f:
            f.write(response.content)
        return path
    except Exception as e:
        raise RuntimeError(f"Failed to download image: {e}")


def refine_image_text_readability(
    image_path: str,
    prompt: str,
    model_id: str = "black-forest-labs/FLUX.1-Kontext-dev",
    strength: float = 0.8,
    guidance_scale: float = 14.0,
    image_guidance_scale: float = 2.0,
    negative_prompt: str = "",
    num_inference_steps: int = 100,
    safety_check: bool = True,
    max_retries: int = 4,
    backoff_seconds: float = 5.0,
) -> Dict[str, Any]:
    """
    Use Livepeer's image-to-image to enhance text legibility on a slide image.

    - Downloads are not required (pass local file path).
    - Retries on transient errors (503) with exponential backoff to allow model warmup.
    - Returns dict with success, image_path (local or remote url), and raw_response.
    """
    attempt = 0
    last_error = None

    while attempt < max_retries:
        attempt += 1
        try:
            with get_livepeer_client() as livepeer:
                # Open file as binary as required by SDK
                with open(image_path, 'rb') as f:
                    print(f"🔧 [refine] Sending image_to_image request (attempt {attempt}) to model {model_id}...")
                    res = livepeer.generate.image_to_image(request={
                        "prompt": prompt,
                        "image": {
                            "file_name": os.path.basename(image_path),
                            "content": f,
                        },
                        "model_id": model_id,
                        "loras": "",
                        "strength": strength,
                        "guidance_scale": guidance_scale,
                        "image_guidance_scale": image_guidance_scale,
                        "negative_prompt": negative_prompt,
                        "safety_check": safety_check,
                        "num_inference_steps": num_inference_steps,
                        "num_images_per_prompt": 1,
                    })

                # Check response
                if getattr(res, 'image_response', None) is None:
                    raise Exception("No image_response returned from image_to_image")

                # Attempt to extract returned image URL
                img_url = None
                images = []
                if hasattr(res.image_response, 'images') and res.image_response.images:
                    for img in res.image_response.images:
                        url = img.url if hasattr(img, 'url') else None
                        images.append({
                            "url": url,
                            "seed": getattr(img, 'seed', None),
                            "nsfw": getattr(img, 'nsfw', None)
                        })
                        if not img_url and url:
                            img_url = url

                # If we got a remote URL, download it to a temp file and return the path
                if img_url:
                    try:
                        refined_path = download_image_to_temp(img_url)
                        return {
                            "success": True,
                            "image_path": refined_path,
                            "image_url": img_url,
                            "images": images,
                            "raw_response": res.image_response
                        }
                    except Exception as e:
                        # If download failed, still return the URL
                        return {
                            "success": True,
                            "image_path": None,
                            "image_url": img_url,
                            "images": images,
                            "raw_response": res.image_response,
                            "warning": f"Could not download refined image locally: {e}"
                        }

                # If no URL but images present, still return raw images structure
                return {
                    "success": True,
                    "image_path": None,
                    "image_url": None,
                    "images": images,
                    "raw_response": res.image_response
                }

        except Exception as e:
            last_error = e
            err_str = str(e)
            # If 503-like error, wait and retry to allow warmup
            if '503' in err_str or 'Service Unavailable' in err_str or 'timed out' in err_str.lower():
                wait = backoff_seconds * attempt
                print(f"⚠️ [refine] Transient error (attempt {attempt}): {err_str}. Waiting {wait}s before retrying...")
                time.sleep(wait)
                continue
            else:
                # Non-retryable
                return {"success": False, "error": err_str}

    return {"success": False, "error": f"All retries failed: {last_error}"}


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
    Generate video from an image URL using Livepeer's image-to-video API.
    Uses stabilityai/stable-video-diffusion-img2vid-xt-1-1 model (Livepeer's warm model).
    Downloads the image, saves it to a temporary file, and sends as file object.
    
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
                        "content": image_file,
                    },
                    "model_id": "stabilityai/stable-video-diffusion-img2vid-xt-1-1",
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
                
                # Extract video from response (Livepeer returns Pydantic objects)
                video_data = None
                if hasattr(res.video_response, 'video') and res.video_response.video:
                    vid = res.video_response.video
                    video_data = {
                        "url": vid.url if hasattr(vid, 'url') else None,
                        "seed": vid.seed if hasattr(vid, 'seed') else None,
                        "nsfw": vid.nsfw if hasattr(vid, 'nsfw') else None
                    }
                
                # Convert response to dict for easier handling
                return {
                    "success": True,
                    "video": video_data,
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
    Downloads the image first, saves it temporarily, then generates the video.
    Uses stabilityai/stable-video-diffusion-img2vid-xt model.
    
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
    
    with get_livepeer_client() as livepeer:
        try:
            print(f"📥 Downloading image from URL...")
            # Download the image
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Save to temporary file with proper extension
            temp_dir = tempfile.gettempdir()
            temp_filename = f"livepeer_image_{os.urandom(8).hex()}.png"
            temp_path = os.path.join(temp_dir, temp_filename)
            
            with open(temp_path, 'wb') as f:
                f.write(response.content)
            
            print(f"💾 Image saved temporarily to: {temp_path}")
            print(f"🎬 Generating video from image...")
            
            # Open and send the file as Livepeer expects
            with open(temp_path, "rb") as image_file:
                res = livepeer.generate.image_to_video(request={
                    "image": {
                        "file_name": temp_filename,
                        "content": image_file,
                    },
                    "model_id": "stabilityai/stable-video-diffusion-img2vid-xt-1-1",
                    "height": height,
                    "width": width,
                    "fps": fps,
                    "motion_bucket_id": motion_bucket_id,
                    "noise_aug_strength": noise_aug_strength,
                    "safety_check": safety_check,
                    "num_inference_steps": num_inference_steps,
                })
            
            # Clean up temporary file
            try:
                os.unlink(temp_path)
                print(f"🧹 Cleaned up temporary file")
            except:
                pass
            
            if res.video_response is None:
                raise Exception("No video response received from Livepeer")
            
            # Extract video from response (Livepeer returns Pydantic objects)
            video_data = None
            if hasattr(res.video_response, 'video') and res.video_response.video:
                vid = res.video_response.video
                video_data = {
                    "url": vid.url if hasattr(vid, 'url') else None,
                    "seed": vid.seed if hasattr(vid, 'seed') else None,
                    "nsfw": vid.nsfw if hasattr(vid, 'nsfw') else None
                }
            
            return {
                "success": True,
                "video": video_data,
                "raw_response": res.video_response
            }
            
        except requests.RequestException as e:
            return {
                "success": False,
                "error": f"Failed to download image: {str(e)}",
                "video": None
            }
        except Exception as e:
            # Clean up temp file if it exists
            try:
                if 'temp_path' in locals():
                    os.unlink(temp_path)
            except:
                pass
            
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


def generate_startup_branding(
    startup_idea: str,
    startup_name: str = "",
    style: str = "modern",
    color_scheme: str = "",
    logo_width: int = 1024,
    logo_height: int = 1024,
    video_fps: int = 8,
    motion_intensity: int = 140,
    include_video: bool = True
) -> Dict[str, Any]:
    """
    Generate complete startup branding: logo image and promotional video from a startup idea.
    Perfect for frontend integration - user describes their startup, gets back branding assets.
    
    Args:
        startup_idea: Description of the startup (e.g., "AI-powered task management for freelancers")
        startup_name: Optional name of the startup (included in prompt if provided)
        style: Visual style - "modern", "minimalist", "playful", "professional", "tech", "elegant"
        color_scheme: Optional color preferences (e.g., "blue and white", "vibrant neon")
        logo_width: Logo image width (default: 1024, square for logo)
        logo_height: Logo image height (default: 1024, square for logo)
        video_fps: Video frame rate (default: 8 for smoother motion)
        motion_intensity: How dynamic the video is, 1-255 (default: 140)
        include_video: Whether to generate video or just logo (default: True)
        
    Returns:
        Dict containing:
            - success: bool
            - logo_url: URL to the generated logo image
            - video_url: URL to the promotional video (if include_video=True)
            - logo_prompt: The actual prompt used for logo generation
            - metadata: Additional info about the generation
            
    Example:
        >>> result = generate_startup_branding(
        ...     startup_idea="AI scheduling assistant for busy professionals",
        ...     startup_name="TimeAI",
        ...     style="modern",
        ...     color_scheme="blue and purple gradient"
        ... )
        >>> print(f"Logo: {result['logo_url']}")
        >>> print(f"Video: {result['video_url']}")
    """
    
    print(f"\n🚀 Generating branding for startup idea: {startup_idea[:60]}...")
    
    # Build an optimized prompt for logo generation
    style_descriptors = {
        "modern": "clean, modern, minimalist, contemporary, sleek",
        "minimalist": "ultra minimalist, simple, clean lines, geometric, understated",
        "playful": "playful, colorful, fun, friendly, approachable, whimsical",
        "professional": "professional, corporate, refined, sophisticated, polished",
        "tech": "futuristic, tech-focused, digital, innovative, cutting-edge, high-tech",
        "elegant": "elegant, luxurious, refined, premium, sophisticated, classy"
    }
    
    style_desc = style_descriptors.get(style.lower(), style_descriptors["modern"])
    
    # Construct the logo generation prompt
    logo_prompt_parts = [
        f"Professional startup logo design",
    ]
    
    if startup_name:
        logo_prompt_parts.append(f"for '{startup_name}'")
    
    logo_prompt_parts.extend([
        f"representing: {startup_idea}",
        f"Style: {style_desc}",
    ])
    
    if color_scheme:
        logo_prompt_parts.append(f"Color scheme: {color_scheme}")
    
    logo_prompt_parts.extend([
        "High quality, vector-style, iconic, memorable",
        "Suitable for app icon and website header",
        "Clean background, centered composition",
        "4K resolution, professional design"
    ])
    
    logo_prompt = ", ".join(logo_prompt_parts)
    
    # Negative prompt for logo generation
    logo_negative_prompt = (
        "text, letters, words, watermark, signature, blurry, low quality, "
        "distorted, noisy, grainy, pixelated, amateur, clipart, low resolution, "
        "ugly, deformed, messy, cluttered, busy, photo realistic people, "
        "photographs, 3D renders of objects"
    )
    
    print(f"📝 Logo prompt: {logo_prompt[:100]}...")
    print(f"🎨 Generating logo image...")
    
    # Step 1: Generate logo image
    logo_result = generate_image_from_text(
        prompt=logo_prompt,
        negative_prompt=logo_negative_prompt,
        width=logo_width,
        height=logo_height,
        guidance_scale=8.0,  # Higher guidance for more precise logo
        num_inference_steps=60,  # More steps for higher quality
        safety_check=True
    )
    
    if not logo_result["success"]:
        return {
            "success": False,
            "error": f"Logo generation failed: {logo_result['error']}",
            "logo_url": None,
            "video_url": None,
            "logo_prompt": logo_prompt,
            "metadata": {}
        }
    
    # Extract logo URL
    logo_url = None
    if logo_result["images"] and len(logo_result["images"]) > 0:
        logo_url = logo_result["images"][0]["url"]
    
    if not logo_url:
        return {
            "success": False,
            "error": "No logo URL in response",
            "logo_url": None,
            "video_url": None,
            "logo_prompt": logo_prompt,
            "metadata": {}
        }
    
    print(f"✅ Logo generated: {logo_url}")
    
    # If video not requested, return just the logo
    if not include_video:
        return {
            "success": True,
            "logo_url": logo_url,
            "video_url": None,
            "logo_prompt": logo_prompt,
            "metadata": {
                "startup_idea": startup_idea,
                "startup_name": startup_name,
                "style": style,
                "logo_dimensions": f"{logo_width}x{logo_height}"
            }
        }
    
    # Step 2: Generate promotional video from logo
    print(f"🎬 Generating promotional video from logo...")
    
    video_result = generate_video_from_image_url(
        image_url=logo_url,
        width=576,  # SVD model works better with 576 width
        height=1024,  # SVD model works better with 1024 height
        fps=6,  # Keep FPS low for stability
        motion_bucket_id=motion_intensity,
        num_inference_steps=25,  # Reduce steps for faster generation
        safety_check=True
    )
    
    if not video_result["success"]:
        # Return logo even if video fails
        print(f"⚠️  Video generation failed: {video_result['error']}")
        return {
            "success": True,  # Still successful since we have logo
            "logo_url": logo_url,
            "video_url": None,
            "logo_prompt": logo_prompt,
            "metadata": {
                "startup_idea": startup_idea,
                "startup_name": startup_name,
                "style": style,
                "logo_dimensions": f"{logo_width}x{logo_height}",
                "video_error": video_result['error']
            }
        }
    
    video_url = None
    if video_result.get("video") and isinstance(video_result["video"], dict):
        video_url = video_result["video"].get("url")
    
    if video_url:
        print(f"✅ Video generated: {video_url}")
    else:
        print(f"⚠️  Video URL not found in response")
    
    return {
        "success": True,
        "logo_url": logo_url,
        "video_url": video_url,
        "logo_prompt": logo_prompt,
        "metadata": {
            "startup_idea": startup_idea,
            "startup_name": startup_name,
            "style": style,
            "color_scheme": color_scheme,
            "logo_dimensions": f"{logo_width}x{logo_height}",
            "video_fps": video_fps,
            "motion_intensity": motion_intensity
        }
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
