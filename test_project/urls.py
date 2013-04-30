from django.conf.urls import patterns, include, url
from django.contrib import admin
from test_project.controllers import LastFmController, GitHubController

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^lastfm/', include(LastFmController.urls())),
    url(r'^github/', include(GitHubController.urls())),
)
