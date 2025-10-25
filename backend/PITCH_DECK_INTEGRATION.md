# Pitch Deck API Integration - Summary

## What Was Done

Successfully integrated the pitch deck generation functionality from `pitch_deck_generator.py` and `lpfuncs.py` into the FastAPI `main.py` endpoint.

## Changes Made

### 1. Updated `main.py`
- **Line 23**: Added import: `from pitch_deck_generator import generate_pitch_deck as generate_deck_slides`
- **Lines 154-213**: Replaced TODO implementation of `LivepeerService.generate_pitch_deck()` with full working implementation

### 2. Key Features Implemented

The `generate_pitch_deck()` function now:
- ✅ Extracts startup name from project summary
- ✅ Calls the actual Livepeer-based pitch deck generator
- ✅ Generates 5 professional slides (Title, Problem, Solution, Market, Business Model)
- ✅ Includes image-to-image refinement for better text readability
- ✅ Returns structured response with:
  - `deck_url`: Preview URL (first slide)
  - `slides`: Array of slide objects with URLs and refined paths
  - `total_slides`: Count of successfully generated slides
  - `status`: "generated" or "failed"
  - `error`: Error message if failed

### 3. Response Format

```json
{
  "deck_url": "https://obj-store.livepeer.cloud/...",
  "slides": [
    {
      "slide_number": 1,
      "title": "Title Slide",
      "image_url": "https://obj-store.livepeer.cloud/...",
      "refined_image_path": "/tmp/lp_image_abc123.png",  // if refinement succeeded
      "refined_image_url": "https://obj-store.livepeer.cloud/..."  // if available
    },
    // ... more slides
  ],
  "total_slides": 5,
  "status": "generated"
}
```

### 4. Error Handling

- Graceful fallback to placeholder on failure
- Returns error details in response
- Catches exceptions and logs them

## How It Works

1. **API Call**: When `LivepeerService.generate_pitch_deck(project_summary)` is called
2. **Name Extraction**: Attempts to extract startup name from summary
3. **Generation**: Calls `generate_deck_slides()` which:
   - Generates 5 slides using Livepeer text-to-image (FLUX.1-dev)
   - Downloads each generated slide
   - Applies image-to-image refinement (FLUX.1-Kontext-dev) to enhance text readability
   - Retries on 503 errors with exponential backoff
4. **Response Formatting**: Packages slides into API-friendly format
5. **Return**: Returns structured JSON response

## Usage in API Flow

The function is called in two places in `main.py`:

1. **Line 419**: During project generation workflow
   ```python
   deck = await LivepeerService.generate_pitch_deck(analysis['information'][:500])
   ```

2. **Line 798**: In the launch preparation endpoint
   ```python
   deck = await LivepeerService.generate_pitch_deck(description[:500])
   ```

## Testing

Run the test script:
```bash
cd backend
python test_pitch_deck_api.py
```

Or test via the full API flow:
```bash
# Start the server
python main.py

# Then use the /generate endpoint with a startup idea
```

## Known Issues & Limitations

1. **Model Warmup**: FLUX.1-Kontext-dev often returns 503 on first calls (requires warmup)
2. **Retry Logic**: Currently retries 4 times with exponential backoff (5s, 10s, 15s, 20s)
3. **Partial Failures**: May generate 3/5 or 4/5 slides if API has transient issues
4. **Synchronous Call**: `generate_deck_slides()` is synchronous (blocks during generation)

## Future Improvements

1. Add async/await support to pitch_deck_generator.py
2. Implement pre-warming calls for FLUX.1-Kontext-dev
3. Add caching for generated slides
4. Store refined images in cloud storage instead of temp files
5. Add progress callbacks for real-time updates
6. Implement slide editing/regeneration endpoints

## Files Modified

- `/backend/main.py` - Added import and implemented generate_pitch_deck()
- `/backend/test_pitch_deck_api.py` - Created test script

## Files Used (No Changes)

- `/backend/lpfuncs.py` - Core Livepeer functions
- `/backend/pitch_deck_generator.py` - Slide generation logic
