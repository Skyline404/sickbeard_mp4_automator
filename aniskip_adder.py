import sys, os, re, json, tempfile, urllib.request, subprocess

def get_mal_id(title):
    query = '''query ($search: String) { Media (search: $search, type: ANIME) { idMal } }'''
    variables = {'search': title}
    url = "https://graphql.anilist.co"
    req = urllib.request.Request(url, method="POST", headers={'Content-Type': 'application/json', 'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, data=json.dumps({'query': query, 'variables': variables}).encode(), timeout=5) as resp:
            res = json.loads(resp.read().decode())
            if res.get('data') and res['data'].get('Media'): return res['data']['Media']['idMal']
    except: pass
    return None

def process_aniskip(filepath):
    if not filepath.lower().endswith(('.mkv', '.mp4')): return
    filename = os.path.basename(filepath)
    match = re.search(r'(?:\]\s*)?([A-Za-z0-9\s\.\-]+?)\s*-\s*(\d+)', filename)
    if not match: return
    title = match.group(1).strip()
    episode = match.group(2).strip()
    mal_id = get_mal_id(title)
    if not mal_id: return
    skip_url = f"https://api.aniskip.com/v2/skip-times/{mal_id}/{episode}?types=op&types=ed&types=recap&types=mixed-op&types=mixed-ed&episodeLength=0"
    req_skip = urllib.request.Request(skip_url, headers={'User-Agent': 'Mozilla/5.0'})
    
    chapters = []
    try:
        with urllib.request.urlopen(req_skip, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if data.get('found'): chapters = data['results']
    except: return
    if not chapters: return
    
    try:
        dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filepath]).decode().strip())
    except:
        dur = 0.0

    chapters.sort(key=lambda x: x['interval']['startTime'])
    
    fd, path = tempfile.mkstemp(suffix=".txt", prefix="aniskip_")
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(";FFMETADATA1\n\n")
        current_time = 0.0
        for st in chapters:
            start = st['interval']['startTime']
            end = st['interval']['endTime']
            t = st['skipType']
            if t == 'ed': c_type = "Ending"
            elif t == 'op': c_type = "Opening"
            elif t == 'mixed-op': c_type = "Opening"
            elif t == 'mixed-ed': c_type = "Ending"
            else: c_type = "Recap"
            if start - current_time > 1.0:
                f.write(f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={int(current_time*1000)}\nEND={int(start*1000)}\ntitle=Episode\n\n")
            f.write(f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={int(start*1000)}\nEND={int(end*1000)}\ntitle={c_type}\n\n")
            current_time = end
        if dur > current_time + 1.0:
            f.write(f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={int(current_time*1000)}\nEND={int((dur)*1000)}\ntitle=Episode\n\n")
            
    out_file = filepath + ".tmp.mkv"
    subprocess.run(["ffmpeg", "-y", "-i", filepath, "-i", path, "-map_metadata", "1", "-map_chapters", "1", "-map", "0", "-c", "copy", out_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(out_file) and os.path.getsize(out_file) > 0:
        os.replace(out_file, filepath)
    os.remove(path)

def process_path(target_path):
    if os.path.isfile(target_path): process_aniskip(target_path)
    elif os.path.isdir(target_path):
        for root, _, files in os.walk(target_path):
            for f in files: process_aniskip(os.path.join(root, f))

if __name__ == "__main__":
    if len(sys.argv) > 1: process_path(sys.argv[1])
