import requests
import re

'''
This class represents a client(i.e. web browser/web app)
It asks the server for remote method execution(like: "What GPU you actually have, my dear server?")
'''
class Client(object):
    def __init__(self, destination_url):
        self.url = destination_url
        self.headers = {'content-type': 'application/json'}

    def send_request(self, payload):
        response = requests.post(
            #self.url, data=json.dumps(payload), headers=self.headers).json()
            self.url, data=payload)
        print("Client has sent a request with payload: ", payload)
        #print("Client has received a response from server: ", response)


def http_post_record(content, Keyword):
    result = "{\"Keywords\":[\"" + str(Keyword) + "\"],\"Text\":\"" + str(content) + "\"}"
    base_url="http://localhost:1234"
    client = Client(base_url)
    payload = result
    client.send_request(payload)    