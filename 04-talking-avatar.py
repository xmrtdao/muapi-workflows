#!/usr/bin/env python3
"""
Workflow 04: Talking Avatar

Creates a talking avatar video with lipsync from audio or script text.

Usage:
    python3 04-talking-avatar.py --text "Hello, I am an AI agent" --agent hermes
    python3 04-talking-avatar.py --audio_url "https://..." --avatar_style realistic
"""

import sys
import os
import json
import urllib.request

MUAPI_BASE = "https://api.muapi.ai/api/v1"
MUAPI_API_KEY = os.environ.get("MUAPI_API_KEY", "")

AVATAR_STYLES = {
    "realistic": "photorealistic human avatar, detailed face, natural expressions",
    "animated": "cartoon/anime style avatar, expressive, stylized",
    "cyberpunk": "cyberpunk AI avatar, neon accents, futuristic, digital",
    "minimalist": "simple clean avatar, minimalist design, modern",
}

AGENT_VOICES = {
    "hermes": "A confident, tech-savvy male voice, clear and articulate, mid-range tone",
    "vex": "A sharp, direct female voice, authoritative, efficient, slightly dry humor",
    "eliza": "A warm, professional female voice, executive tone, measured and thoughtful",
}

def create_talking_avatar(text="", audio_url="", avatar_style="realistic", agent="generic", model="talking-avatar"):
    if not MUAPI_API_KEY:
        raise Exception("Set MUAPI_API_KEY environment variable")
    
    payload = {
        "avatar_style": avatar_style,
        "size": "1024*576",
    }
    
    if audio_url:
        payload["audio_url"] = audio_url
    else:
        voice_desc = AGENT_VOICES.get(agent, "A neutral, professional voice")
        payload["text"] = text
        payload["voice_description"] = voice_desc
    
    req = urllib.request.Request(
        f"{MUAPI_BASE}/{model}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "x-api-key": MUAPI_API_KEY},
        method="POST",
    )
    
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode())
        
        if result.get("success") and result.get("video_url"):
            return {"video_url": result["video_url"], "cost": result.get("cost"), "status": "completed"}
        elif result.get("status") == "processing":
            return poll_avatar(result["request_id"])
        else:
            raise Exception(f"Unexpected response: {result}")

def poll_avatar(request_id, max_attempts=60):
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
                raise Exception(f"Avatar generation failed: {result}")
        time.sleep(3)
    raise Exception("Timeout waiting for avatar generation")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create talking avatar video")
    parser.add_argument("--text", help="Text for the avatar to speak")
    parser.add_argument("--audio_url", help="URL of audio file for lipsync")
    parser.add_argument("--agent", default="generic", choices=list(AGENT_VOICES.keys()) + ["generic"])
    parser.add_argument("--avatar_style", default="realistic", choices=list(AVATAR_STYLES.keys()))
    parser.add_argument("--model", default="talking-avatar")
    args = parser.parse_args()
    
    if not args.text and not args.audio_url:
        print("Error: Provide --text or --audio_url")
        sys.exit(1)
    
    result = create_talking_avatar(args.text, args.audio_url, args.avatar_style, args.agent, args.model)
    print(json.dumps(result, indent=2))
    print(f"\nVideo URL: {result.get('video_url', 'N/A')}")
    cost = result.get('cost', {})
    if isinstance(cost, dict):
        print(f"Cost: ${cost.get('amount_usd', '?')}")
