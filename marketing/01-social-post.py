#!/usr/bin/env python3
"""
Marketing Workflow 01: Social Media Post Generator

Generate platform-optimized social media images.

Usage:
    python3 marketing/01-social-post.py --platform twitter --topic "product launch"
    python3 marketing/01-social-post.py --platform instagram --topic "behind the scenes" --style candid
    python3 marketing/01-social-post.py --batch --count 5 --themes "tips,quotes,product"
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PLATFORM_SPECS = {
    "twitter": {"size": "1200*675", "ratio": "16:9", "desc": "Twitter/X post"},
    "instagram": {"size": "1080*1080", "ratio": "1:1", "desc": "Instagram post"},
    "instagram-story": {"size": "1080*1920", "ratio": "9:16", "desc": "Instagram Story"},
    "linkedin": {"size": "1200*627", "ratio": "1.91:1", "desc": "LinkedIn post"},
    "facebook": {"size": "1200*628", "ratio": "1.91:1", "desc": "Facebook ad"},
    "youtube": {"size": "1280*720", "ratio": "16:9", "desc": "YouTube thumbnail"},
    "pinterest": {"size": "1000*1500", "ratio": "2:3", "desc": "Pinterest pin"},
}

STYLE_PROMPTS = {
    "modern": "clean minimalist design, contemporary aesthetic, sans-serif typography, ample white space, professional",
    "bold": "high contrast, vibrant colors, impactful typography, attention-grabbing, dynamic composition",
    "elegant": "sophisticated design, refined color palette, luxury aesthetic, premium feel, subtle gradients",
    "playful": "bright colors, fun illustrations, energetic vibe, friendly typography, cheerful composition",
    "tech": "futuristic design, neon accents, digital aesthetic, cyberpunk influences, high-tech feel",
    "organic": "natural textures, earth tones, sustainable aesthetic, hand-drawn elements, eco-friendly vibe",
    "retro": "vintage style, nostalgic colors, classic typography, retro patterns, old-school cool",
    "professional": "corporate design, trustworthy aesthetic, clean layout, business-appropriate, polished",
}

TOPIC_PROMPTS = {
    "product launch": "new product announcement, exciting reveal, launch event, product showcase, debut",
    "behind the scenes": "behind the scenes content, team at work, process glimpse, authentic moment, candid",
    "tip": "helpful tip, educational content, value-add advice, expert insight, how-to guidance",
    "quote": "inspirational quote, motivational message, thought leadership, wisdom share, impactful statement",
    "testimonial": "customer testimonial, success story, review highlight, social proof, happy customer",
    "sale": "sale announcement, special offer, limited time deal, discount promotion, shopping opportunity",
    "event": "event promotion, conference, webinar, meetup, gathering, networking opportunity",
    "milestone": "company milestone, achievement celebration, growth metric, success marker, progress update",
}

def generate_social_post(platform, topic, style="modern", custom_prompt=None):
    """Generate social media post image."""
    from mtv_pipeline import generate_image
    
    specs = PLATFORM_SPECS.get(platform, PLATFORM_SPECS["twitter"])
    style_desc = STYLE_PROMPTS.get(style, STYLE_PROMPTS["modern"])
    topic_desc = TOPIC_PROMPTS.get(topic, topic)
    
    if custom_prompt:
        prompt = f"{custom_prompt}, {style_desc}, social media graphic"
    else:
        prompt = f"{topic_desc}, {style_desc}, social media graphic for {specs['desc']}"
    
    print(f"📱 Generating {specs['desc']}...")
    print(f"   Topic: {topic}")
    print(f"   Style: {style}")
    print(f"   Size: {specs['size']} ({specs['ratio']})")
    
    result = generate_image(prompt, "flux-dev-image", specs["size"])
    return result

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate social media post")
    parser.add_argument("--platform", choices=list(PLATFORM_SPECS.keys()), help="Target platform")
    parser.add_argument("--topic", help="Content topic")
    parser.add_argument("--style", default="modern", choices=list(STYLE_PROMPTS.keys()), help="Visual style")
    parser.add_argument("--prompt", help="Custom prompt (overrides topic)")
    parser.add_argument("--output", help="Output directory")
    parser.add_argument("--batch", action="store_true", help="Batch generation mode")
    parser.add_argument("--count", type=int, default=5, help="Number of variations (batch mode)")
    parser.add_argument("--themes", help="Comma-separated themes (batch mode)")
    args = parser.parse_args()
    
    if args.batch:
        themes = [t.strip() for t in (args.themes or "tips,quotes,product").split(",")]
        print(f"🎨 Generating {args.count} social posts with themes: {themes}\n")
        
        results = []
        for i, theme in enumerate(themes[:args.count]):
            print(f"\n--- Post {i+1}/{len(themes)} ---")
            result = generate_social_post("instagram", theme, args.style)
            results.append({"theme": theme, **result})
            print(f"   ✅ {result['image_url']}")
        
        print(f"\n✅ Batch complete! {len(results)} posts generated")
        print(f"   Total cost: ${sum(r['cost_usd'] for r in results):.3f}")
        
        if args.output:
            import json
            os.makedirs(args.output, exist_ok=True)
            with open(os.path.join(args.output, "social-posts.json"), "w") as f:
                json.dump(results, f, indent=2)
            print(f"   📁 Results saved to {args.output}/social-posts.json")
    else:
        if not args.platform or not args.topic:
            parser.error("--platform and --topic required (or use --batch)")
        
        result = generate_social_post(args.platform, args.topic, args.style, args.prompt)
        
        print(f"\n✅ Complete!")
        print(f"   URL: {result['image_url']}")
        print(f"   Cost: ${result['cost_usd']:.3f}")
        
        if args.output:
            import urllib.request
            os.makedirs(args.output, exist_ok=True)
            filename = f"{args.platform}-{args.topic.replace(' ', '-')}.png"
            filepath = os.path.join(args.output, filename)
            print(f"   Saving to {filepath}...")
            urllib.request.urlretrieve(result['image_url'], filepath)
            print(f"   ✅ Saved!")

if __name__ == "__main__":
    main()
