__author__ = 'Jarvis'


import urllib
import requests
import json
import logging

from django.shortcuts import render_to_response, RequestContext
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import ugettext as _
from twython import Twython

from appbid import settings
from utilities import common

log = logging.getLogger('appbid')


@csrf_protect
def authComplete(request, *args, **kwargs):
    access_token = '2.00k2kaSB5zPLLDe61c5e4ed1DVX24B'
    status = 'Yes, the apps walk.'
    params = urllib.urlencode({'source': settings.WEIBO_CLIENT_KEY, 'access_token': access_token, 'status': status})
    try:
        data = urllib.urlopen('https://api.weibo.com/2/statuses/update.json?', params).read()
    except (ValueError, KeyError, IOError) as e:
        print e

    return render_to_response('usersetting/register_active_confirm.html', context_instance=RequestContext(request))


@csrf_protect
def authError(request, *args, **kwargs):
    return None


def shareToWeiBo(*args, **kwargs):
    """Share App info to WeiBo"""
    initParam = kwargs.get('initParam')
    request = initParam.get('request')
    app = initParam.get('app')
    if app and request:
        try:
            url = 'https://upload.api.weibo.com/2/statuses/upload.json'
            app_url = '/'.join([common.getHttpHeader(request), 'query/app-detail', str(app.id)])
            status = ''.join(['App "', app.app_name.encode('utf-8'), '" for sale from AppsWalk. ', app_url])
            data = {
                'source': settings.WEIBO_CLIENT_KEY,
                'access_token': settings.WEIBO_ACCESS_TOKEN,
                'status': status
            }
            path = '/'.join([settings.MEDIA_ROOT, app.appinfo.icon])
            files = {'pic': open(path, mode='rb')}

            result = requests.post(url, data=data, files=files)
            data = json.loads(result.text)

            if data.get('error_code'):
                log.error(_('Share App %(param1)s failed to WeiBo, error:%(param2)s')
                          % {'param1': app.app_name, 'param2': data})
            else:
                log.info(_('Share App %(param1)s success to WeiBo.') % {'param1': app.app_name})
        except Exception as e:
            log.error(_('Share App %(param1)s failed to WeiBo, error:%(param2)s')
                      % {'param1': app.app_name, 'param2': str(e)})


def shareToTwitter(*args, **kwargs):
    """Share App info to Twitter"""
    initParam = kwargs.get('initParam')
    request = initParam.get('request')
    app = initParam.get('app')
    if app and request:
        try:
            # url = 'https://api.twitter.com/1.1/statuses/update_with_media.json'
            app_url = '/'.join([common.getHttpHeader(request), 'query/app-detail', str(app.id)])
            status = ''.join(['App "', app.app_name.encode('utf-8'), '" for sale from AppsWalk. ', app_url])
            pic = open('/'.join([settings.MEDIA_ROOT, app.appinfo.icon]), mode='rb')
            twitter = Twython(
                app_key=settings.TWITTER_CONSUMER_KEY,
                app_secret=settings.TWITTER_CONSUMER_SECRET,
                oauth_token=settings.TWITTER_OAUTH_TOKEN,
                oauth_token_secret=settings.TWITTER_OAUTH_TOKEN_SECRET
            )

            twitter.update_status_with_media(status=status, media=pic)

            log.info(_('Share App %(param1)s success to Twitter.') % {'param1': app.app_name})
        except Exception as e:
            log.error(_('Share App %(param1)s failed to Twitter, error:%(param2)s')
                      % {'param1': app.app_name, 'param2': str(e)})