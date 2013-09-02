__author__ = 'Jarvis'
import json
import urllib


def getITunes(apple_id):
    """Get the app information in apple store by iTunes api, such as:https://itunes.apple.com/lookup?id=639384326"""
    if apple_id.strip() == "":
        return None
    try:
        search_url = ''.join(['https://itunes.apple.com/lookup?id=', apple_id])
        raw = urllib.urlopen(search_url)
        js = raw.read()
        js_object = json.loads(js)
        if js_object is None or js_object.get('resultCount') != 1:
            raise
        result = js_object.get('results', None)[0]
    except:
        return None
    return result

