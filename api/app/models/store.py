from .core import db
from sqlalchemy.orm import relationship

class Orders(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime(True), nullable=False)
    vendor_id = db.Column(db.Integer, nullable=False)
    customer_id = db.Column(db.Integer, nullable=False)

class OrderLines(db.Model):
    __tablename__ = 'order_lines'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.ForeignKey('products.id'), nullable=False)
    product_description = db.Column(db.String(64), nullable=False)
    product_price = db.Column(db.Float, nullable=False)
    product_vat_rate = db.Column(db.Float, nullable=False)
    discount_rate = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    full_price_amount = db.Column(db.Float, nullable=False)
    discounted_amount = db.Column(db.Float, nullable=False)
    vat_amount = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    orders = db.relationship('Orders', backref=db.backref('order_lines', lazy=True))

class Commissions(db.Model):
    __tablename__ = 'commissions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime(True), nullable=False)
    vendor_id = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Float, nullable=False)

class Promotions(db.Model):
    __tablename__ = 'promotions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(128), nullable=False)

class Products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(128), nullable=False)

class ProductPromotions(db.Model):
    __tablename__ = 'product_promotions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime(True), nullable=False)
    product_id = db.Column(db.ForeignKey('products.id'), nullable=False)
    promotion_id = db.Column(db.ForeignKey('promotions.id'), nullable=False)
