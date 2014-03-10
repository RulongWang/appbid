__author__ = 'jia.qianpeng'

import os

from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, RequestContext, redirect, get_object_or_404, Http404
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

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
            offer.position = form.cleaned_data['position']
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
                        form = offerForms.OfferForm(instance=offer)
                        offer.save()
                        if company_icon:
                            #Shrink image to (50*50) for offer company_icon.
                            path = '/'.join([settings.MEDIA_ROOT, str(offer.company_icon)])
                            common.imageThumbnail(path=path, size=[50, 50])
                        initParam['msg'] = _('The offer has been created successful.')
                        return redirect(reverse('offer:offer_detail', kwargs={'pk': offer.id}))
                        #('/'.join(['/job/offer-detail', str(offer.id)]))
                else:
                    initParam['error'] = _('The file type of %(param)s is not supported.') % {'param': company_icon.name}
            else:
                offer.save()
                initParam['msg'] = _('The offer has been created successfully.')
                return redirect(reverse('offer:offer_detail', kwargs={'pk': offer.id}))
                #redirect(reverse('job:offer_detail', kwargs={'pk': offer.id}))
                # '/'.join(['/job/offer-detail', str(offer.id)])
    initParam['form'] = form
    return render_to_response("offer/register_offer.html", initParam, context_instance=RequestContext(request))


@csrf_protect
def offerDetail(request, *args, **kwargs):
    """Get offer detail info."""
    if kwargs.get('pk'):
        initParam = {}
        offer = get_object_or_404(offerModels.Offer, pk=kwargs.get('pk'))
        initParam['offer'] = offer
        initParam['type'] = offerModels.Offer.OFFER_TYPES[offer.type-1][1]
        positions = []
        for position in offer.position.all():
            positions.append(position.name)
        initParam['positions'] = positions
        return render_to_response('offer/offer_detail.html', initParam, context_instance=RequestContext(request))
    raise Http404