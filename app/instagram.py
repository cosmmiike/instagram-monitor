import json
import codecs
from instagram_private_api import Client


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


def get_stories(api: Client) -> dict:
    return api.reels_tray()


def get_feed(api: Client) -> dict:
    return api.feed_timeline()


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
        cached_settings = json.dumps(api.settings, default=to_json)
        print('New settings')
        return cached_settings

    except Exception as e:
        print(e)
        return None


def get_instagram_api(cached_settings):
    try:
        settings = json.loads(cached_settings, object_hook=from_json)
        api = Client(username=None, password=None, settings=settings)
        print('Reusing settings')
        return api

    except Exception as e:
        print(e)
        return None
