from django.conf.urls import patterns, include, url
from django.contrib import admin
from test_project.apps.test_subapp.controllers import MyController, MyApi

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^a/', include(MyController.urls())),
    url(r'^b/', include(MyApi.urls())),
)
