import re
import unicodedata

def remove_new_lines(text):
    p = re.compile(ur'[\r?\n]')
    return re.sub(p, r' ', text)

def clean_text(content):
    content = remove_new_lines(content)
    content = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','URL',content)
    content = re.sub('[\"]', '\'', content)
    #content = re.sub('[^0-9a-zA-Z\s,\.]+', '', content)
    return content

def normalize(text):
    return unicodedata.normalize('NFKD', text).encode('ascii','ignore')