# MUAPI Marketing Workflows

AI-powered marketing content generation using MUAPI — social media, ads, brand assets, and video content.

## Quick Start

```bash
export MUAPI_API_KEY="your_key_here"

# Generate social media post image
python3 marketing/01-social-post.py --platform twitter --topic "product launch"

# Create brand logo variations
python3 marketing/02-logo-generator.py --brand "MyBrand" --style modern

# Generate product photography
python3 marketing/03-product-shot.py --description "wireless headphones" --style studio

# Create talking avatar ad
python3 marketing/04-video-ad.py --script "Welcome to our product..." --style professional
```

## Marketing Workflows

### Social Media

| # | Workflow | Platform | Cost |
|---|----------|----------|------|
| 01 | Social Post Image | Twitter/X, Instagram, LinkedIn | $0.015 |
| 02 | Story/Reel Background | Instagram, TikTok | $0.015 |
| 03 | Profile Banner | Twitter, YouTube, LinkedIn | $0.015 |
| 04 | Carousel Cards | Instagram, LinkedIn | $0.015 × N |

### Brand Assets

| # | Workflow | Purpose | Cost |
|---|----------|---------|------|
| 05 | Logo Generator | Brand identity variations | $0.015 × N |
| 06 | Brand Colors | Palette generation | $0.015 |
| 07 | Brand Mascot | Character design | $0.015 |
| 08 | Icon Set | UI/app icons | $0.015 × N |

### Product Marketing

| # | Workflow | Purpose | Cost |
|---|----------|---------|------|
| 09 | Product Shot | Studio-quality photos | $0.015 |
| 10 | Lifestyle Image | Product in context | $0.015 |
| 11 | Packaging Mockup | Box/bottle design | $0.015 |
| 12 | Before/After | Transformation visuals | $0.030 |

### Video Ads

| # | Workflow | Format | Cost |
|---|----------|--------|------|
| 13 | Talking Head Ad | Spokesperson video | $0.16 |
| 14 | Product Demo | Feature showcase | $0.16 |
| 15 | Testimonial | Customer story | $0.16 |
| 16 | Explainer | How-it-works video | $0.26+ |

### Email Marketing

| # | Workflow | Purpose | Cost |
|---|----------|---------|------|
| 17 | Email Header | Campaign header image | $0.015 |
| 18 | Promo Banner | Sale/offer graphic | $0.015 |
| 19 | Newsletter Visual | Content illustration | $0.015 |

## Complete Campaigns

### Product Launch Campaign (~$2.50)
```bash
# Brand assets
python3 marketing/02-logo-generator.py --brand "ProductName" --style modern
python3 marketing/06-brand-colors.py --vibe "tech, innovative"

# Social media (10 posts)
python3 marketing/01-social-post.py --platform twitter --topic "launch teaser"
python3 marketing/01-social-post.py --platform instagram --topic "product reveal"

# Product visuals
python3 marketing/09-product-shot.py --description "sleek wireless earbuds"
python3 marketing/10-lifestyle-image.py --scene "gym, workout"

# Video ad
python3 marketing/13-talking-head-ad.py --script "Introducing..." --duration 15

# Email assets
python3 marketing/17-email-header.py --campaign "launch"
```

### Social Media Monthly (~$1.50)
```bash
# 20 posts (mix of platforms)
python3 marketing/01-social-post.py --batch --count 20 --themes "tips, quotes, product"

# 4 story backgrounds
python3 marketing/02-story-bg.py --count 4 --style "gradient, abstract"

# Profile refresh
python3 marketing/03-profile-banner.py --platform twitter
python3 marketing/05-profile-pic.py --style professional
```

### Video Ad Campaign (~$1.00)
```bash
# 3 variations of talking head ad
python3 marketing/13-talking-head-ad.py --script "Version A" --avatar professional
python3 marketing/13-talking-head-ad.py --script "Version B" --avatar friendly
python3 marketing/13-talking-head-ad.py --script "Version C" --avatar energetic

# A/B test with different styles
```

## Style Presets

### Brand Vibes
- `modern` — Clean, minimalist, contemporary
- `luxury` — Gold, black, elegant, premium
- `playful` — Bright colors, fun, energetic
- `professional` — Corporate, trustworthy, clean
- `tech` — Futuristic, neon, cyberpunk
- `organic` — Natural, earth tones, sustainable
- `retro` — Vintage, nostalgic, classic
- `bold` — High contrast, impactful, loud

### Platform Specifications

| Platform | Image Size | Aspect Ratio |
|----------|-----------|--------------|
| Twitter Post | 1200×675 | 16:9 |
| Instagram Post | 1080×1080 | 1:1 |
| Instagram Story | 1080×1920 | 9:16 |
| LinkedIn Post | 1200×627 | 1.91:1 |
| Facebook Ad | 1200×628 | 1.91:1 |
| YouTube Thumbnail | 1280×720 | 16:9 |
| Pinterest Pin | 1000×1500 | 2:3 |

## Cost Reference

| Asset Type | Unit Cost | Campaign Qty | Total |
|------------|-----------|--------------|-------|
| Social Post | $0.015 | 20 posts | $0.30 |
| Logo Variation | $0.015 | 5 options | $0.075 |
| Product Shot | $0.015 | 3 angles | $0.045 |
| Video Ad (15s) | $0.16 | 3 variations | $0.48 |
| Email Header | $0.015 | 4 campaigns | $0.06 |
| **Full Campaign** | — | — | **~$1.00–$3.00** |

## Integration

### With Marketing Tools

```bash
# Upload to CMS
python3 marketing/01-social-post.py --output ./assets --format png
# Then upload to WordPress, Contentful, etc.

# Schedule with Buffer/Hootsuite
python3 marketing/01-social-post.py --platform twitter --output ./scheduled
# Import to scheduling tool

# A/B Testing
python3 marketing/13-talking-head-ad.py --script "A" --output variant-a.mp4
python3 marketing/13-talking-head-ad.py --script "B" --output variant-b.mp4
# Test both on Facebook Ads Manager
```

## Best Practices

### Content Calendar
- Generate 2-4 weeks of content in one batch
- Create variations for each platform
- Mix promotional, educational, and engagement posts

### Brand Consistency
- Use same style preset across all assets
- Generate logo/brand colors first, reference in other prompts
- Create brand guidelines document from generated assets

### Video Ads
- Keep scripts under 75 words for 15s videos
- Hook in first 3 seconds
- Include clear CTA at end
- Test multiple avatar styles

### A/B Testing
- Generate 3-5 variations of each asset
- Test different colors, layouts, messaging
- Use data to refine future generations

## Support Files

- `templates/` — Prompt templates for common marketing needs
- `examples/` — Sample outputs and use cases
- `brand-guidelines.md` — How to maintain consistency

## Related

- Main workflows: `../01-generate-pfp.py`, `../06-music-video.py`
- Core pipeline: `../mtv-pipeline.py`, `../mtv-music-video.py`
- [MUAPI Docs](https://docs.muapi.ai/)
