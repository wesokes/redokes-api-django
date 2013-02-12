from pprint import pprint
from django.conf.urls import url
from redokes.request.parser import Parser
from redokes.response import Manager as ResponseManager
from django.http import Http404
from django.conf import settings


class Front(object):

    _app_directories = []
    _url_patterns = ['']
    _auto_discover = False

    def __init__(self, request, request_string, **kwargs):
        self.request_parser = Parser(request, request_string, **kwargs)
        self.response_manager = ResponseManager()
        self.controller_instance = None

    def run(self):
        #Build the import
        import_controller_name = self.request_parser.get_controller_name()
        import_controller_class_name = self.request_parser.get_controller_class_name()
        import_path = '{0}.controller.{1}'.format(self.request_parser.module, import_controller_name)

        paths = [import_path]
        paths += ['{0}.{1}'.format(path, import_path) for path in self._app_directories]
        
        #Try to import the controller
        controller = None

        for path in paths:
            try:
                controller = __import__(path, globals(), locals(), [import_controller_name], -1)
                self.request_parser.module = '.'.join(path.split('.')[:-2])
                self.controller_instance = getattr(controller, import_controller_class_name)(self)
            except:
                pass

            if self.controller_instance is not None:
                break

        if controller is None:
            #Raise a 404 if the controller is not found
            print import_path + " - controller class not found"
            raise Http404

        #Run the action
        self.controller_instance.run()
        return self.controller_instance.send_headers()

    @staticmethod
    def get_urls():
        if Front._auto_discover:
            Front._url_patterns = Front._url_patterns + [
                (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {
                    'url': '/static/index/img/favicon.ico'
                }),
                url(r'^((?!static).*)$', 'redokes.views.route')
            ]

        return Front._url_patterns

    @staticmethod
    def autodiscover(auto=True):
        Front._auto_discover = auto

        # get list of app directories
        paths = set()
        for path in settings.INSTALLED_APPS:
            parts = path.split('.')
            if len(parts) > 1:
                paths.add('.'.join(parts[:-1]))
        Front._app_directories = list(paths)

    @staticmethod
    def register_pattern(pattern=None, module=None, controller=None, action=None):
        config = {}
        if module:
            config['module'] = module
        if controller:
            config['controller'] = controller
        if action:
            config['action'] = action

        Front._url_patterns.append(
            url(r'^({0})$'.format(pattern), 'redokes.views.route', config)
        )

    @staticmethod
    def register_app_directory(name=None):
        Front._app_directories.append(name)
