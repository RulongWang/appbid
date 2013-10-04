__author__ = 'Jarvis'

import json
import urllib2
import re
import datetime

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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


def sortWithIndexLie(A, indexLie=0, order='asc'):
    """Sort with some one lie for Double Dimensional Array. order: asc, desc"""
    if indexLie < 0:
        indexLie = 0
    elif indexLie >= len(A[0]):
        indexLie = 0
    if indexLie != 0:
        for i in range(len(A)):
            (A[i][0], A[i][indexLie]) = (A[i][indexLie], A[i][0])
    if order == 'asc':
        A.sort()
    elif order == 'desc':
        def myCmp(e1, e2):
            return -cmp(e1[0], e2[0])
        A.sort(myCmp)
    if indexLie != 0:
        for i in range(len(A)):
            (A[i][0], A[i][indexLie]) = (A[i][indexLie], A[i][0])


def queryWithPaginator(request, *args, **kwargs):
    """Query method with paginator function."""
    page_range = kwargs.get('page_range')
    page = kwargs.get('page', 1)
    obj = kwargs.get('obj')
    queryMethod = kwargs.get('query_method')

    if page_range is None:
        page_range = getSystemParam(key='page_range', default=10)

    if obj:
        obj_list = []
        for info in obj:
            #info list[0]:The obj info
            info_list = [info]
            obj_list.append(info_list)

        paginator = Paginator(obj_list, page_range)
        try:
            objList = paginator.page(page)
        except PageNotAnInteger:
            objList = paginator.page(1)
        except EmptyPage:
            objList = paginator.page(paginator.num_pages)

        # Just query the obj information showed in the current page.
        if queryMethod:
            for info_list in objList:
                result = queryMethod(request, app=info_list[0])
                if result:
                    info_list.append(result)
        return objList

    return None


def dateRemaining(date=datetime.datetime.now()):
    """Get the remaining time of date - now, such as: 10days, 15hours, 20minutes, 10seconds."""
    interval = (
        (60 * 60 * 24 * 365, 'year'),
        (60 * 60 * 24 * 30, 'month'),
        (60 * 60 * 24 * 7, 'week'),
        (60 * 60 * 24, 'day'),
        (60 * 60, 'hour'),
        (60, 'minute'),
        (1, 'second'),
    )
    if date:
        if not isinstance(date, datetime.datetime):
            date = datetime.datetime(date.year, date.month, date.day)
        delta = date - datetime.datetime.now()
        remaining = delta.total_seconds()
        if remaining > 0:
            for seconds, unit in interval:
                count = remaining // seconds
                if count != 0:
                    break
            return [str(count), unit]
    return [0, 'second']


def dateBefore(date=datetime.datetime.now()):
    """Get the before time of date - now, such as: 10days ago, 15hours ago, 20minutes ago, 10seconds ago."""
    interval = (
        (60 * 60 * 24 * 365, 'year'),
        (60 * 60 * 24 * 30, 'month'),
        (60 * 60 * 24 * 7, 'week'),
        (60 * 60 * 24, 'day'),
        (60 * 60, 'hour'),
        (60, 'minute'),
        (1, 'second'),
    )
    if date:
        if not isinstance(date, datetime.datetime):
            date = datetime.datetime(date.year, date.month, date.day)
        delta = datetime.datetime.now() - date
        remaining = delta.total_seconds()
        if remaining > 0:
            for seconds, unit in interval:
                count = remaining // seconds
                if count != 0:
                    break
            return [str(count), unit, 'ago']
    return [0, 'second', 'ago']