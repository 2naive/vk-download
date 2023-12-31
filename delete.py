import urllib.request, json, os, sys, time, re
from datetime import datetime

V = "5.131"
TYPES = ['video', 'photos', 'wall', 'friends']
DELAY = 0.25 # https://dev.vk.com/ru/api/api-requests#%D0%A7%D0%B0%D1%81%D1%82%D0%BE%D1%82%D0%BD%D1%8B%D0%B5%20%D0%BE%D0%B3%D1%80%D0%B0%D0%BD%D0%B8%D1%87%D0%B5%D0%BD%D0%B8%D1%8F
OFFSET_MAX = 20

if len( sys.argv ) < 2:
    print(f"python3 delete.py [{'|'.join(TYPES)}]")
    print("# Help: https://github.com/2naive/vk-download/tree/master#readme")
    # https://oauth.vk.com/authorize?client_id=51756670&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=friends,photos,video&response_type=token&v=5.131&state=123456
    sys.exit()

TOKEN = sys.argv[1]

with urllib.request.urlopen(f"https://api.vk.com/method/users.get?access_token={TOKEN}&v={V}") as url:
    data = json.load(url)
    if "error" in data:
        print(f"— Error @users.get {data['error']['error_code']}: {data['error']['error_msg']}")
        sys.exit()
    UID = data['response'][0]['id']

TOKEN_MASKED = "{}...{}".format(TOKEN[0:12], TOKEN[-8:])
print(f"Started: TOKEN={TOKEN_MASKED} UID={UID}")

def delete_video(token):
    delete_items(token, 'video.get', 'video.delete', 'video')
    delete_items(token, 'video.getAlbums', 'video.deleteAlbum', 'album')

def delete_photos(token):
    delete_items(token, 'photos.getAll', 'photos.delete', 'photo')
    delete_items(token, 'photos.getAlbums', 'photos.deleteAlbum', 'album')

def delete_wall(token):
    delete_items(token, 'wall.get', 'wall.delete', 'post')

def delete_friends(token):
    delete_items(token, 'friends.get', 'friends.delete', 'user')
    delete_items(token, 'friends.getRequests', 'friends.delete', 'user')
    delete_items(token, 'friends.deleteAllRequests', 'friends.delete', 'user')
    delete_items(token, 'users.getFollowers', 'friends.delete', 'user')

def delete_items(token, method_list, method_delete, item_name, offset=OFFSET_MAX):
    time.sleep(DELAY)
    with urllib.request.urlopen(f"https://api.vk.com/method/{method_list}?access_token={token}&v={V}&count={offset}") as url:
        data = json.load(url)
        if "error" in data:
            print(f"— Error @{method_list} {data['error']['error_code']}: {data['error']['error_msg']}")
            sys.exit()
            return
        if method_list == 'friends.deleteAllRequests':
            print(f"All friend requests deleted")
            return
        items = data['response']['items']
        count = data['response']['count']
        print(f"Deleting {item_name}: {offset}/{count}")
        i=0
        for item in items:
            i+=1
            time.sleep(DELAY)
            item_id = item if method_delete == 'friends.delete' else item['id']
            with urllib.request.urlopen(f"https://api.vk.com/method/{method_delete}?access_token={token}&v={V}&{item_name}_id={item_id}") as url:
                data = json.load(url)
                if "error" in data:
                    print(f"— Error @{method_delete} {data['error']['error_code']}: {data['error']['error_msg']}")
                    sys.exit()
                    return
                print(f"[{i}] {item_id}")
        if offset < count:
            delete_items(token, method_list, method_delete, item_name, offset)
if len( sys.argv ) < 3:
    for item in TYPES:
        globals()[f"delete_{item}"](TOKEN)
else:
    CMD = sys.argv[2]
    globals()[f"delete_{CMD}"](TOKEN)