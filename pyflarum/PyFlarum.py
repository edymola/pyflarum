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
        url = self.base_url + "/api/token"
        data = {
            "identification": username,
            "password": password
        }
        self.token, self.user_id = \
            requests.post(url, json=data, cookies=self.cookies).json().values()

    def _pyflarum_post(self, endpoint, data):
        url = self.base_url + endpoint
        return requests.post(url, headers=self.headers, json=data, cookies=self.cookies)

    def _pyflarum_get(self, endpoint):
        url = self.base_url + endpoint
        return requests.get(url, headers=self.headers, cookies=self.cookies)

    def _pyflarum_patch(self, endpoint, data):
        url = self.base_url + endpoint
        return requests.patch(url, headers=self.headers, json=data, cookies=self.cookies)

class User(PyFlarum):
    def __init__(self,base_url, username=None, password=None, cookies=None):
        super().__init__(base_url,username,password,cookies)
    def get_stats(self):
        return super()._pyflarum_get(END_POINTS["Users"],self.user_id)




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
        response = super()._pyflarum_post(END_POINTS['Discussions'], self.get_string())
        if response.status_code == 201:
            # print(response.text)
            self.discussion_id = response.json().get('data').get('id')
            self.first_post_id = response.json().get('data').get('relationships').get('startPost').get('data').get('id')
            print("Created discussion")
            return response.status_code
        else:
            print(f"Error creating the discusion {response.text}")
            return response.status_code

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
        response = super()._pyflarum_post(END_POINTS['Post'], data)
        if response.status_code == 201:
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
        response = super()._pyflarum_patch(endpoint, self.__gen_context())
        # print(response.text)
        if response.status_code == 201:
            print("Post updated")
        return response.status_code
