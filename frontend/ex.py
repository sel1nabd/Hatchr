from livepeer_ai import Livepeer

with Livepeer(
    http_bearer="d0fdd794-e957-4c79-9a66-38f90a8a03ac",
) as livepeer:

    res = livepeer.generate.text_to_image(request={
        "model_id": "",
        "loras": "",
        "prompt": "cat",
        "height": 576,
        "width": 1024,
        "guidance_scale": 7.5,
        "negative_prompt": "",
        "safety_check": True,
        "num_inference_steps": 50,
        "num_images_per_prompt": 1,
    })

    assert res.image_response is not None

    # Handle response
    print(res.image_response)