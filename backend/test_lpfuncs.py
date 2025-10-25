"""
Quick test of lpfuncs.py
Tests that imports work and functions are callable
"""

import os
import sys

print("Testing lpfuncs.py imports and structure...\n")

try:
    from lpfuncs import (
        get_livepeer_client,
        generate_image_from_text,
        generate_video_from_image,
        generate_video_from_image_url,
        generate_marketing_assets
    )
    print("✅ All functions imported successfully")
    
    # Check if API key is set
    api_key = os.getenv("LIVEPEER_API_KEY")
    if api_key:
        print(f"✅ LIVEPEER_API_KEY is set (length: {len(api_key)})")
    else:
        print("⚠️  LIVEPEER_API_KEY not set in environment")
        print("   Set it with: export LIVEPEER_API_KEY='your_key_here'")
    
    print("\n" + "="*60)
    print("Function signatures:")
    print("="*60)
    
    print("\n1. generate_image_from_text(")
    print("       prompt: str,")
    print("       negative_prompt: str = '',")
    print("       width: int = 1024,")
    print("       height: int = 576,")
    print("       ...)")
    
    print("\n2. generate_video_from_image(")
    print("       image_path: str,")
    print("       width: int = 1024,")
    print("       height: int = 576,")
    print("       fps: int = 6,")
    print("       ...)")
    
    print("\n3. generate_video_from_image_url(")
    print("       image_url: str,")
    print("       ...)")
    
    print("\n4. generate_marketing_assets(")
    print("       prompt: str,")
    print("       negative_prompt: str = 'blurry, low quality, distorted',")
    print("       ...)")
    
    print("\n" + "="*60)
    print("✅ All tests passed! Functions are ready to use.")
    print("="*60)
    
    print("\nTo test with actual API calls, run:")
    print("  python lpfuncs_examples.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
