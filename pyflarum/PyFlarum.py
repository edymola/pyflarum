import requests

END_POINTS = {
    "Login":"/api/token",
    "Forum": "/api/forum",
    "Discussions": "/api/discussions",
    "Post": "/api/posts",
    "Users": "/api/users",
    "Groups": "/api/groups",
    "Notifications": "/api/notifications",
    "Tags": "/api/tags",
}
# Cuentas
DEFAULT_TAG = 28
# Cookie
DEFAULT_COOKIE = {"Cookie": "DefaultCookie"}


class PyFlarum:

    def __init__(self, base_url, username=None, password=None, cookies=None):
        self.base_url = base_url
        self.cookies = cookies
        self.__get_token(username, password)
        # Tamien se puede usar bearer
        self.headers = {"Authorization": f"Token {self.token}"}

    def __get_token(self, username, password):
        url = self.base_url + END_POINTS["Login"]
        data = {
            "identification": username,
            "password": password
        }
        response = requests.post(url, json=data, cookies=self.cookies)
        if response.status_code not in (200,201):
            raise pyflarum_Bad_Credentials
        else:
            self.token, self.user_id = response.json().values()


    # TODO Estaria bien juntar todo esto en uno y que te devolviera directamente el json

    def _pyflarum_post(self, endpoint, data):
        url = self.base_url + endpoint
        response = requests.post(url, headers=self.headers, json=data, cookies=self.cookies)
        if response.status_code not in (200, 201):
            raise pyflarumBadRequest
        else:
            return response

    def _pyflarum_get(self, endpoint):
        url = self.base_url + endpoint
        response = requests.get(url, headers=self.headers, cookies=self.cookies)
        if response.status_code not in (200, 201):
            raise pyflarumBadRequest
        else:
            return response

    def _pyflarum_patch(self, endpoint, data):
        url = self.base_url + endpoint
        response = requests.patch(url, headers=self.headers, json=data, cookies=self.cookies)
        if response.status_code not in (200, 201):
            raise pyflarumBadRequest
        else:
            return response


class User(PyFlarum):
    def __init__(self, base_url, username=None, password=None, cookies=None):
        super().__init__(base_url, username, password, cookies)
        self.__update_stats()

    def get_stats(self, Update=True):
        if Update:
            self.__update_stats()

        return self.stats

    def __update_stats(self):
        response = super()._pyflarum_get(f'{END_POINTS["Users"]}/{self.user_id}')
        if response.status_code == 200:
            self.stats = response.json()
            self.attributes = self.stats['data']['attributes']
            self.discussionsCount = self.attributes['discussionsCount']


class Discussion(PyFlarum):
    def __init__(self,
                 base_url, tittle, description, username=None, password=None, tags_id=(DEFAULT_TAG,),
                 cookies=None):
        super().__init__(base_url, username, password, cookies)
        self.__tittle = tittle
        self.description = description
        self.tags_id = tags_id
        self.discussion_id = None
        self.first_post_id = None

    def get_string(self):
        arra_tags = []
        for tag_id in self.tags_id:
            arra_tags.append({
                "type": "tags",
                "id": tag_id})
        string = {
            "data": {
                "type": "discussions",
                "attributes": {
                    "title": self.__tittle,
                    "content": self.description
                },
                "relationships": {
                    "tags": {
                        "data": arra_tags
                    }
                }
            }
        }
        return string

    def create_discussion(self):
        try:
            response = super()._pyflarum_post(END_POINTS['Discussions'], self.get_string())
            self.discussion_id = response.json().get('data').get('id')
            self.first_post_id = response.json().get('data').get('relationships').get('startPost').get('data').get('id')
            print("Created discussion")
            return True
        except pyflarumBadRequest:
            print(f"Error creating the discusion {response.text}")
            return False

    def post_discussion(self, context_to_post):
        data = {
            "data": {
                "type": "posts",
                "attributes": {
                    "content": context_to_post
                },
                "relationships": {
                    "discussion": {
                        "data": {
                            "type": "discussions",
                            "id": self.discussion_id
                        }
                    }
                }
            }
        }
        try:
            super()._pyflarum_post(END_POINTS['Post'], data)
            print("Post discussion")
            return True
        except pyflarumBadRequest:
            print("Couldn't post")

    # Fixme Ponerlo mas bonito
    def get_first_post(self):
        endpoint = END_POINTS['Post'] + f"/{self.first_post_id}"
        response = super()._pyflarum_get(endpoint)
        context = response.json().get('data').get('attributes').get('content')
        post = Post(self.base_url, context, self.first_post_id, token=self.token)
        return post

    # TODO
    def update_discussion(self):

        return


# Todo hacer un post hijo de Discussion

class Post(PyFlarum):

    def __init__(self,
                 base_url, context, post_id, username=None, password=None, cookies=None):
        super().__init__(base_url, username, password, cookies)
        self.context = context
        self.post_id = post_id

    def __gen_context(self):
        context = {
            "data": {
                "attributes": {
                    "content": self.context
                }
            }
        }
        return context

    def update_post(self):
        endpoint = END_POINTS['Post'] + f"/{self.post_id}"
        try:
            super()._pyflarum_patch(endpoint, self.__gen_context())
            print("Post updated")
            return True
        except pyflarumBadRequest:
            print("Couldn't update")
            return False


class pyflarumBadRequest(Exception):
    """Salta cuando  hay una bad requests"""
    pass
class pyflarum_Bad_Credentials(Exception):
    """Salta """
    pass
