import requests
import re
from mood_logger import Logger

from text_utils import clean_text

class Client(object):
    def __init__(self, destination_url):
        self.url = destination_url
        self.headers = {'content-type': 'application/json'}

    def send_request(self, payload):
        response = requests.post(self.url, data=payload, headers=self.headers)
        Logger.log_debug("Sent payload (length: " + str(len(payload)) + ')')


def http_post_record(content, keyword, source):
    try:
        content = clean_text(content)
        result = "{\"Source\":\"" + source + "\", \"Keywords\":[\"" + str(keyword) + "\"],\"Text\":\"" + str(content) + "\"}"
        base_url="http://localhost:1234"
        client = Client(base_url)
        payload = result
        client.send_request(payload)
        return True
    except:
        e = sys.exc_info()[0]
        Logger.log_error("Failed to send a POST request to " + base_url + ". Exception: " + str(e))
        return False