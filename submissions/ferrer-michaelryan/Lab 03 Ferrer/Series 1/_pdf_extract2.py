"""Extract text and embedded JPEG images from a PDF using only the stdlib."""
import re, zlib, os

PDF = r'c:\Users\Mayk\OneDrive\Desktop\html\figures\Series1.pdf'
outdir = r'c:\Users\Mayk\OneDrive\Desktop\html\_extracted'
os.makedirs(outdir, exist_ok=True)

data = open(PDF, 'rb').read()
print('PDF size:', len(data))

# ---------- decompress all FlateDecode streams ----------
# split on b'stream\r?\n' ... b'endstream'
parts = re.split(b'(stream\r?\n|stream\r?\n|endstream)', data)
streams = []
for i, chunk in enumerate(parts):
    if chunk == b'stream\n' or chunk == b'stream\r\n':
        j = i + 1
        if j < len(parts) - 1:
            payload = parts[j]
            # remove trailing newline before 'endstream'
            if payload.endswith(b'\n'):
                payload = payload[:-1]
            streams.append(payload)

print('num stream objects:', len(streams))
text_parts = []
img_count = 0
for s in streams:
    try:
        d = zlib.decompress(s)
    except Exception:
        d = None
    if d is None:
        # maybe uncompressed (rare) -> try with leading whitespace stripped
        try:
            d = zlib.decompress(s.lstrip(b'\x00\x01\x02'))
        except Exception:
            d = None
    if d is None:
        continue
    # JPEG? check for start marker FFD8FF
    if d[:3] == b'\xff\xd8\xff':
        img_count += 1
        fn = os.path.join(outdir, f'img_{img_count}.jpg')
        open(fn, 'wb').write(d)
        print('wrote', fn, len(d), 'bytes')
        continue
    # textual content stream: capture text in (...) Tj / TJ
    for m in re.finditer(rb'\((?:[^()\\]|\\.)*\)\s*Tj|\[(?:[^\]\\]|\\.)*\]\s*TJ', d):
        text_parts.append(d[max(0, m.start()-200):m.end()+200])

if text_parts:
    print('\n===== TEXT SNIPPETS FOUND IN STREAMS =====')
    seen = set()
    for t in text_parts:
        try:
            txt = t.decode('latin-1')
        except Exception:
            continue
        if txt not in seen:
            seen.add(txt)
            print('----')
            print(txt)
else:
    print('\nno (..)Tj / [..]TJ text found in decompressed streams')

# also search for JPEG images embedded raw (not necessarily in flate streams)
jpegs = re.findall(b'\xff\xd8\xff[\x00-\xff]*?\xff\xd9', data)
for i, j in enumerate(jpegs, start=img_count+1):
    fn = os.path.join(outdir, f'img_{i}.jpg')
    open(fn, 'wb').write(j)
    print('raw jpeg ->', fn, len(j), 'bytes')
print('DONE')