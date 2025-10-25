"""
Test script for pitch deck generation in main.py
Tests the LivepeerService.generate_pitch_deck() function
"""

import asyncio
from main import LivepeerService


async def test_pitch_deck_generation():
    """Test the pitch deck generation endpoint"""
    
    print("\n" + "=" * 80)
    print("TESTING PITCH DECK API INTEGRATION")
    print("=" * 80 + "\n")
    
    # Sample project summary
    project_summary = """
    Name: FlowMaster
    
    FlowMaster is an AI-powered task management platform designed for freelancers 
    and solopreneurs. It helps organize work, track time, and automate repetitive 
    tasks using machine learning.
    
    Key Features:
    - Intelligent task prioritization
    - Automated time tracking
    - Client management dashboard
    - Invoice generation
    - AI-powered insights
    
    Target Market: Freelancers, solopreneurs, and small business owners managing 
    multiple clients.
    
    Business Model: Freemium with premium tiers ($0/month free, $15/month pro, 
    $30/month enterprise)
    """
    
    try:
        print("📊 Generating pitch deck from project summary...")
        result = await LivepeerService.generate_pitch_deck(project_summary)
        
        print("\n✅ Generation complete!")
        print(f"Status: {result.get('status')}")
        print(f"Total slides: {result.get('total_slides', 0)}")
        
        if result.get('slides'):
            print("\n📊 Generated Slides:")
            print("-" * 80)
            for slide in result['slides']:
                print(f"\nSlide {slide['slide_number']}: {slide['title']}")
                print(f"Image URL: {slide['image_url']}")
                if 'refined_image_path' in slide:
                    print(f"Refined Path: {slide['refined_image_path']}")
                if 'refined_image_url' in slide:
                    print(f"Refined URL: {slide['refined_image_url']}")
        
        if result.get('error'):
            print(f"\n⚠️  Error: {result['error']}")
        
        print("\n" + "=" * 80)
        return result
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = asyncio.run(test_pitch_deck_generation())
    
    if result and result.get("status") == "generated":
        print("\n🎉 SUCCESS! Pitch deck API integration working correctly!")
    else:
        print("\n⚠️  Test completed but check for errors above")
