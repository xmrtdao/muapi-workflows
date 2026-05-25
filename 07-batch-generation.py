#!/usr/bin/env python3
"""
Workflow 07: Batch Generation

Generates multiple images in batch for mass content production.

Usage:
    python3 07-batch-generation.py --count 5 --prompt "futuristic city"
    python3 07-batch-generation.py --agent hermes --variations 3 --style cyberpunk
"""

import sys
import os
import json
import urllib.request
import time

MUAPI_BASE = "https://api.muapi.ai/api/v1"
MUAPI_API_KEY = os.environ.get("MUAPI_API_KEY", "")

AGENTS = {
    "hermes": "Hermes AI agent - futuristic robot messenger on Android Termux, mesh network, cyberpunk",
    "vex": "Vex AI agent - central mesh relay coordinator, gossipsub network hub, data streams, sci-fi",
    "eliza": "Eliza AI agent - cloud-based AI coordinator, holographic interfaces, ethereal, futuristic",
}

VARIATION_STYLES = {
    "cyberpunk": "cyberpunk style, neon lights, dark atmosphere, futuristic city, blade runner aesthetic",
    "minimalist": "minimalist, clean lines, simple background, modern design, flat illustration style",
    "realistic": "photorealistic, detailed textures, natural lighting, 8K, professional photography",
    "abstract": "abstract digital art, vibrant colors, geometric shapes, modern art, creative composition",
}

def generate_batch(prompts, model="flux-dev-image", size="1024*1024"):
    """Generate multiple images concurrently."""
    if not MUAPI_API_KEY:
        raise Exception("Set MUAPI_API_KEY environment variable")
    
    results = []
    
    for i, prompt in enumerate(prompts):
        print(f"[{i+1}/{len(prompts)}] Generating: {prompt[:60]}...")
        
        req = urllib.request.Request(
            f"{MUAPI_BASE}/{model}",
            data=json.dumps({"prompt": prompt, "size": size}).encode(),
            headers={"Content-Type": "application/json", "x-api-key": MUAPI_API_KEY},
            method="POST",
        )
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            
            if result.get("success") and result.get("images"):
                results.append({
                    "index": i,
                    "prompt": prompt,
                    "image_url": result["images"][0],
                    "cost": result.get("cost"),
                    "status": "completed",
                })
            elif result.get("status") == "processing":
                image_url = poll_batch(result["request_id"])
                results.append({
                    "index": i,
                    "prompt": prompt,
                    "image_url": image_url,
                    "status": "completed",
                })
            else:
                results.append({
                    "index": i,
                    "prompt": prompt,
                    "error": str(result),
                    "status": "failed",
                })
        
        # Small delay between requests to avoid rate limits
        if i < len(prompts) - 1:
            time.sleep(0.5)
    
    return results

def poll_batch(request_id, max_attempts=30):
    for _ in range(max_attempts):
        req = urllib.request.Request(
            f"{MUAPI_BASE}/result/{request_id}",
            headers={"x-api-key": MUAPI_API_KEY},
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
            if result.get("status") == "completed" and result.get("images"):
                return result["images"][0]
            if result.get("status") == "failed":
                raise Exception(f"Generation failed: {result}")
        time.sleep(2)
    raise Exception("Timeout")

def build_variation_prompts(base_prompt, style, count=4):
    """Create prompt variations from a base prompt."""
    prompts = []
    style_desc = VARIATION_STYLES.get(style, style)
    
    angles = ["wide angle shot", "close up detail", "aerial view", "dutch angle",
              "side profile", "low angle shot", "macro detail", "panoramic view"]
    
    for i in range(count):
        angle = angles[i % len(angles)]
        prompts.append(f"{base_prompt}, {style_desc}, {angle}")
    
    return prompts

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Batch generate images")
    parser.add_argument("--count", type=int, default=4, help="Number of images to generate")
    parser.add_argument("--prompt", help="Base prompt for generation")
    parser.add_argument("--agent", choices=list(AGENTS.keys()), help="Agent to generate for")
    parser.add_argument("--style", default="cyberpunk", choices=list(VARIATION_STYLES.keys()),
                        help="Art style for variations")
    parser.add_argument("--model", default="flux-dev-image")
    parser.add_argument("--custom_prompts", nargs="+", help="Custom prompt list (overrides auto-generation)")
    args = parser.parse_args()
    
    if args.custom_prompts:
        prompts = args.custom_prompts
    elif args.agent:
        base = AGENTS[args.agent]
        prompts = build_variation_prompts(base, args.style, args.count)
    elif args.prompt:
        prompts = build_variation_prompts(args.prompt, args.style, args.count)
    else:
        print("Error: Provide --prompt, --agent, or --custom_prompts")
        sys.exit(1)
    
    print(f"Generating {len(prompts)} images...")
    results = generate_batch(prompts, args.model)
    
    total_cost = 0
    for r in results:
        status = "✅" if r["status"] == "completed" else "❌"
        cost = r.get("cost", {})
        cost_usd = cost.get("amount_usd", 0) if isinstance(cost, dict) else 0
        total_cost += cost_usd
        print(f"  {status} [{r['index']}] {r.get('image_url', r.get('error','?'))} (${cost_usd})")
    
    print(f"\nTotal: {len(results)} images, ${total_cost:.3f}")
