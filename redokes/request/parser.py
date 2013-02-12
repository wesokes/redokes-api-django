import logging
import json
from redokes.config.redokes import RedokesConfig


class Parser(object):

    def init_defaults(self):
        self.logger = None
        self.request = None
        self.params = {}
        self.args = []
        self.request_string = ''
        self.module = None
        self.controller = None
        self.action = None

    def __init__(self, request, request_string, *args, **kwargs):
        self.init_defaults()
        self.request = request
        self.request_string = request_string

        self.url_args = args
        self.url_kwargs = kwargs

        self.update_request_params(request)

        # check for json param to decode
        if 'json' in self.params:
            try:
                # try to decode the value of json
                json_decoded = json.loads(self.params['json'])

                # update the request params with the decoded json values
                self.update_params(json_decoded)

                # delete the string from the request params
                del self.params['json']
            except ValueError:
                pass

        self.logger = logging.getLogger("nooga")

        self.parse(self.request_string)

        self.module = kwargs.get('module', self.module)
        self.controller = kwargs.get('controller', self.controller)
        self.action = kwargs.get('action', self.action)

        config = RedokesConfig.getConfig()
        self.module = self.module or config['default_module']
        self.controller = self.controller or config['default_controller']
        self.action = self.action or config['default_action']

    def update_request_params(self, request):

         # copy get params
        for key, value in request.GET.lists():
            if len(value) == 1:
                value = value[0]
            self.set_param(key, value)

        # copy post params
        for key, value in request.POST.lists():
            if len(value) == 1:
                value = value[0]
            self.set_param(key, value)

    def parse(self, request_string):
        request_string = request_string.strip('/')

        # check if we matched specific parts of the url to be module/controller/action
        num_url_args = len(self.url_args)

        components = [
            'module',
            'controller',
            'action'
        ]

        component_index = 0
        while component_index < num_url_args:
            setattr(self, components[component_index], self.url_args[component_index].replace('/', '.'))
            request_string = request_string.replace(self.url_args[component_index], '')
            request_string = request_string.strip('/')
            component_index += 1

        #Process the request string
        route_list = request_string.split('/')
        route_index = 0
        num_route_parts = len(route_list)
        while route_index < num_route_parts:
            if len(route_list[route_index]):
                if getattr(self, components[component_index]) is None:
                    setattr(self, components[component_index], route_list[route_index])
            route_index += 1
            component_index += 1

        #Look for any extra key values in the url
        extra_parts = route_list[3:]
        self.args = extra_parts
        extra_params = {}
        for i in range(0, len(extra_parts), 2):
            if (i + 1) < (len(extra_parts)):
                extra_params[extra_parts[i]] = extra_parts[i + 1]
            elif len(extra_parts[i]):
                extra_params[extra_parts[i]] = False

        self.update_params(extra_params)

        return {
            "module": self.module,
            "controller": self.controller,
            "action": self.action
        }

    def get_url(self):
        return "/".join([self.module, self.controller, self.action])

    def set_params(self, params):
        self.params = params
        return self

    def update_params(self, params):
        self.params.update(params)
        return self

    def set_param(self, key, value=False):
        self.params[key] = value
        return self

    def get_param(self, key, default_value=None):
        if key in self.params:
            return self.params[key]
        return default_value

    def get_params(self):
        return self.params

    def get_module_name(self, name=False):
        if name is False:
            name = self.module
        parts = name.split('-')
        for i in range(len(parts)):
            parts[i] = parts[i].capitalize()
        return ''.join(parts)

    def get_controller_name(self, name=False):
        if name is False:
            name = self.controller
        parts = name.split('-')
        return '_'.join(parts)

    def get_controller_class_name(self, name=False):
        if name is False:
            name = self.controller
        parts = name.split('-')
        for i in range(len(parts)):
            parts[i] = parts[i].capitalize()
        return ''.join(parts)

    def get_action_name(self, name=False):
        if name is False:
            name = self.action
        name = name.lower()
        parts = name.split('-')
        action_name = '_'.join(parts)
        if (len(action_name)):
            return '%s_action' % action_name
        return False
