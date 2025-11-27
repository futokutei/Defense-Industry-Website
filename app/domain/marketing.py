from app.extensions import db

class CarouselItem(db.Model):
    __tablename__ = 'carousel_item'

    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100))
    desc = db.Column(db.Text)
    text_position = db.Column(db.String(20), default='center')
    button_text = db.Column(db.String(50))
    button_link = db.Column(db.String(200))

    # --- DDD Method: Business Logic ---
    def set_text_position(self, position):
        if position in ['left', 'right', 'center', 'none']:
            self.text_position = position
