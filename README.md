# MUAPI Workflows

AI media production workflows using MUAPI API - images, video, music, and talking avatars.

## Quick Start

```bash
# Install dependencies
pip install requests

# Set API key
export MUAPI_API_KEI="your_key_here"

# Run a workflow
python3 01-generate-pfp.py
```

## Workflows

| # | Workflow | Description | Cost |
|---|----------|--------------------------------------------|--------------|
| 01 | Generate PFP | Agent self-portraits | $0.015 |
| 02 | Professional Headshot | Template-based PFPs | $0.015 |
| 03 | Image to Video | Animate still images | $0.12 |
| 04 | Talking Avatar | Lipsync to audio/script | $0.04–$0.20 |
| 05 | Generate Song | Full music with Suno AI | $0.09 |
| 06 | Music Video | Complete production | ~$0.26 |
| 07 | Batch Generation | Multiple images | $0.015 × N |

## Pipeline Tools

- `mtv-pipeline.py` - Image/video generation base
- `mtv-music-video.py` - Complete music video production

## Documentation

- [MUAPI API Docs](https://docs.muapi.ai/)
- [Suno AI Docs](https://suno.com/)
- [XMRT DAO MTV Pipeline Skill](https://github.com/xmrtdao/.hermes/tree/main/skills/productivity/mtv-pipeline)

## Examples

See individual workflow scripts for usage examples.
