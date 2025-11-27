from app import create_app, db
from app.domain import User, Product, CarouselItem

app = create_app()

def create_initial_data():
    if not User.query.first():
        print("Creating superadmin...")
        admin = User(username='admin', name='Головний Адмін', email='admin@example.com', role='superadmin')
        admin.set_password('12345')
        db.session.add(admin)

    if not Product.query.first():
        print("Creating products...")
        products = [
            Product(name="Atlas", desc="Humanoid robot.", img="hero.png"),
            Product(name="Spot", desc="Robot dog.", img="hero.png")
        ]
        db.session.add_all(products)

    if not CarouselItem.query.first():
        print("Creating carousel items...")
        items = [
            CarouselItem(img="fpv.jpeg", title="FPV Drones", desc="Modern tech.", text_position="left")
        ]
        db.session.add_all(items)

    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_initial_data()
    app.run(debug=True)
