import json
import urllib
import datetime
import random
import string
import re
import os

from django.http import HttpResponse
from django.shortcuts import render_to_response, RequestContext, HttpResponseRedirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.db import transaction
from django.conf import settings

from seller import forms
from appbid import models
from utilities import common

@csrf_protect
@login_required(login_url='/account/home/')
def registerApp(request, *args, **kwargs):
    """The common function for create, update app information."""
    app = None
    # initParam maybe save error message, when validate failed.
    initParam = {'flag': kwargs['flag']}
    form = forms.AppForm()

    if kwargs['pk']:
        app = get_object_or_404(models.App, pk=kwargs['pk'], publisher=request.user)
        form = forms.AppForm(instance=app)
        initParam['app_id'] = app.id
        initParam['attachments'] = models.Attachment.objects.filter(app_id=app.id)
        initParam['selectItems'] = app.paymentItem.all()
        appInfos = models.AppInfo.objects.filter(app_id=app.id)
        if appInfos:
            initParam['appInfoForm'] = forms.AppInfoForm(instance=appInfos[0])
        paymentDetails = models.PaymentDetail.objects.filter(app_id=app.id)
        if paymentDetails:
            initParam['amount'] = paymentDetails[0].amount
        else:
            amount = 0
            paymentItems = models.PaymentItem.objects.filter(is_basic_service=True, end_date__gte=datetime.datetime.now())
            for paymentItem in paymentItems:
                amount += paymentItem.price
            initParam['amount'] = amount
        initParam['verify_token'] = app.verify_token

    if request.method == "POST":
        form = forms.AppForm(request.POST)
        saveMethod = kwargs.pop('saveMethod', None)
        if form.is_valid() and saveMethod is not None:
            newApp = saveMethod(request, form, app, initParam=initParam)
            if newApp is not None:
                return HttpResponseRedirect(reverse(kwargs['nextPage'], kwargs={'pk': newApp.id}))

    initParam['form'] = form
    initParam['attachmentForm'] = forms.AttachmentForm()
    initParam['apps'] = models.App.objects.filter(publisher=request.user).order_by('status')
    initParam['paymentItems'] = models.PaymentItem.objects.filter(end_date__gte=datetime.datetime.now())
    return render_to_response(kwargs['backPage'], initParam, context_instance=RequestContext(request))


@transaction.commit_on_success
def saveAppStoreLink(request, form, model, *args, **kwargs):
    """Save the first register page - AppleStore Link."""
    initParam = kwargs.get('initParam')
    if form.cleaned_data['title'].strip() == "" or form.cleaned_data['app_store_link'].strip() == "":
        return None
    try:
        pattern = re.compile(r'^https://itunes.apple.com/[\w+/]+id(\d+)')
        match = pattern.match(form.cleaned_data['app_store_link'])
        if match is None:
            raise
        result = common.getITunes(match.group(1))
        if result is None:
            raise
    except:
        initParam['app_store_link_error'] = _('The app store link is not correct.')
        return None

    if model is None:
        model = form.save(commit=False)
        model.publisher = models.User.objects.get(id=request.user.id)
        model.status = 1
        #currency is CNY in chinese version, USD in other version.
        model.currency = models.Currency.objects.get(id=1)
        model.minimum_bid = 10#default value is 10.
        token_len = models.SystemParam.objects.get(key='token_len')
        model.verify_token = ''.join(random.sample(string.ascii_letters+string.digits, string.atoi(token_len.value)))
        model.is_verified = False
    else:
        model.title = form.cleaned_data['title']
        model.app_store_link = form.cleaned_data['app_store_link']
    model.rating = result.get('trackContentRating', None)
    model.platform_version = result.get('version', None)
    model.apple_id = result.get('trackId', None)
    model.app_name = result.get('trackName', None)
    model.web_site = result.get('sellerUrl', None)
    model.reviews = result.get('userRatingCount', None)
    model.description = result.get('description', None)
    model.seller_name = result.get('sellerName', None)
    model.save()

    appInfos = models.AppInfo.objects.filter(app_id=model.id)
    if appInfos:
        appInfo = appInfos[0]
    else:
        appInfo = models.AppInfo()
        appInfo.app_id = model.id
    appInfo.price = result.get('price', 0)
    appInfo.release_date = datetime.datetime.strptime(result.get('releaseDate', None), "%Y-%m-%dT%H:%M:%SZ")
    path = '/'.join([settings.MEDIA_ROOT, str(model.publisher.id), str(model.id)])
    if os.path.exists(path) is False:
        os.makedirs(path)
    path = '/'.join([path, 'Icon.jpg'])
    if result.get('artworkUrl512', None):
        urllib.urlretrieve(result.get('artworkUrl512', None), path)
    elif result.get('artworkUrl100', None):
        urllib.urlretrieve(result.get('artworkUrl100', None), path)
    elif result.get('artworkUrl60', None):
        urllib.urlretrieve(result.get('artworkUrl60', None), path)
    appInfo.icon = '/'.join([str(model.publisher.id), str(model.id), 'Icon.jpg'])
    appInfo.save()

    model.category.clear()
    genres = result.get('genres', None)
    for genre in genres:
        categories = models.Category.objects.filter(name=genre)
        if categories:
            category = categories[0]
        else:
            category = models.Category()
            category.name = genre
            category.save()
        model.category.add(category)

    model.device.clear()
    for device in models.Device.objects.all():
        for deviceName in result.get('supportedDevices', None):
            if deviceName.find(device.device) != -1:
                model.device.add(device)
                break
    return model


@transaction.commit_on_success
def saveAppStoreInfo(request, form, model, *args, **kwargs):
    """Save the second register page - AppStore Info."""
    if model is None:
        return None
    initParam = kwargs.get('initParam')
    appInfoForm = forms.AppInfoForm(request.POST)
    appInfo = models.AppInfo.objects.get(app_id=model.id)
    if appInfoForm.is_valid():
        appInfo.price = appInfoForm.cleaned_data['price']
        # appInfo.icon = appInfoForm.cleaned_data['icon']
        appInfo.save()
    else:
        initParam['appInfoForm'] = appInfoForm
        return None
    model.apple_id = form.cleaned_data['apple_id']
    model.platform_version = form.cleaned_data['platform_version']
    model.rating = form.cleaned_data['rating']
    model.category = form.cleaned_data['category']
    model.device = form.cleaned_data['device']
    model.save()

    return model


@transaction.commit_on_success
def saveMarketing(request, form, model, *args, **kwargs):
    """Save the second register page - Marketing."""
    if model is None:
        return None
    model.dl_amount = form.cleaned_data['dl_amount']
    model.revenue = form.cleaned_data['revenue']
    model.monetize = form.cleaned_data['monetize']
    model.save()
    return model


@transaction.commit_on_success
def saveAdditionalInfo(request, form, model, *args, **kwargs):
    """Save the third register page - Additional info."""
    if model is None:
        return None
    initParam = kwargs.get('initParam')
    model.description = form.cleaned_data['description']

    pathList = request.FILES.getlist('path')
    if pathList:
        maxNum = models.SystemParam.objects.filter(key='max_num_attachment')
        attachments = models.Attachment.objects.filter(app_id=model.id)
        if maxNum and len(pathList) + len(attachments) > string.atoi(maxNum[0].value):
            initParam['attachmentError'] = _('The attachment number can not be more than %(number)s.') % {'number': maxNum[0].value}
            return None

        attachmentSize = models.SystemParam.objects.filter(key='attachment_size')
        for path in pathList:
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
            if attachmentSize and path.size > string.atof(attachmentSize[0].value):
                initParam['attachmentError'] = _('The file can not be more than 50M.')
                return None
            attachment.app = model
            attachment.save()
    model.save()
    return model


@transaction.commit_on_success
def saveSale(request, form, model, *args, **kwargs):
    """Save the third register page - Sale."""
    if model is None:
        return None
    model.begin_price = form.cleaned_data['begin_price']
    model.one_price = form.cleaned_data['one_price']
    model.reserve_price = form.cleaned_data['reserve_price']
    model.currency_id = form.cleaned_data['currency']
    model.begin_date = form.cleaned_data['begin_date']
    model.end_date = form.cleaned_data['end_date']
    model.minimum_bid = form.cleaned_data['minimum_bid']
    model.save()
    return model


@transaction.commit_on_success
def saveDelivery(request, form, model, *args, **kwargs):
    """Save the third register page - Delivery."""
    if model is None:
        return None
    model.source_code = form.cleaned_data['source_code']
    model.web_site = form.cleaned_data['web_site']
    model.save()
    return model


@transaction.commit_on_success
def savePayment(request, form, model, *args, **kwargs):
    """Save the third register page - Payment."""
    if model is None:
        return None
    amount = 0
    ids = request.POST.getlist('paymentItem_id')
    model.paymentItem.clear()
    for id in ids:
        try:
            paymentItem = models.PaymentItem.objects.get(id=id)
            amount += paymentItem.price
            model.paymentItem.add(paymentItem)
        except models.PaymentItem.DoesNotExist:
            return None
    try:
        paymentDetail = models.PaymentDetail.objects.get(app_id=model.id, end_date__gte=datetime.datetime.now())
    except models.PaymentDetail.DoesNotExist:
        paymentDetail = models.PaymentDetail()
        paymentDetail.app_id = model.id
        paymentDetail.is_payed = False
        #TODO:Need to change them,after user have payed.
        # paymentDetail.start_date = datetime.datetime.now()
        # paymentDetail.end_date = datetime.datetime.now() + datetime.timedelta(months=1)
        # paymentDetail.gateway = 1
    discount_rate = models.SystemParam.objects.filter(key='discount_rate')
    if discount_rate:
        paymentDetail.actual_amount = string.atof(discount_rate[0].value) * amount
    else:
        paymentDetail.actual_amount = amount
    paymentDetail.amount = amount
    paymentDetail.save()
    return model


@transaction.commit_on_success
def saveVerification(request, form, model, *args, **kwargs):
    """Save the third register page - Verification."""
    if model is None:
        return None
    initParam = kwargs.get('initParam')
    try:
        ownerShipScan = models.OwnerShip_Scan.objects.get(app_id=model.id)
    except models.OwnerShip_Scan.DoesNotExist:
        ownerShipScan = models.OwnerShip_Scan()
        ownerShipScan.app_id = model.id
        ownerShipScan.save()
    initParam['verify_msg'] = _('The verification will be done later. Send the email to you after verified.')
    return None


@csrf_protect
@transaction.commit_on_success
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
        data['message'] = _('The attachment "%(name)s" does not exist.') % {'name': dict.get('name')}
    return HttpResponse(json.dumps(data), mimetype=u'application/json')


def hello(request):
    return HttpResponse(" This is the home page")


def searchItunes(request):
    search_url = 'https://itunes.apple.com/lookup?id=639384326'
    raw = urllib.urlopen(search_url)
    js = raw.read()
    js_object = json.loads(js)
    return render_to_response('home/test.html',{"json_objects":js_object["resultCount"]})


