from redokes.controllers import Api, Action


class TestingAround(Api):

    def index__action(self):
        print 'index test'
        self.set_response_param('testing', 'just a test')


class WesController(Action):

    def index__action(self):
        print 'index test'

