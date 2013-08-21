from django.http import HttpResponse
from django.shortcuts import render_to_response, RequestContext, HttpResponseRedirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.db import transaction
from seller import forms
from appbid import models
import json
import urllib


@csrf_protect
@login_required(login_url='/account/home/')
def registerApp(request, *args, **kwargs):
    """The common function for create, update app information."""
    app = None
    # initParam maybe save error message, when validate failed.
    initParam = {'flag': kwargs['flag']}

    if kwargs['pk']:
        app = get_object_or_404(models.App, pk=kwargs['pk'], publisher=request.user)
        initParam['app_id'] = app.id
        initParam['attachments'] = models.Attachment.objects.filter(app_id=app.id)

    if request.method == "POST":
        form = forms.AppForm(request.POST)
        saveMethod = kwargs.pop('saveMethod', None)
        if form.is_valid() and saveMethod is not None:
            newApp = saveMethod(request, form, app, initParam=initParam)
            if newApp is not None:
                return HttpResponseRedirect(reverse(kwargs['nextPage'], kwargs={'pk': newApp.id}))
    else:
        form = forms.AppForm()
        if kwargs['pk']:
            form = forms.AppForm(instance=app)

    #TODO:Need to change here.
    # appInfos = models.AppInfo.objects.filter(app_id=app.id)
    # if len(appInfos) > 0:
    #     initParam['appInfoForm'] = forms.AppInfoForm(instance=appInfos[0])

    initParam['form'] = form
    initParam['attachmentForm'] = forms.AttachmentForm()
    initParam['apps'] = models.App.objects.filter(publisher=request.user).order_by('status')
    initParam['paymentItems'] = models.PaymentItem.objects.all()
    return render_to_response(kwargs['backPage'], initParam, context_instance=RequestContext(request))


def saveAppStoreLink(request, form, model, *args, **kwargs):
    """Save the first register page - AppleStore Link."""
    initParam = kwargs.get('initParam')
    if form.cleaned_data['title'].strip() == "" or form.cleaned_data['app_store_link'].strip() == "":
        return None
    try:
        js = getITunes(form.cleaned_data['app_store_link'])
        if js is None or js.get('resultCount') != 1:
            raise
    except:
        initParam['app_store_link_error'] = _('The app store link is not correct.')
        return None

    if model is None:
        model = form.save(commit=False)
        model.publisher = models.User.objects.get(id=request.user.id)
        model.status = 1
    else:
        model.title = form.cleaned_data['title']
        model.app_store_link = form.cleaned_data['app_store_link']

    result = js.get('results', None)[0]
    model.rating = result.get('trackContentRating', None)
    model.platform_version = result.get('version', None)
    model.save()

    appInfos = models.AppInfo.objects.filter(app_id=model.id)
    if len(appInfos) == 0:
        appInfo = models.AppInfo()
        appInfo.app_id = model.id
    else:
        appInfo = appInfos[0]
    appInfo.price = result.get('price', 0)
    appInfo.icon = result.get('version', None)
    appInfo.track_id = result.get('trackId', 0)
    appInfo.save()

    model.category.clear()
    genres = result.get('genres', None)
    for genre in genres:
        categorys = models.Category.objects.filter(name=genre)
        if len(categorys) == 0:
            category = models.Category()
            category.name = genre
            category.save()
        else:
            category = categorys[0]
        model.category.add(category)

    model.device.clear()
    for device in models.Device.objects.all():
        for deviceName in result.get('supportedDevices', None):
            if deviceName.find(device.device) != -1:
                model.device.add(device)
                break
    return model


def saveAppStoreInfo(request, form, model, *args, **kwargs):
    """Save the second register page - AppStore Info."""
    # appInfoForm = forms.AppInfoForm(request.POST)
    # appInfo = models.AppInfo.objects.get(app_id=model.id)
    # if appInfoForm.is_valid():
    #     appInfo.price = appInfoForm.cleaned_data['price']
    #     appInfo.icon = appInfoForm.cleaned_data['icon']
    #     appInfo.track_id = appInfoForm.cleaned_data['track_id']
    #     appInfo.save()
    # else:
    #     return None
    model.platform_version = form.cleaned_data['platform_version']
    model.rating = form.cleaned_data['rating']
    model.category = form.cleaned_data['category']
    model.device = form.cleaned_data['device']
    model.save()

    return model


def saveMarketing(request, form, model, *args, **kwargs):
    """Save the second register page - Marketing."""
    model.dl_amount = form.cleaned_data['dl_amount']
    model.revenue = form.cleaned_data['revenue']
    model.monetize = form.cleaned_data['monetize']
    model.save()
    return model


# @transaction.commit_on_success
def saveAdditionalInfo(request, form, model, *args, **kwargs):
    """Save the third register page - Additional info."""
    initParam = kwargs.get('initParam')
    model.description = form.cleaned_data['description']

    if request.FILES.getlist('path'):
        for path in request.FILES.getlist('path'):
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
            if path.size > 50000000:
                initParam['attachmentError'] = _('The file can not be more than 50M.')
                return None
            attachment.app = model
            attachment.save()
    model.save()
    return model


def saveSale(request, form, model, *args, **kwargs):
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


def saveDelivery(request, form, model, *args, **kwargs):
    """Save the third register page - Delivery."""
    model.source_code = form.cleaned_data['source_code']
    model.web_site = form.cleaned_data['web_site']
    model.save()
    return model


def savePayment(request, form, model, *args, **kwargs):
    """Save the third register page - Payment."""
    ids = request.POST.getlist('paymentItem_id')
    currentPrice = request.POST.get('currentPrice')
    amount = request.POST.get('amount')
    price = 0
    paymentItems = []
    for id in ids:
        try:
            paymentItem = models.PaymentItem.objects.get(id=id)
            price += paymentItem.price
            paymentItems.append(paymentItem)
        except models.PaymentItem.DoesNotExist:
            return None
    if float(price) != float(currentPrice):
        return None
    for paymentItem in paymentItems:
        model.paymentItem.add(paymentItem)
    return model


def saveVerification(request, form, model, *args, **kwargs):
    """Save the third register page - Verification."""
    # model.description = form.cleaned_data['description']
    # model.save()
    return None


@csrf_protect
def deleteAttachment(request, *args, **kwargs):
    """Delete the attachment of app by id, app_id etc."""
    data={}
    try:
        dict = request.POST
    except:
        dict = request.GET
    try:
        attachment = models.Attachment.objects.get(id=dict.get('id'))
        attachment.delete()
        data['ok'] = 'true'
    except models.Attachment.DoesNotExist:
        data['ok'] = 'false'
        data['message'] = ''.join(['The attachment "', dict.get('name'), '" does not exist.'])
    return HttpResponse(json.dumps(data), mimetype=u'application/json')


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


