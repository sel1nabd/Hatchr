# Livepeer AI Functions

Functions for generating images and videos using Livepeer AI SDK.

## Features

- **Text-to-Image**: Generate images from text prompts using `SG161222/RealVisXL_V4.0_Lightning` model
- **Image-to-Video**: Animate images into videos using `tencent/HunyuanVideo` model
- **Complete Workflow**: One-function solution for text → image → video

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your Livepeer API key** in `.env`:
   ```bash
   LIVEPEER_API_KEY=your_api_key_here
   ```

## Functions

### `generate_image_from_text(prompt, ...)`

Generate an image from a text description.

**Parameters:**
- `prompt` (str): Text description of the image
- `negative_prompt` (str): What to avoid in the image
- `width` (int): Image width (default: 1024)
- `height` (int): Image height (default: 576)
- `guidance_scale` (float): How closely to follow prompt (default: 7.5)
- `num_inference_steps` (int): Quality/speed tradeoff (default: 50)

**Returns:**
```python
{
    "success": True,
    "images": [{"url": "https://...", ...}],
    "raw_response": <ImageResponse>
}
```

**Example:**
```python
from lpfuncs import generate_image_from_text

result = generate_image_from_text(
    prompt="A futuristic startup office",
    negative_prompt="blurry, low quality"
)

if result["success"]:
    image_url = result["images"][0]["url"]
    print(f"Generated: {image_url}")
```

---

### `generate_video_from_image(image_path, ...)`

Generate a video from a local image file.

**Parameters:**
- `image_path` (str): Path to input image
- `width` (int): Video width (default: 1024)
- `height` (int): Video height (default: 576)
- `fps` (int): Frames per second (default: 6)
- `motion_bucket_id` (int): Motion intensity 1-255 (default: 127)
- `noise_aug_strength` (float): Noise level (default: 0.02)
- `num_inference_steps` (int): Quality/speed tradeoff (default: 25)

**Returns:**
```python
{
    "success": True,
    "video": {"url": "https://...", ...},
    "raw_response": <VideoResponse>
}
```

**Example:**
```python
from lpfuncs import generate_video_from_image

result = generate_video_from_image(
    image_path="my_image.png",
    motion_bucket_id=150  # Higher motion
)

if result["success"]:
    video_url = result["video"]["url"]
    print(f"Generated: {video_url}")
```

---

### `generate_video_from_image_url(image_url, ...)`

Generate a video from an image URL (downloads image first).

**Parameters:** Same as `generate_video_from_image()` but takes `image_url` instead of `image_path`

**Example:**
```python
from lpfuncs import generate_video_from_image_url

result = generate_video_from_image_url(
    image_url="https://example.com/image.png",
    fps=8,
    motion_bucket_id=180
)
```

---

### `generate_marketing_assets(prompt, ...)`

Complete workflow: text → image → video in one call.

**Parameters:**
- `prompt` (str): Text description
- `negative_prompt` (str): What to avoid
- `image_width` (int): Width for both image and video
- `image_height` (int): Height for both image and video
- `video_fps` (int): Video frame rate
- `motion_intensity` (int): Motion level 1-255

**Returns:**
```python
{
    "success": True,
    "image": <image_result>,
    "video": <video_result>,
    "image_url": "https://...",
    "video_url": "https://..."
}
```

**Example:**
```python
from lpfuncs import generate_marketing_assets

result = generate_marketing_assets(
    prompt="Modern tech startup logo with neon colors",
    negative_prompt="blurry, low quality",
    motion_intensity=150
)

if result["success"]:
    print(f"Image: {result['image_url']}")
    print(f"Video: {result['video_url']}")
```

## Models Used

- **Text-to-Image**: `SG161222/RealVisXL_V4.0_Lightning` - High-quality, fast image generation
- **Image-to-Video**: `tencent/HunyuanVideo` - Advanced video generation with motion

## Error Handling

All functions return a dict with `"success"` key:

```python
result = generate_image_from_text("test prompt")

if result["success"]:
    # Success - use result["images"], result["video"], etc.
    pass
else:
    # Error - check result["error"]
    print(f"Error: {result['error']}")
```

## Testing

Run the examples:

```bash
python lpfuncs_examples.py
```

Or test specific functions:

```bash
python lpfuncs.py
```

## Integration with Hatchr

These functions are used in `main.py` for generating marketing assets:

```python
from lpfuncs import generate_marketing_assets

# In your generation pipeline:
assets = generate_marketing_assets(
    prompt=f"Marketing image for {startup_name}: {description}",
    motion_intensity=127
)
```
