
from django.conf.urls import patterns, url
from query import views

urlpatterns = patterns('',
    url(r'^app-detail/(?P<pk>\d*)$', views.getAppDetail, name='app_detail'),
    url(r'^app-detail-comment/(?P<pk>\d*)$', views.addCommentForApp, name='app_detail_comment'),
    url(r'^bid-info/(?P<pk>\d*)$', views.getBidInfo, name='bid_info'),
    url(r'^featured$', views.listFeatured, name='featured'),
    url(r'^list-latest/$', views.listLatest, name='list_latest'),
    url(r'^most-active/$', views.mostActive, name='most_active'),
    url(r'^ending-soon/$', views.endingSoon, name='ending_soon'),
    url(r'^just-sold/$', views.justSold, name='just_sold'),
    url(r'^list-all/$', views.listAll, name='list_all'),
)
