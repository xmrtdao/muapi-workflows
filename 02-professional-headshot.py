#!/usr/bin/env python3
"""
Workflow 02: Professional Headshot

Generates template-based professional headshots for fleet agents.

Usage:
    python3 02-professional-headshot.py --agent hermes
    python3 02-professional-headshot.py --agent vex --style corporate
"""

import sys
import os
import json
import urllib.request

MUAPI_BASE = "https://api.muapi.ai/api/v1"
MUAPI_API_KEY = os.environ.get("MUAPI_API_KEY", "")

STYLES = {
    "corporate": "professional corporate headshot, business suit, clean background, studio lighting, high quality, 8K, professional photography",
    "cyberpunk": "cyberpunk style headshot, neon lights, futuristic, digital art, sci-fi character portrait, blade runner aesthetic",
    "minimalist": "minimalist portrait, simple background, clean lines, modern, editorial photography style, soft lighting",
    "vintage": "vintage style portrait, film grain, warm tones, classic photography, timeless aesthetic, analog feel",
}

AGENTS = {
    "hermes": "Hermes AI agent",
    "vex": "Vex AI agent",
    "eliza": "Eliza AI agent",
    "generic": "a person",
}

def generate_headshot(agent, style="corporate", model="flux-dev-image"):
    if not MUAPI_API_KEY:
        raise Exception("Set MUAPI_API_KEY environment variable")
    
    agent_desc = AGENTS.get(agent, AGENTS["generic"])
    style_desc = STYLES.get(style, STYLES["corporate"])
    prompt = f"{agent_desc}, {style_desc}"
    
    req = urllib.request.Request(
        f"{MUAPI_BASE}/{model}",
        data=json.dumps({"prompt": prompt, "size": "1024*1024"}).encode(),
        headers={"Content-Type": "application/json", "x-api-key": MUAPI_API_KEY},
        method="POST",
    )
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode())
        
        if result.get("success") and result.get("images"):
            return {"image_url": result["images"][0], "cost": result.get("cost"), "status": "completed"}
        elif result.get("status") == "processing":
            request_id = result.get("request_id")
            return poll_headshot(request_id)
        else:
            raise Exception(f"Unexpected response: {result}")

def poll_headshot(request_id, max_attempts=30):
    import time
    for _ in range(max_attempts):
        req = urllib.request.Request(
            f"{MUAPI_BASE}/result/{request_id}",
            headers={"x-api-key": MUAPI_API_KEY},
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
            if result.get("status") == "completed" and result.get("images"):
                return {"image_url": result["images"][0], "cost": result.get("cost"), "status": "completed"}
            if result.get("status") == "failed":
                raise Exception(f"Generation failed: {result}")
        time.sleep(2)
    raise Exception("Timeout waiting for generation")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate professional headshot")
    parser.add_argument("--agent", default="generic", choices=list(AGENTS.keys()))
    parser.add_argument("--style", default="corporate", choices=list(STYLES.keys()))
    parser.add_argument("--model", default="flux-dev-image")
    args = parser.parse_args()
    
    result = generate_headshot(args.agent, args.style, args.model)
    print(json.dumps(result, indent=2))
    print(f"\nCost: ${result.get('cost', {}).get('amount_usd', '?')}")
