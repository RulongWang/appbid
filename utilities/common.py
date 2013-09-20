__author__ = 'Jarvis'

import json
import urllib2
import re

from system import models as systemModels


def getITunes(apple_id):
    """Get the app information in apple store by iTunes api, such as:https://itunes.apple.com/lookup?id=639384326"""
    if apple_id.strip() == "":
        return None
    try:
        search_url = ''.join(['https://itunes.apple.com/lookup?id=', apple_id])
        raw = urllib2.urlopen(search_url)
        js = raw.read()
        js_object = json.loads(js)
        if js_object is None or js_object.get('resultCount') != 1:
            raise
        result = js_object.get('results', None)[0]
    except:
        return None
    return result


def hiddenEmail(email):
    """hidden email, such as: abc@gmail.com - a******c@gmail.com"""
    if email and email.strip() != "":
        if bool(re.match(r"^[a-zA-Z]((\w*\.\w*)|\w*)[a-zA-Z0-9]@(\w+\.)+[a-zA-Z]{2,}$", email)):
            index = email.index('@')
            return ''.join([email[0], '*****', email[index-1:]])
    return None


def hiddenPhone(phone):
    """hidden phone, such as: 13623424568 - 136******568"""
    if phone and phone.strip() != "":
        if bool(re.match(r"^13|14|15|18\d{9}$", phone)):
            return ''.join([phone[0:3], '*****', phone[8:]])
    return None


def getSystemParam(*args, **kwargs):
    """Get the value in system param table by key."""
    key = kwargs.get('key')
    default_value = kwargs.get('default')
    if key:
        params = systemModels.SystemParam.objects.filter(key=key)
        if params:
            return params[0].value
        else:
            if default_value:
                return str(default_value)
    return None

