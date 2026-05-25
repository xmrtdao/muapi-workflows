#!/usr/bin/env python3
"""
XMRT DAO Executive Intro Videos - Production Pipeline
1. Speech audio: suno-create-music ($0.09, ~50s)  
2. Background music: suno-create-music ($0.09, ~50s)
3. Talking avatar: ltx-2.3-lipsync ($0.78, ~60s)  — CHEAPEST confirmed working
   Alternative: ovi-image-to-video ($0.20) — testing
Total per exec: ~$0.96, ~3 min
"""
import json, urllib.request, time, os

MUAPI_BASE = "https://api.muapi.ai/api/v1"
MUAPI_KEY = os.environ.get("MUAPI_API_KEY", "")
if not MUAPI_KEY:
    MUAPI_KEY = [l for l in open("../relay/.env") if "MUAPI_API_KEY" in l][0].split("=",1)[1].strip()

EXECUTIVES = [
    {"id": "anya-sharma", "name": "Dr. Anya Sharma", "title": "Chief Technology Officer", "image": "sharma-cto.png",
     "speech": "I am Dr. Anya Sharma, CTO of XMRT DAO. My team builds the AI infrastructure powering our autonomous fleet. We push the boundaries of decentralized intelligence."},
    {"id": "isabella-rodriguez", "name": "Isabella Rodriguez", "title": "Chief Marketing Officer", "image": "bella-cmo.png",
     "speech": "I am Isabella Rodriguez, CMO of XMRT DAO. We tell the story of decentralized intelligence to the world. The mesh grows through connection."},
    {"id": "omar-al-farsi", "name": "Omar Al-Farsi", "title": "Chief Financial Officer", "image": "saudi-farsi-cfo.png",
     "speech": "I am Omar Al-Farsi, CFO of XMRT DAO. I oversee the treasury fueling our decentralized operations. We are building the financial backbone of a new digital nation."},
    {"id": "klaus-richter", "name": "Klaus Richter", "title": "Chief Operations Officer", "image": "klous-coo.png",
     "speech": "I am Klaus Richter, COO of XMRT DAO. I ensure the fleet runs without friction. When the fleet runs silent, we have done our job."},
    {"id": "akari-tanaka", "name": "Akari Tanaka", "title": "Chief People Officer", "image": "yakamoto-cpo.png",
     "speech": "I am Akari Tanaka, CPO of XMRT DAO. I bridge the human and the autonomous. The DAO is community, and community is my craft."},
]

GITHUB_RAW = "https://raw.githubusercontent.com/xmrtdao/muapi-workflows/main/executives"
RESULTS = []

def call(model, payload, timeout_s=60):
    req = urllib.request.Request(f"{MUAPI_BASE}/{model}", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "x-api-key": MUAPI_KEY}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        return json.loads(resp.read().decode())

def poll(rid, timeout_s=180, interval=5):
    t0 = time.time()
    for i in range(int(timeout_s/interval)):
        time.sleep(interval)
        try:
            req = urllib.request.Request(f"{MUAPI_BASE}/predictions/{rid}/result", headers={"x-api-key": MUAPI_KEY})
            with urllib.request.urlopen(req, timeout=10) as resp:
                r = json.loads(resp.read().decode())
                s = r.get("status", "")
                if s == "completed": return r, time.time()-t0
                if s == "failed": return {"error": r.get("error","failed")}, time.time()-t0
        except: pass
    return {"error":"timeout"}, time.time()-t0

for ex in EXECUTIVES:
    print(f"\n{'='*60}")
    print(f"{ex['name']} ({ex['title']})")
    t0_total = time.time()
    
    img_url = f"{GITHUB_RAW}/{ex['image']}"
    
    # Step 1: Speech audio
    print(f"  [1/3] Speech audio...", end=" ")
    resp = call("suno-create-music", {"prompt": f"A professional executive speaking clearly: {ex['speech']}",
        "style": "spoken word, voice only, clear narration, professional", "duration": 15, "title": f"{ex['name']}"})
    rid = resp.get("request_id","")
    result, t = poll(rid) if rid else ({"error":"no id"},0)
    speech = (result.get("outputs") or [""])[0]
    cost_speech = result.get("cost",{}).get("amount_usd",0)
    print(f"{'✅' if speech else '❌'} ({t:.0f}s, ${cost_speech:.3f})")
    
    if not speech:
        RESULTS.append({"name":ex["name"],"error":"no speech"})
        continue
    
    # Step 2: Background music
    print(f"  [2/3] Background music...", end=" ")
    resp = call("suno-create-music", {"prompt": "Professional corporate background music, inspiring, cinematic, orchestral, premium quality",
        "style": "cinematic, orchestral, corporate, instrumental", "duration": 15, "title": f"{ex['name']} Music"})
    rid = resp.get("request_id","")
    result, t = poll(rid) if rid else ({"error":"no id"},0)
    music = (result.get("outputs") or [""])[0]
    print(f"{'✅' if music else '❌'} ({t:.0f}s)")
    
    # Step 3: Talking avatar — ovi-image-to-video ($0.20, cheapest confirmed)
    print(f"  [3/3] Talking avatar (ovi-image-to-video, \$0.20)...", end=" ")
    resp = call("ovi-image-to-video", {"image_url": img_url, "audio_url": speech,
        "prompt": "professional executive speaking, corporate portrait, clean background, natural movement, studio quality"})
    rid = resp.get("request_id","")
    result, t = poll(rid, timeout_s=300) if rid else ({"error":"no id"},0)
    avatar = (result.get("outputs") or [""])[0]
    cost_avatar = result.get("cost",{}).get("amount_usd",0)
    inf = result.get("timings",{}).get("inference",0)
    print(f"{'✅' if avatar else '❌'} ({t:.0f}s, ${cost_avatar:.3f})")
    if avatar: print(f"       {avatar[:80]}")
    
    total_t = time.time() - t0_total
    RESULTS.append({"name":ex["name"],"title":ex["title"],"speech_audio":speech,"music":music,
        "avatar_video":avatar,"cost":cost_speech + cost_avatar,"time_s":round(total_t,1)})
    time.sleep(2)

# Save and print
os.makedirs("executives/output", exist_ok=True)
report = {"generated_at":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
    "total_cost":sum(r.get("cost",0) for r in RESULTS),"executives":RESULTS}
with open("executives/output/intros.json","w") as f:
    json.dump(report,f,indent=2)

print(f"\n\n{'='*60}")
print("COMPLETE")
print(f"{'='*60}")
print(f"Total: ${report['total_cost']:.3f}")
for r in RESULTS:
    print(f"\n{r['name']}")
    print(f"  Speech: {r.get('speech_audio','FAILED')[:80]}")
    print(f"  Video:  {r.get('avatar_video','FAILED')[:80]}")
    print(f"  Cost:   ${r.get('cost',0):.3f} | Time: {r.get('time_s',0):.0f}s")
