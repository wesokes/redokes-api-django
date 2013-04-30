from redokes.controllers import Api, Action


class TestingAround(Api):

    def index__action(self):
        self.set_response_param('testing', 'just a test')

    def index2__action(self):
        self.set_response_param('testing2', 'just another test')


class Wes(Action):

    def index__action(self):
        pass

