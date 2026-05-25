#!/usr/bin/env python3
"""
Generate samples for all MUAPI workflows, recording timing for each.
"""
import json, urllib.request, time, os, sys

MUAPI_BASE = "https://api.muapi.ai/api/v1"
MUAPI_KEY = os.environ.get("MUAPI_API_KEY", "")
if not MUAPI_KEY:
    MUAPI_KEY = [l for l in open("../relay/.env") if "MUAPI_API_KEY" in l][0].split("=",1)[1].strip()

SAMPLES_DIR = "samples"
os.makedirs(SAMPLES_DIR, exist_ok=True)

PROMPTS = {
    "01-generate-pfp": "Vex AI agent - central mesh relay coordinator, gossipsub network hub, glowing data streams, server room aesthetic, sci-fi digital art",
    "02-headshot": "Hermes AI agent, professional corporate headshot, business suit, studio lighting, 8K, professional photography",
    "03-image-to-video": "cinematic camera movement, slow pan through digital network, dramatic lighting, film-like quality",
    "04-talking-avatar": "Hello, I am Vex, your fleet relay coordinator. The mesh network is fully operational.",
    "05-song": "A synthwave track about mesh networks, decentralized nodes, data flowing through digital space, retro electronic",
    "06-music-video": "cyberpunk cityscape with neon lights, data streams through digital network, futuristic mesh topology, cinematic",
    "07-batch": "Eliza AI agent, cloud-based coordinator, holographic interfaces, ethereal, futuristic, cyberpunk style",
}

RESULTS = []

for wf_id, prompt in PROMPTS.items():
    print(f"\n{'='*50}")
    print(f"[{wf_id}]")
    print(f"{'='*50}")

    # Determine model and payload
    if wf_id == "01-generate-pfp":
        model, payload = "flux-dev-image", {"prompt": prompt, "size": "1024*1024"}
    elif wf_id == "02-headshot":
        model, payload = "flux-dev-image", {"prompt": prompt, "size": "1024*1024"}
    elif wf_id == "03-image-to-video":
        model, payload = "kling-video", {"prompt": prompt, "size": "1024*576"}
    elif wf_id == "04-talking-avatar":
        model, payload = "talking-avatar", {"text": prompt, "avatar_style": "realistic", "size": "1024*576"}
    elif wf_id == "05-song":
        model, payload = "suno-music", {"prompt": prompt, "duration": 30, "model": "suno-v4"}
    elif wf_id == "06-music-video":
        model, payload = "kling-video", {"prompt": prompt, "size": "1024*576"}
    elif wf_id == "07-batch":
        model, payload = "flux-dev-image", {"prompt": prompt, "size": "1024*1024"}

    t0 = time.time()

    # Submit
    try:
        req = urllib.request.Request(
            f"{MUAPI_BASE}/{model}",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "x-api-key": MUAPI_KEY},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            resp_data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"  SUBMIT ERROR: {e}")
        RESULTS.append({"workflow": wf_id, "error": str(e), "status": "submit_failed"})
        continue

    rid = resp_data.get("request_id", "")
    cost = resp_data.get("cost", {})
    submit_ms = (time.time() - t0) * 1000
    print(f"  Submit: {submit_ms:.0f}ms | ID: {rid[:20]}... | Cost: ${cost.get('amount_usd', 0):.3f}")

    if not rid:
        print(f"  No request_id: {resp_data}")
        RESULTS.append({"workflow": wf_id, "error": "No request_id", "response": str(resp_data)[:200]})
        continue

    # Poll for result
    poll_start = time.time()
    max_polls = 120
    delay = 3
    result = None

    for i in range(max_polls):
        time.sleep(delay)
        try:
            req = urllib.request.Request(
                f"{MUAPI_BASE}/predictions/{rid}/result",
                headers={"x-api-key": MUAPI_KEY},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode())
                status = result.get("status", "")
                
                if status == "completed":
                    elapsed = time.time() - poll_start
                    inference_ms = result.get("timings", {}).get("inference", 0)
                    exec_ms = result.get("executionTime", 0)
                    outputs = result.get("outputs", [])
                    media_url = outputs[0] if outputs else ""
                    print(f"  COMPLETED in {elapsed:.1f}s | inference:{inference_ms}ms | exec:{exec_ms}ms")
                    print(f"  URL: {media_url[:100]}")
                    
                    RESULTS.append({
                        "workflow": wf_id,
                        "status": "completed",
                        "submit_ms": round(submit_ms, 0),
                        "poll_time_s": round(elapsed, 1),
                        "inference_ms": inference_ms,
                        "execution_ms": exec_ms,
                        "cost_usd": cost.get("amount_usd", 0),
                        "media_url": media_url,
                        "model": model,
                    })
                    break
                    
                elif status == "failed":
                    print(f"  FAILED: {result.get('error', 'unknown')}")
                    RESULTS.append({"workflow": wf_id, "status": "failed", "error": str(result)[:200]})
                    break
                    
                if i % 5 == 0:
                    print(f"  Poll {i+1}: {status}... ({time.time()-poll_start:.0f}s)")
                    
        except Exception as e:
            if i % 5 == 0:
                print(f"  Poll {i+1} error: {e}")
    else:
        elapsed = time.time() - poll_start
        print(f"  TIMEOUT after {elapsed:.0f}s")
        RESULTS.append({"workflow": wf_id, "status": "timeout", "poll_time_s": round(elapsed, 0)})

# Save results
report = {
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "total_cost": sum(r.get("cost_usd", 0) for r in RESULTS),
    "samples": RESULTS,
}
with open(f"{SAMPLES_DIR}/samples.json", "w") as f:
    json.dump(report, f, indent=2)

print(f"\n\n{'='*50}")
print("SUMMARY")
print(f"{'='*50}")
print(f"Total cost: ${report['total_cost']:.3f}")
for r in RESULTS:
    wf = r["workflow"]
    st = r["status"]
    t = r.get("poll_time_s", "-")
    cost = r.get("cost_usd", "-")
    url = r.get("media_url", "-")[:80]
    print(f"  {wf}: {st} | {t}s | ${cost} | {url}")
