#!/usr/bin/env python3
"""
Marketing Workflow 05: Logo Generator

Generate brand logo variations.

Usage:
    python3 marketing/05-logo-generator.py --brand "TechCorp" --style modern
    python3 marketing/05-logo-generator.py --brand "EcoShop" --style organic --variations 5
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

LOGO_STYLES = {
    "modern": "minimalist logo design, clean geometric shapes, sans-serif typography, contemporary aesthetic, professional, scalable vector style",
    "luxury": "elegant logo design, gold and black color scheme, sophisticated typography, premium feel, luxury brand aesthetic, refined details",
    "playful": "fun logo design, bright vibrant colors, rounded shapes, friendly typography, approachable, energetic brand personality",
    "tech": "futuristic logo design, neon accents, digital aesthetic, cyberpunk influences, high-tech feel, innovative appearance",
    "organic": "natural logo design, earth tones, leaf/botanical elements, hand-drawn aesthetic, sustainable brand, eco-friendly vibe",
    "retro": "vintage logo design, retro color palette, classic typography, nostalgic feel, old-school cool, timeless appeal",
    "bold": "impactful logo design, high contrast, strong typography, attention-grabbing, dynamic shapes, memorable brand mark",
    "professional": "corporate logo design, trustworthy aesthetic, clean layout, business-appropriate, polished, enterprise-grade",
}

COLOR_PALETTES = {
    "modern": "blue, white, gray, clean",
    "luxury": "gold, black, deep purple, premium",
    "playful": "orange, yellow, bright blue, energetic",
    "tech": "neon blue, purple, black, cyberpunk",
    "organic": "green, brown, earth tones, natural",
    "retro": "muted orange, teal, cream, vintage",
    "bold": "red, black, white, high contrast",
    "professional": "navy, gray, white, corporate",
}

def generate_logo(brand_name, style="modern", variations=3, custom_prompt=None):
    """Generate logo variations."""
    from mtv_pipeline import generate_image
    
    style_desc = LOGO_STYLES.get(style, LOGO_STYLES["modern"])
    colors = COLOR_PALETTES.get(style, "")
    
    results = []
    for i in range(variations):
        if custom_prompt:
            prompt = f"{custom_prompt}, logo design, variation {i+1}"
        else:
            prompt = f"{brand_name} logo, {style_desc}, {colors} color palette, logo design variation {i+1}, professional branding, vector style, white background"
        
        print(f"\n🎨 Generating logo {i+1}/{variations}...")
        print(f"   Brand: {brand_name}")
        print(f"   Style: {style}")
        print(f"   Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        
        result = generate_image(prompt, "flux-dev-image", "1024*1024")
        result["variation"] = i+1
        results.append(result)
        print(f"   ✅ {result['image_url']}")
    
    return results

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate logo variations")
    parser.add_argument("--brand", required=True, help="Brand name")
    parser.add_argument("--style", default="modern", choices=list(LOGO_STYLES.keys()), help="Logo style")
    parser.add_argument("--variations", type=int, default=3, help="Number of variations")
    parser.add_argument("--prompt", help="Custom prompt (overrides style)")
    parser.add_argument("--output", help="Output directory")
    args = parser.parse_args()
    
    print(f"🎨 Generating {args.variations} logo variations for '{args.brand}'...")
    print(f"   Style: {args.style}")
    
    results = generate_logo(args.brand, args.style, args.variations, args.prompt)
    
    print(f"\n✅ Logo generation complete!")
    print(f"   Variations: {len(results)}")
    print(f"   Total cost: ${sum(r['cost_usd'] for r in results):.3f}")
    
    if args.output:
        import json
        os.makedirs(args.output, exist_ok=True)
        with open(os.path.join(args.output, f"{args.brand}-logos.json"), "w") as f:
            json.dump(results, f, indent=2)
        print(f"   📁 Results saved to {args.output}/{args.brand}-logos.json")

if __name__ == "__main__":
    main()
