import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Optional, Email
from flask_wtf.file import FileField, FileAllowed
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from functools import wraps

# -------------------- КОНФІГУРАЦІЯ ДОДАТКУ -------------------- #

app = Flask(__name__)
# Секретний ключ для сесій та форм
app.config['SECRET_KEY'] = "your_very_secret_and_secure_key_12345"
# Шлях для збереження завантажених зображень
app.config['UPLOAD_FOLDER'] = "static/img"
# Шлях до файлу бази даних SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Дозволені розширення файлів для завантаження
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# -------------------- ІНІЦІАЛІЗАЦІЯ РОЗШИРЕНЬ -------------------- #

# Ініціалізація SQLAlchemy для роботи з базою даних
db = SQLAlchemy(app)

# Ініціалізація Flask-Login для керування сесіями користувачів
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Сторінка для входу
login_manager.login_message = "Будь ласка, увійдіть, щоб отримати доступ."
login_manager.login_message_category = "info"

# -------------------- МОДЕЛІ БАЗИ ДАНИХ (SQLAlchemy) -------------------- #

# Модель користувача (адміністратора)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    # ЗАМІНЮЄМО is_superuser НА role
    role = db.Column(db.String(20), nullable=False, default='admin')

    @property
    def is_superadmin(self):
        """Перевіряє, чи є користувач суперадміном."""
        return self.role == 'superadmin'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Функція для завантаження користувача з сесії
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Модель продукту
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.Text, nullable=False)
    img = db.Column(db.String(100), nullable=False, default='default.png')

# Модель для елемента каруселі (слайдера)
class CarouselItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100))
    desc = db.Column(db.Text)
    text_position = db.Column(db.String(20), default='center')
    button_text = db.Column(db.String(50))
    button_link = db.Column(db.String(200))

# -------------------- ДЕКОРАТОР ДЛЯ СУПЕРАДМІНА -------------------- #

def superuser_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Використовуємо нову властивість для перевірки
        if not current_user.is_superadmin:
            flash("У вас недостатньо прав для виконання цієї дії.", "danger")
            return redirect(url_for('admin_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# -------------------- ФОРМИ (WTForms) -------------------- #

class LoginForm(FlaskForm):
    username = StringField('Логін', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Увійти')
    
class AdminForm(FlaskForm):
    username = StringField('Логін', validators=[DataRequired(), Length(min=4, max=80)])
    name = StringField('Ім\'я', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Пошта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=5)])
    submit = SubmitField('Додати адміністратора')

class EditAdminForm(FlaskForm):
    name = StringField('Ім\'я', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Пошта', validators=[DataRequired(), Email()])
    role = SelectField('Роль', choices=[('admin', 'Адміністратор'), ('superadmin', 'Суперадміністратор')], validators=[DataRequired()])
    submit = SubmitField('Зберегти зміни')

class ProductForm(FlaskForm):
    name = StringField('Назва продукту', validators=[DataRequired(), Length(min=3, max=100)])
    desc = TextAreaField('Опис', validators=[DataRequired()])
    img_file = FileField('Зображення', validators=[FileAllowed(ALLOWED_EXTENSIONS, 'Дозволені лише зображення!')])
    submit = SubmitField('Зберегти')

class CarouselItemForm(FlaskForm):
    title = StringField('Заголовок', validators=[Optional(), Length(max=100)])
    desc = TextAreaField('Опис', validators=[Optional()])
    img_file = FileField('Зображення', validators=[FileAllowed(ALLOWED_EXTENSIONS, 'Дозволені лише зображення!')])
    text_position = SelectField('Позиція тексту', choices=[('left', 'Зліва'), ('right', 'Справа'), ('center', 'По центру'), ('none', 'Без тексту')])
    button_text = StringField('Текст кнопки', validators=[Optional(), Length(max=50)])
    button_link = StringField('Посилання кнопки', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Зберегти')

# -------------------- ДОПОМІЖНІ ФУНКЦІЇ -------------------- #

def save_picture(form_picture):
    if form_picture:
        filename = secure_filename(form_picture.filename)
        picture_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
        form_picture.save(picture_path)
        return filename
    return None

# -------------------- МАРШРУТИ (ROUTES) -------------------- #

# --- Публічні сторінки ---
@app.route("/")
def index():
    carousel_items = CarouselItem.query.order_by(CarouselItem.id).all()
    return render_template("index.html", carousel_items=carousel_items)

@app.route("/products")
def products_page():
    products = Product.query.order_by(Product.name).all()
    return render_template("products.html", products=products)

@app.route("/products/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product_detail.html", product=product)

# --- Адмін-панель: Автентифікація ---
@app.route("/admin/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Невірний логін або пароль.', 'danger')
    return render_template("admin.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- Адмін-панель: Основні сторінки ---
@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    products = Product.query.all()
    return render_template("admin_dashboard.html", products=products, admin_name=current_user.name)

@app.route("/admin/admins")
@login_required
def admin_list():
    admins = User.query.all()
    return render_template("admin_dashboard_admins.html", admins=admins, admin_name=current_user.name)

# --- Адмін-панель: Керування Адміністраторами (CRUD) ---
@app.route("/admin/add_admin", methods=['GET', 'POST'])
@login_required
@superuser_required
def add_admin():
    form = AdminForm()
    if form.validate_on_submit():
        existing_user = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()
        if existing_user:
            flash('Адміністратор з таким логіном або поштою вже існує.', 'danger')
            return render_template("add_admin.html", form=form)

        new_admin = User(
            username=form.username.data,
            name=form.name.data,
            email=form.email.data
        )
        new_admin.set_password(form.password.data)
        db.session.add(new_admin)
        db.session.commit()
        flash('Нового адміністратора успішно додано!', 'success')
        return redirect(url_for('admin_list'))
    return render_template("add_admin.html", form=form)

@app.route("/admin/delete_admin/<int:admin_id>", methods=['POST'])
@login_required
@superuser_required
def delete_admin(admin_id):
    if admin_id == current_user.id:
        flash('Ви не можете видалити власний обліковий запис.', 'warning')
        return redirect(url_for('admin_list'))
    
    admin_to_delete = User.query.get_or_404(admin_id)
    
    if admin_to_delete.is_superadmin:
        flash('Неможливо видалити обліковий запис суперадміністратора.', 'danger')
        return redirect(url_for('admin_list'))

    db.session.delete(admin_to_delete)
    db.session.commit()
    flash('Адміністратора було видалено.', 'success')
    return redirect(url_for('admin_list'))

@app.route("/admin/edit_admin/<int:admin_id>", methods=['GET', 'POST'])
@login_required
@superuser_required
def edit_admin(admin_id):
    admin_to_edit = User.query.get_or_404(admin_id)
    form = EditAdminForm(obj=admin_to_edit)

    if form.validate_on_submit():
        # Критична перевірка: не дозволяти суперадміну позбавити ролі самого себе
        if admin_to_edit.id == current_user.id and form.role.data != 'superadmin':
            flash('Ви не можете змінити власну роль суперадміністратора.', 'danger')
            return redirect(url_for('edit_admin', admin_id=admin_id))

        admin_to_edit.name = form.name.data
        admin_to_edit.email = form.email.data
        admin_to_edit.role = form.role.data
        db.session.commit()
        flash('Дані адміністратора оновлено.', 'success')
        return redirect(url_for('admin_list'))

    return render_template("edit_admin.html", form=form, admin=admin_to_edit)

# --- Адмін-панель: Керування продуктами (CRUD) ---
@app.route("/admin/add_product", methods=["GET", "POST"])
@login_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        filename = save_picture(form.img_file.data)
        if not filename:
            flash('Зображення є обов\'язковим для нового продукту!', 'warning')
            return render_template("add_product.html", form=form)
        
        new_product = Product(name=form.name.data, desc=form.desc.data, img=filename)
        db.session.add(new_product)
        db.session.commit()
        flash('Продукт успішно додано!', 'success')
        return redirect(url_for("admin_dashboard"))
    return render_template("add_product.html", form=form)

@app.route("/admin/edit_product/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        product.desc = form.desc.data
        if form.img_file.data:
            product.img = save_picture(form.img_file.data)
        db.session.commit()
        flash('Продукт оновлено!', 'success')
        return redirect(url_for("admin_dashboard"))
    return render_template("edit_product.html", form=form, product=product)

@app.route("/admin/delete_product/<int:product_id>", methods=["POST"])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if product.img and product.img != 'default.png':
        try:
            image_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], product.img)
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            flash(f"Помилка при видаленні файлу зображення: {e}", "danger")

    db.session.delete(product)
    db.session.commit()
    flash('Продукт видалено.', 'success')
    return redirect(url_for("admin_dashboard"))

# --- Адмін-панель: Керування каруселлю (CRUD) ---
@app.route("/admin/carousel")
@login_required
def admin_carousel():
    carousel_items = CarouselItem.query.all()
    return render_template("admin_carousel.html", carousel_items=carousel_items, admin_name=current_user.name)

@app.route("/admin/add_carousel_item", methods=["GET", "POST"])
@login_required
def add_carousel_item():
    form = CarouselItemForm()
    if form.validate_on_submit():
        filename = save_picture(form.img_file.data)
        if not filename:
            flash('Зображення є обов\'язковим для нового слайда!', 'warning')
            return render_template("add_carousel_item.html", form=form)
        
        new_item = CarouselItem(
            img=filename, title=form.title.data, desc=form.desc.data,
            text_position=form.text_position.data, button_text=form.button_text.data,
            button_link=form.button_link.data
        )
        db.session.add(new_item)
        db.session.commit()
        flash('Слайд додано!', 'success')
        return redirect(url_for('admin_carousel'))
    return render_template("add_carousel_item.html", form=form)

@app.route("/admin/carousel/edit/<int:item_id>", methods=["GET", "POST"])
@login_required
def edit_carousel(item_id):
    item = CarouselItem.query.get_or_404(item_id)
    form = CarouselItemForm(obj=item)
    if form.validate_on_submit():
        if form.img_file.data:
            item.img = save_picture(form.img_file.data)
        item.title = form.title.data
        item.desc = form.desc.data
        item.text_position = form.text_position.data
        item.button_text = form.button_text.data
        item.button_link = form.button_link.data
        db.session.commit()
        flash('Слайд оновлено!', 'success')
        return redirect(url_for('admin_carousel'))
    return render_template("edit_carousel.html", form=form, item=item)

@app.route("/admin/carousel/delete/<int:item_id>", methods=["POST"])
@login_required
def delete_carousel_item(item_id):
    item = CarouselItem.query.get_or_404(item_id)

    if item.img:
        try:
            image_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], item.img)
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            flash(f"Помилка при видаленні файлу зображення: {e}", "danger")

    db.session.delete(item)
    db.session.commit()
    flash('Слайд видалено.', 'success')
    return redirect(url_for('admin_carousel'))

# -------------------- СТВОРЕННЯ БД ТА ПОЧАТКОВИХ ДАНИХ -------------------- #

def create_initial_data():
    if not User.query.first():
        print("Створення початкового суперадміністратора...")
        admin = User(
            username='admin',
            name='Головний Адмін',
            email='admin@example.com',
            role='superadmin'  # Призначаємо роль напряму
        )
        admin.set_password('12345')
        db.session.add(admin)

    if not Product.query.first():
        print("Створення початкових продуктів...")
        products = [
            Product(name="Atlas", desc="Гуманоїдний робот для мобільності та досліджень.", img="hero.png"),
            Product(name="Spot", desc="Робот-собака для промислових і оборонних задач.", img="hero.png"),
            Product(name="Handle", desc="Робот для складів та логістики.", img="hero.png")
        ]
        db.session.add_all(products)

    if not CarouselItem.query.first():
        print("Створення початкових слайдів...")
        items = [
            CarouselItem(img="su-27.jpg", title="Технології для нашої авіації", desc="Технології, з якими 'Привид Києва' став Легендою.", text_position="right", button_text="Переглянути продукцію", button_link="/products"),
            CarouselItem(img="fpv.jpeg", title="FPV — дрони", desc="Зброя, що змінила сучасну війну.", text_position="left", button_text="Переглянути продукцію", button_link="/products"),
            CarouselItem(img="ssu2.jpg", title="Якісне спорядження", desc="Комфорт та безпека.", text_position="center", button_text="Переглянути продукцію", button_link="/products")
        ]
        db.session.add_all(items)
    
    db.session.commit()

# Створення таблиць бази даних та початкових даних
with app.app_context():
    db.create_all()
    create_initial_data()

# -------------------- ЗАПУСК ДОДАТКУ -------------------- #

if __name__ == "__main__":
    app.run(debug=True)
