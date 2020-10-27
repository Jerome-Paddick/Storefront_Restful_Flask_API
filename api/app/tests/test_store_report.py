from app.models.core import db
from app.app_factory import create_app
from app.config import TestConfig
from app.resources.store import StoreReport
from psycopg2.errors import UniqueViolation

def populate_test_db(db):
    from app.cli.commands import populate_database
    populate_database(base_path='/usr/src/api/app/tests/data/')

class TestClass:
    @classmethod
    def setup_class(cls):
        cls.app = create_app(TestConfig)
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

        try:
            populate_test_db(db)
        except UniqueViolation:
            db.session.remove()
            db.drop_all()
            db.session.commit()

        print ('\nsetup_class()')

    @classmethod
    def teardown_class(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()
        print ('teardown_class()')

    # def setup_method(self, method):
    #     print ('\nsetup_method()')
    #
    # def teardown_method(self, method):
    #     print ('\nteardown_method()')

    def test_store_report_date_exists(self):
        """ tests report generates from test data in test db """
        report = StoreReport().get('2019-08-01')

        assert report == {
            'customers': 2,
            'total_discount_amount': 200.0,
            'orders_count': 2,
            'order_total_avg': 900.0,
            'discount_rate_avg': 0.3,
            'commissions': {
                'promotions':
                    {
                        2: 100.0,
                        1: 50.0
                    },
                'total': 150.0,
                'order_average': 75.0}
        }

    def test_store_report_date_doesnt_exist(self):
        """ tests no data is returned for out of date query """
        report = StoreReport().get('2020-01-01')

        print(report)

        assert report == {
            'customers': 0,
            'total_discount_amount':None,
            'orders_count': 0,
            'order_total_avg': None,
            'discount_rate_avg': None,
            'commissions': {
                'promotions':
                    {
                    },
                'total': None,
                'order_average': None,}
        }