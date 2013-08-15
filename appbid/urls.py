from django.conf.urls import patterns, include, url
from django.contrib import admin
from home.views import hello
from home.tests import test
import seller.urls
import seller.views
import account.urls
import account.views



# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    #home
    url(r'^$', 'home.views.home', name='home'),
    # url(r'^appbid/', include('appbid.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^test/$', test, name='goodtest'),
    url(r'^seller/', include(seller.urls, namespace='seller')),
    url(r'^searchItunes/$',seller.views.searchItunes),
    url(r'^account/',include(account.urls,namespace='account')),
    #homepage

)
