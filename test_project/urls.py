from django.conf.urls import patterns, include, url
from django.contrib import admin
from test_project.controllers import TestingAround

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^wes', include(TestingAround.urls()))
)
