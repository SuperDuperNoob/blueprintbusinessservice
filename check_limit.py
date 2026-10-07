import subprocess
KEY = [l.strip().split('=', 1)[1] for l in open('/root/.hermes/.env') if l.startswith('GROQ_API_KEY=')][0]
r = subprocess.run(['curl', '-s', '-o', '/dev/null', '-D', '-',
    'https://api.groq.com/openai/v1/audio/transcriptions',
    '-H', f'Authorization: Bearer {KEY}',
    '-F', 'model=whisper-large-v3-turbo', '--max-time', '30'],
    capture_output=True, text=True, timeout=40)
print(r.stdout[-1500:])
