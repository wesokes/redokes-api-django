import json
from pprint import pprint
from redokes.controllers.base import Api, Action
from redokes.controllers.thirdparty import LastFm, GitHub
import requests


class TestingAround(Api):

    def index__action(self):
        self.set_response_param('testing', 'just a test')

    def index2__action(self):
        self.set_response_param('testing2', 'just another test')


class Wes(Action):

    def index__action(self):
        pass


class LastFmController(LastFm):

    def init_defaults(self):
        super(LastFmController, self).init_defaults()


    def index__action(self):
        self.set_response_param('api_key', self.api_key)
        response = requests.get(self.api_url)


class GitHubController(GitHub):

    def init_defaults(self):
        super(GitHubController, self).init_defaults()


    def index__action(self):
        api_url = 'https://api.github.com/user/repos'
        response = requests.get(
            api_url,
            params={
                'sort': 'pushed',
                'direction': 'desc'
            },
            auth=(
                
            )
        )
        self.set_response_param('response', json.loads(response.text))

