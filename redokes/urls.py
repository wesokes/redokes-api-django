from django.conf.urls import patterns, url
from redokes.controller.front import Front

urlpatterns = patterns(*Front.get_urls())
