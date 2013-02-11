from redokes.controller.crud import Crud

class ExternalApi(Crud):
    
    def init_defaults(self):
        Crud.init_defaults(self)
        self.allowed_params = {}