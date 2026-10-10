#!/usr/bin/env python3
"""Batch transcribe all BBS modules via Groq whisper-large-v3-turbo.
Polite: sequential, one video at a time, sleeps between calls, resume-safe.
Usage: python3 transcribe_all.py [--limit N] [--sleep S]
"""
import json, os, sys, time, subprocess, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'bbs_data.json')
OUTDIR = os.path.join(BASE, 'transcripts')
os.makedirs(OUTDIR, exist_ok=True)

def get_key():
    for line in open('/root/.hermes/.env', encoding='utf-8', errors='ignore'):
        if line.startswith('GROQ_API_KEY='):
            return line.strip().split('=', 1)[1]
    return ''

KEY = get_key()
if not KEY:
    print('GROQ_API_KEY missing'); sys.exit(1)

limit = int(sys.argv[sys.argv.index('--limit') + 1]) if '--limit' in sys.argv else 0
sleep_s = float(sys.argv[sys.argv.index('--sleep') + 1]) if '--sleep' in sys.argv else 5

d = json.load(open(DATA, encoding='utf-8'))
mods = [m for m in d['Module'] if m.get('video_url') and m.get('thumbnail_url')]
print(f'total with video: {len(mods)}')

done = 0
skip = 0
fail = 0
consec_rl = 0  # circuit breaker: abort run when API quota is dead
todo = mods[:limit] if limit else mods
for i, m in enumerate(todo):
    mid = m['id']
    out = os.path.join(OUTDIR, mid + '.txt')
    if os.path.exists(out) and os.path.getsize(out) > 10:
        skip += 1
        continue
    thumb = m['thumbnail_url']
    cdn_base = thumb.rsplit('/', 1)[0]  # strip thumbnail.jpg
    playlist = cdn_base + '/240p/video.m3u8'
    mp3 = f'/tmp/bbs_{mid}.mp3'
    try:
        # 1. extract audio (low bandwidth 240p, 16k mono 32kbit)
        r = subprocess.run(
            ['ffmpeg', '-y', '-loglevel', 'error',
             '-headers', 'Referer: https://coachadib.com/',
             '-i', playlist, '-vn', '-ar', '16000', '-ac', '1',
             '-c:a', 'libmp3lame', '-b:a', '32k', mp3],
            timeout=300)
        if r.returncode != 0 or not os.path.exists(mp3):
            # fallback: try 360p
            playlist360 = cdn_base + '/360p/video.m3u8'
            r = subprocess.run(
                ['ffmpeg', '-y', '-loglevel', 'error',
                 '-headers', 'Referer: https://coachadib.com/',
                 '-i', playlist360, '-vn', '-ar', '16000', '-ac', '1',
                 '-c:a', 'libmp3lame', '-b:a', '32k', mp3],
                timeout=300)
            if r.returncode != 0 or not os.path.exists(mp3):
                print(f'[{i+1}/{len(todo)}] FAIL dl {m["title"][:50]}')
                fail += 1
                continue
        if os.path.getsize(mp3) > 24000000:
            print(f'[{i+1}/{len(todo)}] SKIP too big {m["title"][:50]}')
            fail += 1
            try: os.remove(mp3)
            except: pass
            continue
        # 2. Groq transcribe via curl (multipart)
        r = subprocess.run(
            ['curl', '-s', '--fail-with-body', '--max-time', '300',
             'https://api.groq.com/openai/v1/audio/transcriptions',
             '-H', f'Authorization: Bearer {KEY}',
             '-F', f'file=@{mp3}',
             '-F', 'model=whisper-large-v3-turbo',
             '-F', 'response_format=text'],
            capture_output=True, text=True, timeout=320)
        try: os.remove(mp3)
        except: pass
        if r.returncode != 0:
            print(f'[{i+1}/{len(todo)}] FAIL groq {m["title"][:50]} :: {r.stderr[:100]} {r.stdout[:100]}')
            fail += 1
            if 'rate' in (r.stdout + r.stderr).lower() or '429' in (r.stdout + r.stderr):
                consec_rl += 1
                if consec_rl >= 5:
                    print(f'quota dead ({consec_rl} consecutive rate-limits), aborting run — will retry next cron')
                    break
                print('rate-limited, sleeping 60s')
                time.sleep(60)
            else:
                time.sleep(sleep_s)
            continue
        text = r.stdout.strip()
        if len(text) < 5:
            print(f'[{i+1}/{len(todo)}] EMPTY {m["title"][:50]}')
            fail += 1
            time.sleep(sleep_s)
            continue
        meta = {'id': mid, 'title': m['title'], 'duration_minutes': m.get('duration_minutes')}
        with open(out, 'w', encoding='utf-8') as f:
            f.write(json.dumps(meta, ensure_ascii=False) + '\n' + text)
        done += 1
        consec_rl = 0
        print(f'[{i+1}/{len(todo)}] OK ({len(text)}ch) {m["title"][:50]}')
    except subprocess.TimeoutExpired:
        print(f'[{i+1}/{len(todo)}] TIMEOUT {m["title"][:50]}')
        fail += 1
        try: os.remove(mp3)
        except: pass
    except Exception as e:
        print(f'[{i+1}/{len(todo)}] ERR {m["title"][:50]} :: {e}')
        fail += 1
    time.sleep(sleep_s)

print(f'DONE new={done} skipped={skip} failed={fail}')
