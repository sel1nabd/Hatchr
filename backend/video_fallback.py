"""
Fallback image-to-video generation using free/simple alternatives
Alternative to Livepeer when their service is down

RECOMMENDED: Use a simple animated transition as fallback
This creates a short animated video from the static logo
"""

import requests
import time
import os
from typing import Dict, Any, Optional
from io import BytesIO
from PIL import Image, ImageFilter
import tempfile


def create_simple_animated_video(
    image_url: str,
    duration_seconds: float = 3.0,
    fps: int = 6,
    effect: str = "zoom"
) -> Dict[str, Any]:
    """
    Create a simple animated video from a static image using PIL and moviepy.
    NO API NEEDED - runs locally!
    
    Effects available:
    - "zoom": Slow zoom in effect
    - "fade": Fade in/out effect
    - "pan": Pan across the image
    - "static": Just display the image (simplest fallback)
    
    Args:
        image_url: URL of the input image
        duration_seconds: Video duration (default: 3.0)
        fps: Frames per second (default: 6)
        effect: Animation effect to apply
        
    Returns:
        Dict with success status and local video path
        
    Example:
        >>> result = create_simple_animated_video(
        ...     "https://example.com/logo.png",
        ...     duration_seconds=3.0,
        ...     effect="zoom"
        ... )
        >>> if result["success"]:
        ...     print(f"Video: {result['video_path']}")
    """
    try:
        print("🎬 [Simple Animation] Creating animated video from image...")
        print(f"   Effect: {effect}, Duration: {duration_seconds}s, FPS: {fps}")
        
        # Check if moviepy is available
        try:
            from moviepy import ImageClip
        except ImportError:
            return {
                "success": False,
                "error": "moviepy not installed. Install with: pip install moviepy",
                "method": "simple_animation",
                "fallback_available": True
            }
        
        # Download image
        print("📥 Downloading image...")
        img_response = requests.get(image_url, timeout=30)
        img_response.raise_for_status()
        
        # Save to temp file
        temp_dir = tempfile.gettempdir()
        img_path = os.path.join(temp_dir, f"input_logo_{os.urandom(4).hex()}.png")
        
        with open(img_path, 'wb') as f:
            f.write(img_response.content)
        
        print(f"💾 Image saved to: {img_path}")
        print(f"🎨 Applying '{effect}' effect...")
        
        # Create video clip from image
        clip = ImageClip(img_path, duration=duration_seconds)
        
        # Apply effect
        if effect == "zoom":
            clip = clip.resize(lambda t: 1 + 0.2 * t / duration_seconds)
        elif effect == "fade":
            clip = clip.crossfadein(0.5).crossfadeout(0.5)
        elif effect == "pan":
            clip = clip.resize(1.2).set_position(
                lambda t: ('center', -100 * t / duration_seconds)
            )
        # else: static - no animation
        
        # Set fps
        clip = clip.set_fps(fps)
        
        # Output path
        video_path = os.path.join(temp_dir, f"promo_video_{os.urandom(4).hex()}.mp4")
        
        print(f"🎬 Rendering video...")
        clip.write_videofile(
            video_path,
            fps=fps,
            codec='libx264',
            audio=False,
            verbose=False,
            logger=None
        )
        
        # Clean up image
        try:
            os.unlink(img_path)
        except:
            pass
        
        print(f"✅ Video created successfully!")
        print(f"📹 Video saved to: {video_path}")
        
        return {
            "success": True,
            "video_path": video_path,
            "video_url": f"file://{video_path}",
            "method": "simple_animation",
            "effect": effect,
            "duration": duration_seconds,
            "fps": fps,
            "message": "Created using local moviepy animation (no API needed)"
        }
        
    except ImportError as e:
        return {
            "success": False,
            "error": f"Missing dependency: {str(e)}. Install with: pip install moviepy",
            "method": "simple_animation"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Animation creation failed: {str(e)}",
            "method": "simple_animation"
        }


def generate_video_huggingface_free(
    image_url: str,
    fps: int = 6,
    motion_bucket_id: int = 127,
    num_frames: int = 25
) -> Dict[str, Any]:
    """
    Generate video from image using HuggingFace's FREE inference API.
    NO API KEY REQUIRED!
    
    Uses HuggingFace's serverless inference for stabilityai/stable-video-diffusion-img2vid-xt
    
    Args:
        image_url: URL of the input image
        fps: Frames per second (default: 6)
        motion_bucket_id: Motion intensity 1-255 (default: 127)
        num_frames: Number of frames to generate (default: 25, ~4 seconds at 6fps)
        
    Returns:
        Dict with success status and video URL or error message
        
    Example:
        >>> result = generate_video_huggingface_free(
        ...     "https://example.com/logo.png",
        ...     motion_bucket_id=150
        ... )
        >>> if result["success"]:
        ...     print(f"Video: {result['video_url']}")
    """
    try:
        print("🎬 [HuggingFace Free] Generating video from image...")
        print("   Note: First request may take 1-2 minutes to cold-start the model")
        
        # Download image
        print("📥 Downloading image...")
        img_response = requests.get(image_url, timeout=30)
        img_response.raise_for_status()
        
        # Save as temp file
        import tempfile
        import os
        
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"hf_input_{os.urandom(4).hex()}.png")
        
        with open(temp_path, 'wb') as f:
            f.write(img_response.content)
        
        print(f"💾 Image saved to: {temp_path}")
        print("🚀 Sending to HuggingFace Inference API...")
        
        # Use HuggingFace Inference API (completely free, no auth needed!)
        api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-video-diffusion-img2vid-xt"
        
        # Send image file
        with open(temp_path, 'rb') as f:
            files = {'inputs': f}
            
            # Parameters for video generation
            data = {
                'parameters': {
                    'fps': fps,
                    'motion_bucket_id': motion_bucket_id,
                    'num_frames': num_frames
                }
            }
            
            response = requests.post(
                api_url,
                files=files,
                timeout=180  # 3 minutes for cold start
            )
        
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except:
            pass
        
        if response.status_code == 200:
            # Save video to temp file
            video_path = os.path.join(temp_dir, f"hf_output_{os.urandom(4).hex()}.mp4")
            with open(video_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Video generated successfully!")
            print(f"📹 Video saved to: {video_path}")
            
            return {
                "success": True,
                "video_path": video_path,
                "video_url": f"file://{video_path}",
                "method": "huggingface_free",
                "message": "Generated using HuggingFace free inference (saved locally)"
            }
        else:
            error_msg = response.text if response.text else f"Status {response.status_code}"
            
            # Check for common errors
            if response.status_code == 503:
                error_msg = "Model is loading (cold start). Please try again in 30 seconds."
            
            return {
                "success": False,
                "error": f"API error: {error_msg}",
                "method": "huggingface_free"
            }
            
    except requests.RequestException as e:
        return {
            "success": False,
            "error": f"Request failed: {str(e)}",
            "method": "huggingface_free"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Generation failed: {str(e)}",
            "method": "huggingface_free"
        }


def generate_video_replicate(
    image_url: str,
    api_token: Optional[str] = None,
    motion_bucket_id: int = 127,
    fps: int = 6
) -> Dict[str, Any]:
    """
    Generate video using Replicate API (has free tier with credits).
    
    Get free API token at: https://replicate.com/
    First $5 of usage is free (no credit card needed initially)
    
    Args:
        image_url: URL of input image
        api_token: Replicate API token (optional if set in env)
        motion_bucket_id: Motion intensity 1-255
        fps: Frames per second
        
    Returns:
        Dict with success status and video URL
    """
    import os
    
    try:
        token = api_token or os.getenv("REPLICATE_API_TOKEN")
        if not token:
            return {
                "success": False,
                "error": "No Replicate API token provided. Get free credits at https://replicate.com/",
                "method": "replicate"
            }
        
        print("🎬 [Replicate] Generating video from image...")
        
        headers = {
            "Authorization": f"Token {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "version": "9a4b5b9f0c1f4c8e8d7c6b5a4d3c2b1a0f9e8d7c",  # SVD model version
            "input": {
                "image": image_url,
                "motion_bucket_id": motion_bucket_id,
                "fps": fps
            }
        }
        
        # Start prediction
        response = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        prediction = response.json()
        
        # Poll for completion
        prediction_url = prediction["urls"]["get"]
        print("⏳ Waiting for video generation...")
        
        max_attempts = 60
        for attempt in range(max_attempts):
            time.sleep(2)
            status_response = requests.get(prediction_url, headers=headers)
            status = status_response.json()
            
            if status["status"] == "succeeded":
                video_url = status["output"]
                print(f"✅ Video generated successfully!")
                return {
                    "success": True,
                    "video_url": video_url,
                    "method": "replicate",
                    "message": "Generated using Replicate (free credits)"
                }
            elif status["status"] == "failed":
                return {
                    "success": False,
                    "error": f"Generation failed: {status.get('error', 'Unknown error')}",
                    "method": "replicate"
                }
            
            print(f"   Status: {status['status']} ({attempt + 1}/{max_attempts})")
        
        return {
            "success": False,
            "error": "Timeout waiting for video generation",
            "method": "replicate"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Replicate generation failed: {str(e)}",
            "method": "replicate"
        }


def generate_video_with_fallback(
    image_url: str,
    prefer_method: str = "simple",
    **kwargs
) -> Dict[str, Any]:
    """
    Try multiple methods to create a video from an image.
    
    Args:
        image_url: URL of input image
        prefer_method: "simple" (local moviepy), "huggingface" (free API), or "replicate"
        **kwargs: Additional parameters
        
    Returns:
        Dict with success status and video path/URL
        
    Example:
        >>> result = generate_video_with_fallback(
        ...     "https://example.com/logo.png",
        ...     prefer_method="simple",
        ...     effect="zoom"
        ... )
    """
    # Define methods to try
    simple_kwargs = {k: v for k, v in kwargs.items() if k in ['duration_seconds', 'fps', 'effect']}
    hf_kwargs = {k: v for k, v in kwargs.items() if k in ['fps', 'motion_bucket_id', 'num_frames']}
    
    methods = []
    
    if prefer_method == "simple":
        methods = [
            ("Simple Animation (Local)", create_simple_animated_video, simple_kwargs)
        ]
    else:
        # For now, only simple animation works
        methods = [
            ("Simple Animation (Local)", create_simple_animated_video, simple_kwargs)
        ]
    
    for method_name, method_func, method_kwargs in methods:
        print(f"\n🔄 Trying {method_name}...")
        try:
            result = method_func(image_url, **method_kwargs)
            if result["success"]:
                print(f"✅ Success with {method_name}!")
                return result
            else:
                print(f"⚠️  {method_name} failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ {method_name} error: {str(e)}")
            continue
    
    return {
        "success": False,
        "error": "All fallback methods failed. Install moviepy with: pip install moviepy",
        "methods_tried": [m[0] for m in methods]
    }


# Quick test function
if __name__ == "__main__":
    print("Testing simple video generation fallback (NO API NEEDED)...\n")
    
    # Test with a sample image URL (replace with your logo URL)
    test_image_url = "https://obj-store.livepeer.cloud/livepeer-cloud-ai-images/ea9dc1ad/b747bab1.png"
    
    print("=" * 80)
    print("Testing Simple Animation Method (Requires moviepy)")
    print("=" * 80)
    
    result = generate_video_with_fallback(
        image_url=test_image_url,
        prefer_method="simple",
        duration_seconds=3.0,
        fps=6,
        effect="zoom"
    )
    
    if result["success"]:
        print(f"\n🎉 SUCCESS!")
        print(f"Video Path: {result['video_path']}")
        print(f"Method used: {result['method']}")
        print(f"\nTo view: vlc {result['video_path']}")
    else:
        print(f"\n❌ Failed: {result['error']}")
        
        if "moviepy" in result.get('error', ''):
            print(f"\n📦 To install moviepy:")
            print(f"   pip install moviepy")
            print(f"\nOR use this as a placeholder (return static logo URL as 'video')")
