# Livepeer AI Integration - Complete Guide

## Overview

Hatchr now uses **Livepeer AI** to generate professional marketing assets (logo and pitch deck) using the **enriched prompt from GPT-4o**. This ensures high-quality, context-aware branding that reflects the actual market research and competitive analysis.

## Architecture

### Flow

```
User Idea
    ↓
GPT-4o Enrichment
    ├─ Market research
    ├─ Competitor analysis
    ├─ Feature identification
    └─ Detailed enriched prompt (with context)
    ↓
Sonnet 4.5 Code Generation
    ├─ FastAPI backend
    └─ SQLite database
    ↓
Render Deployment
    └─ Live backend URL
    ↓
Livepeer AI Image Generation (using enriched prompt!)
    ├─ Startup Logo (1024x1024)
    └─ 5-Slide Pitch Deck (1024x576 each)
    ↓
Display in LaunchPage
    ├─ Logo preview
    └─ Pitch deck slides grid
```

## Backend Implementation

### Files

**lpfuncs.py** - Core Livepeer functions
- `generate_image_from_text()` - Text-to-image using FLUX.1-dev model
- `generate_startup_branding()` - Complete logo generation workflow
- `refine_image_text_readability()` - Image-to-image refinement for text clarity
- `generate_video_from_image()` - Image-to-video (optional)

**pitch_deck_generator.py** - Pitch deck generation
- `generate_pitch_deck()` - Creates 5 professional slides:
  1. Title Slide - Company name + logo
  2. Problem Slide - What problem is being solved
  3. Solution Slide - How the startup solves it
  4. Market Opportunity - TAM/SAM/SOM metrics
  5. Business Model - Pricing tiers

**main.py** - Integration
- `LivepeerService.generate_startup_logo(enriched_spec)` - Uses full GPT-4o context
- `LivepeerService.generate_pitch_deck(enriched_spec)` - Uses enriched data
- Stores results in `projects_db[project_id]['marketing_assets']`

### Key Changes

**Before:**
```python
# Only used short description
deck = await LivepeerService.generate_pitch_deck(description[:500])
```

**After:**
```python
# Uses full enriched spec from GPT-4o
enriched_spec = result.get('spec', {})  # Contains enriched_prompt, market_context, etc.
logo = await LivepeerService.generate_startup_logo(enriched_spec)
deck = await LivepeerService.generate_pitch_deck(enriched_spec)
```

## Enriched Prompt Structure

The `enriched_spec` from GPT-4o contains:

```json
{
  "project_name": "Short project name",
  "description": "One-sentence description",
  "enriched_prompt": "MEGA DETAILED prompt with market context, competitors, features, technical requirements",
  "example_companies": ["Competitor1", "Competitor2", "Competitor3"],
  "market_context": "Brief market analysis",
  "key_features": ["Feature1", "Feature2", ...],
  "database_schema": "Table descriptions",
  "api_endpoints": ["GET /items", "POST /items", ...]
}
```

## Logo Generation

**Context passed to Livepeer:**
```python
logo_context = f"{project_name}: {description}. {enriched_prompt[:300]}"
```

**Example:**
- Input: "AI task manager for freelancers"
- GPT-4o adds: Market context, competitors (Asana, Trello), key features
- Livepeer receives: "TaskFlow: AI-powered task management. Market: Productivity SaaS competing with Asana and Trello. Features: Smart scheduling, time tracking..."
- Result: Logo that visually represents the concept better

## Pitch Deck Generation

**Context passed to Livepeer:**
```python
startup_idea = f"{description}. {enriched_prompt[:400]}"
industry = enriched_spec.get('market_context', '')
```

**Slide Generation:**
- Uses enriched context to create more accurate slides
- Each slide: 1024x576px (presentation format)
- Text refinement step improves readability
- Returns both original and refined image URLs

## Frontend Display

### LaunchPage.tsx

**New "Marketing Assets" Card:**

```tsx
{projectData?.marketing_assets && (
  <Card>
    {/* Startup Logo */}
    {projectData.marketing_assets.logo?.logo_url && (
      <img src={projectData.marketing_assets.logo.logo_url} />
    )}

    {/* Pitch Deck Slides */}
    {projectData.marketing_assets.pitch_deck?.slides?.map((slide) => (
      <img src={slide.refined_image_url || slide.image_url} />
    ))}
  </Card>
)}
```

**Features:**
- Logo displayed in bordered container with gradient background
- "View Full Size" button to open logo in new tab
- Pitch deck slides in 2-column grid (responsive)
- Click any slide to view full resolution
- Shows refined images when available (better text clarity)
- Conditional rendering - only shows if assets exist

## Project Data Structure

Projects now include:

```json
{
  "project_id": "uuid",
  "project_name": "StartupName",
  "description": "...",
  "live_url": "https://...",
  "tech_stack": ["FastAPI", "SQLite", "Python"],
  "marketing_assets": {
    "logo": {
      "success": true,
      "logo_url": "https://livepeer.studio/...",
      "metadata": {...}
    },
    "pitch_deck": {
      "success": true,
      "deck_url": "https://...",
      "slides": [
        {
          "slide_number": 1,
          "title": "Title Slide",
          "image_url": "https://...",
          "refined_image_url": "https://..." // Optional
        },
        ...
      ],
      "total_slides": 5
    }
  },
  "spec": {...} // Full enriched spec from GPT-4o
}
```

## Benefits of Using Enriched Prompts

### Without Enriched Prompt (Old Way)
```
Livepeer prompt: "AI task manager for freelancers"
Result: Generic, abstract logo
```

### With Enriched Prompt (New Way)
```
Livepeer prompt: "TaskFlow: AI-powered task management for freelancers.
                  Competing with Asana, Trello, ClickUp.
                  Features: smart scheduling, time tracking, automation.
                  Market: $2B productivity SaaS space."

Result: Logo with specific visual elements reflecting the concept better
```

## API Endpoints

### Get Project (includes marketing assets)
```
GET /api/project/{project_id}

Response:
{
  "project_id": "...",
  "marketing_assets": {
    "logo": {...},
    "pitch_deck": {...}
  },
  ...
}
```

## Testing

To test logo generation:
```bash
cd backend
python quick_logo_test.py
```

To test pitch deck:
```bash
cd backend
python pitch_deck_generator.py
```

To test complete flow:
1. Submit startup idea in frontend
2. Wait for generation to complete
3. Navigate to Launch page
4. See "Marketing Assets" card with logo and pitch deck

## Livepeer Models Used

- **Text-to-Image**: `black-forest-labs/FLUX.1-dev` (high quality, fast)
- **Image-to-Image**: `black-forest-labs/FLUX.1-Kontext-dev` (text refinement)
- **Image-to-Video**: `stabilityai/stable-video-diffusion-img2vid-xt-1-1` (optional)

## Configuration

**Environment Variables:**
```bash
LIVEPEER_API_KEY=your_api_key_here
```

**Image Dimensions:**
- Logo: 1024x1024 (square, high res)
- Pitch Deck Slides: 1024x576 (16:9 presentation ratio)

## Future Enhancements

1. **Video Generation**: Uncomment video generation in LivepeerService
2. **Custom Styles**: Allow users to select visual style
3. **Color Customization**: Let users specify brand colors
4. **Download Assets**: Add download buttons for logo/slides
5. **Asset Library**: Store all generated assets for user's account

## Troubleshooting

**Logo not showing:**
- Check `projectData.marketing_assets.logo.success` is true
- Verify `logo_url` exists in browser console
- Check backend logs for Livepeer API errors

**Pitch deck slides not showing:**
- Check `projectData.marketing_assets.pitch_deck.slides` is populated
- Verify Livepeer API key is set
- Check pitch_deck_generator logs for errors

**Livepeer API errors:**
- Ensure LIVEPEER_API_KEY is set in environment
- Check API quota/limits
- Verify network connectivity to Livepeer
