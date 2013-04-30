from redokes.controllers.base import ExternalApi


class LastFm(ExternalApi):

    def init_defaults(self):
        super(LastFm, self).init_defaults()
        self.api_url = 'http://ws.audioscrobbler.com/2.0/'
        self.api_key = None
        self.api_secret = None


class GitHub(ExternalApi):

    def init_defaults(self):
        super(GitHub, self).init_defaults()
        self.api_url = 'https://api.github.com/'