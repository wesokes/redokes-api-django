from redokes.controller.Crud import Crud
from django.http import Http404
from django.conf import settings

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
        
    
    