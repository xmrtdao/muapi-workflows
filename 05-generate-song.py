#!/usr/bin/env python3
"""
Workflow 05: Generate Song

Creates full music tracks using Suno AI via MUAPI bridge.

Usage:
    python3 05-generate-song.py --style "cyberpunk synthwave" --theme "mesh network"
    python3 05-generate-song.py --style "orchestral" --theme "zero knowledge" --duration 30
"""

import sys
import os
import json
import urllib.request

MUAPI_BASE = "https://api.muapi.ai/api/v1"
MUAPI_API_KEY = os.environ.get("MUAPI_API_KEY", "")

GENRE_STYLES = {
    "synthwave": "synthwave, retrowave, electronic, 80s inspired, arpeggios, analog synths",
    "cyberpunk": "cyberpunk, dark electronic, industrial, glitch, dystopian, aggressive beats",
    "orchestral": "orchestral, cinematic, epic, strings, brass, full orchestra, dramatic",
    "ambient": "ambient, atmospheric, drone, spacey, meditative, evolving textures",
    "lo-fi": "lo-fi, chillhop, relaxed beats, vinyl crackle, jazzy chords, mellow",
    "hiphop": "hip hop, trap, 808s, heavy beats, modern production, urban",
}

THEMES = {
    "mesh": "mesh network, decentralized nodes, data flowing through dark space, digital connections",
    "dao": "decentralized autonomous organization, governance, voting, collective intelligence",
    "monero": "monero, private transactions, digital gold, cryptographic security, anonymity",
    "freedom": "digital freedom, open source, privacy, empowerment, breaking chains",
    "zeroknowledge": "zero knowledge proofs, cryptography, privacy technology, mathematical beauty",
}

def generate_song(style="synthwave", theme="mesh", duration=30, instrumental=False, model="suno-music"):
    if not MUAPI_API_KEY:
        raise Exception("Set MUAPI_API_KEY environment variable")
    
    style_desc = GENRE_STYLES.get(style, style)
    theme_desc = THEMES.get(theme, theme)
    
    prompt = f"A {style_desc} track about {theme_desc}"
    if instrumental:
        prompt += ", instrumental, no vocals"
    
    payload = {
        "prompt": prompt,
        "duration": duration,
        "model": "suno-v4",
    }
    
    req = urllib.request.Request(
        f"{MUAPI_BASE}/{model}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "x-api-key": MUAPI_API_KEY},
        method="POST",
    )
    
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode())
        
        if result.get("success") and result.get("audio_url"):
            return {"audio_url": result["audio_url"], "title": result.get("title", ""), "cost": result.get("cost"), "status": "completed"}
        elif result.get("status") == "processing":
            return poll_song(result["request_id"])
        else:
            raise Exception(f"Unexpected response: {result}")

def poll_song(request_id, max_attempts=60):
    import time
    for _ in range(max_attempts):
        req = urllib.request.Request(
            f"{MUAPI_BASE}/result/{request_id}",
            headers={"x-api-key": MUAPI_API_KEY},
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
            if result.get("status") == "completed" and result.get("audio_url"):
                return {"audio_url": result["audio_url"], "title": result.get("title", ""), "cost": result.get("cost"), "status": "completed"}
            if result.get("status") == "failed":
                raise Exception(f"Song generation failed: {result}")
        time.sleep(3)
    raise Exception("Timeout waiting for song generation")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate AI song")
    parser.add_argument("--style", default="synthwave", choices=list(GENRE_STYLES.keys()) + ["custom"],
                        help="Music genre/style")
    parser.add_argument("--theme", default="mesh", choices=list(THEMES.keys()) + ["custom"],
                        help="Song theme")
    parser.add_argument("--custom_style", help="Custom style description (if style=custom)")
    parser.add_argument("--custom_theme", help="Custom theme description (if theme=custom)")
    parser.add_argument("--duration", type=int, default=30, help="Song duration in seconds")
    parser.add_argument("--instrumental", action="store_true", help="Instrumental only, no vocals")
    parser.add_argument("--model", default="suno-music")
    args = parser.parse_args()
    
    style = args.custom_style if args.style == "custom" else args.style
    theme = args.custom_theme if args.theme == "custom" else args.theme
    
    result = generate_song(style, theme, args.duration, args.instrumental, args.model)
    print(json.dumps(result, indent=2))
    print(f"\nTitle: {result.get('title', 'N/A')}")
    print(f"Audio URL: {result.get('audio_url', 'N/A')}")
    cost = result.get('cost', {})
    if isinstance(cost, dict):
        print(f"Cost: ${cost.get('amount_usd', '?')}")
