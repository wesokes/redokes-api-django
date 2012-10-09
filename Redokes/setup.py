setup(
    name = "Redokes",
    version = "0.1",
    packages = [
        "redokes",
        "redokes.controller",
        "redokes.database",
        "redokes.request",
        "redokes.templatetags"
    ],
    url = "https://github.com/redokes/redokes-api-django",
    description = "Redokes Framework.",
    long_description = open('README.md').read(),
    install_requires = [
        "django>=1.4",
        "python-memcached",
        "django_extensions",
        "ipython",
        "beautifulsoup4",
        "jsonpickle",
    ]
)

