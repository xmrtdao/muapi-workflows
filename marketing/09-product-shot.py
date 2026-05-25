#!/usr/bin/env python3
"""
Marketing Workflow 09: Product Photography

Generate studio-quality product shots.

Usage:
    python3 marketing/09-product-shot.py --description "wireless headphones" --style studio
    python3 marketing/09-product-shot.py --description "smart watch" --style lifestyle --scene "gym"
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SHOT_STYLES = {
    "studio": {
        "bg": "clean white background, professional studio lighting, seamless backdrop, product photography",
        "lighting": "softbox lighting, even illumination, no shadows, commercial quality",
    },
    "lifestyle": {
        "bg": "real-world context, natural environment, lifestyle photography, authentic setting",
        "lighting": "natural lighting, golden hour, warm tones, lifestyle aesthetic",
    },
    "dramatic": {
        "bg": "dark moody background, dramatic shadows, high contrast, cinematic atmosphere",
        "lighting": "directional lighting, rim lighting, dramatic shadows, editorial style",
    },
    "minimal": {
        "bg": "minimalist background, ample negative space, clean composition, simple aesthetic",
        "lighting": "soft even lighting, minimal shadows, clean look, modern aesthetic",
    },
    "luxury": {
        "bg": "premium background, marble/velvet texture, luxury setting, high-end aesthetic",
        "lighting": "sophisticated lighting, warm highlights, premium feel, elegant atmosphere",
    },
    "tech": {
        "bg": "futuristic background, neon accents, digital aesthetic, tech environment",
        "lighting": "RGB lighting, neon glow, cyberpunk aesthetic, high-tech feel",
    },
}

LIFESTYLE_SCENES = {
    "gym": "gym/fitness setting, workout equipment, active lifestyle, health-conscious environment",
    "office": "modern office desk, professional workspace, laptop, coffee, business environment",
    "home": "cozy home setting, living room, warm atmosphere, comfortable furniture",
    "outdoor": "outdoor nature setting, park, natural light, fresh air, adventure",
    "cafe": "trendy cafe, coffee shop, urban setting, social environment, millennial aesthetic",
    "travel": "travel setting, airport, hotel, suitcase, adventure, wanderlust",
    "kitchen": "modern kitchen, cooking environment, culinary setting, home chef",
    "bedroom": "bedroom setting, bedside table, relaxation, sleep environment, cozy",
}

def generate_product_shot(description, style="studio", scene=None, custom_prompt=None):
    """Generate product photography."""
    from mtv_pipeline import generate_image
    
    style_config = SHOT_STYLES.get(style, SHOT_STYLES["studio"])
    
    if custom_prompt:
        prompt = custom_prompt
    elif style == "lifestyle" and scene:
        scene_desc = LIFESTYLE_SCENES.get(scene, LIFESTYLE_SCENES["office"])
        prompt = f"{description} product photography, {scene_desc}, {style_config['bg']}, {style_config['lighting']}, commercial quality, professional"
    else:
        prompt = f"{description} product photography, {style_config['bg']}, {style_config['lighting']}, commercial quality, professional, high detail, 8k"
    
    print(f"📸 Generating product shot...")
    print(f"   Product: {description}")
    print(f"   Style: {style}")
    if scene:
        print(f"   Scene: {scene}")
    
    result = generate_image(prompt, "flux-dev-image", "1024*1024")
    return result

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate product photography")
    parser.add_argument("--description", required=True, help="Product description")
    parser.add_argument("--style", default="studio", choices=list(SHOT_STYLES.keys()), help="Photography style")
    parser.add_argument("--scene", choices=list(LIFESTYLE_SCENES.keys()), help="Lifestyle scene (for lifestyle style)")
    parser.add_argument("--prompt", help="Custom prompt (overrides style/scene)")
    parser.add_argument("--variations", type=int, default=1, help="Number of variations")
    parser.add_argument("--output", help="Output directory")
    args = parser.parse_args()
    
    print(f"📸 Generating {args.variations} product shot(s): {args.description}\n")
    
    results = []
    for i in range(args.variations):
        if args.variations > 1:
            print(f"\n--- Variation {i+1}/{args.variations} ---")
        
        result = generate_product_shot(args.description, args.style, args.scene, args.prompt)
        result["variation"] = i+1
        results.append(result)
    
    print(f"\n✅ Product photography complete!")
    print(f"   Shots generated: {len(results)}")
    print(f"   Total cost: ${sum(r['cost_usd'] for r in results):.3f}")
    
    if args.output:
        import json
        os.makedirs(args.output, exist_ok=True)
        with open(os.path.join(args.output, "product-shots.json"), "w") as f:
            json.dump(results, f, indent=2)
        print(f"   📁 Results saved to {args.output}/product-shots.json")

if __name__ == "__main__":
    main()
