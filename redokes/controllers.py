import inspect
from optparse import OptionParser
import os
from pprint import pprint
from django import template
from django.conf import settings
from django.conf.urls import url, patterns
from django.contrib.auth.models import Group
from django.forms import model_to_dict
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import feedgenerator
from redokes.request.parser import Parser
from redokes.response import Manager as ResponseManager
import redokes.util
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden, HttpResponse


class Action(object):

    util = redokes.util

    def init_defaults(self):
        self.request = None
        self.action = None
        self.response_manager = ResponseManager()
        self.parser = None
        self.template = None
        self.redirect = None
        self.do_render = True
        # self.front_controller = None
        # self._front_controller = None
        self.auto_template = True
        self.output_type = 'html'
        self.access = None

    def __init__(self, **kwargs):
        self.init_defaults()

        #Setup items we get from front controller
        # self.front_controller = front_controller
        # self.request = front_controller.request_parser.request
        # self.parser = front_controller.request_parser

        #Apply the kwargs
        self.util.apply_config(self, kwargs)
        #Set the front controller to be in the template
#        self.set_response_param('_front_controller', self.front_controller)
        #Initialize the logger
#        self.logger = logging.getLogger("nooga")

        #Run the init method
        self.init()

         # check if we need to automatically set the template
        # if self.auto_template:
        #     self.auto_set_template()

    def init(self):
        pass

    @classmethod
    def get_methods(cls):
        return inspect.getmembers(cls, predicate=inspect.ismethod)

    @classmethod
    def get_action_method_names(cls):
        method_names = []
        methods = cls.get_methods()
        for method_name, method in methods:
            if '__action' in method_name:
                method_names.append(method_name[:-8])
        return method_names

    @classmethod
    def urls(cls):
        pattern_list = []
        for method_name in cls.get_action_method_names():
            pattern_list.append((r'(?P<action>{0})'.format(method_name), cls.route))
        url_patterns = patterns(
            '',
            *pattern_list
        )
        return url_patterns

    def dispatch_action(self, request=None, action=None):
        """
        Checks if the action exists and invokes the method for the action
        @param request: the django request object
        @type request: HttpRequest
        @param action: the action to be performed as determined by the url
        @type action: str
        """
        if request is not None:
            self.request = request
        if action is not None:
            self.action = action
        method_name = '{0}__action'.format(self.action)
        if hasattr(self, method_name):
            getattr(self, method_name)()

    @classmethod
    def route(cls, request, **kwargs):
        """
        @param request: the django request object
        @type request: HttpRequest
        @param kwargs: additional params
        @type kwargs: dict
        @return: the django response object
        @rtype: HttpResponse
        """
        action = kwargs.get('action')
        api = cls(request=request, action=action)
        api.dispatch_action()
        return api.get_response()

    def user_can_access(self, method_name):
        # Check if all methods are public
        if self.access is None:
            return True
        else:
            # Get the logged in user
            user = self.get_user()

            # Methods are private so check access
            permissions = ['admin']
            permission_info = {}

            # Check if specific method access is defined
            if method_name in self.access:
                permission_info = self.access[method_name]
            elif '*' in self.access:
                permission_info = self.access['*']

            #Check if not none and reset
            if permission_info is not None:
                permissions = []

            #Add all permissions
            if type(permission_info) is str:
                permissions.append(permission_info)
            elif permission_info is not None:
                # check group
                if 'group' in permission_info:
                    # check if user is in group
                    groups = permission_info['group']
                    if type(groups) is str:
                        groups = [groups]
                    group_set = Group.objects.filter(name__in=groups).prefetch_related()
                    for group in group_set:
                        group_permissions = list(group.permissions.all())
                        permissions = permissions + group_permissions

                # check access
                if 'access' in permission_info:
                    access_list = permission_info['access']
                    if type(access_list) is str:
                        access_list = [access_list]
                    permissions = permissions + access_list

                    if "admin" in permissions:
                        if not user.is_superuser:
                            return False
            else:
                permissions = None

            # Check perms
            if permissions is None:
                return True
            elif not len(permissions):
                return False
            else:
                return user.has_perms(permissions)

    def get_template_name(self):
        return '%s/%s/%s.html' % (self.parser.module.replace('.', '/'), self.parser.controller, self.parser.action)

    def get_template_names(self):
        names = []
        return []
        parts = [self.parser.controller, '{0}.html'.format(self.parser.action)]
        for i in range(len(parts)):
            names.append('/'.join(parts[i:]))
        return names

    def auto_set_template(self):
#        self.set_template(self.get_template_name())
        self.set_templates(self.get_template_names())

    def set_template(self, template_name):
        if self.template_exists(template_name):
            self.template = template_name
            return self.template

        return None

    def set_templates(self, template_names):
        for template_name in template_names:
            if self.template_exists(template_name):
                self.template = template_name
                return self.template

        return None

    def template_exists(self, template_name):
        try:
            template.loader.get_template(template_name)
            return True
        except template.TemplateDoesNotExist:
            return False
        return False

    def run(self):
        return self.action_call()

    def catch(self):
        """
        Catches an unknown action.
        By default all this method will do is raise a 404 error.
        Override to provide custom redirection
        """
        raise Http404

    def forward(self, action, module=None, controller=None):
        self.parser.action = action
        if module is not None:
            self.parser.module = module
        if controller is not None:
            self.parser.controller = controller
        return self.front_controller.run()

    def action_call(self):
        """
        Calls an action if it exists, or else calls the catch method
        """
        #Check if the action exists
        if self.action_exists() is False:
            return self.catch()

        # Check permissions
        if self.user_can_access(self.get_action_method_name()):
            #Run the action method
            return getattr(self, self.get_action_method_name())()
        else:
            self.output_type = '403'

    def get_action_method_name(self):
        return self.front_controller.request_parser.get_action_name(self.parser.action)

    def action_exists(self):
        #Check if the view instance has the action
        return hasattr(self, self.get_action_method_name())

    def render_template(self, template, context):
        return render_to_response(template, context, context_instance=RequestContext(self.request))

    def set_response_param(self, key, value=None):
        self.response_manager.set_param(key, value)

    def set_response_params(self, params):
        self.response_manager.set_params(params)

    def update_response_params(self, params):
        self.response_manager.update_params(params)

    def get_response_param(self, key, value=None):
        return self.response_manager.get_param(key, value)

    def get_response_params(self):
        return self.response_manager.get_params()

    def get_response(self):
        method_name = 'get_output_%s' % self.output_type
        if hasattr(self, method_name):
            return getattr(self, method_name)()

    def get_output_html(self):
        return self.render_template(self.template, self.get_response_params())

    def get_output_403(self):
        return HttpResponseForbidden("Default 403 template")

    def set_redirect(self, url):
        self.redirect = url
        self.output_type = 'redirect'

    def get_output_redirect(self):
        return HttpResponseRedirect(self.redirect)

    def set_request_param(self, key, value):
        self.front_controller.request_parser.set_param(key, value)

    def get_request_param(self, key, value=None):
        return self.front_controller.request_parser.get_param(key, value)

    def get_request_params(self):
        return self.front_controller.request_parser.params

    def get_user(self):
        return self.front_controller.request_parser.request.user

    def get_cache_key(self, *args, **kwargs):
        return self.generate_cache_key(self, self.front_controller.request_parser.action, *args, **kwargs)

    @staticmethod
    def generate_cache_key(instance, *args, **kwargs):
        parts = instance.__module__.lower().split('.')
        parts += args
        for key in sorted(kwargs.iterkeys()):
            parts.append(str(key))
            parts.append(str(kwargs[key]))
        return '_'.join(parts)


class Api(Action):
    def init_defaults(self):
        Action.init_defaults(self)
        self.auto_template = False,
        self.output_type = 'json',
        self.access = {
            '*': {
                'access': 'admin'
            }
        }

    def get_output_403(self):
        self.add_error("You do not have permission to complete this action - {0}".format(self.parser.request_string))
        return self.get_output_json()

    def get_output_json(self):
        return HttpResponse(self.response_manager.get_response_string(), mimetype="application/json")

    def convert_models(self, models):
        records = []
        for model in models:
            records.append(model_to_dict(model))
        return records

    def add_message(self, str):
        self.response_manager.add_message(str)

    def add_error(self, message, field=''):
        self.response_manager.add_error(message, field)


class Crud(Api):

    def init_defaults(self):
        Api.init_defaults(self)

        self.form_class = False
        self.primary_key = False

        self.model_class = False
        self.lookup_class = False
        self.lookup_instance = False

        self.access_module = None
        self.access_model = None

    def init(self):
        Api.init(self)

        #Create the lookup class
        if self.lookup_class:
            self.lookup_instance = self.lookup_class(params=self.front_controller.request_parser.params)
            self.lookup_instance.front_controller = self.front_controller

        #Create the access based on the access_module and access_model
        """
        access = {
            "*": {
                "access": "admin"
            },
            "create_action": {
                "access": "article.add_article"
            },
            "read_action": {
                "access": "article.view_article"
            },
            "update_action": {
                "access": "article.change_article"
            },
            "delete_action": {
                "access": "article.delete_article"
            },
        }
        """
        if self.access is not None and self.access_module is not None and self.access_model is not None:
            action_permission_map = {
                'create': 'add',
                'read': 'view',
                'update': 'change',
                'delete': 'delete'
            }
            actions = ['create', 'read', 'update', 'delete']
            for action in actions:
                action_key = "{0}_action".format(action)
                if action_key in self.access:
                    continue
                self.access.update({
                    action_key: {
                        "access": "{0}.{1}_{2}".format(
                            self.access_module,
                            action_permission_map[action], self.access_model
                        )
                    }
                })

    def get_item_ids(self):
        ids = self.get_request_param('id', [])
        if type(ids) is not list:
            ids = [ids]

        return ids

    def create_action(self):
        if not self.form_class or not self.model_class or not self.lookup_class:
            return

        #get response manager
        response_manager = self.front_controller.response_manager

        #Create the form
        form = self.form_class(self.parser.request.POST)
        form.request = self.parser.request
        if form.is_valid():
            form.save()
        else:
            for field, error in form.errors.iteritems():
                for message in error:
                    response_manager.add_error(message, field)

        #Return the record if we had zero errors
        if not response_manager.any_errors():
            lookup = self.lookup_class({
                "id": form.instance.pk
            })
            self.set_response_param('record', lookup.get_row())
            self.set_response_param('id', form.instance.pk)

        return form.instance

    def update_action(self):
        if not self.form_class:
            return

        id = int(self.get_request_param('id', 0))
        model = self.model_class.objects.get(pk=id)

        #get response manager
        response_manager = self.front_controller.response_manager

        #Create the form
        form = self.form_class(self.parser.request.POST, instance=model)
        form.request = self.parser.request
        if form.is_valid():
            form.save()
        else:
            for field, error in form.errors.iteritems():
                for message in error:
                    response_manager.add_error(message, field)

        #Return the record if we had zero errors
        if not response_manager.any_errors():
            lookup = self.lookup_class({
                "id": form.instance.pk
            })
            self.set_response_param('record', lookup.get_row())
            self.set_response_param('id', form.instance.pk)

        return form.instance

    def read_action(self):
        if self.lookup_instance:

            meta = {}

            # run the lookup query to get the rows
            rows = list(self.lookup_instance.get_rows())
            query = self.lookup_instance.get_query_set().query

            # add records to the response
            meta['num_records'] = self.lookup_instance.get_num_records()
            meta['total_records'] = self.lookup_instance.get_total_records()
            meta['current_page'] = self.lookup_instance.get_current_page()
            meta['total_pages'] = self.lookup_instance.get_num_pages()
            meta['next'] = None
            meta['previous'] = None

            if settings.DEBUG:
                debug = {}
                debug['query'] = str(query)
                self.set_response_param('debug', debug)

            self.set_response_param('meta', meta)
            self.set_response_param('records', rows)

    def delete_action(self):
        """
        Looks for the param of id.
        This can be a single digit or an array of digits
        """
        #Check if we have a model class
        if not self.model_class:
            return

        #Process the ids
        ids = self.get_item_ids()

        #Get the objects to delete
        delete_items = self.model_class.objects.filter(pk__in=ids)
        for delete_item in delete_items:
            delete_item.delete()

        self.set_response_param('records', ids)


class Rest(Crud):

    def init_defaults(self):
        Crud.init_defaults(self)
        self.pk_value = None

    def init(self):
        Crud.init(self)

        self.pk_value = self.parser.action
        if self.lookup_instance and self.pk_value:
            self.lookup_instance.default_queryset = self.lookup_instance.default_queryset.filter(pk=self.pk_value)

        self.parser.action = self.front_controller.request.method

    def get_item_ids(self):
        ids = Crud.get_item_ids(self)

        if len(ids) == 0:
            ids = [self.pk_value]

        return ids

    def get_action(self):
        return self.read_action()

    def post_action(self):
        return self.create_action()

    def put_action(self):
        return self.update_action()


class Feed(Crud):
    """
    Abstract the field names in rss_action to reference the parent class definitions
    """
    def __init__(self, *args, **kwargs):
        #Add additional variables
        self.rss_feed = False
        self.title = ''
        self.link = ''
        self.description = ''
        self.item_title = ''
        self.item_link = ''
        self.item_description = ''
        self.item_pubdate = ''
        self.item_author_name = ''
        self.item_category_name = ''
        self.item_slug = ''

        #Call parent
        Crud.__init__(self, *args, **self.util.config(
            kwargs,
            output_type='rss'
        ))

    def rss_action(self):
        self.lookup_instance.add_sorter('published_at', 'desc')
        self.lookup_instance.add_filter('published', 1)
        self.read_action()
        self.rss_feed = feedgenerator.Rss201rev2Feed(
            title=self.title,
            link=self.link,
            description=self.description
        )

        for item in self.lookup_instance.get_models():
            self.rss_feed.add_item(
                title=getattr(item, self.item_title),
                link=self.get_item_link(item),
                description=self.get_item_description(item),
                pubdate=getattr(item, self.item_pubdate),
                author_name=self.get_author_name(item)
            )

    def get_item_description(self, item):
        return getattr(item, self.item_description)

    def get_author_name(self, item):
        return getattr(item, self.item_author_name)

    def get_item_link(self, item):
        return ''

    def get_rss_string(self):
        if self.rss_feed:
            return

    def get_output_rss(self):
        return HttpResponse(self.rss_feed.writeString('UTF-8'), mimetype="application/rss+xml")


class ExternalApi(Crud):

    def init_defaults(self):
        Crud.init_defaults(self)
        self.allowed_params = {}


class Stats(Api):

    def init_defaults(self):
        Api.init_defaults(self)
        self.access = None
        self.model = None
        self.model_class = None
        self.stats_class = None
        self.stats_instance = None

        self.entity_class = None
        self.entity_query_set = None
        self.entity_values = []
        self.entity_excludes = {}
        self.entity_legend_prefix = ''
        self.entity_legend_map_field = ''
        self.entity_format = ''
        self.entity_formatters = []

    def init(self):
        # Create the stats class
        if self.stats_class:
            self.stats_instance = self.stats_class(params=self.front_controller.request_parser.params)
        if self.entity_class:
            self.entity_query_set = self.entity_class.objects.values(
                *self.entity_values
            ).exclude(
                **self.entity_excludes
            ).distinct()

    def read_action(self):
        # Get the main stats
        for entity in self.entity_query_set:
            format_data = [entity[data] for data in self.entity_formatters]
            self.stats_instance.legend_map['{0}__{1}'.format(
                self.entity_legend_prefix,
                entity[self.entity_legend_map_field]
            )] = self.entity_format.format(*format_data)
#        stats.filters.append(Q(reporter__id=4))

        # Add records to the response
        rows = self.stats_instance.get_rows()
        self.set_response_param('total_records', len(rows))
        self.set_response_param('records', rows)
        self.set_response_param('legend_map', self.stats_instance.legend_map)
        self.set_response_param('x_label', self.stats_instance.x_label)
        self.set_response_param('y_label', self.stats_instance.y_label)


class Front(object):

    _app_directories = []
    _url_patterns = ['']
    _auto_discover = False

    def __init__(self, request, request_string, *args, **kwargs):
        self.request_parser = Parser(request, request_string, *args, **kwargs)
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
        Front._url_patterns.append(
            url(r'({0}/?.*)'.format(pattern), 'redokes.views.route', config)
        )

    @staticmethod
    def register_app_directory(name=None):
        Front._app_directories.append(name)
