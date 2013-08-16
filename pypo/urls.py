from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login, logout_then_login

from readme import views

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pypo.views.home', name='home'),
    # url(r'^pypo/', include('pypo.foo.urls')),

    url(r'^$', login_required(views.IndexView.as_view()), name='index'),
    url(r'^add/$', login_required(views.AddView.as_view()), name='item_add'),
    url(r'^view/(?P<pk>\d+)$', login_required(views.ItemView.as_view()), name='item_view'),
    url(r'^accounts/login/$', login, name='login'),
    url(r'^accounts/logout/$', logout_then_login, name='logout'),


    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
