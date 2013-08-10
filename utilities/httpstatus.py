__author__ = 'rulongwang'
from appbid.models import App
from django.shortcuts import render
from django.http import Http404
# ...
def detail(request, app_id):
    try:
        poll = App.objects.get(pk=app_id)
    except App.DoesNotExist:
        raise Http404
    return render(request, 'polls/detail.html', {'poll': poll})