from instagram_private_api import Client


def insta_api(username: str, password: str) -> Client:
    """Get access to instagram api for a specified user"""
    try:
        api = Client(username, password)
        return api
    except Exception as e:
        print(e.code, e)
        if str(e) == "checkpoint_challenge_required":
            return -1
        return None


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


def stories(api: Client) -> dict:
    return api.reels_tray()


# if __name__ == "__main__":
#     api = insta_api('cosmmiike', '31219787q')
#     print(self_info(api))
