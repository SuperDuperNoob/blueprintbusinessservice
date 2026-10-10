#!/usr/bin/env python3
"""Batch transcribe BBS modules via Gemini (free tier, separate quota from Groq).
Same resume-safe .txt format as transcribe_all.py (JSON meta first line).
Rotates between 2 API keys on 429. Inline base64 audio (files are small 16k/32k mp3).
Usage: python3 transcribe_gemini.py [--limit N] [--sleep S]
"""
import json, os, sys, time, subprocess, base64, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'bbs_data.json')
OUTDIR = os.path.join(BASE, 'transcripts')
os.makedirs(OUTDIR, exist_ok=True)

def get_keys():
    keys = []
    for line in open('/root/.hermes/.env', encoding='utf-8', errors='ignore'):
        line = line.strip()
        if line.startswith('GEMINI_API_KEY_2='):
            keys.append(line.split('=', 1)[1])
        elif line.startswith('GEMINI_API_KEY='):
            keys.insert(0, line.split('=', 1)[1])
    return [k for k in keys if k]

KEYS = get_keys()
if not KEYS:
    print('no GEMINI keys'); sys.exit(1)
print(f'{len(KEYS)} gemini keys loaded')

MODEL = 'gemini-2.5-flash'
ki = 0  # rotating key index

def gemini_transcribe(mp3_path):
    global ki
    raw = open(mp3_path, 'rb').read()
    b64 = base64.b64encode(raw).decode()
    payload = json.dumps({
        'contents': [{'parts': [
            {'text': 'Transcribe this audio verbatim in its original language. Output only the transcript, no commentary.'},
            {'inline_data': {'mime_type': 'audio/mp3', 'data': b64}},
        ]}],
    }).encode()
    last_err = ''
    for _ in range(len(KEYS)):
        key = KEYS[ki % len(KEYS)]
        ki += 1
        try:
            req = urllib.request.Request(
                f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={key}',
                data=payload, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=300) as r:
                res = json.load(r)
            parts = res.get('candidates', [{}])[0].get('content', {}).get('parts', [])
            text = ''.join(p.get('text', '') for p in parts).strip()
            return text, ''
        except Exception as e:
            last_err = str(e)[:150]
            if '429' in last_err or 'RESOURCE_EXHAUSTED' in last_err:
                continue  # try next key
            return '', last_err
    return '', last_err or 'all keys 429'

limit = int(sys.argv[sys.argv.index('--limit') + 1]) if '--limit' in sys.argv else 0
sleep_s = float(sys.argv[sys.argv.index('--sleep') + 1]) if '--sleep' in sys.argv else 5

d = json.load(open(DATA, encoding='utf-8'))
mods = [m for m in d['Module'] if m.get('video_url') and m.get('thumbnail_url')]
print(f'total with video: {len(mods)}')

done = skip = fail = 0
consec_rl = 0  # circuit breaker: abort run when both keys are dead
todo = mods[:limit] if limit else mods
for i, m in enumerate(todo):
    mid = m['id']
    out = os.path.join(OUTDIR, mid + '.txt')
    if os.path.exists(out) and os.path.getsize(out) > 10:
        skip += 1
        continue
    thumb = m['thumbnail_url']
    cdn_base = thumb.rsplit('/', 1)[0]
    mp3 = f'/tmp/bbsg_{mid}.mp3'
    try:
        r = subprocess.run(
            ['ffmpeg', '-y', '-loglevel', 'error',
             '-headers', 'Referer: https://coachadib.com/',
             '-i', cdn_base + '/240p/video.m3u8', '-vn', '-ar', '16000', '-ac', '1',
             '-c:a', 'libmp3lame', '-b:a', '32k', mp3],
            timeout=300)
        if r.returncode != 0 or not os.path.exists(mp3):
            r = subprocess.run(
                ['ffmpeg', '-y', '-loglevel', 'error',
                 '-headers', 'Referer: https://coachadib.com/',
                 '-i', cdn_base + '/360p/video.m3u8', '-vn', '-ar', '16000', '-ac', '1',
                 '-c:a', 'libmp3lame', '-b:a', '32k', mp3],
                timeout=300)
            if r.returncode != 0 or not os.path.exists(mp3):
                print(f'[{i+1}/{len(todo)}] FAIL dl {m["title"][:50]}', flush=True)
                fail += 1
                continue
        if os.path.getsize(mp3) > 19000000:
            print(f'[{i+1}/{len(todo)}] SKIP too big {m["title"][:50]}', flush=True)
            fail += 1
            try: os.remove(mp3)
            except Exception: pass
            continue
        text, err = gemini_transcribe(mp3)
        try: os.remove(mp3)
        except Exception: pass
        if not text or len(text) < 5:
            print(f'[{i+1}/{len(todo)}] FAIL gemini {m["title"][:50]} :: {err[:100]}', flush=True)
            fail += 1
            if '429' in err or 'EXHAUSTED' in err:
                consec_rl += 1
                if consec_rl >= 5:
                    print(f'both keys dead ({consec_rl} consecutive 429), aborting run — will retry next cron', flush=True)
                    break
                print('both keys limited, sleeping 120s', flush=True)
                time.sleep(120)
            else:
                time.sleep(sleep_s)
            continue
        meta = {'id': mid, 'title': m['title'], 'duration_minutes': m.get('duration_minutes'), 'via': 'gemini'}
        with open(out, 'w', encoding='utf-8') as f:
            f.write(json.dumps(meta, ensure_ascii=False) + '\n' + text)
        done += 1
        consec_rl = 0
        print(f'[{i+1}/{len(todo)}] OK ({len(text)}ch) {m["title"][:50]}', flush=True)
    except subprocess.TimeoutExpired:
        print(f'[{i+1}/{len(todo)}] TIMEOUT {m["title"][:50]}', flush=True)
        fail += 1
        try: os.remove(mp3)
        except Exception: pass
    except Exception as e:
        print(f'[{i+1}/{len(todo)}] ERR {m["title"][:50]} :: {e}', flush=True)
        fail += 1
    time.sleep(sleep_s)

print(f'DONE new={done} skipped={skip} failed={fail}')
