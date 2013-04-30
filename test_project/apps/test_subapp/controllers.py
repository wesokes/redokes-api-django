from redokes.controllers.base import Api, Action


class MyController(Action):

    def index__action(self):
        self.set_response_param('testing', 'my template var')


class MyApi(Api):

    def index__action(self):
        self.set_response_param('param', 'just some param')

    def custom__action(self):
        self.set_response_param('custom', 'just a custom param')

    def error__action(self):
        self.add_error('fake error')

