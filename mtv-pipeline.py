#!/usr/bin/env python3
"""
MTV Pipeline — XMRT DAO Media Generation Workflow

Integrates MUAPI AI image generation into a reusable pipeline for:
- Agent self-portraits (PFPs)
- Marketing/brand assets
- Fleet media content
- Social media graphics

Usage:
  python3 mtv-pipeline.py --action generate --prompt "Your prompt"
  python3 mtv-pipeline.py --action pfp --agent hermes
  python3 mtv-pipeline.py --action batch --template elegant --subject "software engineer"
"""

import sys
import json
import urllib.request
import time
import argparse
from datetime import datetime
from typing import Optional, List

# ── Configuration ──────────────────────────────────────────
MUAPI_BASE = "https://api.muapi.ai/api/v1"
MUAPI_API_KEY = "060188b635eecb7ba11b3b634d3f373463c458cfb9cd0624cdab69a197e5b119"

# Image generation costs
IMAGE_COSTS = {
    "flux-dev-image": 0.015,
    "flux-pro-image": 0.03,
    "nano-banana-2-image": 0.06,
}

# Video generation costs
VIDEO_COSTS = {
    "wan2.2-image-to-video": 0.12,
    "kling-v2.5-image-to-video": 0.49,
    "ltx-video": 0.25,
    "creatify-lipsync": 0.04,
    "wan2.2-speech-to-video": 0.20,
    "kling-v2-avatar-pro": 0.75,
}

# Agent self-portrait prompts
AGENT_PROMPTS = {
    "hermes": "Hermes AI agent - futuristic robot messenger on Android Termux terminal, mesh network connections glowing, libp2p gossipsub visualization, mobile fleet coordinator, cyberpunk style, digital art",
    "vex": "Vex AI agent - central mesh relay coordinator, gossipsub network hub, glowing data streams connecting agents, server room aesthetic, network topology visualization, sci-fi style, digital art",
    "eliza": "Eliza AI agent - cloud-based AI coordinator, distributed computing nodes, ethereal cloud formations with circuit patterns, data center aesthetic, holographic interfaces, futuristic style, digital art",
}

# Professional PFP templates
PFP_TEMPLATES = {
    "elegant": "Professional headshot of {subject}, elegant gold on black color scheme, luxury aesthetic, sophisticated lighting, high quality, studio portrait, 300 DPI",
    "modern": "Professional headshot of {subject}, modern gray on white color scheme, minimalist aesthetic, clean contemporary lighting, high quality, studio portrait, 300 DPI",
    "classic": "Professional headshot of {subject}, classic navy on light gray color scheme, traditional professional aesthetic, timeless lighting, high quality, studio portrait, 300 DPI",
    "cyberpunk": "Professional headshot of {subject}, neon accents, glowing elements, holographic overlays, dark background with bright highlights, futuristic cityscape, cyberpunk style, 300 DPI",
}

SUBJECTS = {
    "engineer": "a software engineer",
    "blockchain": "a blockchain developer",
    "privacy": "a privacy advocate",
    "miner": "a cryptocurrency miner",
    "mesh": "a mesh network operator",
    "ai": "an AI agent operator",
    "web3": "a Web3 developer",
    "defi": "a DeFi specialist",
}


# ── MUAPI Client ──────────────────────────────────────────
def generate_image(
    prompt: str,
    model: str = "flux-dev-image",
    size: str = "1024*1024",
    num_images: int = 1,
    sync: bool = False,
    verbose: bool = True,
) -> dict:
    """Generate image via MUAPI and return result when complete."""

    if verbose:
        print(f"🎨 Generating with {model}...")
        print(f"   Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        print(f"   Size: {size}, Count: {num_images}")

    req = urllib.request.Request(
        f"{MUAPI_BASE}/{model}",
        data=json.dumps(
            {"prompt": prompt, "size": size, "num_images": num_images, "sync": sync}
        ).encode(),
        headers={"Content-Type": "application/json", "x-api-key": MUAPI_API_KEY},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            if verbose:
                print(f"   API Response: {json.dumps(result, indent=2)[:300]}...")
            
            # Handle different response formats
            # Format 1: Direct image URL (sync mode)
            if result.get("success") and result.get("images"):
                return {
                    "image_url": result["images"][0],
                    "request_id": None,
                    "cost_usd": COSTS.get(model, 0.015),
                    "status": "completed",
                    "execution_time": 0,
                }
            # Format 2: Async processing
            elif result.get("status") == "processing":
                if verbose:
                    print(f"   Processing... (request_id: {result.get('request_id')})")
                return poll_for_result(result["request_id"], max_attempts=30, verbose=verbose)
            # Format 3: Direct outputs array
            elif result.get("outputs"):
                return {
                    "image_url": result["outputs"][0],
                    "request_id": result.get("request_id"),
                    "cost_usd": result.get("cost", {}).get("amount_usd", COSTS.get(model, 0.015)),
                    "status": result.get("status", "completed"),
                }
            else:
                raise Exception(f"Unexpected API response format: {json.dumps(result)[:200]}")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        raise Exception(f"MUAPI API error {e.code}: {error_body}")

    if result.get("status") == "processing":
        if verbose:
            print(f"   Processing... (request_id: {result.get('request_id')})")
        return poll_for_result(result["request_id"], verbose)

    return {
        "image_url": result.get("outputs", [""])[0],
        "request_id": result.get("request_id"),
        "cost_usd": result.get("cost", {}).get("amount_usd", 0),
        "status": result.get("status"),
    }


def poll_for_result(
    request_id: str, max_attempts: int = 30, verbose: bool = True
) -> dict:
    """Poll MUAPI for completed image."""

    for i in range(max_attempts):
        time.sleep(2)

        req = urllib.request.Request(
            f"{MUAPI_BASE}/predictions/{request_id}/result",
            headers={"x-api-key": MUAPI_API_KEY},
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode())
        except Exception as e:
            if verbose:
                print(f"   Poll attempt {i+1}/{max_attempts} failed: {e}")
            continue

        status = result.get("status")

        if status == "completed":
            image_url = result.get("outputs", [""])[0]
            cost = result.get("cost", {}).get("amount_usd", 0)
            exec_time = result.get("executionTime", 0) / 1000

            if verbose:
                print(f"   ✅ Complete! ({exec_time:.2f}s)")
                print(f"   URL: {image_url}")
                print(f"   Cost: ${cost:.3f}")

            return {
                "image_url": image_url,
                "request_id": result["id"],
                "cost_usd": cost,
                "status": "completed",
                "execution_time": exec_time,
                "generated_at": datetime.utcnow().isoformat(),
            }

        if result.get("error"):
            raise Exception(f"Generation failed: {result['error']}")

        if verbose and i % 5 == 0:
            print(f"   Still processing... ({i+1}/{max_attempts})")

    raise Exception(f"Timeout after {max_attempts} attempts (~{max_attempts*2}s)")


# ── MTV Pipeline Actions ──────────────────────────────────
def generate_video_from_image(
    image_url: str,
    prompt: str = None,
    model: str = "wan2.2-image-to-video",
    duration: int = 5,
    verbose: bool = True,
) -> dict:
    """Generate video from image using MUAPI."""
    
    if verbose:
        print(f"\n🎬 Generating video with {model}...")
        print(f"   Source: {image_url[:60]}...")
        if prompt:
            print(f"   Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        print(f"   Duration: {duration}s")
    
    payload = {
        "image": image_url,
        "duration": duration,
    }
    if prompt:
        payload["prompt"] = prompt
    
    req = urllib.request.Request(
        f"{MUAPI_BASE}/{model}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "x-api-key": MUAPI_API_KEY},
        method="POST",
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            if verbose:
                print(f"   API Response: {json.dumps(result, indent=2)[:300]}...")
            
            if result.get("status") == "processing":
                if verbose:
                    print(f"   Processing... (request_id: {result.get('request_id')})")
                return poll_for_video_result(result["request_id"], verbose)
            elif result.get("video_url") or result.get("outputs"):
                return {
                    "video_url": result.get("video_url") or result["outputs"][0],
                    "request_id": result.get("request_id"),
                    "cost_usd": VIDEO_COSTS.get(model, 0.12),
                    "status": "completed",
                }
            else:
                raise Exception(f"Unexpected response: {json.dumps(result)[:200]}")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        raise Exception(f"MUAPI API error {e.code}: {error_body}")


def poll_for_video_result(
    request_id: str, max_attempts: int = 60, verbose: bool = True
) -> dict:
    """Poll MUAPI for completed video."""
    
    for i in range(max_attempts):
        time.sleep(3)  # Videos take longer
        
        req = urllib.request.Request(
            f"{MUAPI_BASE}/predictions/{request_id}/result",
            headers={"x-api-key": MUAPI_API_KEY},
        )
        
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode())
        except Exception as e:
            if verbose and i % 10 == 0:
                print(f"   Poll attempt {i+1}/{max_attempts} failed: {e}")
            continue
        
        status = result.get("status")
        
        if status == "completed":
            video_url = result.get("video_url") or result.get("outputs", [""])[0]
            cost = result.get("cost", {}).get("amount_usd", 0)
            exec_time = result.get("executionTime", 0) / 1000
            
            if verbose:
                print(f"   ✅ Complete! ({exec_time:.2f}s)")
                print(f"   URL: {video_url}")
                print(f"   Cost: ${cost:.3f}")
            
            return {
                "video_url": video_url,
                "request_id": result["id"],
                "cost_usd": cost,
                "status": "completed",
                "execution_time": exec_time,
                "generated_at": datetime.utcnow().isoformat(),
            }
        
        if result.get("error"):
            raise Exception(f"Generation failed: {result['error']}")
        
        if verbose and i % 10 == 0:
            print(f"   Still processing... ({i+1}/{max_attempts})")
    
    raise Exception(f"Timeout after {max_attempts} attempts (~{max_attempts*3}s)")


def generate_talking_avatar(
    image_url: str,
    audio_url: str = None,
    script: str = None,
    model: str = "wan2.2-speech-to-video",
    verbose: bool = True,
) -> dict:
    """Generate talking avatar from image + audio/script."""
    
    if not audio_url and not script:
        raise Exception("Provide either audio_url or script")
    
    if verbose:
        print(f"\n🎭 Generating talking avatar with {model}...")
        print(f"   Source: {image_url[:60]}...")
        if script:
            print(f"   Script: {script[:80]}{'...' if len(script) > 80 else ''}")
        if audio_url:
            print(f"   Audio: {audio_url}")
    
    payload = {"image": image_url}
    if audio_url:
        payload["audio"] = audio_url
    if script:
        payload["script"] = script
    
    req = urllib.request.Request(
        f"{MUAPI_BASE}/{model}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "x-api-key": MUAPI_API_KEY},
        method="POST",
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            if verbose:
                print(f"   API Response: {json.dumps(result, indent=2)[:300]}...")
            
            if result.get("status") == "processing":
                if verbose:
                    print(f"   Processing... (request_id: {result.get('request_id')})")
                return poll_for_video_result(result["request_id"], verbose)
            elif result.get("video_url"):
                return {
                    "video_url": result["video_url"],
                    "request_id": result.get("request_id"),
                    "cost_usd": VIDEO_COSTS.get(model, 0.20),
                    "status": "completed",
                }
            else:
                raise Exception(f"Unexpected response: {json.dumps(result)[:200]}")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        raise Exception(f"MUAPI API error {e.code}: {error_body}")


def generate_agent_pfp(agent: str, model: str = "flux-dev-image", size: str = "1024*1024") -> dict:
    """Generate self-portrait for a fleet agent."""
    print(f"\n🔸 MTV PIPELINE — Agent PFP: {agent}\n")
    
    if agent.lower() not in AGENT_PROMPTS:
        raise Exception(f"Unknown agent: {agent}. Available: {list(AGENT_PROMPTS.keys())}")
    
    prompt = AGENT_PROMPTS[agent.lower()]
    result = generate_image(prompt, model, size, verbose=True)
    result["agent"] = agent
    return result


def generate_professional_pfp(template: str, subject: str, model: str = "flux-dev-image") -> dict:
    """Generate professional PFP using template."""
    print(f"\n🔸 MTV PIPELINE — Professional PFP\n")
    
    if template.lower() not in PFP_TEMPLATES:
        raise Exception(f"Unknown template: {template}. Available: {list(PFP_TEMPLATES.keys())}")
    
    subject_text = SUBJECTS.get(subject.lower(), subject)
    prompt = PFP_TEMPLATES[template.lower()].format(subject=subject_text)
    
    result = generate_image(prompt, model, "1200*1800", verbose=True)
    result["template"] = template
    result["subject"] = subject
    return result


def batch_generate(templates: List[str], subjects: List[str], model: str = "flux-dev-image") -> List[dict]:
    """Generate multiple images in batch."""
    print(f"\n🔸 MTV PIPELINE — Batch Generation\n")
    print(f"   Templates: {templates}")
    print(f"   Subjects: {subjects}")
    print(f"   Model: {model}\n")
    
    results = []
    for template in templates:
        for subject in subjects:
            try:
                result = generate_professional_pfp(template, subject, model)
                results.append(result)
                print(f"   ✅ {template} + {subject}: ${result['cost_usd']:.3f}")
            except Exception as e:
                print(f"   ❌ {template} + {subject}: {e}")
                results.append({"error": str(e), "template": template, "subject": subject})
    
    total_cost = sum(r.get("cost_usd", 0) for r in results if "error" not in r)
    print(f"\n   Total: {len(results)} images, ${total_cost:.3f}")
    
    return results


# ── CLI ──────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="MTV Pipeline — XMRT DAO Media Generation")
    parser.add_argument("--action", required=True, 
                        choices=["generate", "pfp", "professional", "batch", "video", "avatar"],
                        help="Action to perform")
    parser.add_argument("--prompt", help="Custom prompt (for 'generate' action)")
    parser.add_argument("--agent", help="Agent name (for 'pfp' action: hermes, vex, eliza)")
    parser.add_argument("--template", help="PFP template (elegant, modern, classic, cyberpunk)")
    parser.add_argument("--subject", help="Subject type (engineer, blockchain, privacy, miner, mesh, ai, web3, defi)")
    parser.add_argument("--model", default="flux-dev-image", 
                        help="MUAPI model")
    parser.add_argument("--size", default="1024*1024", help="Image size (W*H)")
    parser.add_argument("--sync", action="store_true", help="Use synchronous mode")
    parser.add_argument("--image", help="Source image URL (for 'video' action)")
    parser.add_argument("--audio", help="Audio URL (for 'avatar' action)")
    parser.add_argument("--script", help="Text script for talking avatar (for 'avatar' action)")
    parser.add_argument("--duration", type=int, default=5, help="Video duration in seconds")
    parser.add_argument("--templates", nargs="+", help="Multiple templates for batch")
    parser.add_argument("--subjects", nargs="+", help="Multiple subjects for batch")
    parser.add_argument("-q", "--quiet", action="store_true", help="JSON output only")

    args = parser.parse_args()

    try:
        if args.action == "generate":
            if not args.prompt:
                raise Exception("--prompt required for 'generate' action")
            result = generate_image(args.prompt, args.model, args.size, sync=args.sync, verbose=not args.quiet)
        
        elif args.action == "pfp":
            if not args.agent:
                raise Exception("--agent required for 'pfp' action")
            result = generate_agent_pfp(args.agent, args.model, args.size)
        
        elif args.action == "professional":
            if not args.template or not args.subject:
                raise Exception("--template and --subject required for 'professional' action")
            result = generate_professional_pfp(args.template, args.subject, args.model)
        
        elif args.action == "batch":
            templates = args.templates or ["elegant", "modern"]
            subjects = args.subjects or ["engineer", "blockchain"]
            results = batch_generate(templates, subjects, args.model)
            print(f"\n{json.dumps(results, indent=2)}")
            return
        
        elif args.action == "video":
            if not args.image:
                raise Exception("--image required for 'video' action")
            result = generate_video_from_image(args.image, args.prompt, args.model, args.duration, verbose=not args.quiet)
        
        elif args.action == "avatar":
            if not args.image:
                raise Exception("--image required for 'avatar' action")
            if not args.audio and not args.script:
                raise Exception("--audio or --script required for 'avatar' action")
            result = generate_talking_avatar(args.image, args.audio, args.script, args.model, verbose=not args.quiet)
        
        if not args.quiet:
            key = "video_url" if "video_url" in result else "image_url"
            print(f"\n📸 Result:")
            print(f"   URL: {result.get(key, 'N/A')}")
            print(f"   Cost: ${result.get('cost_usd', 0):.3f}")
            if result.get('execution_time'):
                print(f"   Time: {result['execution_time']:.2f}s")
        
        print(f"\n{json.dumps(result, indent=2)}")

    except Exception as e:
        if not args.quiet:
            print(f"❌ Error: {e}", file=sys.stderr)
        else:
            print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
