from django.conf.urls import patterns, include, url
from django.contrib import admin, comments
from django.conf import settings
from django.conf.urls.static import static
from home.views import hello
from home.tests import test
import seller.urls
import usersetting.urls
import query.urls
import bid.urls


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
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^test/$', test, name='goodtest'),
    url(r'^seller/', include(seller.urls, namespace='seller')),
    url(r'^searchItunes/$', seller.views.searchItunes),
    url(r'^usersetting/', include(usersetting.urls, namespace='usersetting')),
    url(r'^query/', include(query.urls, namespace='query')),
    url(r'^bid/', include(bid.urls, namespace='bid')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
