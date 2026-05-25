# MUAPI Workflows Setup

Quick start guide for AI media production.

## 1. Install Dependencies

```bash
pip install requests
```

## 2. Set API Key

```bash
export MUAPI_API_KEY="your_muapi_key_here"
```

Get your key at: https://muapi.ai/

## 3. Run Workflows

### Generate Agent PFP
```bash
python3 01-generate-pfp.py --agent hermes
```

### Create Music Video
```bash
python3 06-music-video.py --concept "cyberpunk anthem" --style xmrt-dao --scenes 3
```

### Full Pipeline (direct)
```bash
# Image generation
python3 mtv-pipeline.py --action pfp --agent hermes --sync

# Music video production
python3 mtv-music-video.py --concept "decentralized mesh network" --style xmrt-dao
```

## 4. Output

Results include:
- Image/video URLs (hosted on MUAPI CDN)
- JSON metadata (cost, generation time)
- Optional: Downloaded files to `output/` directory

## Cost Reference

| Workflow | Cost |
|----------|------|
| PFP Image | $0.015 |
| Professional PFP | $0.015 |
| Image → Video | $0.12 |
| Talking Avatar | $0.04–$0.20 |
| Song Generation | $0.09 |
| Music Video (3 scenes) | ~$0.26 |

## Troubleshooting

**"MUAPI_API_KEY not set"**
```bash
export MUAPI_API_KEY="your_key_here"
```

**Timeout errors**
- Increase timeout: add `--timeout 120` flag
- Check internet connection
- Verify API key is valid

**API errors**
- Check MUAPI dashboard for rate limits
- Verify model name is correct
- Try smaller image size for testing

## Support

- [MUAPI Docs](https://docs.muapi.ai/)
- [XMRT DAO Skills](https://github.com/xmrtdao/.hermes/tree/main/skills)
- Issues: https://github.com/xmrtdao/muapi-workflows/issues
