# Опис Сутностей Домену (Domain Entities)

Цей документ описує структуру та поведінку ключових сутностей (Entities) у нашій системі.

## 1. User (Користувач)
**Тип:** Entity (Root Aggregate)
**Контекст:** Identity & Access

### Поля (Attributes)
* `id`: Унікальний ідентифікатор (Integer).
* `username`: Логін для входу (String, Unique).
* `email`: Електронна пошта (String, Unique).
* `password_hash`: Хеш пароля (String). Ми не зберігаємо чисті паролі.
* `role`: Рівень доступу (`admin` або `superadmin`).
* `name`: Повне ім'я співробітника.

### Поведінка (Methods)
* `set_password(password)`: Генерує безпечний хеш пароля.
* `check_password(password)`: Перевіряє введений пароль проти хешу.
* `promote_to_superadmin()`: Підвищує права користувача до рівня Superadmin.
* `is_superadmin()`: (Властивість) Повертає True, якщо роль == 'superadmin'.

---

## 2. Product (Продукт)
**Тип:** Entity
**Контекст:** Catalog

### Поля (Attributes)
* `id`: Унікальний ідентифікатор товару.
* `name`: Назва продукту (наприклад, "Atlas Robot").
* `desc`: Детальний технічний опис.
* `img`: Ім'я файлу зображення (наприклад, `robot.jpg`), що лежить у `static/img`.

### Поведінка (Methods)
* `update_details(name, desc)`: Дозволяє безпечно оновити основну інформацію про продукт.

---

## 3. CarouselItem (Елемент Слайдера)
**Тип:** Entity
**Контекст:** Marketing

### Поля (Attributes)
* `id`: Унікальний ідентифікатор слайда.
* `title`: Заголовок, що відображається поверх зображення.
* `desc`: Короткий опис або слоган.
* `img`: Фонове зображення слайда.
* `text_position`: Налаштування візуального відображення (`left`, `right`, `center`, `none`).
* `button_text`: Текст на кнопці заклику до дії (CTA).
* `button_link`: URL, куди веде кнопка.

### Поведінка (Methods)
* `set_text_position(position)`: Встановлює вирівнювання тексту, перевіряючи, чи входить значення у список дозволених (`left`, `right`...).
