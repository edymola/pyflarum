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

    datos_to_chungos = "texto"

    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.__get_token(username, password)

    def __get_token(self, username, password):
        url = self.base_url + "/api/token"
        data = {
            "identification": username,
            "password": password
        }
        self.token, self.user_id = \
            requests.post(url, json=data).json().values()
    def post_url(self, endpoint, data):
        url = self.base_url+endpoint
        headers = {'Authorization': "Token HqsHgn06cdw8kz7KhoO3zHUVq4jyvh5cNjVAoXCz"}
        return requests.post(url,headers=headers,json=data)




class Discussion(PyFlarum):

    def __init__(self,
                 base_url, username, password,
                 tittle, description, tag_id=DEFAULT_TAG):
        self.__init__(base_url,username,password)
        self.tittle = tittle
        self.description = description
        self.tag_id = tag_id

    def __str__(self):
        json = {
            "data": {
                "type": "discussions",
                "attributes": {
                    "title": self.tittle,
                    "content": self.description
                },
                "relationships": {
                    "recipientUsers": {
                        "data": [
                            {
                                "type": "users",
                                "id": "9"
                            }
                        ]
                    },
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
        return json
    def create_discussion(self, discusion):
        data = str(discusion)
        return
