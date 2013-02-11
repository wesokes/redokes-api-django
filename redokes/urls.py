from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {
        'url': '/static/index/img/favicon.ico'
    }),
    url(r'^((?!static).*)$', 'redokes.views.route')
)
