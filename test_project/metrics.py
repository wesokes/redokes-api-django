from querybuilder.fields import SumField, AggregateField, FieldFactory
from redokes.report.metrics import Metric
from test_project.models import Order


class OrderMetric(Metric):
    """
    Defines the basic transformations and information for LME Order drivers.
    """

    def init_defaults(self):
        super(OrderMetric, self).init_defaults()

        self.model = Order
        self.time_field = 'time'


class MarginMetric(OrderMetric):
    name = 'margin'

    def init_defaults(self):
        super(MarginMetric, self).init_defaults()
        self.aggregate_field = 'margin'
        self.aggregate_function = SumField


class RevenueMetric(OrderMetric):
    name = 'revenue'

    def init_defaults(self):
        super(RevenueMetric, self).init_defaults()
        self.aggregate_field = 'revenue'
        self.aggregate_function = SumField


class CostMetric(OrderMetric):
    name = 'cost'

    def init_defaults(self):
        super(CostMetric, self).init_defaults()
        self.aggregate_field = 'cost'
        self.aggregate_function = SumField


class MarginPercentField(AggregateField):
    function_name = 'MarginPercent'

    def __init__(self, field=None, table=None, alias=None, over=None, margin_field=None, gross_pay_field=None,
                 empty_value=0):
        super(MarginPercentField, self).__init__(field, table, alias, over)

        if margin_field is None:
            margin_field = 'margin'
        if gross_pay_field is None:
            gross_pay_field = 'cost'

        self.margin_field = FieldFactory(margin_field)
        self.gross_pay_field = FieldFactory(gross_pay_field)

        self.auto_alias = 'margin_percent'
        self.empty_value = empty_value

    def get_select_sql(self):
        return (
            '(CASE WHEN SUM({1}) = 0 THEN {2} WHEN (SUM({0}) / SUM({1}) < -1.0) THEN -100.0 '
            'ELSE (SUM({0}) / SUM({1}) * 100) END)'.format(
                self.margin_field.get_identifier(),
                self.gross_pay_field.get_identifier(),
                self.empty_value
            )
        )

    def get_field_identifier(self):
        return ''


class MarginPercentMetric(OrderMetric):
    name = 'margin_percent'

    def init_defaults(self):
        super(MarginPercentMetric, self).init_defaults()
        self.aggregate_field = 'margin_percent'
        self.aggregate_function = SumField

    def generate_value_field(self):
        return MarginPercentField(alias='{0}__value'.format(self.aggregate_field))
