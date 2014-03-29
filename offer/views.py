__author__ = 'jia.qianpeng'

import os

from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, RequestContext, redirect, get_object_or_404, Http404
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.conf import settings
from offer import models as offerModels
from offer import forms as offerForms
from utilities import common


@csrf_protect
@login_required(login_url='/usersetting/home/')
def registerOffer(request, *args, **kwargs):
    """The function for create, update offer information."""
    offer = None
    initParam = {}
    form = offerForms.OfferForm()

    #Initial data
    if kwargs.get('pk'):
        offer = get_object_or_404(offerModels.Offer, pk=kwargs.get('pk'), publisher_id=request.user.id)
        form = offerForms.OfferForm(instance=offer)

    #Create or update offer.
    if request.method == "POST":
        form = offerForms.OfferForm(request.POST, instance=offer)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.publisher = request.user
            offer.save()

            offer.position.clear()
            for position in form.cleaned_data['position']:
                offer.position.add(position)

            company_icon = request.FILES.get('company_icon')
            if company_icon:
                if company_icon.content_type.startswith('image'):
                    if company_icon.size > 1000000:
                        initParam['error'] = _('The image size must be not larger than 1M.')
                    else:
                        path = '/'.join([settings.MEDIA_ROOT, str(request.user.id)])
                        if os.path.exists(path) is False:
                            os.makedirs(path)
                        if offer.company_icon:
                            path = '/'.join([settings.MEDIA_ROOT, str(offer.company_icon)])
                            if os.path.exists(path):
                                os.remove(path)
                        offer.company_icon = company_icon
                        offer.save()
                        if company_icon:
                            #Shrink image to (50*50) for offer company_icon.
                            path = '/'.join([settings.MEDIA_ROOT, str(offer.company_icon)])
                            common.imageThumbnail(path=path, size=[100, 100])
                        initParam['msg'] = _('The offer has been created successful.')
                        return redirect(reverse('offer:offer_detail', kwargs={'pk': offer.id}))
                else:
                    initParam['error'] = _('The file type of %(param)s is not supported.') % {'param': company_icon.name}
            else:
                initParam['msg'] = _('The offer has been created successfully.')
                return redirect(reverse('offer:offer_detail', kwargs={'pk': offer.id}))
    initParam['form'] = form
    return render_to_response("offer/register_offer.html", initParam, context_instance=RequestContext(request))


@csrf_protect
def offerDetail(request, *args, **kwargs):
    """Get offer detail info."""
    if kwargs.get('pk'):
        initParam = {}
        offer = get_object_or_404(offerModels.Offer, pk=kwargs.get('pk'))
        if not offer.status and request.user != offer.publisher:
            raise Http404
        initParam['offer'] = offer
        initParam['type'] = offerModels.Offer.OFFER_TYPES[offer.type-1][1]
        positions = []
        for position in offer.position.all():
            positions.append(position.name)
        initParam['positions'] = positions
        offerRecords = offerModels.OfferRecord.objects.filter(offer_id=offer.id).all()
        viewCount = 0
        applyCount = 0
        if request.user.id is None or request.user != offer.publisher:
            if offerRecords:
                offerRecord = offerRecords[0]
                offerRecord.view_count += 1
            else:
                offerRecord = offerModels.OfferRecord()
                offerRecord.offer = offer
                offerRecord.view_count = 1
                offerRecord.apply_count = 0
            offerRecord.save()
            viewCount = offerRecord.view_count
            applyCount = offerRecord.apply_count
        else:
            if offerRecords:
                viewCount = offerRecords[0].view_count
                applyCount = offerRecords[0].apply_count
        initParam['viewCount'] = viewCount
        initParam['applyCount'] = applyCount
        return render_to_response('offer/offer_detail.html', initParam, context_instance=RequestContext(request))
    raise Http404


@csrf_protect
def offerList(request, *args, **kwargs):
    initParam = {}
    page = request.GET.get('page', 1)
    offers = offerModels.Offer.objects.filter(status=True)
    initParam['offers'] = queryAppsWithPaginator(request, page=page, offers=offers)
    return render_to_response('offer/offer_list.html', initParam, context_instance=RequestContext(request))


def queryAppsWithPaginator(request, *args, **kwargs):
    """Offer query function"""
    page_range = kwargs.get('page_range')
    page = kwargs.get('page', 1)
    offers = kwargs.get('offers')
    if page_range is None:
        page_range = common.getSystemParam(key='page_range', default=10)
    if offers:
        offer_list = []
        for offer in offers:
            #info list[0]:The offer info
            info_list = [offer]
            offer_list.append(info_list)

        paginator = Paginator(offer_list, page_range)
        try:
            offerInfoList = paginator.page(page)
        except PageNotAnInteger:
            offerInfoList = paginator.page(1)
        except EmptyPage:
            offerInfoList = paginator.page(paginator.num_pages)
        #Query offer record showed in the current page.
        for info_list in offerInfoList:
            info_list.append(offerModels.Offer.OFFER_TYPES[info_list[0].type-1][1])
            records = offerModels.OfferRecord.objects.filter(offer_id=info_list[0].id)
            if records:
                info_list.append(records[0].view_count)
                info_list.append(records[0].apply_count)
            else:
                info_list.append(0)
                info_list.append(0)
    else:
        return None

    return offerInfoList


@csrf_protect
@login_required(login_url='/usersetting/home/')
def myOfferList(request, *args, **kwargs):
    print ''