import sys
import requests
import json

# TODO plan how to use it inside web app(i.e. Flask, Rails)
# TODO create json schema, in order to avoid writing own response parser
#      (Gynvael's YT video https://www.youtube.com/watch?v=xR0hAJPp1vs)
# TODO validate against PEP8 standard

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
            self.url, data=json.dumps(payload), headers=self.headers).json()
        print("Client has sent a request with payload: ", payload)
        assert response["jsonrpc"]
        assert response["id"] == 0
        print("Client has received a response from server: ", response)

if __name__ == "__main__":
    client = Client("http://localhost:4000/jsonrpc")

    payload = {
        "method": "cpu_cores",
        "params": [],
        "jsonrpc": "2.0",
        "id": 0,
    }
    client.send_request(payload)