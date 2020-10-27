import traceback
from flask import current_app
from ..models.core import db
from flask_restful import reqparse, Resource
from flask_restful_swagger import swagger
from flask_restful import fields, inputs
import datetime



@swagger.model
class CommissionsNested:
    resource_fields = {
        "promotions": fields.Float,
        "total": fields.Integer,
        "order_average": fields.Float,
    }
    required = ["promotions", "total", "order_average"]

@swagger.model #
@swagger.nested(commissions=CommissionsNested.__name__)
class StoreReportResponse:
    resource_fields = {
        "customers": fields.Integer,
        "total_discount_amount": fields.Float,
        "orders_count": fields.Integer,
        "order_total_avg": fields.Float,
        "discount_rate_avg": fields.Float,
        "commissions": fields.Nested(CommissionsNested.resource_fields)
    }
    required = ["customers", "total_discount_amount", "orders_count",
                "order_total_avg", "discount_rate_avg", "commissions",]


class StoreReport(Resource):
    @swagger.operation(
        responseClass=StoreReportResponse.__name__,
        parameters=[],
        responseMessages=[
            {"code": 200, "message": "Successful Request"},
            {"code": 400, "message": "Invalid Request"},
            {"code": 500, "message": "Unexpected error"},
        ]
    )
    def get(self, date_timestamp):
        """ Generates Store Report on date, accepts ISO format date
            eg. 2019-08-01 """
        try:
            try:
                # needs to accept ISO format timestamp eg. 2019-08-01
                start_time = datetime.date.fromisoformat(date_timestamp)
                # start_time = datetime.datetime.strptime(date_timestamp, '%Y-%m-%d').replace(tzinfo=datetime.timezone.utc)
                end_time = start_time + datetime.timedelta(days=1)
            except ValueError:
                return {'status': 'invalid_request', 'message': 'Invalid Timestamp, please use ISO format'}, 400

            if not end_time > start_time:
                return {'status': 'invalid_request', 'message': 'Start time cannot be ahead of End time'}, 400

            from ..models.store import Orders, Products, OrderLines, Commissions, Promotions, ProductPromotions
            from sqlalchemy.sql import func, distinct

            date_filter = (Orders.created_at >= start_time, Orders.created_at < end_time)

            # The total number of items sold on that day.
            # The total number of customers that made an order that day.
            # The total amount of discount given that day.
            # The average discount rate applied to the items sold that day
            # The average order total for that day
            discounted_query = db.session.query(
                    func.count(distinct(Orders.id)),
                    func.count(distinct(Orders.customer_id)),
                    func.sum(OrderLines.discounted_amount),
                    func.avg(OrderLines.discount_rate),
                    func.avg(OrderLines.total_amount),
                                                ) \
                .join(Orders, Orders.id == OrderLines.order_id)\
                .filter(*date_filter)\
                .all()[0]

            orders_count = discounted_query[0]
            distinct_customers = discounted_query[1]
            discounted_total = discounted_query[2]
            discounted_rate_average = discounted_query[3]
            average_order_total = discounted_query[4]

            # The total amount of commissions generated that day.
            # The average amount of commissions per order for that day.
            commisions_query = db.session.query(
                func.sum(OrderLines.product_price * Commissions.rate),
                func.avg(OrderLines.product_price * Commissions.rate),
                                                ) \
                .join(Orders, Orders.id == OrderLines.order_id)\
                .join(Commissions, Commissions.vendor_id==Commissions.vendor_id)\
                .filter(Commissions.date>=start_time).filter(Commissions.date < end_time)\
                .filter(*date_filter)\
                .all()[0]

            commisions_total = commisions_query[0]
            commisions_average = commisions_query[1]

            # The total amount of commissions earned per promotion that day.
            promotion_query = db.session.query(
                    ProductPromotions.promotion_id,
                    func.sum(OrderLines.product_price * Commissions.rate)
                                                ) \
                .join(Orders, Orders.id == OrderLines.order_id)\
                .join(Commissions, Commissions.vendor_id==Commissions.vendor_id) \
                .join(ProductPromotions, ProductPromotions.product_id==OrderLines.product_id) \
                .filter(Commissions.date>=start_time).filter(Commissions.date < end_time)\
                .filter(*date_filter).group_by(ProductPromotions.promotion_id)\
                .all()

            promotions_summary = {item[0]: item[1] for item in promotion_query}

            return {
                "customers": distinct_customers,
                "total_discount_amount": discounted_total,
                "orders_count": orders_count,
                "order_total_avg": average_order_total,
                "discount_rate_avg": discounted_rate_average,
                "commissions": {
                    "promotions": promotions_summary,
                    "total": commisions_total,
                    "order_average": commisions_average,
                    }
                }

        except Exception as ex:
                return {'status': 'error',
                        'message': f'Unexpected Error in {self.__class__.__name__} get',
                        'error': str(ex)}, 500
