import urllib.request, json, os, sys, time, re
from datetime import datetime

V = "5.131"
OFFSET_MAX = 100

if len( sys.argv ) < 4:
    print("python3 video.py TOKEN remixnsid remixsid [UID]")
    print("# Help: https://github.com/2naive/vk-download/tree/master#readme")
    # https://oauth.vk.com/authorize?client_id=51756670&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=friends,photos,video&response_type=token&v=5.131&state=123456
    sys.exit()

TOKEN = sys.argv[1]
remixnsid = sys.argv[2]
remixsid = sys.argv[3]
if len( sys.argv ) > 4:
    UID = int(sys.argv[4])

else:
    with urllib.request.urlopen(f"https://api.vk.com/method/users.get?access_token={TOKEN}&v={V}") as url:
        data = json.load(url)
        if "error" in data:
            print(f"— Error @users.get {data['error']['error_code']}: {data['error']['error_msg']}")
            sys.exit()
        UID = data['response'][0]['id']

TOKEN_MASKED = "{}...{}".format(TOKEN[0:12], TOKEN[-8:])
print(f"Started: TOKEN={TOKEN_MASKED} UID={UID}")

def dump_albums(token, uid, path="."):
    time.sleep(0.25)
    level = path.count('/') + 1
    with urllib.request.urlopen(f"https://api.vk.com/method/video.getAlbums?access_token={token}&owner_id={uid}&v={V}&extended=1&need_system=1&count={OFFSET_MAX}") as url:
        data = json.load(url)
        if "error" in data:
            print(f"— Error @video.getAlbums {data['error']['error_code']}: {data['error']['error_msg']}")
            return
        albums = data['response']['items']
        path = f"{path}/Video_{UID}"
        if not os.path.exists(path):
            os.mkdir(path)
        print(path)
        with open(f"{path}/{UID}.albums.json", 'w', encoding='utf-8') as f:
            json.dump(albums, f, ensure_ascii=False, indent=2)

        for album in albums:
            if album['id'] < -1000:
                continue
            if not lock(path, album['id']):
                continue
            dump_videos(TOKEN, album['id'], path+'/'+re.sub(r'[^\w]+', '_', album['title'])+'_'+str(album['id']))
            unlock(path)

def dump_videos(token, album_id, path=".", offset=0):
    time.sleep(0.25) # https://dev.vk.com/ru/api/api-requests#%D0%A7%D0%B0%D1%81%D1%82%D0%BE%D1%82%D0%BD%D1%8B%D0%B5%20%D0%BE%D0%B3%D1%80%D0%B0%D0%BD%D0%B8%D1%87%D0%B5%D0%BD%D0%B8%D1%8F
    with urllib.request.urlopen(f"https://api.vk.com/method/video.get?access_token={token}&album_id={album_id}&v={V}&extended=1&count={OFFSET_MAX}&offset={offset}") as url:
        data = json.load(url)
        if "error" in data:
            print(f"— Error @video.get {data['error']['error_code']}: {data['error']['error_msg']}")
            return
        videos = data['response']['items']
        count = data['response']['count'] if data['response']['count'] < OFFSET_MAX else OFFSET_MAX
        total = data['response']['count']
        print(f"{path}: {offset+count}/{total}")
        with open(f"{path}.videos.json", 'w', encoding='utf-8') as f:
            json.dump(videos, f, ensure_ascii=False, indent=2)
        for video in videos:
            fname = f"{datetime.utcfromtimestamp(video['date']).strftime('%Y%m%d')}_{video['id']}"
            print(f"{path}/{fname}")
            if not os.path.exists(f"{path}"):
                os.mkdir(f"{path}")
            time.sleep(0.25) # https://dev.vk.com/ru/api/api-requests#%D0%A7%D0%B0%D1%81%D1%82%D0%BE%D1%82%D0%BD%D1%8B%D0%B5%20%D0%BE%D0%B3%D1%80%D0%B0%D0%BD%D0%B8%D1%87%D0%B5%D0%BD%D0%B8%D1%8F
            if not lock(path, video['id']):
                continue
            if 'player' in video:
                download_video(video['player'], f"{path}/{fname}")
            else:
                print("[x] No vk video")
            unlock(path)
    if offset+count<total:
        offset+=OFFSET_MAX
        dump_videos(token, album_id, path, offset)

def download_video(url, path):
    print(f"— {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,zh-TW;q=0.5,zh;q=0.4',
        'Cache-Control': 'no-cache',
        'Cookie': f"remixnsid={remixnsid}; remixsid={remixsid};"
    }
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request) as response:
        result =  response.read().decode("cp1251")
        for line in result.splitlines():
            if re.search("var playerParams = ", line):
                # print(line)
                data = json.loads(line[19:-1])
                video_url = ''
                size = ''
                try:
                    data = data['params'][0]
                except:
                    print("[x] No player params")
                # print(json.dumps(data, indent=2))
                # @todo Не работает для dash_sep и hls
                if 'url2160' in data:
                    video_url = data['url2160']
                    size = '2160'
                elif 'url1440' in data:
                    video_url = data['url1440']
                    size = '1440'
                elif 'url1080' in data:
                    video_url = data['url1080']
                    size = '1080'
                elif 'url720' in data:
                    video_url = data['url720']
                    size = '720'
                elif 'url480' in data:
                    video_url = data['url480']
                    size = '480'
                elif 'url360' in data:
                    video_url = data['url360']
                    size = '360'
                elif 'url240' in data:
                    video_url = data['url240']
                    size = '240'
                elif 'url144' in data:
                    video_url = data['url144']
                    size = '144'
                else:
                    print("[x] No video URL")
                if video_url:
                    print(f"— {video_url}")
                    time.sleep(0.25) # https://dev.vk.com/ru/api/api-requests#%D0%A7%D0%B0%D1%81%D1%82%D0%BE%D1%82%D0%BD%D1%8B%D0%B5%20%D0%BE%D0%B3%D1%80%D0%B0%D0%BD%D0%B8%D1%87%D0%B5%D0%BD%D0%B8%D1%8F
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'), ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'), ('Accept-Language', 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,zh-TW;q=0.5,zh;q=0.4'), ('Cache-Control', 'no-cache'), ('Cookie', f"remixnsid={remixnsid}; remixsid={remixsid};")]
                    urllib.request.install_opener(opener)
                    urllib.request.urlretrieve(video_url, f"{path}.{size}.mp4")
                    # print(f"— {path}.{size}.mp4")
    # sys.exit()

def lock(path, uid):
    try:
        f = open(f"{path}/id.lock", "r")
        last_id = int(f.read())
        # print(f"Last ID: {last_id}")
        f.close()
    except FileNotFoundError:
        last_id = 0
    if last_id != 0:
        if uid != last_id:
            print(f"Last ID: {last_id}\tSkipping: {uid}")
            return False
        else:
            return True
    else:
        f = open(f"{path}/id.lock", "w")
        f.write(f"{uid}")
        f.close()
        return True

def unlock(path):
    try:
        os.remove(f"{path}/id.lock")
        # print(f"Removed {path}/id.lock")
    except:
        pass

dump_albums(TOKEN, UID)