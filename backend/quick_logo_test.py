"""
Quick test - Generate logo only (no video)
Faster and works even if video API has issues
"""

import os
from dotenv import load_dotenv
from lpfuncs import generate_startup_branding

load_dotenv()

def quick_logo_test():
    """Generate just a logo for testing"""
    
    print("\n" + "=" * 80)
    print("QUICK LOGO GENERATION TEST")
    print("=" * 80 + "\n")
    
    # Test with logo only (skip video)
    result = generate_startup_branding(
        startup_idea="SaaS for automated product acquisition buying and immediate relisting for the reselling game",
        startup_name="Flippify",
        style="complex in the style of Stripe",
        color_scheme="Pastel colour scheme mainly blue",
        include_video=False  # Skip video to test faster
    )
    
    if result["success"]:
        print("✅ SUCCESS!\n")
        print("=" * 80)
        print("GENERATED LOGO:")
        print("=" * 80)
        print(f"\n{result['logo_url']}\n")
        print("=" * 80)
        
        return result["logo_url"]
    else:
        print(f"❌ Failed: {result['error']}")
        return None


if __name__ == "__main__":
    logo_url = quick_logo_test()
    
    if logo_url:
        print(f"\n✅ Logo successfully generated!")
        print(f"   You can view it at: {logo_url}")
        print(f"   Or use it in your application!\n")
