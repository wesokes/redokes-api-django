from pprint import pprint
from django.test import TestCase
from redokes.report.dimensions import YearDimension, MonthDimension, WeekDimension, DayDimension
from redokes.report.metrics import Driver
from test_project.dimensions import OrganizationDimension, TeamDimension, AccountDimension
from test_project.metrics import MarginMetric


def get_comparison_str(item1, item2):
    return 'Items are not equal.\nGot:\n{0}\nExpected:\n{1}'.format(item1, item2)


class TestBase(TestCase):

    fixtures = [
        'test_project/test_data.json'
    ]

    def setUp(self):
        super(TestBase, self).setUp()
        self.init_defaults()
        self.init_driver()
        self.init_metrics()
        self.init_dimensions()

    def init_defaults(self):
        pass

    def init_driver(self):
        self.driver = Driver()

    def init_metrics(self):
        self.driver.add_metric(MarginMetric())

    def init_dimensions(self):
        # self.driver.add_dimension(DayDimension())
        # self.driver.add_dimension(WeekDimension())
        # self.driver.add_dimension(MonthDimension())
        # self.driver.add_dimension(YearDimension())

        # self.driver.add_dimension(AccountDimension())
        # self.driver.add_dimension(TeamDimension())
        self.driver.add_dimension(OrganizationDimension())

    def assert_close_enough(self, first, second, msg=None, precision=4):
        self.assertEqual(round(first, precision), round(second, precision), msg)

    def test_test(self):
        pprint(self.driver.fetch_all())
