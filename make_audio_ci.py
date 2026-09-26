import asyncio, json, re, sys
from pathlib import Path
import edge_tts

VOICE = "en-US-AriaNeural"
RATE = "-5%"
here = Path(__file__).resolve().parent.parent
html = (here / "index.html").read_text(encoding="utf-8")
m = re.search(r"const D=(\{.*?\});\s*\nconst P", html, re.S)
if not m:
    print("مقدرتش ألاقي بيانات الجمل جوه index.html"); sys.exit(1)
data = json.loads(m.group(1))
sentences = [s[0] for s in data["s"]]
out = here / "audio"
out.mkdir(parents=True, exist_ok=True)
print(f"هولّد {len(sentences)} ملف صوت...")

async def one(i, text, sem):
    f = out / f"{i}.mp3"
    if f.exists() and f.stat().st_size > 800:
        return
    async with sem:
        for attempt in range(5):
            try:
                await edge_tts.Communicate(text, VOICE, rate=RATE).save(str(f))
                return
            except Exception as e:
                if attempt == 4:
                    print("فشل:", i, text, e)
                await asyncio.sleep(2)

async def main():
    sem = asyncio.Semaphore(8)
    tasks = [one(i + 1, t, sem) for i, t in enumerate(sentences)]
    for k in range(0, len(tasks), 100):
        await asyncio.gather(*tasks[k:k + 100])
        print(min(k + 100, len(tasks)), "/", len(tasks))

asyncio.run(main())
print("خلصت توليد الصوت.")
