#!/usr/bin/env python3
"""Batch transcribe BBS modules via Gemini (free tier, separate quota from Groq).
Same resume-safe .txt format as transcribe_all.py (JSON meta first line).
Rotates across every GEMINI_API_KEY[_N] key on 429. Inline base64 audio (files are small 16k/32k mp3).
Usage: python3 transcribe_gemini.py [--limit N] [--sleep S]
"""
import json, os, sys, time, subprocess, base64, urllib.request, tempfile, glob, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'bbs_data.json')
OUTDIR = os.path.join(BASE, 'transcripts')
os.makedirs(OUTDIR, exist_ok=True)

def get_keys():
    """All GEMINI_API_KEY / GEMINI_API_KEY_<n> entries, deduped, ordered by suffix."""
    found = {}
    for line in open('/root/.hermes/.env', encoding='utf-8', errors='ignore'):
        line = line.strip()
        if not line.startswith('GEMINI_API_KEY'):
            continue
        name, _, val = line.partition('=')
        val = val.strip()
        if not val:
            continue
        sfx = name[len('GEMINI_API_KEY'):]
        n = int(sfx[1:]) if sfx.startswith('_') and sfx[1:].isdigit() else 1
        found[n] = val
    keys, seen = [], set()
    for n in sorted(found):
        if found[n] not in seen:
            seen.add(found[n])
            keys.append(found[n])
    return keys

KEYS = get_keys()
if not KEYS:
    print('no GEMINI keys'); sys.exit(1)
print(f'{len(KEYS)} gemini keys loaded')

# Tried in order per key. Newer Google projects lost access to gemini-2.5-flash
# ("no longer available to new users"), so 3.x is first and 2.5 is the legacy fallback.
# 503 = overloaded, 404 = retired/not entitled -> fall through to the next model.
MODELS = ['gemini-3-flash-preview', 'gemini-3.5-flash', 'gemini-2.5-flash']
MODEL = MODELS[0]
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
    last_err, saw_429 = '', False
    for _ in range(len(KEYS)):
        key = KEYS[ki % len(KEYS)]
        ki += 1
        for model in MODELS:
            try:
                req = urllib.request.Request(
                    f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}',
                    data=payload, headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=300) as r:
                    res = json.load(r)
                parts = res.get('candidates', [{}])[0].get('content', {}).get('parts', [])
                text = ''.join(p.get('text', '') for p in parts).strip()
                if text:
                    return text, ''
                last_err = f'{model}: empty response'
                continue
            except urllib.error.HTTPError as e:
                detail = e.read().decode('utf-8', 'ignore')[:120]
                last_err = f'{model}: {e.code} {detail}'
                if e.code == 429 or 'RESOURCE_EXHAUSTED' in detail:
                    saw_429 = True
                    break          # key is spent -> rotate to the next key
                continue           # 404 retired / 503 overloaded -> next model, same key
            except Exception as e:
                last_err = f'{model}: {type(e).__name__} {str(e)[:80]}'
                continue
    if saw_429:
        return '', f'429 all {len(KEYS)} keys exhausted (last: {last_err})'
    return '', (last_err or 'all keys 429')

def gemini_transcribe_any(mp3_path):
    """Under the inline limit -> single request. Over it -> split into ~30 min
    segments (well under the limit at 32 kbps mono), transcribe each, join."""
    LIMIT = 19000000
    if os.path.getsize(mp3_path) <= LIMIT:
        return gemini_transcribe(mp3_path)
    tmpdir = tempfile.mkdtemp(prefix='bbschunk_')
    try:
        r = subprocess.run(
            ['ffmpeg', '-y', '-loglevel', 'error', '-i', mp3_path,
             '-f', 'segment', '-segment_time', '1800', '-c', 'copy',
             os.path.join(tmpdir, 'part_%03d.mp3')],
            timeout=900)
        parts = [p for p in sorted(glob.glob(os.path.join(tmpdir, 'part_*.mp3')))
                 if os.path.getsize(p) > 1000]  # segment muxer can emit a 0-byte tail
        if r.returncode != 0 or not parts:
            return '', 'chunk split produced nothing'
        chunks = []
        for p in parts:
            t, e = gemini_transcribe(p)
            if not t:
                return '', f'{os.path.basename(p)}: {e}'
            chunks.append(t)
        return ' '.join(chunks), ''
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


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
            print(f'[{i+1}/{len(todo)}] CHUNK >19MB {m["title"][:50]}', flush=True)
        text, err = gemini_transcribe_any(mp3)
        try: os.remove(mp3)
        except Exception: pass
        if not text or len(text) < 5:
            print(f'[{i+1}/{len(todo)}] FAIL gemini {m["title"][:50]} :: {err[:100]}', flush=True)
            fail += 1
            if '429' in err or 'EXHAUSTED' in err:
                consec_rl += 1
                if consec_rl >= 5:
                    print(f'all {len(KEYS)} keys dead ({consec_rl} consecutive 429 sweeps), aborting run — retry next cron', flush=True)
                    break
                print(f'all {len(KEYS)} keys limited, sleeping 120s', flush=True)
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
