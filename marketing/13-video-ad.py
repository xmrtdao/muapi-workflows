#!/usr/bin/env python3
"""
Marketing Workflow 13: Video Ad Generator

Create talking avatar video ads for social media.

Usage:
    python3 marketing/13-video-ad.py --script "Our product changes everything..." --style professional
    python3 marketing/13-video-ad.py --script "Special offer today only!" --style energetic --duration 15
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

AVATAR_STYLES = {
    "professional": {
        "prompt": "professional business person, corporate attire, confident expression, office background, clean lighting, trustworthy appearance",
        "model": "wan2.2-speech-to-video",
    },
    "friendly": {
        "prompt": "friendly approachable person, casual professional attire, warm smile, bright background, natural lighting, relatable appearance",
        "model": "wan2.2-speech-to-video",
    },
    "energetic": {
        "prompt": "energetic enthusiastic person, modern casual attire, dynamic expression, vibrant background, high energy lighting, exciting appearance",
        "model": "wan2.2-speech-to-video",
    },
    "expert": {
        "prompt": "industry expert, professional attire, authoritative presence, tech background, studio lighting, knowledgeable appearance",
        "model": "wan2.2-speech-to-video",
    },
    "influencer": {
        "prompt": "social media influencer, trendy attire, camera-ready appearance, instagram aesthetic, ring light lighting, engaging personality",
        "model": "wan2.2-speech-to-video",
    },
}

AD_TEMPLATES = {
    "product-launch": {
        "hook": "Introducing [PRODUCT] - the future of [INDUSTRY] is here.",
        "body": "We've spent [TIME] perfecting every detail. [FEATURE 1]. [FEATURE 2]. [FEATURE 3].",
        "cta": "Get yours today at [WEBSITE]. Limited launch offer - [DISCOUNT] off!",
    },
    "special-offer": {
        "hook": "STOP SCROLLING! This offer ends in [TIMEFRAME]!",
        "body": "Get [DISCOUNT] off [PRODUCT]. That's [SAVINGS] in your pocket. But hurry - only [QUANTITY] left!",
        "cta": "Click the link NOW before it's gone! [WEBSITE]",
    },
    "testimonial": {
        "hook": "I was skeptical at first, but [PRODUCT] changed everything.",
        "body": "Before: [PAIN POINT]. After: [BENEFIT]. I can't imagine going back. Best decision ever!",
        "cta": "Try it risk-free for [DAYS] days. Link in bio! [WEBSITE]",
    },
    "how-it-works": {
        "hook": "Ever wondered how [PRODUCT] actually works? Let me show you.",
        "body": "Step 1: [STEP ONE]. Step 2: [STEP TWO]. Step 3: [STEP THREE]. That's it!",
        "cta": "Ready to try? Get started free at [WEBSITE]",
    },
    "problem-solution": {
        "hook": "Tired of [PAIN POINT]? You're not alone.",
        "body": "We've all been there. That's why we built [PRODUCT]. It [SOLUTION] in seconds.",
        "cta": "Join [NUMBER] happy customers. Start your free trial: [WEBSITE]",
    },
}

def generate_video_ad(script, style="professional", duration=15, custom_avatar=None):
    """Generate talking avatar video ad."""
    from mtv_pipeline import generate_image, generate_talking_avatar
    
    avatar_config = AVATAR_STYLES.get(style, AVATAR_STYLES["professional"])
    
    print(f"🎬 Creating video ad...")
    print(f"   Style: {style}")
    print(f"   Duration: {duration}s")
    print(f"   Script: {script[:80]}{'...' if len(script) > 80 else ''}")
    
    # Step 1: Generate avatar image
    print(f"\n   Step 1/2: Generating avatar...")
    avatar_prompt = custom_avatar or avatar_config["prompt"]
    avatar_result = generate_image(avatar_prompt, "flux-dev-image", "1024*1024")
    print(f"   ✅ Avatar generated")
    
    # Step 2: Generate talking video
    print(f"   Step 2/2: Generating talking video...")
    video_result = generate_talking_avatar(
        avatar_result["image_url"],
        script=script,
        model=avatar_config["model"],
    )
    
    video_result["avatar_image"] = avatar_result["image_url"]
    return video_result

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Create video ad")
    parser.add_argument("--script", required=True, help="Ad script/spoken dialogue")
    parser.add_argument("--style", default="professional", choices=list(AVATAR_STYLES.keys()), help="Avatar style")
    parser.add_argument("--duration", type=int, default=15, help="Video duration (seconds)")
    parser.add_argument("--template", choices=list(AD_TEMPLATES.keys()), help="Use ad template")
    parser.add_argument("--product", help="Product name (for template)")
    parser.add_argument("--website", help="Website URL (for template)")
    parser.add_argument("--output", help="Output directory")
    args = parser.parse_args()
    
    # Build script from template if provided
    script = args.script
    if args.template:
        template = AD_TEMPLATES[args.template]
        script = f"{template['hook']} {template['body']} {template['cta']}"
        if args.product:
            script = script.replace("[PRODUCT]", args.product)
        if args.website:
            script = script.replace("[WEBSITE]", args.website)
    
    result = generate_video_ad(script, args.style, args.duration)
    
    print(f"\n✅ Video ad complete!")
    print(f"   Video: {result['video_url']}")
    print(f"   Avatar: {result['avatar_image']}")
    print(f"   Cost: ${result['cost_usd']:.3f}")
    
    if args.output:
        import json
        os.makedirs(args.output, exist_ok=True)
        with open(os.path.join(args.output, "video-ad.json"), "w") as f:
            json.dump(result, f, indent=2)
        print(f"   📁 Results saved to {args.output}/video-ad.json")

if __name__ == "__main__":
    main()
