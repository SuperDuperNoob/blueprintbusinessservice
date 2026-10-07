import urllib.request, json

d = json.load(open('/root/blueprintbusinessservice/bbs_data.json'))
mods = d['Module']
# shortest videos first
mods_sorted = sorted([m for m in mods if m.get('video_url')], key=lambda m: m.get('duration_minutes') or 99)
for m in mods_sorted[:5]:
    print(m['duration_minutes'], 'min |', m['title'], '|', m['video_url'], '| thumb:', m['thumbnail_url'])
