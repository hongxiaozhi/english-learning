#!/usr/bin/env python3
"""CET-6 Audio Player - scan audio files and open HTML player in browser."""

import os
import sys
import base64
import webbrowser
import tempfile

AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "exam-pdfs", "CET-6")
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}


def scan_audios(folder):
    """Scan all audio files recursively."""
    audios = []
    for root, dirs, files in os.walk(folder):
        dirs.sort()
        for f in sorted(files):
            if os.path.splitext(f)[1].lower() in AUDIO_EXTS:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, folder)
                audios.append((rel, full))
    return audios


def generate_html(audios):
    """Generate HTML player with embedded audio."""
    items = []
    for rel, full in audios:
        ext = os.path.splitext(full)[1].lower()
        mime = {
            ".mp3": "audio/mpeg", ".wav": "audio/wav",
            ".m4a": "audio/mp4", ".aac": "audio/aac",
            ".flac": "audio/flac", ".ogg": "audio/ogg",
        }.get(ext, "audio/mpeg")
        with open(full, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        items.append({"name": rel, "data": f"data:{mime};base64,{b64}"})

    items_json = str(items).replace("'", '"')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CET-6 Listening Practice</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, sans-serif; background: #1a1a2e; color: #eee; padding: 20px; max-width: 650px; margin: 0 auto; }}
  h1 {{ font-size: 20px; margin-bottom: 16px; color: #e0e0e0; }}
  select {{ width: 100%; padding: 10px; font-size: 14px; margin-bottom: 16px; border-radius: 6px; border: 1px solid #444; background: #16213e; color: #eee; }}

  /* Progress bar */
  .progress-wrap {{ position: relative; margin-bottom: 8px; }}
  .progress-bar {{ width: 100%; height: 8px; background: #333; border-radius: 4px; cursor: pointer; position: relative; overflow: visible; }}
  .progress-fill {{ height: 100%; background: #4A90D9; border-radius: 4px; width: 0%; transition: width 0.3s; }}
  .section-markers {{ position: relative; height: 24px; margin-top: 2px; }}
  .section-marker {{ position: absolute; top: 0; font-size: 10px; color: #aaa; transform: translateX(-50%); cursor: pointer; white-space: nowrap; }}
  .section-marker:hover {{ color: #4A90D9; }}
  .section-marker::before {{ content: ''; position: absolute; top: -10px; left: 50%; width: 1px; height: 8px; background: #666; }}

  .time-display {{ display: flex; justify-content: space-between; font-size: 12px; color: #888; margin-bottom: 12px; }}

  /* Controls */
  .controls {{ display: flex; gap: 8px; margin-bottom: 12px; align-items: center; }}
  button {{ padding: 8px 18px; font-size: 14px; border: none; border-radius: 6px; cursor: pointer; transition: all 0.2s; }}
  button:active {{ transform: scale(0.96); }}
  .btn-play {{ background: #4A90D9; color: white; min-width: 70px; }}
  .btn-play:hover {{ background: #357ABD; }}
  .btn-pause {{ background: #f0ad4e; color: white; min-width: 70px; }}
  .btn-pause:hover {{ background: #ec971f; }}
  .btn-stop {{ background: #d9534f; color: white; }}
  .btn-stop:hover {{ background: #c9302c; }}
  .btn-rw {{ background: #555; color: #ddd; }}
  .btn-rw:hover {{ background: #666; }}
  .btn-speed {{ background: #333; color: #ccc; font-size: 12px; padding: 6px 10px; }}
  .btn-speed.active {{ background: #4A90D9; color: white; }}
  .speed-group {{ display: flex; gap: 4px; margin-bottom: 12px; align-items: center; }}
  .speed-label {{ font-size: 12px; color: #888; margin-right: 4px; }}

  .status {{ font-size: 13px; color: #888; margin-bottom: 12px; min-height: 20px; }}
  .hint {{ font-size: 11px; color: #666; margin-bottom: 12px; }}

  textarea {{ width: 100%; height: 150px; font-size: 15px; padding: 12px; border-radius: 6px; border: 1px solid #444; background: #16213e; color: #eee; resize: vertical; font-family: inherit; }}
  textarea:focus {{ outline: none; border-color: #4A90D9; }}

  .btn-done {{ background: #4CAF50; color: white; font-weight: bold; padding: 10px 24px; }}
  .btn-done:hover {{ background: #45a049; }}
  .btn-clear {{ background: #555; color: #ccc; }}
  .btn-clear:hover {{ background: #666; }}
  .done-row {{ margin-top: 12px; display: flex; gap: 8px; }}
  .msg {{ background: #1b4332; padding: 12px; border-radius: 6px; margin-top: 12px; display: none; font-size: 14px; color: #95d5b2; }}
</style>
</head>
<body>
<h1>CET-6 Listening Practice</h1>
<select id="fileSelect" onchange="loadAudio()"><option>-- Select audio --</option></select>

<!-- Progress bar -->
<div class="progress-wrap">
  <div class="progress-bar" id="progressBar" onclick="seekTo(event)">
    <div class="progress-fill" id="progressFill"></div>
  </div>
  <div class="section-markers" id="sectionMarkers"></div>
</div>
<div class="time-display">
  <span id="currentTime">0:00</span>
  <span id="totalTime">0:00</span>
</div>

<!-- Controls -->
<div class="controls">
  <button class="btn-play" id="btnPlay" onclick="togglePlay()">Play</button>
  <button class="btn-rw" onclick="rewind()">-5s</button>
  <button class="btn-rw" onclick="forward()">+5s</button>
  <button class="btn-stop" onclick="stopAudio()">Stop</button>
</div>
<div class="speed-group">
  <span class="speed-label">Speed:</span>
  <button class="btn-speed" onclick="setSpeed(0.5)" data-speed="0.5">0.5x</button>
  <button class="btn-speed" onclick="setSpeed(0.75)" data-speed="0.75">0.75x</button>
  <button class="btn-speed active" onclick="setSpeed(1)" data-speed="1">1x</button>
  <button class="btn-speed" onclick="setSpeed(1.25)" data-speed="1.25">1.25x</button>
</div>
<div class="status" id="status"></div>
<div class="hint">Space = Play/Pause | &larr; = -5s | &rarr; = +5s</div>

<textarea id="input" placeholder="Type what you hear here..."></textarea>
<div class="done-row">
  <button class="btn-done" onclick="done()">Done - Copy to Chat</button>
  <button class="btn-clear" onclick="clearText()">Clear</button>
</div>
<div class="msg" id="msg">Copied! Go back to chat and paste (Cmd+V).</div>

<audio id="audio"></audio>
<script>
const items = {items_json};
const sel = document.getElementById('fileSelect');
const audio = document.getElementById('audio');
const statusEl = document.getElementById('status');
const progressBar = document.getElementById('progressBar');
const progressFill = document.getElementById('progressFill');
const sectionMarkers = document.getElementById('sectionMarkers');
const btnPlay = document.getElementById('btnPlay');

// CET-6 typical sections
const defaultSections = [
  {{ name: 'A1 News', pct: 0 }},
  {{ name: 'A2 News', pct: 12 }},
  {{ name: 'A3 News', pct: 24 }},
  {{ name: 'B1 Conv', pct: 40 }},
  {{ name: 'B2 Conv', pct: 55 }},
  {{ name: 'C1 Pass', pct: 70 }},
  {{ name: 'C2 Pass', pct: 82 }},
  {{ name: 'C3 Pass', pct: 94 }},
];

let sections = defaultSections;
let duration = 0;

// Load audio list
items.forEach((item, i) => {{
  const opt = document.createElement('option');
  opt.value = i;
  opt.textContent = item.name;
  sel.appendChild(opt);
}});
if (items.length > 0) {{ sel.value = 0; loadAudio(); }}

function loadAudio() {{
  const i = sel.value;
  if (i >= 0 && items[i]) {{
    audio.src = items[i].data;
    statusEl.textContent = 'Loaded: ' + items[i].name;
    progressFill.style.width = '0%';
    document.getElementById('currentTime').textContent = '0:00';
  }}
}}

audio.addEventListener('loadedmetadata', () => {{
  duration = audio.duration;
  document.getElementById('totalTime').textContent = formatTime(duration);
  renderSections();
}});

audio.addEventListener('timeupdate', () => {{
  if (duration > 0) {{
    const pct = (audio.currentTime / duration) * 100;
    progressFill.style.width = pct + '%';
    document.getElementById('currentTime').textContent = formatTime(audio.currentTime);
  }}
}});

audio.addEventListener('ended', () => {{
  btnPlay.textContent = 'Play';
  btnPlay.className = 'btn-play';
  statusEl.textContent = 'Ended.';
}});

function renderSections() {{
  sectionMarkers.innerHTML = '';
  sections.forEach(s => {{
    const el = document.createElement('span');
    el.className = 'section-marker';
    el.style.left = s.pct + '%';
    el.textContent = s.name;
    el.onclick = () => {{ audio.currentTime = duration * s.pct / 100; }};
    sectionMarkers.appendChild(el);
  }});
}}

function formatTime(s) {{
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  return m + ':' + (sec < 10 ? '0' : '') + sec;
}}

function togglePlay() {{
  if (audio.paused) {{
    audio.play();
    btnPlay.textContent = 'Pause';
    btnPlay.className = 'btn-pause';
    statusEl.textContent = 'Playing...';
  }} else {{
    audio.pause();
    btnPlay.textContent = 'Play';
    btnPlay.className = 'btn-play';
    statusEl.textContent = 'Paused at ' + formatTime(audio.currentTime);
  }}
}}

function stopAudio() {{
  audio.pause();
  audio.currentTime = 0;
  btnPlay.textContent = 'Play';
  btnPlay.className = 'btn-play';
  statusEl.textContent = 'Stopped.';
  progressFill.style.width = '0%';
}}

function rewind() {{
  audio.currentTime = Math.max(0, audio.currentTime - 5);
  statusEl.textContent = formatTime(audio.currentTime);
}}

function forward() {{
  audio.currentTime = Math.min(duration, audio.currentTime + 5);
  statusEl.textContent = formatTime(audio.currentTime);
}}

function seekTo(e) {{
  const rect = progressBar.getBoundingClientRect();
  const pct = (e.clientX - rect.left) / rect.width;
  audio.currentTime = duration * pct;
}}

function setSpeed(s) {{
  audio.playbackRate = s;
  document.querySelectorAll('.btn-speed').forEach(b => {{
    b.classList.toggle('active', parseFloat(b.dataset.speed) === s);
  }});
  statusEl.textContent = 'Speed: ' + s + 'x';
}}

function clearText() {{
  document.getElementById('input').value = '';
  document.getElementById('input').focus();
}}

function done() {{
  const text = document.getElementById('input').value.trim();
  if (!text) {{ alert('Please type what you hear first!'); return; }}
  navigator.clipboard.writeText(text).then(() => {{
    document.getElementById('msg').style.display = 'block';
  }});
}}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {{
  if (e.target.tagName === 'TEXTAREA' || e.target.tagName === 'INPUT') return;
  if (e.code === 'Space') {{ e.preventDefault(); togglePlay(); }}
  else if (e.code === 'ArrowLeft') {{ e.preventDefault(); rewind(); }}
  else if (e.code === 'ArrowRight') {{ e.preventDefault(); forward(); }}
}});
</script>
</body>
</html>"""


def main():
    if not os.path.isdir(AUDIO_DIR):
        print(f"Folder not found: {AUDIO_DIR}")
        sys.exit(1)

    audios = scan_audios(AUDIO_DIR)
    if not audios:
        print(f"No audio files found in {AUDIO_DIR}")
        sys.exit(1)

    print(f"Found {len(audios)} audio file(s):")
    for i, (rel, _) in enumerate(audios, 1):
        print(f"  {i}. {rel}")

    html = generate_html(audios)
    tmp = tempfile.mktemp(suffix=".html")
    with open(tmp, "w") as f:
        f.write(html)

    print(f"\nOpening player in browser...")
    webbrowser.open("file://" + tmp)
    print("After practice, click 'Done' and paste text in chat.")


if __name__ == "__main__":
    main()
