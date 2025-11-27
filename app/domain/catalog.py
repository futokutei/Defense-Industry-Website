from app.extensions import db

class Product(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.Text, nullable=False)
    img = db.Column(db.String(100), nullable=False, default='default.png')

    # --- DDD Method: Business Logic ---
    def update_details(self, name=None, desc=None):
        if name:
            self.name = name
        if desc:
            self.desc = desc
