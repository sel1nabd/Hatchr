# This could be placed in your backend, e.g., in a new file `backend/livepeer_client.py`
import os
import requests
import time
import sys

# As per your SETUP.md, the API key is loaded from environment variables.
# Make sure you have run `export LIVEPEER_API_KEY='your_key_here'` or set it in a .env file.
API_KEY = os.getenv("LIVEPEER_API_KEY", "d0fdd794-e957-4c79-9a66-38f90a8a03ac") # Uses env var, with a fallback for testing
GATEWAY_URL = "https://dream-gateway.livepeer.cloud"
STATUS_URL = "https://livepeer.studio/api/daydream"

def generate_image_from_text(prompt: str):
    """
    Generates an image from a text prompt using the Livepeer API.

    Args:
        prompt: The text prompt for the image.

    Returns:
        The URL of the generated image asset.
    """
    if not API_KEY:
        print("Error: LIVEPEER_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    # Step 1: Initiate the generation job
    print(f"Requesting image generation for prompt: '{prompt}'")
    start_payload = {"prompt": prompt}
    try:
        start_response = requests.post(
            f"{GATEWAY_URL}/text-to-image",
            headers=headers,
            json=start_payload
        )
        start_response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Error starting job: {e}", file=sys.stderr)
        return

    job_id = start_response.json().get("id")
    print(f"Successfully started job with ID: {job_id}")

    # Step 2: Poll for the job status until it's completed or fails
    while True:
        print("Polling for job status...")
        time.sleep(5)  # Wait for 5 seconds before checking again

        try:
            status_response = requests.get(f"{STATUS_URL}/jobs/{job_id}", headers=headers)
            status_response.raise_for_status()
            result = status_response.json()

            status = result.get("status")
            print(f"Current job status: {status}")

            if status == "completed":
                asset_url = result.get("asset", {}).get("url")
                print(f"Job completed! Asset URL: {asset_url}")
                return asset_url
            elif status == "failed":
                error = result.get("error")
                print(f"Job failed: {error}", file=sys.stderr)
                return None

        except requests.exceptions.RequestException as e:
            print(f"Error polling for status: {e}", file=sys.stderr)
            # Decide if you want to break the loop or retry on polling errors
            break

if __name__ == "__main__":
    # Example usage when running the script directly
    example_prompt = "A photorealistic image of a cat wearing a tiny wizard hat"
    image_url = generate_image_from_text(example_prompt)

    if image_url:
        print("\n---")
        print("Final Image URL:")
        print(image_url)
        print("---")