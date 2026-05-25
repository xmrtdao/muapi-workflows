#!/usr/bin/env python3
"""
MTV Pipeline v3.0 — XMRT DAO Music Video Production

Full music video pipeline:
1. Generate lyrics from concept
2. Create full song (vocals + instruments)
3. Generate visual scenes
4. Animate scenes to video
5. Lipsync to audio

Usage:
  python3 mtv-music-video.py --concept "cyberpunk anthem about mesh networks"
  python3 mtv-music-video.py --lyrics-file lyrics.txt --style "electronic, synthwave"
  python3 mtv-music-video.py --action lyrics --concept "AI taking over the world"
  python3 mtv-music-video.py --action song --lyrics "Verse 1..." --style "rock"
"""

import sys
import json
import urllib.request
import time
import argparse
import os
from datetime import datetime
from typing import Optional, List, Dict

# ── Configuration ──────────────────────────────────────────
MUAPI_BASE = "https://api.muapi.ai/api/v1"
MUAPI_API_KEY = "060188b635eecb7ba11b3b634d3f373463c458cfb9cd0624cdab69a197e5b119"

# Costs
COSTS = {
    "lyrics": 0.003,
    "song": 0.09,
    "image": 0.015,
    "video": 0.12,
    "lipsync": 0.04,
    "extend": 0.09,
    "remix": 0.09,
}

# Music genre/style presets
MUSIC_STYLES = {
    "cyberpunk": "synthwave, electronic, cyberpunk, dark electronic, industrial, futuristic, neon, dystopian",
    "pop": "pop, catchy, upbeat, radio hit, mainstream, polished production",
    "rock": "rock, electric guitar, drums, energetic, powerful, arena rock",
    "hiphop": "hip hop, rap, trap beats, urban, rhythmic, bass heavy",
    "electronic": "EDM, electronic dance, house, techno, beats, club",
    "ambient": "ambient, atmospheric, chill, meditative, soundscape, ethereal",
    "jazz": "jazz, smooth, saxophone, piano, swing, sophisticated",
    "classical": "classical, orchestral, symphony, strings, cinematic, epic",
    "country": "country, acoustic guitar, folk, storytelling, americana",
    "rnb": "R&B, soul, smooth vocals, groove, contemporary",
    "metal": "metal, heavy guitar, aggressive, powerful, hard rock",
    "reggae": "reggae, ska, island vibes, laid back, offbeat",
    "xmrt-dao": "electronic, crypto, blockchain, futuristic, tech house, digital currency, mesh network, decentralized",
}

# Visual scene templates for music videos
VISUAL_THEMES = {
    "cyberpunk": "neon cityscape, futuristic buildings, holographic advertisements, rain-slicked streets, flying vehicles, cybernetic enhancements, dark atmosphere with bright neon accents",
    "abstract": "geometric shapes, flowing colors, particle effects, fractals, kaleidoscope patterns, surreal landscapes, dreamlike visuals",
    "performance": "musician on stage, concert lighting, crowd silhouettes, spotlights, dramatic shadows, live performance energy",
    "narrative": "storytelling scenes, character journey, emotional moments, cinematic framing, dramatic lighting, film noir aesthetic",
    "nature": "natural landscapes, mountains, oceans, forests, sunsets, wildlife, environmental beauty, epic vistas",
    "urban": "city streets, graffiti, street culture, urban decay, metropolitan life, concrete jungle, street lights",
    "space": "cosmic scenes, stars, galaxies, nebulae, astronauts, spacecraft, zero gravity, celestial bodies",
    "xmrt-dao": "mesh network visualization, glowing data streams, blockchain nodes, cryptocurrency symbols, digital currency flow, decentralized network, libp2p gossipsub, agent coordination, Termux terminal aesthetic",
}


# ── Suno Music Functions ──────────────────────────────────
def generate_lyrics(
    concept: str,
    style: str = None,
    structure: str = "verse-chorus-verse-chorus-bridge-chorus",
    verbose: bool = True,
) -> dict:
    """Generate song lyrics from concept."""
    
    if verbose:
        print(f"\n📝 Generating lyrics...")
        print(f"   Concept: {concept[:80]}{'...' if len(concept) > 80 else ''}")
        if style:
            print(f"   Style: {style}")
        print(f"   Structure: {structure}")
    
    prompt = f"Write song lyrics about: {concept}"
    if style:
        prompt += f". Music style: {style}"
    prompt += f". Song structure: {structure}"
    
    payload = {
        "prompt": prompt,
        "make_instrumental": False,
    }
    
    req = urllib.request.Request(
        f"{MUAPI_BASE}/suno-generate-lyrics",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "x-api-key": MUAPI_API_KEY},
        method="POST",
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            if verbose:
                print(f"   API Response: {json.dumps(result, indent=2)[:300]}...")
            
            # Poll if processing
            if result.get("status") == "processing":
                return poll_for_lyrics(result.get("request_id"), verbose=verbose)
            
            return {
                "lyrics": result.get("lyrics", ""),
                "title": result.get("title", "Untitled"),
                "style": style,
                "cost_usd": COSTS["lyrics"],
                "status": "completed",
            }
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        raise Exception(f"Suno API error {e.code}: {error_body}")


def poll_for_lyrics(request_id: str, max_attempts: int = 30, verbose: bool = True) -> dict:
    """Poll for completed lyrics."""
    
    for i in range(max_attempts):
        time.sleep(3)
        
        req = urllib.request.Request(
            f"{MUAPI_BASE}/predictions/{request_id}/result",
            headers={"x-api-key": MUAPI_API_KEY},
        )
        
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode())
                if verbose and i % 5 == 0:
                    print(f"   Status: {result.get('status', 'unknown')}")
        except Exception as e:
            if verbose and i % 10 == 0:
                print(f"   Poll {i+1}/{max_attempts}: {e}")
            continue
        
        if result.get("status") == "completed":
            lyrics = result.get("lyrics", "")
            if not lyrics and result.get("outputs"):
                lyrics = result["outputs"][0] if isinstance(result["outputs"], list) else result["outputs"]
            if verbose:
                print(f"   ✅ Lyrics generated! ({len(lyrics)} chars)")
            return {
                "lyrics": lyrics,
                "title": result.get("title", "Untitled"),
                "cost_usd": result.get("cost", {}).get("amount_usd", COSTS["lyrics"]),
                "status": "completed",
            }
        
        if result.get("error"):
            raise Exception(f"Lyrics generation failed: {result['error']}")
    
    raise Exception(f"Timeout after {max_attempts} attempts (~{max_attempts*3}s)")


def create_song(
    lyrics: str = None,
    prompt: str = None,
    style: str = None,
    make_instrumental: bool = False,
    title: str = None,
    verbose: bool = True,
) -> dict:
    """Create full song with Suno AI."""
    
    if not lyrics and not prompt:
        raise Exception("Provide either lyrics or prompt")
    
    if verbose:
        print(f"\n🎵 Creating song with Suno AI...")
        if title:
            print(f"   Title: {title}")
        print(f"   Style: {style}")
        print(f"   Instrumental: {make_instrumental}")
        if lyrics:
            print(f"   Lyrics: {lyrics[:60]}{'...' if len(lyrics) > 60 else ''}")
        if prompt:
            print(f"   Prompt: {prompt[:60]}{'...' if len(prompt) > 60 else ''}")
    
    payload = {
        "make_instrumental": make_instrumental,
    }
    
    if lyrics:
        payload["lyrics"] = lyrics
    if prompt:
        payload["prompt"] = prompt
    if style:
        payload["style"] = style
    if title:
        payload["title"] = title
    
    req = urllib.request.Request(
        f"{MUAPI_BASE}/suno-create-music",
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
                return poll_for_song(result["request_id"], verbose=verbose)
            elif result.get("audio_url"):
                return {
                    "audio_url": result["audio_url"],
                    "video_url": result.get("video_url"),  # Some models return lyric video
                    "title": result.get("title"),
                    "style": result.get("style"),
                    "duration": result.get("duration"),
                    "cost_usd": COSTS["song"],
                    "status": "completed",
                }
            else:
                raise Exception(f"Unexpected response: {json.dumps(result)[:200]}")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        raise Exception(f"Suno API error {e.code}: {error_body}")


def poll_for_song(request_id: str, max_attempts: int = 60, verbose: bool = True) -> dict:
    """Poll for completed song."""
    
    for i in range(max_attempts):
        time.sleep(3)  # Songs take longer
        
        req = urllib.request.Request(
            f"{MUAPI_BASE}/predictions/{request_id}/result",
            headers={"x-api-key": MUAPI_API_KEY},
        )
        
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode())
        except Exception as e:
            if verbose and i % 10 == 0:
                print(f"   Poll attempt {i+1}/{max_attempts}")
            continue
        
        status = result.get("status")
        
        if status == "completed":
            audio_url = result.get("audio_url")
            video_url = result.get("video_url")
            duration = result.get("duration", 0)
            cost = result.get("cost", {}).get("amount_usd", COSTS["song"])
            
            if verbose:
                print(f"   ✅ Song complete! ({duration}s)")
                print(f"   Audio: {audio_url}")
                if video_url:
                    print(f"   Video: {video_url}")
                print(f"   Cost: ${cost:.3f}")
            
            return {
                "audio_url": audio_url,
                "video_url": video_url,
                "title": result.get("title"),
                "style": result.get("style"),
                "duration": duration,
                "cost_usd": cost,
                "status": "completed",
                "generated_at": datetime.utcnow().isoformat(),
            }
        
        if result.get("error"):
            raise Exception(f"Song generation failed: {result['error']}")
        
        if verbose and i % 10 == 0:
            print(f"   Still processing... ({i+1}/{max_attempts})")
    
    raise Exception(f"Timeout after {max_attempts} attempts")


# ── Video Functions ──────────────────────────────────
def generate_scene(
    prompt: str,
    model: str = "flux-dev-image",
    size: str = "1024*1024",
    verbose: bool = True,
) -> dict:
    """Generate a visual scene for the music video."""
    
    if verbose:
        print(f"\n🎨 Generating scene...")
        print(f"   Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
    
    payload = {
        "prompt": prompt,
        "size": size,
    }
    
    req = urllib.request.Request(
        f"{MUAPI_BASE}/{model}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "x-api-key": MUAPI_API_KEY},
        method="POST",
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            
            if result.get("success") and result.get("images"):
                return {
                    "image_url": result["images"][0],
                    "cost_usd": COSTS["image"],
                    "status": "completed",
                }
            elif result.get("status") == "processing":
                return poll_for_image(result["request_id"], verbose)
            else:
                raise Exception(f"Unexpected response: {json.dumps(result)[:200]}")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        raise Exception(f"MUAPI API error {e.code}: {error_body}")


def poll_for_image(request_id: str, max_attempts: int = 30, verbose: bool = True) -> dict:
    """Poll for completed image."""
    
    for i in range(max_attempts):
        time.sleep(2)
        
        req = urllib.request.Request(
            f"{MUAPI_BASE}/predictions/{request_id}/result",
            headers={"x-api-key": MUAPI_API_KEY},
        )
        
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode())
        except:
            continue
        
        if result.get("status") == "completed":
            image_url = result.get("outputs", [""])[0]
            if verbose:
                print(f"   ✅ Scene ready: {image_url}")
            return {
                "image_url": image_url,
                "cost_usd": result.get("cost", {}).get("amount_usd", COSTS["image"]),
                "status": "completed",
            }
        
        if result.get("error"):
            raise Exception(f"Image generation failed: {result['error']}")
    
    raise Exception("Timeout waiting for image")


def animate_scene(
    image_url: str,
    audio_url: str = None,
    prompt: str = None,
    model: str = "wan2.2-image-to-video",
    duration: int = 5,
    verbose: bool = True,
) -> dict:
    """Animate scene into video, optionally lipsynced to audio."""
    
    if verbose:
        print(f"\n🎬 Animating scene...")
        print(f"   Source: {image_url[:60]}...")
        if audio_url:
            print(f"   Audio: {audio_url[:60]}...")
            print(f"   Model: lipsync")
        else:
            print(f"   Model: {model}")
            if prompt:
                print(f"   Motion: {prompt[:60]}...")
    
    # If audio provided, use lipsync model
    if audio_url:
        payload = {
            "image": image_url,
            "audio": audio_url,
        }
        model = "creatify-lipsync"
    else:
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
            
            if result.get("status") == "processing":
                return poll_for_video(result["request_id"], verbose)
            elif result.get("video_url"):
                return {
                    "video_url": result["video_url"],
                    "cost_usd": COSTS["video"] if not audio_url else COSTS["lipsync"],
                    "status": "completed",
                }
            else:
                raise Exception(f"Unexpected response: {json.dumps(result)[:200]}")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        raise Exception(f"MUAPI API error {e.code}: {error_body}")


def poll_for_video(request_id: str, max_attempts: int = 60, verbose: bool = True) -> dict:
    """Poll for completed video."""
    
    for i in range(max_attempts):
        time.sleep(3)
        
        req = urllib.request.Request(
            f"{MUAPI_BASE}/predictions/{request_id}/result",
            headers={"x-api-key": MUAPI_API_KEY},
        )
        
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode())
        except:
            continue
        
        if result.get("status") == "completed":
            video_url = result.get("video_url") or result.get("outputs", [""])[0]
            cost = result.get("cost", {}).get("amount_usd", 0)
            
            if verbose:
                print(f"   ✅ Video ready: {video_url}")
                print(f"   Cost: ${cost:.3f}")
            
            return {
                "video_url": video_url,
                "cost_usd": cost,
                "status": "completed",
            }
        
        if result.get("error"):
            raise Exception(f"Video generation failed: {result['error']}")
    
    raise Exception("Timeout waiting for video")


# ── Full Music Video Pipeline ──────────────────────────────────
def create_music_video(
    concept: str,
    style: str = "electronic",
    num_scenes: int = 3,
    verbose: bool = True,
) -> dict:
    """Create complete music video from concept."""
    
    if verbose:
        print("\n" + "="*60)
        print("🎵 MTV PIPELINE — MUSIC VIDEO PRODUCTION")
        print("="*60)
        print(f"Concept: {concept}")
        print(f"Style: {style}")
        print(f"Scenes: {num_scenes}")
    
    total_cost = 0
    results = {"concept": concept, "style": style, "scenes": []}
    
    # Step 1: Generate lyrics
    try:
        lyrics_result = generate_lyrics(concept, style, verbose=verbose)
        results["lyrics"] = lyrics_result
        results["title"] = lyrics_result.get("title", "Untitled")
        total_cost += lyrics_result["cost_usd"]
    except Exception as e:
        if verbose:
            print(f"   ⚠️ Lyrics generation skipped: {e}")
        results["lyrics"] = {"error": str(e)}
    
    # Step 2: Create song
    try:
        song_result = create_song(
            lyrics=results.get("lyrics", {}).get("lyrics"),
            style=MUSIC_STYLES.get(style, style),
            title=results.get("title"),
            verbose=verbose,
        )
        results["song"] = song_result
        total_cost += song_result["cost_usd"]
        audio_url = song_result.get("audio_url")
    except Exception as e:
        if verbose:
            print(f"   ⚠️ Song generation failed: {e}")
        results["song"] = {"error": str(e)}
        audio_url = None
    
    # Step 3: Generate and animate scenes
    visual_theme = VISUAL_THEMES.get(style, VISUAL_THEMES["abstract"])
    
    for i in range(num_scenes):
        if verbose:
            print(f"\n🎬 Scene {i+1}/{num_scenes}")
        
        try:
            # Generate scene image
            scene_prompt = f"{visual_theme}, music video scene {i+1}, cinematic lighting, high quality"
            image_result = generate_scene(scene_prompt, verbose=verbose)
            total_cost += image_result["cost_usd"]
            
            # Animate scene
            if audio_url:
                # Lipsync to song
                video_result = animate_scene(
                    image_result["image_url"],
                    audio_url=audio_url,
                    verbose=verbose,
                )
            else:
                # Just animate
                video_result = animate_scene(
                    image_result["image_url"],
                    prompt="smooth motion, cinematic",
                    verbose=verbose,
                )
            total_cost += video_result["cost_usd"]
            
            results["scenes"].append({
                "scene_number": i+1,
                "image": image_result,
                "video": video_result,
            })
            
        except Exception as e:
            if verbose:
                print(f"   ⚠️ Scene {i+1} failed: {e}")
            results["scenes"].append({"scene_number": i+1, "error": str(e)})
    
    results["total_cost_usd"] = total_cost
    results["status"] = "completed"
    
    if verbose:
        print("\n" + "="*60)
        print(f"✅ MUSIC VIDEO COMPLETE")
        print(f"   Title: {results.get('title', 'Untitled')}")
        print(f"   Scenes: {len(results['scenes'])}")
        print(f"   Total Cost: ${total_cost:.3f}")
        print("="*60)
    
    return results


# ── CLI ──────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="MTV Pipeline — Music Video Production")
    parser.add_argument("--concept", help="Song concept/theme")
    parser.add_argument("--lyrics", help="Pre-written lyrics")
    parser.add_argument("--style", default="electronic", help=f"Music style: {list(MUSIC_STYLES.keys())}")
    parser.add_argument("--scenes", type=int, default=3, help="Number of video scenes")
    parser.add_argument("--action", choices=["lyrics", "song", "video", "full"], default="full",
                        help="Action: lyrics only, song only, video from audio, or full pipeline")
    parser.add_argument("--audio", help="Audio URL (for video action)")
    parser.add_argument("--output", help="Output directory for results")
    parser.add_argument("-q", "--quiet", action="store_true", help="JSON output only")
    
    args = parser.parse_args()
    
    verbose = not args.quiet
    
    try:
        if args.action == "lyrics":
            if not args.concept:
                raise Exception("--concept required for lyrics action")
            result = generate_lyrics(args.concept, args.style, verbose=verbose)
        
        elif args.action == "song":
            if not args.lyrics and not args.concept:
                raise Exception("--lyrics or --concept required for song action")
            result = create_song(
                lyrics=args.lyrics,
                prompt=args.concept,
                style=MUSIC_STYLES.get(args.style, args.style),
                verbose=verbose,
            )
        
        elif args.action == "video":
            if not args.audio:
                raise Exception("--audio required for video action")
            # Generate scenes and lipsync to provided audio
            result = create_music_video(
                concept=args.concept or "Abstract music video",
                style=args.style,
                num_scenes=args.scenes,
                verbose=verbose,
            )
        
        elif args.action == "full":
            if not args.concept:
                raise Exception("--concept required for full pipeline")
            result = create_music_video(
                concept=args.concept,
                style=args.style,
                num_scenes=args.scenes,
                verbose=verbose,
            )
        
        if not args.quiet:
            print(f"\n{json.dumps(result, indent=2)}")
        else:
            print(json.dumps(result, indent=2))
        
        # Save results if output dir specified
        if args.output:
            os.makedirs(args.output, exist_ok=True)
            with open(f"{args.output}/results.json", "w") as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Results saved to {args.output}/results.json")
    
    except Exception as e:
        if not args.quiet:
            print(f"❌ Error: {e}", file=sys.stderr)
        else:
            print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
