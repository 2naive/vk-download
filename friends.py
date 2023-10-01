import urllib.request, json, os, sys, time, re

V = "5.131"
DELAY = 1.01 # https://dev.vk.com/ru/api/api-requests#%D0%A7%D0%B0%D1%81%D1%82%D0%BE%D1%82%D0%BD%D1%8B%D0%B5%20%D0%BE%D0%B3%D1%80%D0%B0%D0%BD%D0%B8%D1%87%D0%B5%D0%BD%D0%B8%D1%8F

if len( sys.argv ) < 3:
    print("python3 friends.py TOKEN UID [DEPTH=1]")
    print("# TOKEN howto: https://github.com/2naive/vk-download/tree/master#readme")
    # https://oauth.vk.com/authorize?client_id=51756670&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=friends,photos,video,wall&response_type=token&v=5.131&state=123457
    sys.exit()
TOKEN = sys.argv[1]
UID = sys.argv[2]
LIMIT = 1 if len( sys.argv ) < 4 else int(sys.argv[3])

TOKEN_MASKED = "{}...{}".format(TOKEN[0:12], TOKEN[-8:])
print(f"Started: TOKEN={TOKEN_MASKED} UID={UID}")

def dump_user(uid, path="."):
    level = path.count('/') + 1

    # print(f"Level: {level}")
    if (level>LIMIT):
        print("Limited: {level}/{LIMIT}")
        unlock(path)
        return

    if not os.path.exists(path):
        os.mkdir(path)

    if level > 1:
        if not lock(path, uid):
            return

    time.sleep(DELAY)
    with urllib.request.urlopen(f"https://api.vk.com/method/users.get?access_token={TOKEN}&user_id={uid}&v={V}&order=name&fields=activities,about,blacklisted,blacklisted_by_me,books,bdate,can_be_invited_group,can_post,can_see_all_posts,can_see_audio,can_send_friend_request,can_write_private_message,career,common_count,connections,contacts,city,country,crop_photo,domain,education,exports,followers_count,friend_status,has_photo,has_mobile,home_town,photo_100,photo_200,photo_200_orig,photo_400_orig,photo_50,sex,site,schools,screen_name,status,verified,games,interests,is_favorite,is_friend,is_hidden_from_feed,last_seen,maiden_name,military,movies,music,nickname,occupation,online,personal,photo_id,photo_max,photo_max_orig,quotes,relation,relatives,timezone,tv,universities&count=") as url:
        data = json.load(url)
        if "error" in data:
            print(f"— Error @users.get {data['error']['error_code']}: {data['error']['error_msg']}")
            if data['error']['error_code'] in [29,5]:
                sys.exit()
            unlock(path)
            return
        profile = data['response'][0]
        fname = re.sub(r'[^\w]+', '_', profile['first_name']) + '_' + re.sub(r'[^\w]+', '_', profile['last_name']) + '_' + str(profile['id'])
        print(f"{path}/{fname}")
        with open(f"{path}/{fname}.profile.json", 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
        try:
            time.sleep(DELAY)
            urllib.request.urlretrieve(profile['photo_max_orig'], f"{path}/{fname}.jpg")
        except:
            print('[x] No photo')

    time.sleep(DELAY)
    with urllib.request.urlopen(f"https://api.vk.com/method/friends.get?access_token={TOKEN}&user_id={uid}&v={V}&order=name&fields=bdate,can_post,can_see_all_posts,can_write_private_message,city,contacts,country,domain,education,has_mobile,timezone,last_seen,nickname,online,photo_100,photo_200_orig,photo_50,relation,sex,status,universities&count=") as url:
        data = json.load(url)
        if "error" in data:
            print(f"— Error @friends.get {data['error']['error_code']}: {data['error']['error_msg']}")
            if data['error']['error_code'] in [29,5]:
                sys.exit()
            unlock(path)
            return
        friends = data['response']['items']
        # print(json.dumps(friends, sort_keys=True, indent=2, ensure_ascii=False))
        with open(f"{path}/{fname}.friends.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        if level<LIMIT:
            print(f"{path}/{fname}: {len(friends)}")
            for friend in friends:
                dump_user(friend['id'], f"{path}/{fname}")
        unlock(path)

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

dump_user(UID)