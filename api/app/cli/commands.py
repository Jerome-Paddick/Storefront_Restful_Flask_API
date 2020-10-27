from ..models.store import Orders, OrderLines, Commissions, Promotions, Products, ProductPromotions
import csv
from ..models.core import db


def clear_database():
    Orders.query.delete()
    OrderLines.query.delete()
    Commissions.query.delete()
    Promotions.query.delete()
    Products.query.delete()
    ProductPromotions.query.delete()
    db.session.commit()


def populate_database(base_path='/usr/src/api/app/data/'):

    with open(base_path + 'orders.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            order = Orders(
                #
                id = row['id'],
                created_at = row['created_at'],
                vendor_id = row['vendor_id'],
                customer_id = row['customer_id'],
            )
            db.session.add(order)

    with open(base_path + 'products.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            products = Products(
                id = row['id'],
                description = row['description'],
            )
            db.session.add(products)

    with open(base_path + 'promotions.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            promotions = Promotions(
                id = row['id'],
                description = row['description'],
            )
            db.session.add(promotions)

    with open(base_path + 'commissions.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            commision = Commissions(
                date = row['date'],
                vendor_id = row['vendor_id'],
                rate = row['rate'],
            )
            db.session.add(commision)

    db.session.commit()

    with open(base_path + 'order_lines.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            order_lines = OrderLines(
                order_id = row['order_id'],
                product_id = row['product_id'],
                product_description = row['product_description'],
                product_price = row['product_price'],
                product_vat_rate = row['product_vat_rate'],
                discount_rate = row['discount_rate'],
                quantity = row['quantity'],
                full_price_amount = row['full_price_amount'],
                discounted_amount = row['discounted_amount'],
                vat_amount = row['vat_amount'],
                total_amount = row['total_amount'],
            )
            db.session.add(order_lines)

    db.session.commit()

    with open(base_path + 'product_promotions.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            product_promotions = ProductPromotions(
                #
                date = row['date'],
                product_id = row['product_id'],
                promotion_id = row['promotion_id'],
            )
            db.session.add(product_promotions)


    db.session.commit()

