from django.http import HttpResponse
from django.shortcuts import render_to_response, RequestContext, HttpResponseRedirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from seller import forms
from appbid import models
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.core.serializers.json import Deserializer
import urllib


@csrf_protect
# @method_decorator(login_required)
def register_app(request, *args, **kwargs):
    app = {}
    isExist = False
    # initParam maybe save error message, when validate failed.
    initParam = {'flag': kwargs['flag']}

    if kwargs['pk']:
        app = get_object_or_404(models.App, pk=kwargs['pk'])
        initParam['app_id'] = app.id
        isExist = True

    if request.method == "POST":
        form = forms.AppForm(request.POST)
        saveMethod = kwargs.pop('saveMethod', None)
        if form.is_valid():
            if not isExist:
                app = createApp(form)
            elif saveMethod is not None:
                pathList = request.FILES.getlist('path')
                if pathList:
                    app = saveMethod(form, app, initParam=initParam, pathList=pathList)
                else:
                    app = saveMethod(form, app, initParam=initParam)
            if app is not None:
                return HttpResponseRedirect(reverse(kwargs['nextPage'], kwargs={'pk': app.id}))
    else:
        form = forms.AppForm()
        attachmentForm = forms.AttachmentForm()
        initParam['attachmentForm'] = attachmentForm
        if isExist:
            form = forms.AppForm(instance=app)
            attachments = models.Attachment.objects.filter(app_id=app.id)
            initParam['attachments'] = attachments
    initParam['form'] = form
    return render_to_response(kwargs['backPage'], initParam, context_instance=RequestContext(request))


def createApp(form, *args, **kwargs):
    if form.cleaned_data['title'].strip() == "" or form.cleaned_data['app_store_link'].strip() == "":
        return None
    js = getITunes(form.cleaned_data['app_store_link'])
    if js is None or js.get('resultCount') != 1:
        return None

    model = form.save(commit=False)
    result = js.get('results', None)[0]
    model.rating = result.get('trackContentRating', None)
    model.platform_version = result.get('version', None)
    model.publisher = models.User.objects.get(pk=1)
    model.status = 1
    model.save()

    for device in models.Device.objects.all():
        for deviceName in result.get('supportedDevices', None):
            if deviceName.find(device.device) != -1:
                model.device.add(device)
                break
    return model


def saveAppStoreLink(form, model, *args, **kwargs):
    """Save the first register page - AppleStore Link."""
    if form.cleaned_data['title'].strip() == "" or form.cleaned_data['app_store_link'].strip() == "":
        return None

    model.title = form.cleaned_data['title']
    model.app_store_link = form.cleaned_data['app_store_link']
    model.save()
    return model


def saveAppStoreInfo(form, model, *args, **kwargs):
    """Save the second register page - AppStore Info."""
    model.platform_version = form.cleaned_data['platform_version']
    model.rating = form.cleaned_data['rating']
    model.device = form.cleaned_data['device']
    model.save()
    return model


def saveMarketing(form, model, *args, **kwargs):
    """Save the second register page - Marketing."""
    model.dl_amount = form.cleaned_data['dl_amount']
    model.revenue = form.cleaned_data['revenue']
    model.monetize = form.cleaned_data['monetize']
    model.save()
    return model


def saveAdditionalInfo(form, model, *args, **kwargs):
    """Save the third register page - Additional info."""
    initParam = kwargs.get('initParam')
    model.description = form.cleaned_data['description']
    model.save()

    if kwargs.get('pathList'):
        for path in kwargs.get('pathList'):
            attachment = models.Attachment(path=path)
            attachment.name = path.name
            if path.content_type.find('image') != -1:
                attachment.type = 1
            elif path.content_type == 'application/pdf':
                attachment.type = 3
            elif path.content_type.find('application') != -1:
                attachment.type = 4
            else:
                attachment.type = 4
            #The attachment size can not be more than 50M.
            if path.size > 50000000:
                initParam['attachmentError'] = ''.join(['The attachment \'', path.name, '\' is too large.'])
                # initParam['attachmentForm'] = forms.AttachmentForm(path=path)
                return None
            attachment.app = model
            attachment.save()
    return model


def saveSale(form, model, *args, **kwargs):
    """Save the third register page - Sale."""
    model.begin_price = form.cleaned_data['begin_price']
    model.one_price = form.cleaned_data['one_price']
    model.reserve_price = form.cleaned_data['reserve_price']
    model.currency_id = form.cleaned_data['currency']
    model.begin_date = form.cleaned_data['begin_date']
    model.end_date = form.cleaned_data['end_date']
    model.minimum_bid = form.cleaned_data['minimum_bid']
    model.save()
    return model


def saveDelivery(form, model, *args, **kwargs):
    """Save the third register page - Delivery."""
    # model.description = form.cleaned_data['description']
    # model.save()
    return None


def savePayment(form, model, *args, **kwargs):
    """Save the third register page - Payment."""
    # model.description = form.cleaned_data['description']
    # model.save()
    return None


def saveVerification(form, model, *args, **kwargs):
    """Save the third register page - Verification."""
    # model.description = form.cleaned_data['description']
    # model.save()
    return None


def getITunes(search_url):
    """Get the app information in apple store by iTunes api, such as:https://itunes.apple.com/lookup?id=639384326"""
    if search_url.strip() == "":
        return None
    raw = urllib.urlopen(search_url)
    js = raw.read()
    js_object = json.loads(js)
    return js_object


def hello(request):
    return HttpResponse(" This is the home page")


def searchItunes(request):
    search_url = 'https://itunes.apple.com/lookup?id=639384326'
    raw = urllib.urlopen(search_url)
    js = raw.read()
    js_object = json.loads(js)
    return render_to_response('home/test.html',{"json_objects":js_object["resultCount"]})


