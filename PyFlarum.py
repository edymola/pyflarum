import requests




class Discussion:

    def __init__(self,
                 tittle,
                 description,
                 tag_id):
        self.tittle = tittle
        self.description = description
        self.tag_id = tag_id



    def __str__(self):
        json = {
                    "type": "discussions",
                    "attributes":{
                        "title": self.tittle,
                        "content": self.description
                    },
                    "relationships":{
                        "tags":{
                            "data":[
                                {
                                    "type":"tags",
                                    "id":self.tag_id
                                }
                            ]
                        }
                    }
                }

        return json


class PyFlarum:

    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.__get_token(username,password)

    def __get_token(self, username, password):
        url = self.base_url + "/api/token"
        data = {
            "identification": username,
            "password": password
        }
        self.token, self.user_id = \
            requests.post(url, json=data).json().values()

    def create_discussion(self,discussion):
        discussion
