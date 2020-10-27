import traceback
from flask import current_app
from flask_restful import reqparse, Resource
from ..models.wedding_gifts import Products, Gifts
from flask_restful_swagger import swagger
from flask_restful import fields, inputs

@swagger.model
class GiftData:
    resource_fields = {
        "id": fields.Integer,
        "product_id": fields.Integer,
        "purchased": fields.Boolean,
        "name": fields.String,
        "brand": fields.String,
        "price": fields.String,
        "in_stock_quantity": fields.Integer,
    }
    required = ['id', "product_id", "purchased", "name", "brand", "price", "in_stock_quantity"]

@swagger.model
@swagger.nested(data=GiftData.__name__)
class GiftsResponse:
    resource_fields = {
        "status": fields.String,
        "data": fields.List(fields.Nested(GiftData.resource_fields))
    }
    required = ['status']

@swagger.model
class GenericResponse:
    resource_fields = {
        "status": fields.String,
    }
    required = ['status']


class GiftsResource(Resource):
    @swagger.operation(
        responseClass=GiftsResponse.__name__,
        parameters=[],
        responseMessages=[
            {"code": 200, "message": "Successful Request"},
            {"code": 500, "message": "Unexpected error"},
        ]
    )
    def get(self):
        """ Gets List of gifts on list """
        try:
            gifts_query = Gifts.query.all()
            gifts = [
                {
                "id": gift.id,
                "product_id": gift.product_id,
                "purchased": gift.purchased,
                "name": gift.product.name,
                "brand": gift.product.brand,
                "price": gift.product.price,
                "in_stock_quantity": gift.product.in_stock_quantity,
                } for gift in gifts_query
            ]
            return {'status': 'ok',
                    'data': gifts}, 200
        except Exception as ex:
            return {'status': 'error',
                    'message': 'Unexpected Error in GiftsResource get',
                    'error': str(ex)}, 500

    @swagger.model
    class CreateGiftRequest:
        resource_fields = {
            "product_id": fields.Integer
        }
        required=['product_id']
    @swagger.operation(
        responseClass=GenericResponse.__name__,
        parameters=[{
                "dataType": CreateGiftRequest.__name__,
                "name": "payload", "required": True, "allowMultiple": False, "paramType": "body",
            },],
        responseMessages=[
            {"code": 200, "message": "Successful Request"},
            {"code": 400, "message": "Invalid Request"},
            {"code": 400, "message": "Product not found"},
            {"code": 500, "message": "Unexpected error"},
        ]
    )
    def post(self):
        """ Adds Item to List """
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('product_id', required=True, type=int)
            args = parser.parse_args()
        except:
            return {'status': 'error', 'message': 'Invalid Request'}, 400
        try:
            product_id = args.get('product_id')
            product = Products.query.get(product_id)

            if not product:
                return {'status': 'error', 'message': 'Product not found'}, 400

            gift = Gifts(
                product_id = product_id,
            )
            current_app.db.session.add(gift)
            current_app.db.session.commit()

            return {'status': f'Successfully Added gift id:{gift.id}'}, 200

        except Exception as ex:
            return {'status': 'error',
                    'message': 'Unexpected Error in GiftsResource post',
                    'error': str(ex)}, 500



class PutRemoveGiftsResource(Resource):
    @swagger.operation(
        responseClass=GenericResponse.__name__,
        parameters=[],
        responseMessages=[
            {"code": 200, "message": "Successful Request"},
            {"code": 400, "message": "Gift already purchased, please choose another"},
            {"code": 400, "message": "Gift out of stock, please contact us for availability"},
            {"code": 500, "message": "Unexpected error"},
        ]
    )
    def put(self, gift_id):
        """ Purchases a gift from the list """
        try:
            gift = Gifts.query.get(gift_id)
            if not gift:
                return {'status': 'error', 'message': 'Gift not found'}, 400

            if gift.purchased:
                return {'status': 'error', 'message': 'Gift already purchased, please choose another'}, 400

            if gift.product.in_stock_quantity == 0:
                return {'status': 'error', 'message': 'Gift out of stock, please contact us for availability'}, 400

            gift.purchased = True
            current_app.db.session.commit()

            return {'status': 'Successfully Purchased'}, 200
        except Exception as ex:
            return {'status': 'error',
                    'message': 'Unexpected Error in PutRemoveGiftsResource put',
                    'error': str(ex)}, 500

    @swagger.operation(
        responseClass=GenericResponse.__name__,
        parameters=[],
        responseMessages=[
            {"code": 200, "message": "Successful Request"},
            {"code": 400, "message": "Gift not found"},
            {"code": 400, "message": "Gift has already been purchased"},
            {"code": 500, "message": "Unexpected error"},
        ]
    )
    def delete(self, gift_id):
        """ Removes a gift from the list """
        try:
            gift = Gifts.query.get(gift_id)
            if not gift:
                return {'status': 'error', 'message': 'Gift not found'}, 400
            if gift.purchased:
                return {'status': 'error', 'message': 'Gift has already been purchased'}, 400
            Gifts.query.filter(Gifts.id==gift_id).delete()
            current_app.db.session.commit()

            return {'status': 'Successfully Deleted'}, 200
        except Exception as ex:
            return {'status': 'error',
                    'message': 'Unexpected Error in PutRemoveGiftsResource delete',
                    'error': str(ex)}, 500


@swagger.model
@swagger.nested(purchased=GiftData.__name__, not_purchased=GiftData.__name__)
class GiftsReportResponse:
    resource_fields = {
        "status": fields.String,
        "purchased": fields.List(fields.Nested(GiftData.resource_fields)),
        "not_purchased": fields.List(fields.Nested(GiftData.resource_fields)),
    }
    required = ['status']

class GiftsReportResource(Resource):
    @swagger.operation(
        responseClass=GiftsReportResponse.__name__,
        parameters=[],
        responseMessages=[
            {"code": 200, "message": "Successful Request"},
            {"code": 500, "message": "Unexpected error"},
        ]
    )
    def get(self):
        """ Generates Report on Gifts """
        try:
            gifts_query = Gifts.query.all()
            gifts = [
                {
                    "id": gift.id,
                    "product_id": gift.product_id,
                    "purchased": gift.purchased,
                    "name": gift.product.name,
                    "brand": gift.product.brand,
                    "price": gift.product.price,
                    "in_stock_quantity": gift.product.in_stock_quantity,
                } for gift in gifts_query
            ]
            purchased = [gift for gift in gifts if gift.get('purchased')]
            not_purchased = [gift for gift in gifts if not gift.get('purchased')]

            return {'status': 'ok',
                    'purchased': purchased,
                    'not_purchased': not_purchased}, 200
        except Exception as ex:
            return {'status': 'error',
                    'message': 'Unexpected Error in GiftsReportResource get',
                    'error': str(ex)}, 500