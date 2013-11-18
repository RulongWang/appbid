__author__ = 'Jarvis'


import urllib
import requests
import json
import logging

from django.shortcuts import render_to_response, RequestContext
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import ugettext as _

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
    except (ValueError, KeyError, IOError), e:
        print e

    return render_to_response('usersetting/register_active_confirm.html', context_instance=RequestContext(request))


@csrf_protect
def authError(request, *args, **kwargs):
    return None


def shareToWeiBo(request, *args, **kwargs):
    """Share App info to WeiBo"""
    app = kwargs.get('app')
    if app:
        try:
            url = 'https://api.weibo.com/2/statuses/upload.json'
            app_url = '/'.join([common.getHttpHeader(request), 'query/app-detail', str(app.id)])
            status = ''.join(['App "', app.app_name, '" for sale from AppsWalk. ', app_url])
            data = {'source': settings.WEIBO_CLIENT_KEY, 'access_token': settings.WEIBO_ACCESS_TOKEN, 'status': status}
            files = {'pic': open('/'.join([settings.MEDIA_ROOT, app.appinfo.icon]), 'rb')}
            result = requests.post(url, data=data, files=files)
            data = json.loads(result.text)
            if data.get('error_code'):
                log.error(_('Share App %(param1)s failed to WeiBo, error:%(param2)s') % {'param1': app.app_name, 'param2': data})
            else:
                log.info(_('Share App %(param1)s success to WeiBo.') % {'param1': app.app_name})
        except Exception, e:
            log.error(_('Share App %(param1)s failed to WeiBo, error:%(param2)s') % {'param1': app.app_name, 'param2': e})