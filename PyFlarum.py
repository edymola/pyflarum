import requests

END_POINTS = {
    "Forum": "/forum",
    "Discussions": "/discussions",
    "Post": "/posts",
    "Users": "/users",
    "Groups": "/groups",
    "Notifications": "/notifications",
    "Tags": "/tags",
}
# Cuentas
DEFAULT_TAG = 4


class PyFlarum:

    def __init__(self, base_url, username=None, password=None, token=None):
        self.base_url = base_url
        if username is None or password is None:
            self.token = token
        else:
            self.__get_token(username, password)
        self.headers = {"Authorization": f"Token {self.token}"}

    def __get_token(self, username, password):
        url = self.base_url + "/api/token"
        data = {
            "identification": username,
            "password": password
        }
        self.token, self.user_id = \
            requests.post(url, json=data).json().values()

    def _pyflarum_post(self, endpoint, data):
        url = self.base_url + endpoint
        return requests.post(url, headers=self.headers, json=data)

    def _pyflarum_get(self, endpoint):
        url = self.base_url + endpoint
        return requests.get(url, headers=self.headers)

    def _pyflarum_patch(self, endpoint, data):
        url = self.base_url + endpoint
        return requests.patch(url, headers=self.headers, json=data)


class Discussion(PyFlarum):
    def __init__(self,
                 base_url, tittle, description, username=None, password=None, token=None, tag_id=DEFAULT_TAG):
        super().__init__(base_url, username, password, token)
        self.__tittle = tittle
        self.description = description
        self.tag_id = tag_id
        self.discussion_id = None
        self.first_post_id = None

    def __get_string(self):
        string = {
            "data": {
                "type": "discussions",
                "attributes": {
                    "title": self.__tittle,
                    "content": self.description
                },
                "relationships": {
                    "tags": {
                        "data": [
                            {
                                "type": "tags",
                                "id": self.tag_id
                            }
                        ]
                    }
                }
            }
        }
        return string

    def create_discussion(self):
        response = super()._pyflarum_post(END_POINTS['Discussions'], self.__get_string())
        # print(response.text)
        self.discussion_id = response.json().get('data').get('id')
        self.first_post_id = response.json().get('data').get('relationships').get('startPost').get('data').get('id')
        if response.status_code==201:
            print("Created discussion")
        return response.status_code

    # TODO
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
        response = super()._pyflarum_post(END_POINTS['Post'],data)
        if response.status_code==201:
            print("Post discussion")
        return response.status_code

    # Fixme Ponerlo mas bonito
    def get_first_post(self):
        endpoint = END_POINTS['Post'] + f"/{self.first_post_id}"
        response = super()._pyflarum_get(endpoint)
        context = response.json().get('data').get('attributes').get('content')
        post = Post(self.base_url, context, self.first_post_id, token=self.token)
        return post

    # TODO
    def get_discussion(self):
        return

    # TODO
    def update_discussion(self):
        return


# Todo hacer un post hijo de Discussion

class Post(PyFlarum):

    def __init__(self,
                 base_url, context, post_id, username=None, password=None, token=None, ):
        super().__init__(base_url, username, password, token)
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
        response = super()._pyflarum_patch(endpoint, self.__gen_context())
        # print(response.text)
        if response.status_code==201:
            print("Post updated")
        return response.status_code
