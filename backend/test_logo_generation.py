"""
Test script for logo generation in main.py
Tests the LivepeerService.generate_startup_logo() function
"""

import asyncio
from main import LivepeerService


async def test_logo_generation():
    """Test the logo generation endpoint"""
    
    print("\n" + "=" * 80)
    print("TESTING LOGO GENERATION API INTEGRATION")
    print("=" * 80 + "\n")
    
    # Test Case 1: Full details
    print("Test 1: Logo with full details")
    print("-" * 80)
    result1 = await LivepeerService.generate_startup_logo(
        startup_idea="AI-powered task management platform for freelancers",
        startup_name="FlowMaster",
        style="modern",
        color_scheme="blue and purple gradient"
    )
    
    print(f"Status: {result1.get('status')}")
    print(f"Logo URL: {result1.get('logo_url')}")
    if result1.get('metadata'):
        print(f"Metadata: {result1['metadata']}")
    if result1.get('error'):
        print(f"Error: {result1['error']}")
    
    # Test Case 2: Minimal details
    print("\n" + "=" * 80)
    print("Test 2: Logo with minimal details (auto-naming)")
    print("-" * 80)
    result2 = await LivepeerService.generate_startup_logo(
        startup_idea="SaaS for automated product acquisition and immediate relisting"
    )
    
    print(f"Status: {result2.get('status')}")
    print(f"Logo URL: {result2.get('logo_url')}")
    if result2.get('metadata'):
        print(f"Metadata: {result2['metadata']}")
    if result2.get('error'):
        print(f"Error: {result2['error']}")
    
    # Test Case 3: Different styles
    print("\n" + "=" * 80)
    print("Test 3: Logo with 'tech' style")
    print("-" * 80)
    result3 = await LivepeerService.generate_startup_logo(
        startup_idea="Blockchain-based supply chain tracking",
        startup_name="ChainTrack",
        style="tech",
        color_scheme="neon green and black"
    )
    
    print(f"Status: {result3.get('status')}")
    print(f"Logo URL: {result3.get('logo_url')}")
    if result3.get('metadata'):
        print(f"Metadata: {result3['metadata']}")
    if result3.get('error'):
        print(f"Error: {result3['error']}")
    
    print("\n" + "=" * 80)
    
    # Summary
    successes = sum(1 for r in [result1, result2, result3] if r.get('status') == 'generated')
    print(f"\n✅ {successes}/3 logos generated successfully")
    
    return [result1, result2, result3]


async def test_quick_logo():
    """Quick single logo test"""
    
    print("\n" + "=" * 80)
    print("QUICK LOGO TEST")
    print("=" * 80 + "\n")
    
    result = await LivepeerService.generate_startup_logo(
        startup_idea="SaaS for automated product acquisition buying and immediate relisting for the reselling game",
        startup_name="Flippify",
        style="modern",
        color_scheme="Pastel colour scheme mainly blue"
    )
    
    if result.get("status") == "generated":
        print("✅ SUCCESS!\n")
        print("=" * 80)
        print("GENERATED LOGO:")
        print("=" * 80)
        print(f"\n{result['logo_url']}\n")
        print("=" * 80)
        
        if result.get('metadata'):
            print("\nMetadata:")
            for key, value in result['metadata'].items():
                print(f"  {key}: {value}")
        
        return result['logo_url']
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        return None


if __name__ == "__main__":
    import sys
    
    # Check for quick test flag
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        logo_url = asyncio.run(test_quick_logo())
        if logo_url:
            print(f"\n✅ Logo successfully generated!")
            print(f"   You can view it at: {logo_url}")
            print(f"   Or use it in your application!\n")
    else:
        results = asyncio.run(test_logo_generation())
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        for i, result in enumerate(results, 1):
            status_emoji = "✅" if result.get('status') == 'generated' else "❌"
            print(f"{status_emoji} Test {i}: {result.get('status')}")
            if result.get('logo_url') and 'placeholder' not in result['logo_url']:
                print(f"   URL: {result['logo_url']}")
