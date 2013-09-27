import json
import urllib
import datetime
import random
import string
import re
import os

from django.http import HttpResponse
from django.shortcuts import render_to_response, RequestContext, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.db import transaction
from django.conf import settings
from order import models as orderModels

from seller import forms
from appbid import models as appModels
from utilities import common

@csrf_protect
@login_required(login_url='/usersetting/home/')
def registerApp(request, *args, **kwargs):
    """The common function for create, update app information."""
    app = None
    # initParam maybe save error message, when validate failed.
    initParam = kwargs.copy()
    form = forms.AppForm()

    #Initial data
    if kwargs.get('pk'):
        app = get_object_or_404(appModels.App, pk=kwargs.get('pk'), publisher=request.user)
        form = forms.AppForm(instance=app)
        initParam['app_id'] = app.id
        initParam['attachments'] = appModels.Attachment.objects.filter(app_id=app.id)
        initParam['verify_token'] = app.verify_token
        appInfos = appModels.AppInfo.objects.filter(app_id=app.id)
        if appInfos:
            initParam['appInfoForm'] = forms.AppInfoForm(instance=appInfos[0])
        initParam['serviceDetails'] = orderModels.ServiceDetail.objects.filter(app_id=app.id)
        if kwargs.get('sn'):
            serviceDetail = get_object_or_404(orderModels.ServiceDetail, app_id=app.id, sn=kwargs.get('sn'))
            initParam['selectItems'] = serviceDetail.serviceitem.all()
            initParam['serviceDetail'] = serviceDetail
            initParam['amount'] = serviceDetail.amount
        else:
            amount = 0
            serviceItems = orderModels.ServiceItem.objects.filter(is_basic_service=True, end_date__gte=datetime.datetime.now())
            for serviceItem in serviceItems:
                amount += serviceItem.price
            initParam['amount'] = amount
        initParam['service_expiry_date'] = common.getSystemParam(key='service_expiry_date', default=1)

    if request.method == "POST":
        form = forms.AppForm(request.POST)
        saveMethod = kwargs.pop('saveMethod', None)
        if form.is_valid() and saveMethod:
            result = saveMethod(request, form, app, initParam=initParam)
            if result:
                return result

    initParam['form'] = form
    initParam['attachmentForm'] = forms.AttachmentForm()
    initParam['apps'] = appModels.App.objects.filter(publisher=request.user).order_by('-status', 'create_time')
    initParam['serviceItems'] = orderModels.ServiceItem.objects.filter(end_date__gte=datetime.datetime.now())
    return render_to_response(kwargs.get('backPage'), initParam, context_instance=RequestContext(request))


@transaction.commit_on_success
def saveAppStoreLink(request, form, model, *args, **kwargs):
    """Save the first register page - AppleStore Link."""
    initParam = kwargs.get('initParam')
    if form.cleaned_data['title'].strip() == "" or form.cleaned_data['app_store_link'].strip() == "":
        return None
    try:
        pattern = re.compile(r'^https://itunes.apple.com/[\S+/]+id(\d+)')
        match = pattern.match(form.cleaned_data['app_store_link'])
        if match is None:
            raise
        result = common.getITunes(match.group(1))
        if result is None:
            raise
    except Exception, e:
        #print e #TODO:log the error message
        initParam['app_store_link_error'] = _('The app store link is not correct.')
        return None

    #Save app data
    if model is None:
        model = form.save(commit=False)
        #New app, and init some data
        model.publisher = appModels.User.objects.get(id=request.user.id)
        model.store_type = 1
        model.status = 1
        model.source_code = True
        model.unique_sell = True
        currency_id = common.getSystemParam(key='currency', default=1)
        model.currency = get_object_or_404(appModels.Currency, pk=currency_id)
        model.minimum_bid = common.getSystemParam(key='minimum_bid', default=10)
        token_len = common.getSystemParam(key='token_len', default=10)
        model.verify_token = ''.join(random.sample(string.ascii_letters+string.digits, string.atoi(token_len)))
        model.is_verified = False
    else:
        model.title = form.cleaned_data['title'].strip()
        model.app_store_link = form.cleaned_data['app_store_link'].strip()
    model.rating = result.get('averageUserRating', None)
    model.platform_version = result.get('version', None)
    model.apple_id = result.get('trackId', None)
    model.app_name = result.get('trackName', None)
    model.web_site = result.get('sellerUrl', None)
    model.reviews = result.get('userRatingCount', None)
    model.description = result.get('description', None)
    model.seller_name = result.get('sellerName', None)
    model.save()

    #Save date in appinfo table.
    appInfos = appModels.AppInfo.objects.filter(app_id=model.id)
    if appInfos:
        appInfo = appInfos[0]
    else:
        appInfo = appModels.AppInfo()
        appInfo.app_id = model.id
    appInfo.price = result.get('price', 0)
    appInfo.release_date = datetime.datetime.strptime(result.get('releaseDate', None), "%Y-%m-%dT%H:%M:%SZ")
    try:
        path = '/'.join([settings.MEDIA_ROOT, str(model.publisher.id), str(model.id)])
        if os.path.exists(path) is False:
            os.makedirs(path)
        path = '/'.join([path, 'Icon.jpg'])
        if os.path.exists(path):
            os.remove(path)
        if result.get('artworkUrl512', None):
            if os.path.exists(path):
                os.remove(path)
            urllib.urlretrieve(result.get('artworkUrl512', None), path)
        elif result.get('artworkUrl100', None):
            urllib.urlretrieve(result.get('artworkUrl100', None), path)
        elif result.get('artworkUrl60', None):
            urllib.urlretrieve(result.get('artworkUrl60', None), path)
    except Exception, e:
        #print e #TODO:log the error message
        initParam['app_store_link_error'] = _('The app store link is not correct.')
        return None
    appInfo.icon = '/'.join([str(model.publisher.id), str(model.id), 'Icon.jpg'])
    appInfo.save()

    #Save monetize data
    monetize_id = common.getSystemParam(key='monetize', default=4)
    model.monetize.add(get_object_or_404(appModels.Monetize, pk=monetize_id))

    #Save category, subcategory data
    model.category.clear()
    model.subcategory.clear()
    genres = result.get('genres', None)
    genreIds = result.get('genreIds', None)
    if genres and genreIds and len(genres) == len(genreIds):
        for i in range(len(genreIds)):
            categories = appModels.Category.objects.filter(apple_id=string.atoi(genreIds[i]))
            if categories:
                model.category.add(categories[0])
            else:
                subCategories = appModels.SubCategory.objects.filter(apple_id=string.atoi(genreIds[i]))
                if subCategories:
                    model.subcategory.add(subCategories[0])
                else:
                    category = appModels.Category()
                    category.apple_id = genreIds[i]
                    category.name = genres[i]
                    category.save()
                    model.category.add(category)
                    #TODO:Auto send email to administrator to add new category

    #Save device data
    model.device.clear()
    for device in appModels.Device.objects.all():
        for deviceName in result.get('supportedDevices', None):
            if deviceName.find(device.device) != -1:
                model.device.add(device)
                break
    return redirect(reverse(initParam.get('nextPage'), kwargs={'pk': model.id}))


@transaction.commit_on_success
def saveAppStoreInfo(request, form, model, *args, **kwargs):
    """Save the second register page - AppStore Info."""
    if model is None:
        return None

    initParam = kwargs.get('initParam')
    #App Store info need not save,because of these values from apple store
    # initParam = kwargs.get('initParam')
    # appInfoForm = forms.AppInfoForm(request.POST)
    # appInfo = models.AppInfo.objects.get(app_id=model.id)
    # if appInfoForm.is_valid():
    #     appInfo.price = appInfoForm.cleaned_data['price']
    #     # appInfo.icon = appInfoForm.cleaned_data['icon']
    #     appInfo.save()
    # else:
    #     initParam['appInfoForm'] = appInfoForm
    #     return None
    # model.apple_id = form.cleaned_data['apple_id']
    # model.platform_version = form.cleaned_data['platform_version']
    # model.rating = form.cleaned_data['rating']
    # model.category = form.cleaned_data['category']
    # model.device = form.cleaned_data['device']
    # model.save()
    return redirect(reverse(initParam.get('nextPage'), kwargs={'pk': model.id}))


@transaction.commit_on_success
def saveMarketing(request, form, model, *args, **kwargs):
    """Save the second register page - Marketing."""
    if model is None:
        return None

    initParam = kwargs.get('initParam')
    model.dl_amount = form.cleaned_data['dl_amount']
    model.revenue = form.cleaned_data['revenue']
    model.monetize = form.cleaned_data['monetize']
    model.save()
    return redirect(reverse(initParam.get('nextPage'), kwargs={'pk': model.id}))


@transaction.commit_on_success
def saveAdditionalInfo(request, form, model, *args, **kwargs):
    """Save the third register page - Additional info."""
    if model is None:
        return None

    initParam = kwargs.get('initParam')
    model.description = form.cleaned_data['description']
    pathList = request.FILES.getlist('path')
    if pathList:
        maxNum = common.getSystemParam(key='max_num_attachment', default=50)
        attachments = appModels.Attachment.objects.filter(app_id=model.id)
        if len(pathList) + len(attachments) > string.atoi(maxNum):
            initParam['attachmentError'] = _('The attachment number can not be more than %(number)s.') % {'number': maxNum[0].value}
            return None

        attachmentSize = common.getSystemParam(key='attachment_size', default=50000000)
        for path in pathList:
            attachment = appModels.Attachment(path=path)
            attachment.name = path.name
            if path.content_type.find('image') != -1:
                attachment.type = 1
            elif path.content_type == 'application/pdf':
                attachment.type = 3
            elif path.content_type.find('application') != -1:
                attachment.type = 4
            else:
                attachment.type = 4
            if path.size > string.atof(attachmentSize):
                initParam['attachmentError'] = _('The file can not be more than 50M.')
                return None
            attachment.app = model
            attachment.save()
    model.save()
    return redirect(reverse(initParam.get('nextPage'), kwargs={'pk': model.id}))


@transaction.commit_on_success
def saveSale(request, form, model, *args, **kwargs):
    """Save the third register page - Sale."""
    if model is None:
        return None

    initParam = kwargs.get('initParam')
    if model.status == 1:
        model.begin_price = form.cleaned_data['begin_price']
        model.one_price = form.cleaned_data['one_price']
        model.reserve_price = form.cleaned_data['reserve_price']
        model.currency_id = form.cleaned_data['currency']
        model.begin_date = form.cleaned_data['begin_date']
        model.end_date = form.cleaned_data['end_date']
        model.minimum_bid = form.cleaned_data['minimum_bid']
        model.save()
    return redirect(reverse(initParam.get('nextPage'), kwargs={'pk': model.id}))


@transaction.commit_on_success
def saveDelivery(request, form, model, *args, **kwargs):
    """Save the third register page - Delivery."""
    if model is None:
        return None

    initParam = kwargs.get('initParam')
    if model.status == 1:
        model.unique_sell = form.cleaned_data['unique_sell']
        model.source_code = form.cleaned_data['source_code']
        model.delivery_detail = form.cleaned_data['delivery_detail'].strip()
        model.web_site = form.cleaned_data['web_site']
        model.save()
    return redirect('/'.join([initParam.get('nextPage'), str(model.id), kwargs.get('sn', '')]))


@transaction.commit_on_success
def saveService(request, form, model, *args, **kwargs):
    """Save the third register page - Service."""
    if model is None:
        return None

    amount = 0
    initParam = kwargs.get('initParam')
    sn = request.POST.get('sn')
    if sn:
        serviceDetail = get_object_or_404(orderModels.ServiceDetail, app_id=model.id, sn=sn)
        serviceDetail.serviceitem.clear()
    else:
        #Check if there is the unpaid payment, before create the new one.
        if model.servicedetail_set.filter(is_payed=False):
            initParam['payment_msg'] = _('You have the unpaid payment.')
            return None
        #Create the new service detail.
        serviceDetail = orderModels.ServiceDetail()
        serviceDetail.app_id = model.id
        serviceDetail.is_payed = False
        serviceDetail.sn = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        serviceDetail.save()

    #Save service items
    for id in request.POST.getlist('serviceItem_id'):
        try:
            serviceItem = orderModels.ServiceItem.objects.get(id=id)
            amount += serviceItem.price
            serviceDetail.serviceitem.add(serviceItem)
        except orderModels.ServiceItem.DoesNotExist:
            return None
    #Update amount value
    discount_rate = common.getSystemParam(key='discount_rate', default=0)
    serviceDetail.actual_amount = string.atof(discount_rate) * amount
    serviceDetail.amount = amount
    #TODO:Need to change them,after user have payed.
    # serviceDetail.start_date = datetime.datetime.now()
    # serviceDetail.end_date = datetime.datetime.now() + datetime.timedelta(months=1)
    serviceDetail.save()

    #Check if the app is verified before check out.
    if model.is_verified == False:
        initParam['payment_msg'] = _('The service is made, but can payment after app is verified. Please click verification to send request message to us.')
        initParam['selectItems'] = serviceDetail.serviceitem.all()
        initParam['serviceDetail'] = serviceDetail
        initParam['amount'] = serviceDetail.amount
        return None

    return redirect(reverse(initParam.get('nextPage'), kwargs={'pk': model.id}))


@transaction.commit_on_success
def saveVerification(request, form, model, *args, **kwargs):
    """Save the third register page - Verification."""
    if model is None:
        return None
    initParam = kwargs.get('initParam')
    try:
        ownerShipScan = appModels.OwnerShip_Scan.objects.get(app_id=model.id)
    except appModels.OwnerShip_Scan.DoesNotExist:
        ownerShipScan = appModels.OwnerShip_Scan()
        ownerShipScan.app_id = model.id
        ownerShipScan.save()
    initParam['verify_msg'] = _('The verification will be done later. Send the email to you after verified.')
    return None


@csrf_protect
@transaction.commit_on_success
def deleteAttachment(request, *args, **kwargs):
    """Delete the attachment of app by id, app_id etc."""
    data = {}
    try:
        dict = request.POST
    except:
        dict = request.GET
    try:
        attachment = appModels.Attachment.objects.get(id=dict.get('id'))
        attachment.delete()
        data['ok'] = 'true'
    except appModels.Attachment.DoesNotExist:
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


