import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.domain import User, Product, CarouselItem
from app.forms import LoginForm, AdminForm, EditAdminForm, ProductForm, CarouselItemForm
from app.utils import save_picture, superuser_required

# Створюємо Blueprint з префіксом /admin
admin = Blueprint('admin', __name__, url_prefix='/admin')

# --- АВТЕНТИФІКАЦІЯ ---

@admin.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.admin_dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Невірний логін або пароль.', 'danger')
    return render_template("admin.html", form=form)

@admin.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# --- ГОЛОВНА ПАНЕЛЬ ---

@admin.route("/dashboard")
@login_required
def admin_dashboard():
    products = Product.query.all()
    return render_template("admin_dashboard.html", products=products, admin_name=current_user.name)

@admin.route("/admins")
@login_required
def admin_list():
    admins = User.query.all()
    return render_template("admin_dashboard_admins.html", admins=admins, admin_name=current_user.name)

# --- КЕРУВАННЯ АДМІНІСТРАТОРАМИ ---

@admin.route("/add_admin", methods=['GET', 'POST'])
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
        return redirect(url_for('admin.admin_list'))
    return render_template("add_admin.html", form=form)

@admin.route("/delete_admin/<int:admin_id>", methods=['POST'])
@login_required
@superuser_required
def delete_admin(admin_id):
    if admin_id == current_user.id:
        flash('Ви не можете видалити власний обліковий запис.', 'warning')
        return redirect(url_for('admin.admin_list'))
    
    admin_to_delete = User.query.get_or_404(admin_id)
    
    if admin_to_delete.is_superadmin:
        flash('Неможливо видалити обліковий запис суперадміністратора.', 'danger')
        return redirect(url_for('admin.admin_list'))

    db.session.delete(admin_to_delete)
    db.session.commit()
    flash('Адміністратора було видалено.', 'success')
    return redirect(url_for('admin.admin_list'))

@admin.route("/edit_admin/<int:admin_id>", methods=['GET', 'POST'])
@login_required
@superuser_required
def edit_admin(admin_id):
    admin_to_edit = User.query.get_or_404(admin_id)
    form = EditAdminForm(obj=admin_to_edit)

    if form.validate_on_submit():
        if admin_to_edit.id == current_user.id and form.role.data != 'superadmin':
            flash('Ви не можете змінити власну роль суперадміністратора.', 'danger')
            return redirect(url_for('admin.edit_admin', admin_id=admin_id))

        admin_to_edit.name = form.name.data
        admin_to_edit.email = form.email.data
        admin_to_edit.role = form.role.data
        db.session.commit()
        flash('Дані адміністратора оновлено.', 'success')
        return redirect(url_for('admin.admin_list'))

    return render_template("edit_admin.html", form=form, admin=admin_to_edit)

# --- КЕРУВАННЯ ПРОДУКТАМИ ---

@admin.route("/add_product", methods=["GET", "POST"])
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
        return redirect(url_for("admin.admin_dashboard"))
    return render_template("add_product.html", form=form)

@admin.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
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
        return redirect(url_for("admin.admin_dashboard"))
    return render_template("edit_product.html", form=form, product=product)

@admin.route("/delete_product/<int:product_id>", methods=["POST"])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if product.img and product.img != 'default.png':
        try:
            # Використовуємо current_app для доступу до шляхів
            image_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], product.img)
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            flash(f"Помилка при видаленні файлу зображення: {e}", "danger")

    db.session.delete(product)
    db.session.commit()
    flash('Продукт видалено.', 'success')
    return redirect(url_for("admin.admin_dashboard"))

# --- КЕРУВАННЯ КАРУСЕЛЛЮ ---

@admin.route("/carousel")
@login_required
def admin_carousel():
    carousel_items = CarouselItem.query.all()
    return render_template("admin_carousel.html", carousel_items=carousel_items, admin_name=current_user.name)

@admin.route("/add_carousel_item", methods=["GET", "POST"])
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
        return redirect(url_for('admin.admin_carousel'))
    return render_template("add_carousel_item.html", form=form)

@admin.route("/carousel/edit/<int:item_id>", methods=["GET", "POST"])
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
        return redirect(url_for('admin.admin_carousel'))
    return render_template("edit_carousel.html", form=form, item=item)

@admin.route("/carousel/delete/<int:item_id>", methods=["POST"])
@login_required
def delete_carousel_item(item_id):
    item = CarouselItem.query.get_or_404(item_id)

    if item.img:
        try:
            image_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], item.img)
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            flash(f"Помилка при видаленні файлу зображення: {e}", "danger")

    db.session.delete(item)
    db.session.commit()
    flash('Слайд видалено.', 'success')
    return redirect(url_for('admin.admin_carousel'))