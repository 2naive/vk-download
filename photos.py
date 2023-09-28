import urllib.request, json, os, sys, time, re
from datetime import datetime

V = "5.131"
if len( sys.argv ) < 2:
    print("python3 photos.py TOKEN [UID]")
    print("# TOKEN howto: https://github.com/2naive/vk-download/tree/master#readme")
    # https://oauth.vk.com/authorize?client_id=51756670&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=friends,photos,video&response_type=token&v=5.131&state=123456
    sys.exit()

TOKEN = sys.argv[1]
if len( sys.argv ) > 2:
    UID = int(sys.argv[2])
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
    with urllib.request.urlopen(f"https://api.vk.com/method/photos.getAlbums?access_token={token}&owner_id={uid}&v={V}&extended=1&photo_sizes=1&need_system=1&need_covers=1&count=200") as url:
        data = json.load(url)
        if "error" in data:
            print(f"— Error @photos.getAlbums {data['error']['error_code']}: {data['error']['error_msg']}")
            return
        albums = data['response']['items']
        path = f"{path}/Photo_{UID}"
        if not os.path.exists(path):
            os.mkdir(path)
        print(path)
        with open(f"{path}/{UID}.albums.json", 'w', encoding='utf-8') as f:
            json.dump(albums, f, ensure_ascii=False, indent=2)

        for album in albums:
            if album['id'] < -1000:
                continue
            dump_photos(TOKEN, album['id'], path+'/'+re.sub(r'[^\w]+', '_', album['title'])+'_'+str(album['id']))

def dump_photos(token, album_id, path=".", offset=0):
    time.sleep(0.25) # https://dev.vk.com/ru/api/api-requests#%D0%A7%D0%B0%D1%81%D1%82%D0%BE%D1%82%D0%BD%D1%8B%D0%B5%20%D0%BE%D0%B3%D1%80%D0%B0%D0%BD%D0%B8%D1%87%D0%B5%D0%BD%D0%B8%D1%8F
    with urllib.request.urlopen(f"https://api.vk.com/method/photos.get?access_token={token}&album_id={album_id}&v={V}&extended=1&photo_sizes=1&count=200&offset={offset}") as url:
        data = json.load(url)
        if "error" in data:
            print(f"— Error @photos.get {data['error']['error_code']}: {data['error']['error_msg']}")
            return
        photos = data['response']['items']
        count = data['response']['count'] if data['response']['count'] < 200 else 200
        total = data['response']['count']
        print(f"{path}: {offset+count}/{total}")
        with open(f"{path}.photos.json", 'w', encoding='utf-8') as f:
            json.dump(photos, f, ensure_ascii=False, indent=2)
        for photo in photos:
            fname = f"{datetime.utcfromtimestamp(photo['date']).strftime('%Y%m%d')}_{photo['id']}"
            print(f"{path}/{fname}")
            if not os.path.exists(f"{path}"):
                os.mkdir(f"{path}")
            photo['sizes'].sort(key = lambda photo: photo['type'], reverse=True)
            try:
                photo_url = photo['sizes'][0]['url']
                for size in photo['sizes']:
                    if size['type'] == "w":
                        photo_url = size['url']
                time.sleep(0.25) # https://dev.vk.com/ru/api/api-requests#%D0%A7%D0%B0%D1%81%D1%82%D0%BE%D1%82%D0%BD%D1%8B%D0%B5%20%D0%BE%D0%B3%D1%80%D0%B0%D0%BD%D0%B8%D1%87%D0%B5%D0%BD%D0%B8%D1%8F
                urllib.request.urlretrieve(photo_url, f"{path}/{fname}.jpg")
            except:
                print('[x] No photo')
    if offset+count<total:
        offset+=200
        dump_photos(token, album_id, path, offset)

dump_albums(TOKEN, UID)