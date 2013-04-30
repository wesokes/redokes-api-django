from django.contrib.contenttypes.models import ContentType
from redokes.report.dimensions import ModelDimension
from test_project.models import Account, Order, Team, Organization


class OrderDimension(ModelDimension):
    model = Order
    id_name = 'order_id'
    required_joins = []

    def init_defaults(self):
        super(OrderDimension, self).init_defaults()
        self.model = Order


class AccountDimension(ModelDimension):
    model = Account
    name = 'account'
    id_name = 'account_id'
    required_joins = []

    def add_joins_to_query(self, query):
        super(AccountDimension, self).add_joins_to_query(query)
        query.join(Account)


class TeamDimension(ModelDimension):
    model = Team
    name = 'team'
    id_name = 'team_id'
    required_joins = [AccountDimension]

    def add_joins_to_query(self, query):
        super(TeamDimension, self).add_joins_to_query(query)
        query.join(
            Team,
            left_table=Account,
        )


class OrganizationDimension(ModelDimension):
    model = Organization
    name = 'organization'
    id_name = 'organization_id'
    required_joins = [AccountDimension]
    partition_for = [AccountDimension]

    def add_joins_to_query(self, query):
        super(OrganizationDimension, self).add_joins_to_query(query)
        query.join(
            Organization,
            left_table=Account,
        )
