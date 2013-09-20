
from django.conf.urls import patterns, url
from query import views

urlpatterns = patterns('',
    url(r'^app-detail/(?P<pk>\d*)$', views.getDetail, name='app_detail'),
    url(r'^bid-info/(?P<pk>\d*)$', views.getBidInfo, name='bid_info'),
    url(r'^app-list/$', views.list_latest, name='app_list'),
    url(r'^most_active/$', views.most_active, name='most_active'),
    url(r'^ending_soon/$', views.list_ending_soon, name='ending_soon'),
    url(r'^just_sold/$', views.list_just_sold, name='just_sold'),
    url(r'^featured$', views.listFeatured, name='featured'),
)
