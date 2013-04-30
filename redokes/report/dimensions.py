import datetime
from dateutil.relativedelta import relativedelta
from querybuilder.datetime_helpers import datetime_floor
from querybuilder.fields import GroupEpoch


class Dimension(object):
    name = None

    def __init__(self, **kwargs):
        """
        Initializes the entity by setting default values
        """
        # set default property values
        self.init_defaults()

    def init_defaults(self):
        pass

    def add_to_query(self, query):
        self.add_joins_to_query(query)
        self.add_field_to_query(query)
        self.add_group_to_query(query)

    def add_joins_to_query(self, query):
        pass

    def add_field_to_query(self, query):
        pass

    def add_group_to_query(self, query, is_outer=False):
        pass


class TimeDimension(Dimension):
    name = None
    time_group_value = None

    def init_defaults(self):
        self.time_field = 'time'

    def add_to_query(self, query):
        super(TimeDimension, self).add_to_query(query)
        field = GroupEpoch(self.time_field, date_group_name=self.name)
        query.tables[0].add_field(field)
        query.group_by(field)

    def get_time(self, dimensions):
        utc_epoch = int(dimensions.get(self.time_field))
        return datetime_floor(datetime.datetime.utcfromtimestamp(utc_epoch), self.name)

    def get_end_time(self, dimensions):
        utc_epoch = int(dimensions.get(self.time_field))
        time = datetime_floor(datetime.datetime.utcfromtimestamp(utc_epoch), self.name)

        # calculate the end date as the date plus one unit of the date grouping
        date_diff = relativedelta(**{'{0}s'.format(self.name): 1})
        return time + date_diff


class DayDimension(TimeDimension):
    """
    Performs daily time groupings.
    """
    name = 'day'
    time_group_value = 1


class WeekDimension(TimeDimension):
    """
    Performs weekly time groupings.
    """
    name = 'week'
    time_group_value = 2


class MonthDimension(TimeDimension):
    """
    Performs monthly time groupings.
    """
    name = 'month'
    time_group_value = 3


class QuarterDimension(TimeDimension):
    """
    Performs quarterly time groupings.
    """
    name = 'quarter'
    time_group_value = 4


class YearDimension(TimeDimension):
    """
    Performs quarterly time groupings.
    """
    name = 'year'
    time_group_value = 5


class AllDimension(TimeDimension):
    """
    Performs all-time groupings.
    """
    name = 'all'
    time_group_value = 6


class ModelDimension(Dimension):
    content_type = None
    pk = 'id'
    id_name = 'id'
    required_joins = []
    partition_for = []

    def add_joins_to_query(self, query):
        for required_join_item in self.required_joins:
            item = required_join_item()
            item.add_joins_to_query(query)

    def add_field_to_query(self, query):
        table = query.find_table(self.model)
        table.add_field({
            self.id_name: self.pk
        })

    def add_group_to_query(self, query, is_outer=False):
        if is_outer:
            query.group_by(self.id_name)
        else:
            query.group_by(self.pk, self.model)

