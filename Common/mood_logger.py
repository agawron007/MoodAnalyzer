import requests
import re
from datetime import datetime
import time
from text_utils import remove_new_lines

class Logger:
    @staticmethod
    def log(severity, text):
        text = remove_new_lines(text)
        print str(datetime.now()) + '\t' + severity + '\t' + text

    @staticmethod
    def log_error(text):
        Logger.log("ERROR", text)
    
    @staticmethod
    def log_debug(text):
        Logger.log("DEBUG", text)