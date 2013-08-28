from django.conf.urls import patterns, include, url
from query.views import register_app,getDetail, list_latest

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin


urlpatterns = patterns('',
    # Examples:
    #home
    #url(r'^$', 'home.views.hello', name='hello'),
    # url(r'^appbid/', include('appbid.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),
    #url(r'^test/$', test, name='goodtest')
    #homepage
    #url(r'^register_app/$', register_app, name="register_app")
    url(r'^app-detail/(?P<pk>\d*)$', getDetail, name='app_detail'),
    url(r'^app-list/$', list_latest, name='app_list'),

)
