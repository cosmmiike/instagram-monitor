import json
import codecs
import re
from instagram_private_api import Client
from instagram_web_api import Client as Client_web


def user_id_to_username(api: Client, id: int) -> dict:
    """Translate user id into username"""
    return api.user_info(id)['user']['username']


def username_to_user_id(api: Client, username: str) -> dict:
    """Translate username into user id"""
    return api.username_info(username)['user']['pk']


def self_info(api: Client) -> dict:
    """Get current user info"""
    return api.current_user()


def user_info(api: Client, username: str) -> dict:
    """Get user info for a specified username"""
    user_id = username_to_user_id(api, username)
    return api.user_info(user_id)


def get_stories(api: Client, username: str) -> dict:
    user_id = username_to_user_id(api, username)
    reels = api.reels_media([user_id])['reels']
    if str(user_id) in reels:
        return reels[str(user_id)]
    return None


def get_posts(api: Client, username: str) -> dict:
    """Get the feed for a specified user username"""
    user_id = username_to_user_id(api, username)
    return api.user_feed(user_id)


def get_highligts(api: Client, username: str) -> dict:
    user_id = username_to_user_id(api, username)
    return api.highlights_user_feed(user_id)


def get_followings(api: Client, username: str) -> dict:
    """Get user followings"""
    user_id = username_to_user_id(api, username)
    rank_token = Client.generate_uuid()
    followings = api.user_following(user_id, rank_token)
    return followings


def get_stories_tray(api: Client) -> dict:
    return api.reels_tray()


def get_feed(api: Client) -> dict:
    return api.feed_timeline()


def get_post_info(web_api: Client, shortcode: str) -> dict:
    return web_api.media_info2(shortcode)


def link_to_shortcode(link: str) -> bool:
    res = re.search('(?<=instagram.com/p/)[\d\w-]+', link);
    if res is not None:
        return res.group(0)


def link_to_username(link: str) -> bool:
    res = re.search('(?<=instagram.com/)[\d\w.-]+', link);
    if res is not None:
        return res.group(0)


def to_json(python_object):
    if isinstance(python_object, bytes):
        return {'__class__': 'bytes',
                '__value__': codecs.encode(python_object, 'base64').decode()}
    raise TypeError(repr(python_object) + ' is not JSON serializable')


def from_json(json_object):
    if '__class__' in json_object and json_object['__class__'] == 'bytes':
        return codecs.decode(json_object['__value__'].encode(), 'base64')
    return json_object


def set_instagram_cookies(username, password):
    try:
        api = Client(username, password)
        web_api = Client_web(auto_patch=True, drop_incompat_keys=False,
                             username='cosmmiike', password='36912desirDESIR')
        cached_settings = json.dumps(api.settings, default=to_json)
        cached_settings_web = json.dumps(web_api.settings, default=to_json)
        print('New settings')
        return cached_settings, cached_settings_web

    except Exception as e:
        print(e)
        if str(e) == 'checkpoint_challenge_required':
            return -1, -1
        return None, None


def get_instagram_api(cached_settings, cached_settings_web):
    try:
        settings = json.loads(cached_settings, object_hook=from_json)
        settings_web = json.loads(cached_settings_web, object_hook=from_json)
        api = Client(username=None, password=None, settings=settings)
        web_api = Client_web(username=None, password=None, settings=settings_web)
        print('Reusing settings')
        return api, web_api

    except Exception as e:
        print(e)
        if str(e) == 'checkpoint_challenge_required':
            return -1, -1
        return None, None


# cached_settings, cached_settings_web = set_instagram_cookies(username = '', password='')
# api, web_api = get_instagram_api(cached_settings, cached_settings_web)
# print('Connection API & WEB API')
#
# xxx = api.current_user()
# username = ''
# user_id = username_to_user_id(api, username)
# shortcode = ''
# yyy = web_api.media_info2(shortcode)
#
# print(json.dumps(xxx))
# with open('test.json', 'w') as f:
#     print(json.dump(yyy, f))
