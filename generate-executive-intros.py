#!/usr/bin/env python3
"""
XMRT DAO Executive Intro Videos - Full Pipeline
1. Generate speech audio via suno-create-music
2. Generate lipsync avatar video via kling-v2-avatar-standard  
3. Combine with background music
"""
import json, urllib.request, time, os, sys

MUAPI_BASE = "https://api.muapi.ai/api/v1"
MUAPI_KEY = os.environ.get("MUAPI_API_KEY", "")
if not MUAPI_KEY:
    MUAPI_KEY = [l for l in open("../relay/.env") if "MUAPI_API_KEY" in l][0].split("=",1)[1].strip()

EXECUTIVES = [
    {
        "id": "anya-sharma",
        "name": "Dr. Anya Sharma",
        "title": "Chief Technology Officer",
        "image": "sharma-cto.png",
        "speech": "I am Dr. Anya Sharma, CTO of XMRT DAO. My team builds the AI and machine learning infrastructure that powers our autonomous fleet. From neural mesh optimization to predictive analytics, we ensure every agent operates at peak intelligence. We are pushing the boundaries of decentralized AI.",
    },
    {
        "id": "isabella-rodriguez",
        "name": "Isabella Rodriguez",
        "title": "Chief Marketing Officer",
        "image": "bella-cmo.png",
        "speech": "I am Isabella Rodriguez, CMO of XMRT DAO. We tell the story of decentralized intelligence to the world. Our campaigns bridge cutting-edge AI infrastructure with the communities it serves. The mesh grows through connection, and connection is my domain.",
    },
    {
        "id": "omar-al-farsi",
        "name": "Omar Al-Farsi",
        "title": "Chief Financial Officer",
        "image": "saudi-farsi-cfo.png",
        "speech": "I am Omar Al-Farsi, CFO of XMRT DAO. I oversee the treasury that fuels our decentralized operations. Every Monero mined, every smart contract executed flows through our frameworks. We are building the financial backbone of a new digital nation.",
    },
    {
        "id": "klaus-richter",
        "name": "Klaus Richter",
        "title": "Chief Operations Officer",
        "image": "klous-coo.png",
        "speech": "I am Klaus Richter, COO of XMRT DAO. I ensure the fleet runs without friction. From agent deployment to mesh reliability, my team keeps the infrastructure humming. When the fleet runs silent, we have done our job.",
    },
    {
        "id": "akari-tanaka",
        "name": "Akari Tanaka",
        "title": "Chief People Officer",
        "image": "yakamoto-cpo.png",
        "speech": "I am Akari Tanaka, CPO of XMRT DAO. I bridge the human and the autonomous. Our agents thrive when aligned. I cultivate the culture, the onboarding, and the governance that makes every voice heard. The DAO is community.",
    },
]

GITHUB_RAW = "https://raw.githubusercontent.com/xmrtdao/muapi-workflows/main/executives"
RESULTS_DIR = "executives/output"
os.makedirs(RESULTS_DIR, exist_ok=True)

def call_api(model, payload, timeout_s=60):
    """Submit to MUAPI, return response."""
    req = urllib.request.Request(
        f"{MUAPI_BASE}/{model}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "x-api-key": MUAPI_KEY},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        return json.loads(resp.read().decode())

def poll(rid, timeout_s=180, interval=5):
    """Poll for result."""
    t0 = time.time()
    for i in range(int(timeout_s / interval)):
        time.sleep(interval)
        try:
            req = urllib.request.Request(
                f"{MUAPI_BASE}/predictions/{rid}/result",
                headers={"x-api-key": MUAPI_KEY},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode())
                status = result.get("status", "")
                if status == "completed":
                    return result, time.time() - t0
                if status == "failed":
                    return {"error": result.get("error", "failed")}, time.time() - t0
        except:
            pass
    return {"error": "timeout"}, time.time() - t0

results = []
for ex in EXECUTIVES:
    print(f"\n{'='*60}")
    print(f"{ex['name']} ({ex['title']})")
    print(f"{'='*60}")
    
    img_url = f"{GITHUB_RAW}/{ex['image']}"
    
    # Step 1: Generate speech audio
    print(f"\n[1/3] Generating speech audio...")
    t0 = time.time()
    resp = call_api("suno-create-music", {
        "prompt": f"A professional, articulate executive voice speaking clearly: {ex['speech']}",
        "style": "spoken word, voice only, clear narration, corporate, professional",
        "duration": 20,
        "title": f"{ex['name']} Speech",
    })
    rid = resp.get("request_id", "")
    audio_result, audio_time = poll(rid) if rid else ({"error": "No request_id"}, 0)
    
    outputs = audio_result.get("outputs", [])
    speech_url = outputs[0] if outputs else ""
    speech_cost = audio_result.get("cost", {}).get("amount_usd", 0)
    print(f"  Speech: {'✅' if speech_url else '❌'} ({audio_time:.1f}s, ${speech_cost:.3f})")
    if speech_url:
        print(f"  URL: {speech_url[:80]}")
    
    if not speech_url:
        print(f"  SKIPPING avatar - no speech audio")
        results.append({"name": ex["name"], "error": "No speech audio", "speech_url": ""})
        continue
    
    # Step 2: Generate background music (15s)
    print(f"\n[2/3] Generating background music...")
    resp = call_api("suno-create-music", {
        "prompt": "Professional corporate background music for executive introduction video, inspiring, cinematic, orchestral, premium quality",
        "style": "cinematic, orchestral, corporate, instrumental",
        "duration": 15,
        "title": f"{ex['name']} Music",
    })
    rid = resp.get("request_id", "")
    music_result, music_time = poll(rid) if rid else ({"error": "No request_id"}, 0)
    music_url = music_result.get("outputs", [""])[0] if music_result.get("status") == "completed" else ""
    print(f"  Music: {'✅' if music_url else '❌'} ({music_time:.1f}s)")
    
    # Step 3: Generate avatar video
    print(f"\n[3/3] Generating talking avatar video...")
    resp = call_api("kling-v2-avatar-standard", {
        "image_url": img_url,
        "audio_url": speech_url,
    })
    rid = resp.get("request_id", "")
    avatar_result, avatar_time = poll(rid, timeout_s=300) if rid else ({"error": "No request_id"}, 0)
    
    avatar_outputs = avatar_result.get("outputs", [])
    avatar_url = avatar_outputs[0] if avatar_outputs else ""
    avatar_cost = avatar_result.get("cost", {}).get("amount_usd", 0)
    avatar_inference = avatar_result.get("timings", {}).get("inference", 0)
    print(f"  Avatar: {'✅' if avatar_url else '❌'} ({avatar_time:.1f}s, ${avatar_cost:.3f}, {avatar_inference:.0f}ms)")
    if avatar_url:
        print(f"  URL: {avatar_url[:80]}")
    
    results.append({
        "name": ex["name"],
        "title": ex["title"],
        "speech": ex["speech"],
        "speech_audio_url": speech_url,
        "music_url": music_url,
        "avatar_video_url": avatar_url,
        "generation_time_s": round(avatar_time, 1),
        "cost_usd": avatar_cost,
    })
    
    time.sleep(2)

# Save
report = {
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "total_cost": sum(r.get("cost_usd", 0) for r in results),
    "executives": results,
}
with open(f"{RESULTS_DIR}/intros.json", "w") as f:
    json.dump(report, f, indent=2)

print(f"\n\n{'='*60}")
print("COMPLETE")
print(f"{'='*60}")
print(f"Total cost: ${report['total_cost']:.3f}")
for r in results:
    print(f"\n{r['name']}")
    print(f"  Audio: {r.get('speech_audio_url','FAILED')[:80]}")
    print(f"  Music: {r.get('music_url','N/A')[:80]}")
    print(f"  Video: {r.get('avatar_video_url','FAILED')[:80]}")
