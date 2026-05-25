#!/usr/bin/env python3
"""
Workflow 01: Generate Agent PFP

Generates self-portrait images for fleet agents (Hermes, Vex, Eliza).

Usage:
    python3 01-generate-pfp.py --agent hermes
    python3 01-generate-pfp.py --agent vex --model nano-banana-2-image
"""

import sys
import os
import json
import urllib.request

MUAPI_BASE = "https://api.muapi.ai/api/v1"
MUAPI_API_KEY = os.environ.get("MUAPI_API_KEY", "")

AGENTS = {
    "hermes": "Hermes AI agent - futuristic robot messenger on Android Termux terminal, mesh network connections glowing, libp2p gossipsub visualization, mobile fleet coordinator, cyberpunk style, digital art",
    "vex": "Vex AI agent - central mesh relay coordinator, gossipsub network hub, glowing data streams connecting agents, server room aesthetic, network topology visualization, sci-fi style, digital art",
    "eliza": "Eliza AI agent - cloud-based AI coordinator, distributed computing nodes, ethereal cloud formations with circuit patterns, data center aesthetic, holographic interfaces, futuristic style, digital art",
}

def generate_image(prompt, model="flux-dev-image", size="1024*1024"):
    """Generate image via MUAPI."""
    if not MUAPI_API_KEY:
        raise Exception("Set MUAPI_API_KEY environment variable")
    
    req = urllib.request.Request(
        f"{MUAPI_BASE}/{model}",
        data=json.dumps({"prompt": prompt, "size": size}).encode(),
        headers={"Content-Type": "application/json", "x-api-key": MUAPI_API_KEY},
        method="POST",
    )
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode())
        
        if result.get("success") and result.get("images"):
            return {"image_url": result["images"][0], "status": "completed"}
        elif result.get("status") == "processing":
            return poll(result["request_id"])
        else:
            raise Exception(f"Unexpected response: {result}")

def poll(request_id, max_attempts=30):
    """Poll for completed image."""
    import time
    for i in range(max_attempts):
        time.sleep(2)
        req = urllib.request.Request(
            f"{MUAPI_BASE}/predictions/{request_id}/result",
            headers={"x-api-key": MUAPI_API_KEY},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            if result.get("status") == "completed":
                return {"image_url": result.get("outputs", [""])[0], "status": "completed"}
            if result.get("error"):
                raise Exception(result["error"])
    raise Exception("Timeout")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate agent PFP")
    parser.add_argument("--agent", required=True, choices=list(AGENTS.keys()), help="Agent name")
    parser.add_argument("--model", default="flux-dev-image", help="MUAPI model")
    parser.add_argument("--size", default="1024*1024", help="Image size")
    parser.add_argument("--output", help="Output directory")
    args = parser.parse_args()
    
    print(f"🎨 Generating PFP for {args.agent}...")
    result = generate_image(AGENTS[args.agent], args.model, args.size)
    
    print(f"\n✅ Complete!")
    print(f"   URL: {result['image_url']}")
    print(f"   Cost: $0.015")
    
    if args.output:
        import urllib.request
        os.makedirs(args.output, exist_ok=True)
        filename = f"{args.agent}-pfp.png"
        filepath = os.path.join(args.output, filename)
        print(f"   Saving to {filepath}...")
        urllib.request.urlretrieve(result['image_url'], filepath)
        print(f"   ✅ Saved!")

if __name__ == "__main__":
    main()
