#!/usr/bin/env python3
"""
Workflow 03: Image to Video

Animates still images into short video clips using MUAPI.

Usage:
    python3 03-image-to-video.py --image_url "https://..." --prompt "gentle motion"
    python3 03-image-to-video.py --agent hermes --motion cinematic
"""

import sys
import os
import json
import urllib.request

MUAPI_BASE = "https://api.muapi.ai/api/v1"
MUAPI_API_KEY = os.environ.get("MUAPI_API_KEY", "")

MOTION_STYLES = {
    "cinematic": "cinematic camera movement, slow pan, dramatic, film-like quality",
    "gentle": "gentle motion, subtle animation, soft movement, ambient",
    "energetic": "dynamic movement, fast cuts, energetic transitions, action-packed",
    "zoom": "slow zoom in, dramatic reveal, focus pull, depth",
}

def image_to_video(image_url, prompt="animate this image", model="kling-video"):
    if not MUAPI_API_KEY:
        raise Exception("Set MUAPI_API_KEY environment variable")
    
    req = urllib.request.Request(
        f"{MUAPI_BASE}/{model}",
        data=json.dumps({
            "image_url": image_url,
            "prompt": prompt,
            "size": "1024*576",
        }).encode(),
        headers={"Content-Type": "application/json", "x-api-key": MUAPI_API_KEY},
        method="POST",
    )
    
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode())
        
        if result.get("success") and result.get("video_url"):
            return {"video_url": result["video_url"], "cost": result.get("cost"), "status": "completed"}
        elif result.get("status") == "processing":
            return poll_video(result["request_id"])
        else:
            raise Exception(f"Unexpected response: {result}")

def poll_video(request_id, max_attempts=60):
    import time
    for _ in range(max_attempts):
        req = urllib.request.Request(
            f"{MUAPI_BASE}/result/{request_id}",
            headers={"x-api-key": MUAPI_API_KEY},
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
            if result.get("status") == "completed" and result.get("video_url"):
                return {"video_url": result["video_url"], "cost": result.get("cost"), "status": "completed"}
            if result.get("status") == "failed":
                raise Exception(f"Generation failed: {result}")
        time.sleep(3)
    raise Exception("Timeout waiting for video generation")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Animate image to video")
    parser.add_argument("--image_url", help="URL of source image")
    parser.add_argument("--prompt", default="cinematic motion, smooth animation")
    parser.add_argument("--motion", choices=list(MOTION_STYLES.keys()), help="Motion style preset")
    parser.add_argument("--model", default="kling-video")
    args = parser.parse_args()
    
    prompt = args.prompt
    if args.motion:
        prompt = f"{MOTION_STYLES[args.motion]}. {prompt}"
    
    result = image_to_video(args.image_url, prompt, args.model)
    print(json.dumps(result, indent=2))
    print(f"\nVideo URL: {result.get('video_url', 'N/A')}")
    cost = result.get('cost', {})
    if isinstance(cost, dict):
        print(f"Cost: ${cost.get('amount_usd', '?')}")
