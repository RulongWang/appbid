import json
import urllib
import datetime
import random
import string
import re
import os
import logging

from django.http import HttpResponse
from django.shortcuts import render_to_response, RequestContext, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.db import transaction
from django.conf import settings

from payment import models as paymentModels
from appbid import models as appModels
from order import models as orderModels
from seller import forms
from utilities import common

log = logging.getLogger('appbid')


@csrf_protect
@login_required(login_url='/usersetting/home/')
def registerApp(request, *args, **kwargs):
    """The common function for create, update app information."""
    app = None
    # initParam maybe save error message, when validate failed.
    initParam = kwargs.copy()
    flag = kwargs.get('flag')
    form = forms.AppForm()

    #Initial data
    if kwargs.get('pk'):
        app = get_object_or_404(appModels.App, pk=kwargs.get('pk'), publisher=request.user)
        form = forms.AppForm(instance=app)
        initParam['app_id'] = app.id
        initParam['app_status'] = app.status
        #For Additional Info
        if flag == 3:
            attachmentSize = string.atoi(common.getSystemParam(key='attachment_size', default=50000000))
            initParam['attachmentSize'] = attachmentSize / 1000000
            initParam['attachments'] = appModels.Attachment.objects.filter(app_id=app.id)
        #For App Verification
        if flag == 7:
            initParam['verify_token'] = app.verify_token
        #For App Attributes
        if flag == 1.2:
            appInfos = appModels.AppInfo.objects.filter(app_id=app.id)
            if appInfos:
                initParam['appInfoForm'] = forms.AppInfoForm(instance=appInfos[0])
        #For Payment
        if flag == 6:
            initParam['serviceItems'] = orderModels.ServiceItem.objects.filter(end_date__gte=datetime.datetime.now())
            serviceDetails = orderModels.ServiceDetail.objects.filter(app_id=app.id).order_by('-pk')
            sn = kwargs.get('sn', None)
            if sn and sn != 'new':
                #For query service detail by sn.
                serviceDetail = get_object_or_404(orderModels.ServiceDetail, app_id=app.id, sn=sn)
                initParam['selectItems'] = serviceDetail.serviceitem.all()
                initParam['serviceDetail'] = serviceDetail
                initParam['amount'] = serviceDetail.amount
            elif (sn is None or sn == '') and serviceDetails:
                #For query the latest payment. The rule: Publisher just has one unpaid payment.
                initParam['selectItems'] = serviceDetails[0].serviceitem.all()
                initParam['serviceDetail'] = serviceDetails[0]
                initParam['amount'] = serviceDetails[0].amount
            else:
                #Create the new payment.
                amount = 0
                serviceItems = orderModels.ServiceItem.objects.filter(is_basic_service=True, end_date__gte=datetime.datetime.now())
                for serviceItem in serviceItems:
                    amount += serviceItem.price
                initParam['amount'] = amount
    #Get app Nav status.
    appNavStatus(app=app, initParam=initParam)

    #Create or update app.
    if request.method == "POST":
        form = forms.AppForm(request.POST)
        saveMethod = kwargs.pop('saveMethod', None)
        if form.is_valid() and saveMethod:
            result = saveMethod(request, form, app, initParam=initParam)
            if result:
                return result

    #Initial data
    initParam['form'] = form
    if flag == 3:
        initParam['attachmentForm'] = forms.AttachmentForm()
    if flag == 1.1:
        initParam['apps'] = appModels.App.objects.filter(publisher=request.user, status=1).order_by('create_time')
    return render_to_response(kwargs.get('backPage'), initParam, context_instance=RequestContext(request))


def appNavStatus(*args, **kwargs):
    """Get app nav status."""
    app = kwargs.get('app')
    initParam = kwargs.get('initParam')
    if app:
        initParam['app_store_link'] = 'green'
        initParam['app_store_info'] = 'green'
        if app.dl_amount >= 0 or app.revenue >= 0:
            initParam['marketing'] = 'green'
        else:
            initParam['marketing'] = 'grey'
        initParam['additional_info'] = 'green'
        if app.begin_price >= 0:
            initParam['sale'] = 'green'
        else:
            initParam['sale'] = 'grey'
        initParam['delivery'] = 'green'
        if orderModels.ServiceDetail.objects.filter(app_id=app.id, is_payed=True).count():
            initParam['payment'] = 'green'
        else:
            initParam['payment'] = 'grey'
        if app.is_verified:
            initParam['verification'] = 'green'
        else:
            initParam['verification'] = 'grey'
    else:
        initParam['app_store_link'] = 'grey'



@transaction.commit_on_success
def saveAppStoreLink(request, form, model, *args, **kwargs):
    """Save the first register page - AppleStore Link."""
    initParam = kwargs.get('initParam')
    # The app in status=3 can not be edit.
    if model and model.status == 3:
        return redirect(reverse(initParam.get('nextPage'), kwargs={'pk': model.id}))

    title = form.cleaned_data['title'].strip()
    app_store_link = form.cleaned_data['app_store_link'].strip()
    if title == "" or app_store_link == "":
        return None

    #Verify whether the draft app exist.
    if model:
        if appModels.App.objects.filter(publisher_id=request.user.id, status=1,
                                        app_store_link__iexact=app_store_link).exclude(pk=model.id).count():
            initParam['error_msg'] = _('App with link %(param1)s has existed in your draft apps.') % {'param1': app_store_link}
            return None
    elif appModels.App.objects.filter(publisher_id=request.user.id, status=1,
                                      app_store_link__iexact=app_store_link).count():
        initParam['error_msg'] = _('App with link %(param1)s has existed in your draft apps.') % {'param1': app_store_link}
        return None

    try:
        pattern = re.compile(r'^https://itunes.apple.com/[\S+/]+id(\d+)')
        match = pattern.match(app_store_link)
        if match is None:
            raise
        result = common.getITunes(match.group(1))
        if result is None:
            raise
    except Exception, e:
        initParam['error_msg'] = _('Link %(param)s is not correct.') % {'param': ''}
        log.error(_('The app store link %(param)s is not correct.') % {'param': match.group(1)})
        log.error(e.message)
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
        model.title = title
        model.app_store_link = app_store_link
    model.rating = result.get('averageUserRating', 0)
    model.platform_version = result.get('version', None)
    model.apple_id = result.get('trackId', None)
    model.app_name = result.get('trackName', None)
    model.web_site = result.get('sellerUrl', None)
    model.reviews = result.get('userRatingCount', None)
    model.description = result.get('description', None)
    model.seller_name = result.get('sellerName', None)
    model.artist_id = result.get('artistId', None)
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
            #Shrink image From (1024*1024) to (200*200)
            common.imageThumbnail(path=path, size=(200, 200))
        elif result.get('artworkUrl100', None):
            urllib.urlretrieve(result.get('artworkUrl100', None), path)
        elif result.get('artworkUrl60', None):
            urllib.urlretrieve(result.get('artworkUrl60', None), path)
    except Exception, e:
        initParam['error_msg'] = _('Link %(param)s is not correct.') % {'param': ''}
        log.error(_('The app store link %(param)s is not correct.') % {'param': match.group(1)})
        log.error(e.message)
        return None
    appInfo.icon = '/'.join([str(model.publisher.id), str(model.id), 'Icon.jpg'])

    #Make the image of two dimension code for app store link
    if appInfo.app_store_link_code is None:
        app_store_link_code = '/'.join([str(model.publisher.id), str(model.id), 'app_store_link_code.jpg'])
        path = '/'.join([settings.MEDIA_ROOT, app_store_link_code])
        common.makeTwoDimensionCode(data=model.app_store_link, path=path)
        appInfo.app_store_link_code = app_store_link_code

    #Make the image of two dimension code for app detail link
    if appInfo.app_detail_code is None:
        data = '/'.join([common.getHttpHeader(request), 'query/app-detail', str(model.id)])
        app_detail_code = '/'.join([str(model.publisher.id), str(model.id), 'app_detail_code.jpg'])
        path = '/'.join([settings.MEDIA_ROOT, app_detail_code])
        common.makeTwoDimensionCode(data=data, path=path)
        appInfo.app_detail_code = app_detail_code

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
    kind = result.get('kind', None)
    model.device.clear()
    if kind and kind == 'software':
        for device in appModels.Device.objects.all():
            for deviceName in result.get('supportedDevices'):
                if deviceName.find(device.device) != -1:
                    model.device.add(device)
                    break
    elif kind and kind == 'mac-software':
        device = appModels.Device.objects.get(device='MAC')
        model.device.add(device)

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

    # The app in status=3 can not be edit.
    if model.status != 3:
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
    # The app in status=3 can not be edit.
    if model.status == 3:
        return redirect(reverse(initParam.get('nextPage'), kwargs={'pk': model.id}))

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
            if path.name.endswith('.txt') and path.content_type == 'text/plain':
                attachment.type = 1
            elif path.content_type.startswith('image'):
                attachment.type = 2
            elif path.name.endswith('.pdf') and path.content_type == 'application/pdf':
                attachment.type = 3
            # elif path.name.endswith('.doc') and path.content_type == 'application/msword':
            #     attachment.type = 4
            # elif path.name.endswith('.xls') and path.content_type == 'application/vnd.ms-excel':
            #     attachment.type = 4
            # elif path.name.endswith('.ppt') and path.content_type == 'application/vnd.ms-powerpoint':
            #     attachment.type = 4
            else:
                initParam['attachmentError'] = _('The file type of %(param)s does not supported.') % {'param': path.name}
                return None
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
    # The app in status =2 and status=3 can not be edit.
    if model.status == 1:
        one_price = form.cleaned_data['one_price']
        reserve_price = form.cleaned_data['reserve_price']
        if one_price and reserve_price and one_price > reserve_price:
            initParam['error_msg'] = _('Reserve price should be greater than one price.')
            return None
        model.begin_price = form.cleaned_data['begin_price']
        model.one_price = one_price
        model.reserve_price = reserve_price
        model.currency_id = form.cleaned_data['currency']
        model.minimum_bid = form.cleaned_data['minimum_bid']
        model.save()
    return redirect(reverse(initParam.get('nextPage'), kwargs={'pk': model.id}))


@transaction.commit_on_success
def saveDelivery(request, form, model, *args, **kwargs):
    """Save the third register page - Delivery."""
    if model is None:
        return None

    initParam = kwargs.get('initParam')
    # The app in status=3 can not be edit.
    if model.status != 3:
        model.unique_sell = form.cleaned_data['unique_sell']
        model.source_code = form.cleaned_data['source_code']
        model.delivery_detail = form.cleaned_data['delivery_detail'].strip()
        model.web_site = form.cleaned_data['web_site']
        model.save()
        #Save the app updating.
        appHistory = appModels.AppHistory()
        appHistory.app = model
        appHistory.content = ''.join(['unique_sell:', str(model.unique_sell), '; source_code:', str(model.source_code),
                                     '; delivery_detail:', model.delivery_detail, ' web_site:', model.web_site])
        appHistory.save()
    return redirect('/'.join([initParam.get('nextPage'), str(model.id), kwargs.get('sn', '')]))


@transaction.commit_on_success
def saveService(request, form, model, *args, **kwargs):
    """Save the third register page - Service."""
    if model is None:
        return None
    initParam = kwargs.get('initParam')
    sn = request.POST.get('sn')
    if sn:
        serviceDetail = get_object_or_404(orderModels.ServiceDetail, app_id=model.id, sn=sn)
        serviceDetail.serviceitem.clear()
    else:
        #Check if there is the unpaid payment, before create the new one.
        serviceDetails = model.servicedetail_set.filter(is_payed=False)
        if serviceDetails:
            serviceDetail = serviceDetails[0]
            serviceDetail.serviceitem.clear()
        else:
            #Create the new service detail.
            serviceDetail = orderModels.ServiceDetail()
            serviceDetail.app_id = model.id
            serviceDetail.is_payed = False
            serviceDetail.sn = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            serviceDetail.save()

    #Save service items
    amount = 0
    for id in request.POST.getlist('serviceItem_id'):
        try:
            serviceItem = orderModels.ServiceItem.objects.get(id=id)
            amount += serviceItem.price
            serviceDetail.serviceitem.add(serviceItem)
        except orderModels.ServiceItem.DoesNotExist:
            return None
    #Update amount value
    discount_rate = common.getSystemParam(key='discount_rate', default=1)
    serviceDetail.actual_amount = string.atof(discount_rate) * amount
    serviceDetail.amount = amount
    serviceDetail.save()

    #Check if the app is verified before check out.
    if not model.is_verified:
        initParam['payment_msg'] = _('The service is made, but can payment after app is verified. Please click \'App Verification\' to send verification request to us.')
        initParam['selectItems'] = serviceDetail.serviceitem.all()
        initParam['serviceDetail'] = serviceDetail
        initParam['amount'] = serviceDetail.amount
        return None

    #Check if user's payment account is set.
    acceptGateway = paymentModels.AcceptGateway.objects.filter(user_id=request.user.id, is_active=True, is_default=True).count()
    if acceptGateway == 0:
        #Go back this page, after payment account setting.
        next = '/'.join(['order/checkout', str(model.id), str(serviceDetail.id), str(serviceDetail.sn)])
        #redirect payment account setting page.
        page_url = '/'.join(['/usersetting/payment-setting', next])
        return redirect(page_url)

    return redirect(reverse(initParam.get('nextPage'), kwargs={'app_id': model.id, 'service_id': serviceDetail.id, 'service_sn': serviceDetail.sn}))


@transaction.commit_on_success
def saveVerification(request, form, model, *args, **kwargs):
    """Save the third register page - Verification."""
    if model is None or model.status == 3:
        return None
    initParam = kwargs.get('initParam')
    if model.is_verified is True:
        initParam['verify_msg'] = _('The app has been verified successfully. No need verify again.')
        return None
    try:
        ownerShipScan = appModels.OwnerShip_Scan.objects.get(app_id=model.id)
        ownerShipScan.times = 0
        ownerShipScan.save()
    except appModels.OwnerShip_Scan.DoesNotExist:
        ownerShipScan = appModels.OwnerShip_Scan()
        ownerShipScan.app_id = model.id
        ownerShipScan.times = 0
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
