# MUAPI Workflows

AI media production workflows using MUAPI API - images, video, music, and talking avatars.

## Quick Start

```bash
# Install dependencies
pip install requests

# Set API key
export MUAPI_API_KEY="your_key_here"

# Run a workflow
python3 01-generate-pfp.py
```

## Workflows

| # | Workflow | Script | Description | Cost |
|---|----------|--------|--------------------------------------------|--------------|
| 01 | Generate PFP | `01-generate-pfp.py` | Agent self-portraits (Hermes, Vex, Eliza) | $0.015 |
| 02 | Professional Headshot | `02-professional-headshot.py` | Template-based headshots with style options | $0.015 |
| 03 | Image to Video | `03-image-to-video.py` | Animate still images with motion presets | $0.12 |
| 04 | Talking Avatar | `04-talking-avatar.py` | Lipsync avatar from text or audio | $0.04-$0.20 |
| 05 | Generate Song | `05-generate-song.py` | Full music with Suno AI (6 genres) | $0.09 |
| 06 | Music Video | `06-music-video.py` | Complete production pipeline | ~$0.26 |
| 07 | Batch Generation | `07-batch-generation.py` | Multiple images with auto-variations | $0.015 x N |

## Pipeline Tools

- `mtv-pipeline.py` - Image/video generation base
- `mtv-music-video.py` - Complete music video production

## Documentation

- [MUAPI API Docs](https://docs.muapi.ai/)
- [Suno AI Docs](https://suno.com/)
- [XMRT DAO MTV Pipeline Skill](https://github.com/xmrtdao/.hermes/tree/main/skills/productivity/mtv-pipeline)

## Examples

See individual workflow scripts for usage examples.
