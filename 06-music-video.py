#!/usr/bin/env python3
"""
Workflow 06: Complete Music Video

Full music video production from concept to final video.

Usage:
    python3 06-music-video.py --concept "cyberpunk anthem" --style xmrt-dao
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mtv_music_video import create_music_video

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Create complete music video")
    parser.add_argument("--concept", required=True, help="Song concept")
    parser.add_argument("--style", default="electronic", help="Music style")
    parser.add_argument("--scenes", type=int, default=3, help="Number of scenes")
    parser.add_argument("--output", help="Output directory")
    args = parser.parse_args()
    
    print(f"🎵 Creating music video: {args.concept}")
    result = create_music_video(args.concept, args.style, args.scenes)
    
    print(f"\n✅ Production complete!")
    print(f"   Title: {result.get('title', 'Untitled')}")
    print(f"   Scenes: {len(result.get('scenes', []))}")
    print(f"   Total Cost: ${result['total_cost_usd']:.3f}")
    
    if args.output:
        import json
        os.makedirs(args.output, exist_ok=True)
        with open(os.path.join(args.output, "results.json"), "w") as f:
            json.dump(result, f, indent=2)
        print(f"   📁 Results saved to {args.output}/results.json")

if __name__ == "__main__":
    main()
