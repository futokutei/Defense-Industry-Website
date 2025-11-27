from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Optional, Email
from flask_wtf.file import FileField, FileAllowed

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

class LoginForm(FlaskForm):
    username = StringField('Логін', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Увійти')

class AdminForm(FlaskForm):
    username = StringField('Логін', validators=[DataRequired(), Length(min=4, max=80)])
    name = StringField('Ім\'я', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Пошта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=5)])
    submit = SubmitField('Додати')

class EditAdminForm(FlaskForm):
    name = StringField('Ім\'я', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Пошта', validators=[DataRequired(), Email()])
    role = SelectField('Роль', choices=[('admin', 'Адміністратор'), ('superadmin', 'Суперадміністратор')])
    submit = SubmitField('Зберегти')

class ProductForm(FlaskForm):
    name = StringField('Назва', validators=[DataRequired()])
    desc = TextAreaField('Опис', validators=[DataRequired()])
    img_file = FileField('Зображення', validators=[FileAllowed(ALLOWED_EXTENSIONS)])
    submit = SubmitField('Зберегти')

class CarouselItemForm(FlaskForm):
    title = StringField('Заголовок', validators=[Optional()])
    desc = TextAreaField('Опис', validators=[Optional()])
    img_file = FileField('Зображення', validators=[FileAllowed(ALLOWED_EXTENSIONS)])
    text_position = SelectField('Позиція', choices=[('left', 'Зліва'), ('right', 'Справа'), ('center', 'Центр')])
    button_text = StringField('Кнопка', validators=[Optional()])
    button_link = StringField('Лінк', validators=[Optional()])
    submit = SubmitField('Зберегти')
