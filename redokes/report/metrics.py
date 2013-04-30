from querybuilder.fields import CountField, AvgField
from querybuilder.query import Query
from redokes.report.dimensions import TimeDimension, ModelDimension


class Metric(object):
    name = None

    def __init__(self):
        """
        Initializes the entity by setting default values
        """
        # set default property values
        self.init_defaults()

    def init_defaults(self):
        self.model = None
        self.time_field = None
        self.value_field = None
        self.aggregate_function = CountField
        self.aggregate_field = None
        self.value_alias = 'value'
        self.empty_value = 0

    @property
    def value_name(self):
        return '{0}__value'.format(self.aggregate_field)

    @property
    def average_name(self):
        return '{0}__average'.format(self.aggregate_field)

    @property
    def time_name(self):
        return '{0}__epoch'.format(self.time_field)

    def add_to_query(self, query):
        if self.value_field is None:
            self.value_field = self.generate_value_field()
        query.tables[0].add_field(self.value_field)
        query.tables[0].add_field({
            self.average_name: AvgField(self.aggregate_field)
        })

    def generate_value_field(self):
        """
        Automatically creates the value field. This can be overridden by subclasses
        to modify the value field
        @return: the value field to be used for the metric aggregation
        @rtype: Field
        """
        return {
            self.value_name: self.aggregate_function(self.aggregate_field)
        }


class Driver(object):

    def __init__(self, **kwargs):
        """
        Initializes the driver by setting default values, filter params, and
        the metric config data.
        """
        # set default property values
        self.init_defaults()

        # update params with passed params
        self.params.update(kwargs)

    def init_defaults(self):
        """
        Initializes the default values
        """
        self.params = {}
        self.metrics = []
        self.dimensions = []
        self.query = None
        self.time_field = None

    def add_metric(self, new_metric):
        self.metrics.append(new_metric)
        self.time_field = new_metric.time_field

    def add_dimension(self, new_dimension):
        self.dimensions.append(new_dimension)

    def fetch_all(self):
        # generate query
        query = self.get_query()
        return query.select()

    def get_query(self):
        """
        Builds the default metric query from the metric model and value_field
        @return: The generated query
        @rtype: Query
        """
        # there must be at least one metric
        if len(self.metrics) == 0:
            # TODO: error
            return

        self.query = Query().from_table(
            table=self.metrics[0].model,
            fields=None
        )

        # add a count field
        self.query.tables[0].add_field({
            'num_items': CountField('*', cast='INT')
        })

        # add metric fields
        for metric_item in self.metrics:
            metric_item.add_to_query(self.query)

        # add dimensions
        for dimension_item in self.dimensions:
            dimension_item.time_field = self.time_field
            dimension_item.add_to_query(self.query)

        return self.query

    def get_time_dimensions(self):
        time_dimensions = []
        for dimension_item in self.dimensions:
            if isinstance(dimension_item, TimeDimension):
                time_dimensions.append(dimension_item)
        return time_dimensions

    def get_model_dimensions(self):
        model_dimensions = []
        for dimension_item in self.dimensions:
            if isinstance(dimension_item, ModelDimension):
                model_dimensions.append(dimension_item)
        return model_dimensions