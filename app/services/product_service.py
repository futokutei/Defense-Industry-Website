from app.extensions import db
from app.domain.catalog import Product

class ProductService:
    def get_all(self):
        return Product.query.all()

    def get_by_id(self, product_id):
        return Product.query.get(product_id)

    def create(self, data):
        new_product = Product(
            name=data.get('name'),
            desc=data.get('desc'),
            img=data.get('img', 'default.png')
        )
        db.session.add(new_product)
        db.session.commit()
        return new_product

    def update(self, product_id, data):
        product = Product.query.get(product_id)
        if not product:
            return None
        
        if 'name' in data:
            product.name = data['name']
        if 'desc' in data:
            product.desc = data['desc']
            
        db.session.commit()
        return product

    def delete(self, product_id):
        product = Product.query.get(product_id)
        if not product:
            return False
            
        db.session.delete(product)
        db.session.commit()
        return True