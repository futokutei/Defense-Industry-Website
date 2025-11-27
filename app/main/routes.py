from flask import Blueprint, render_template
from app.domain import CarouselItem, Product

main = Blueprint('main', __name__)

@main.route("/")
def index():
    carousel_items = CarouselItem.query.order_by(CarouselItem.id).all()
    return render_template("index.html", carousel_items=carousel_items)

@main.route("/products")
def products_page():
    products = Product.query.order_by(Product.name).all()
    return render_template("products.html", products=products)

@main.route("/products/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product_detail.html", product=product)
