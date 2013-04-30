from django.conf.urls import patterns, include, url
from django.contrib import admin
from test_project.controllers import TestingAround, Wes

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^wes/', include(TestingAround.urls())),
    url(r'^wes2/', include(Wes.urls())),
    url(r'^subapp/', include('test_project.apps.test_subapp.urls')),
)
